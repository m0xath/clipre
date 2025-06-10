# Real-Time Clipboard Redactor

A lightweight Python tool that continuously monitors the system clipboard and automatically redacts Personally Identifiable Information (PII) using Microsoft Presidio to prevent data leaks to AI tools and malware.

## Features

- Real-time clipboard monitoring - Continuously watches for new clipboard content
- Advanced PII detection - Uses Microsoft Presidio for accurate detection of:
  - Names and personal information
  - Email addresses and phone numbers
  - Credit card numbers and SSNs
  - IP addresses and crypto addresses
  - Medical licenses and government IDs
- Automatic redaction - Replaces sensitive data with [REDACTED] placeholders
- Performance monitoring - Tracks detection accuracy and processing speed
- Minimal resource usage - Lightweight background operation
- Privacy-focused - No data logging or transmission

## Security Benefits

- Prevents accidental data leaks to cloud-based AI tools (ChatGPT, etc.)
- Protects against clipboard-hijacking malware
- Reduces risk of pasting sensitive data into untrusted applications
- Real-time protection without user intervention

## Requirements

- Windows 10/11, macOS, or Linux
- Python 3.8 or higher
- Internet connection for initial setup (downloading NLP models)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/m0xath/clipre.git
   cd clipre
   ```

2. Run the setup script:
   ```bash
   python setup.py
   ```

   This will automatically:
   - Install Python dependencies
   - Download required NLP models
   - Test the installation
   - Create startup scripts (Windows .bat file)

## Usage

### Basic Usage

Run the clipboard redactor:
```bash
python main.py
```

The tool will start monitoring your clipboard in the background. Copy any text containing PII to see it automatically redacted.

### Configuration

Customize behavior by editing `config.py`:

- Adjust polling intervals
- Configure PII entity types
- Set confidence thresholds
- Customize redaction patterns

## Performance Metrics

The tool tracks several performance metrics:

- Detection accuracy - Precision and recall for PII detection
- Processing speed - Average time to analyze and redact content
- Resource usage - Memory and CPU utilization
- Redaction statistics - Number of successful redactions

View statistics by pressing Ctrl+C to stop the tool.

## Supported PII Types

The tool detects the following PII types by default:

- PERSON - Names and personal identifiers
- EMAIL_ADDRESS - Email addresses
- PHONE_NUMBER - Phone numbers
- IP_ADDRESS - IP addresses
- CRYPTO - Cryptocurrency addresses
- LOCATION - Geographic locations
- DATE_TIME - Dates and times

For a complete list of supported recognizers and entities, see the [Presidio Supported Recognizers and Entities](https://microsoft.github.io/presidio/supported_entities/) documentation.

## Logging

The tool creates detailed logs in `clipboard_redactor.log`:

- INFO level - General operation status and redaction events
- DEBUG level - Detailed analysis information and performance metrics
- ERROR level - Error conditions and exceptions

## Limitations

- Text-only support - Images and binary clipboard data are not processed
- English language - Optimized for English text (can be extended)
- False positives - May occasionally redact non-sensitive data
- Performance impact - Slight latency on very large clipboard content

## Privacy & Security

- No data storage - Clipboard content is processed in memory only
- No network transmission - All processing happens locally
- Minimal logging - Only redaction events are logged (not content)
- Open source - Full transparency of operations

## Troubleshooting

### Common Issues

1. Import errors:
   ```bash
   python setup.py
   ```

2. Clipboard access issues:
   - Ensure no other clipboard managers are interfering
   - On Linux, you may need to install additional clipboard utilities (xclip, xsel)
   - On Windows, run as administrator if needed

3. High CPU usage:
   - Increase poll interval in config.py
   - Reduce monitored PII types

4. False positives:
   - Review and customize the PII entity list in config.py
   - Adjust Presidio confidence thresholds

### Platform-Specific Notes

**Windows:**
- The setup script creates a convenient `.bat` file for easy startup
- May require administrator privileges for clipboard access in some cases

**macOS:**
- Clipboard access should work out of the box
- Python 3.8+ recommended via Homebrew

**Linux:**
- May require additional packages: `sudo apt install xclip` (Ubuntu/Debian) or equivalent
- Ensure your desktop environment supports clipboard access

## Author

**Moath Aloufi**

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 
