#!/usr/bin/env python3
"""
Real-Time Clipboard Redactor for Windows
Monitors clipboard content and redacts PII using Microsoft Presidio
"""

import time
import threading
import logging
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime

try:
    import pyperclip
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import OperatorConfig
    from config import *  # Import configuration settings
except ImportError as e:
    print(f"Missing required dependencies: {e}")
    print("Please install required packages using: pip install -r requirements.txt")
    print("Or run the setup script: python setup.py")
    exit(1)


class ClipboardRedactor:
    """Real-time clipboard monitor and PII redactor"""
    
    def __init__(self, poll_interval: Optional[float] = None, log_level: Optional[str] = None):
        """
        Initialize the clipboard redactor
        
        Args:
            poll_interval: How often to check clipboard (seconds) - uses config if None
            log_level: Logging level - uses config if None
        """
        # Load configuration
        load_from_env()  # Load environment overrides
        config_errors = validate_config()
        if config_errors:
            print("Configuration errors:")
            for error in config_errors:
                print(f"  - {error}")
            raise ValueError("Invalid configuration")
        
        self.poll_interval = poll_interval or CLIPBOARD_POLL_INTERVAL
        self.running = False
        self.last_clipboard_hash = None
        
        # Setup logging
        log_handlers = []
        if LOG_TO_FILE:
            log_handlers.append(logging.FileHandler(LOG_FILE))
        log_handlers.append(logging.StreamHandler())
        
        logging.basicConfig(
            level=getattr(logging, (log_level or LOG_LEVEL).upper()),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=log_handlers
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize Presidio engines
        self.logger.info("Initializing Presidio engines...")
        try:
            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()
            self.logger.info("Presidio engines initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Presidio: {e}")
            raise
        
        # Performance metrics
        self.stats = {
            'total_checks': 0,
            'redactions_performed': 0,
            'avg_processing_time': 0,
            'false_positives': 0,
            'start_time': datetime.now()
        }
        
        # Use configured PII entities
        self.pii_entities = PII_ENTITIES.copy()
        self.logger.info(f"Monitoring {len(self.pii_entities)} PII entity types")
        self.logger.debug(f"PII entities: {', '.join(self.pii_entities)}")

    def _get_clipboard_hash(self, text: str) -> str:
        """Generate hash of clipboard content for change detection"""
        if HASH_ALGORITHM == "sha256":
            return hashlib.sha256(text.encode('utf-8')).hexdigest()
        elif HASH_ALGORITHM == "sha1":
            return hashlib.sha1(text.encode('utf-8')).hexdigest()
        else:  # default to md5
            return hashlib.md5(text.encode('utf-8')).hexdigest()

    def _analyze_text(self, text: str) -> list:
        """
        Analyze text for PII using Presidio
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected PII entities
        """
        try:
            start_time = time.time()
            results = self.analyzer.analyze(
                text=text,
                entities=self.pii_entities,
                language=PRESIDIO_LANGUAGE,
                score_threshold=PRESIDIO_CONFIDENCE_THRESHOLD
            )
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Update performance stats
            if ENABLE_PERFORMANCE_MONITORING:
                self.stats['total_checks'] += 1
                self.stats['avg_processing_time'] = (
                    (self.stats['avg_processing_time'] * (self.stats['total_checks'] - 1) + processing_time) 
                    / self.stats['total_checks']
                )
            
            self.logger.debug(f"Analysis completed in {processing_time:.2f}ms, found {len(results)} entities")
            
            # Check performance target
            if ENABLE_PERFORMANCE_MONITORING and processing_time > PERFORMANCE_TARGET_MS:
                self.logger.warning(f"Processing time {processing_time:.2f}ms exceeds target {PERFORMANCE_TARGET_MS}ms")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing text: {e}")
            return []

    def _redact_text(self, text: str, analyzer_results: list) -> str:
        """
        Redact PII from text using Presidio anonymizer
        
        Args:
            text: Original text
            analyzer_results: Results from Presidio analyzer
            
        Returns:
            Redacted text
        """
        try:
            if not analyzer_results:
                return text
            
            # Configure redaction operators using config
            operators = {}
            for entity_type, redaction_text in REDACTION_PATTERNS.items():
                operators[entity_type] = OperatorConfig("replace", {"new_value": redaction_text})
            
            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=analyzer_results,
                operators=operators
            )
            
            return anonymized_result.text
            
        except Exception as e:
            self.logger.error(f"Error redacting text: {e}")
            return text

    def _process_clipboard_content(self, content: str) -> Optional[str]:
        """
        Process clipboard content and return redacted version if needed
        
        Args:
            content: Clipboard content
            
        Returns:
            Redacted content if PII found, None if no changes needed
        """
        if not content or not content.strip():
            return None
        
        # Skip very long content to avoid performance issues
        if len(content) > MAX_CLIPBOARD_SIZE:
            self.logger.warning(f"Skipping large clipboard content ({len(content)} chars, max: {MAX_CLIPBOARD_SIZE})")
            return None
        
        # Analyze for PII
        pii_results = self._analyze_text(content)
        
        if not pii_results:
            self.logger.debug("No PII detected in clipboard content")
            return None
        
        # Log detected PII types (without content for privacy)
        detected_types = [result.entity_type for result in pii_results]
        confidence_scores = [f"{result.entity_type}({result.score:.2f})" for result in pii_results]
        
        self.logger.info(f"PII detected: {', '.join(set(detected_types))}")
        self.logger.debug(f"PII details: {', '.join(confidence_scores)}")
        
        # Redact the content
        redacted_content = self._redact_text(content, pii_results)
        
        if redacted_content != content:
            self.stats['redactions_performed'] += 1
            self.logger.info(f"Clipboard content redacted ({len(pii_results)} entities)")
            
            # Save redaction example if enabled
            if SAVE_REDACTION_EXAMPLES:
                self._save_redaction_example(content, redacted_content, detected_types)
            
            return redacted_content
        
        return None

    def _save_redaction_example(self, original: str, redacted: str, pii_types: list):
        """Save redaction example for analysis (if enabled)"""
        try:
            import json
            from pathlib import Path
            
            example = {
                "timestamp": datetime.now().isoformat(),
                "original_length": len(original),
                "redacted_length": len(redacted),
                "pii_types": pii_types,
                "redacted_text": redacted  # Only save redacted version for privacy
            }
            
            examples_file = Path(EXAMPLES_FILE)
            examples = []
            
            if examples_file.exists():
                with open(examples_file, 'r') as f:
                    examples = json.load(f)
            
            examples.append(example)
            
            # Keep only last 100 examples
            if len(examples) > 100:
                examples = examples[-100:]
            
            with open(examples_file, 'w') as f:
                json.dump(examples, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save redaction example: {e}")

    def _monitor_clipboard(self):
        """Main clipboard monitoring loop"""
        self.logger.info("Starting clipboard monitoring...")
        
        while self.running:
            try:
                # Get current clipboard content
                current_content = pyperclip.paste()
                
                if current_content:
                    if ENABLE_CONTENT_HASHING:
                        current_hash = self._get_clipboard_hash(current_content)
                        
                        # Check if clipboard content has changed
                        if current_hash != self.last_clipboard_hash:
                            self.last_clipboard_hash = current_hash
                            self.logger.debug("Clipboard content changed, analyzing...")
                            
                            # Process the content
                            redacted_content = self._process_clipboard_content(current_content)
                            
                            if redacted_content:
                                # Update clipboard with redacted content
                                pyperclip.copy(redacted_content)
                                self.last_clipboard_hash = self._get_clipboard_hash(redacted_content)
                                self.logger.info("Clipboard updated with redacted content")
                    else:
                        # Process without hashing (less efficient but simpler)
                        redacted_content = self._process_clipboard_content(current_content)
                        if redacted_content:
                            pyperclip.copy(redacted_content)
                            self.logger.info("Clipboard updated with redacted content")
                
                time.sleep(self.poll_interval)
                
            except Exception as e:
                self.logger.error(f"Error in clipboard monitoring: {e}")
                time.sleep(1)  # Wait longer on error

    def start(self):
        """Start the clipboard monitoring in a background thread"""
        if self.running:
            self.logger.warning("Clipboard redactor is already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Clipboard redactor started successfully")

    def stop(self):
        """Stop the clipboard monitoring"""
        if not self.running:
            self.logger.warning("Clipboard redactor is not running")
            return
        
        self.running = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=2)
        self.logger.info("Clipboard redactor stopped")

    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        runtime = datetime.now() - self.stats['start_time']
        return {
            **self.stats,
            'runtime_seconds': runtime.total_seconds(),
            'checks_per_second': self.stats['total_checks'] / max(runtime.total_seconds(), 1),
            'config': {
                'poll_interval': self.poll_interval,
                'max_clipboard_size': MAX_CLIPBOARD_SIZE,
                'pii_entities_count': len(self.pii_entities),
                'confidence_threshold': PRESIDIO_CONFIDENCE_THRESHOLD,
                'performance_target_ms': PERFORMANCE_TARGET_MS
            }
        }

    def print_stats(self):
        """Print current performance statistics"""
        stats = self.get_stats()
        print("\n" + "="*50)
        print("CLIPBOARD REDACTOR STATISTICS")
        print("="*50)
        print(f"Runtime: {stats['runtime_seconds']:.1f} seconds")
        print(f"Total clipboard checks: {stats['total_checks']}")
        print(f"Redactions performed: {stats['redactions_performed']}")
        print(f"Average processing time: {stats['avg_processing_time']:.2f}ms")
        print(f"Checks per second: {stats['checks_per_second']:.2f}")
        print(f"Performance target: {stats['config']['performance_target_ms']}ms")
        print(f"PII entities monitored: {stats['config']['pii_entities_count']}")
        print("="*50)


def main():
    """Main function to run the clipboard redactor"""
    print("Real-Time Clipboard Redactor for Windows")
    print("Using Microsoft Presidio for PII Detection")
    print("-" * 50)
    
    # Create and start the redactor
    try:
        redactor = ClipboardRedactor()
    except Exception as e:
        print(f"Failed to initialize clipboard redactor: {e}")
        print("Please check your configuration and dependencies.")
        return
    
    try:
        redactor.start()
        print("Clipboard redactor is running...")
        print("Copy some text with PII to test the redaction.")
        print("Press Ctrl+C to stop.")
        
        # Keep the main thread alive
        while True:
            time.sleep(10)
            # Print stats every 10 seconds in debug mode
            if redactor.logger.level <= logging.DEBUG:
                redactor.print_stats()
                
    except KeyboardInterrupt:
        print("\nShutting down clipboard redactor...")
        redactor.stop()
        redactor.print_stats()
        print("Goodbye!")
    except Exception as e:
        print(f"Unexpected error: {e}")
        redactor.stop()


if __name__ == "__main__":
    main()
