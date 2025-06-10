#!/usr/bin/env python3
"""
Setup script for Real-Time Clipboard Redactor
Automates installation of dependencies and required models
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"SUCCESS: {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"SUCCESS: Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"ERROR: Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("Please install Python 3.8 or higher")
        return False

def install_requirements():
    """Install Python requirements"""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("ERROR: requirements.txt not found")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )

def download_spacy_model():
    """Download required spaCy model"""
    return run_command(
        f"{sys.executable} -m spacy download en_core_web_sm",
        "Downloading spaCy English model"
    )

def test_installation():
    """Test if installation was successful"""
    print("\nTesting installation...")
    try:
        # Test imports
        import pyperclip
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine
        import spacy
        
        # Test spaCy model
        nlp = spacy.load("en_core_web_sm")
        
        # Test Presidio engines
        analyzer = AnalyzerEngine()
        anonymizer = AnonymizerEngine()
        
        print("SUCCESS: All components installed successfully")
        return True
        
    except ImportError as e:
        print(f"ERROR: Import error: {e}")
        return False
    except OSError as e:
        print(f"ERROR: Model loading error: {e}")
        print("Try running: python -m spacy download en_core_web_sm")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False

def create_startup_script():
    """Create a Windows startup script"""
    script_content = f"""@echo off
cd /d "{os.getcwd()}"
python main.py
pause
"""
    
    try:
        with open("start_clipboard_redactor.bat", "w") as f:
            f.write(script_content)
        print("SUCCESS: Created startup script: start_clipboard_redactor.bat")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create startup script: {e}")
        return False

def main():
    """Main setup function"""
    print("Real-Time Clipboard Redactor - Setup Script")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install requirements
    if not install_requirements():
        print("\nERROR: Failed to install requirements. Please check your internet connection and try again.")
        return False
    
    # Download spaCy model
    if not download_spacy_model():
        print("\nERROR: Failed to download spaCy model. Please check your internet connection and try again.")
        return False
    
    # Test installation
    if not test_installation():
        print("\nERROR: Installation test failed. Please check the error messages above.")
        return False
    
    # Create startup script
    create_startup_script()
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETED SUCCESSFULLY!")
    print("\nNext steps:")
    print("1. Run the clipboard redactor: python main.py")
    print("2. Test the functionality: python test_redactor.py")
    print("3. For interactive testing: python test_redactor.py --interactive")
    print("4. Use start_clipboard_redactor.bat for easy startup")
    print("\nFor automatic startup on Windows:")
    print("- Add start_clipboard_redactor.bat to Windows Task Scheduler")
    print("- Or add to Windows Startup folder")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 