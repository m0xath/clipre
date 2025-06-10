#!/bin/bash
# Startup script for clipboard redactor

# Check if virtual environment exists
if [ ! -d "clipre_env" ]; then
    echo "ERROR: Virtual environment not found. Please run setup first:"
    echo "  python setup.py"
    echo "  Or manually: python -m venv clipre_env && source clipre_env/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source clipre_env/bin/activate

# Check if dependencies are installed
python -c "import presidio_analyzer, presidio_anonymizer, pyperclip" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: Dependencies not installed. Installing now..."
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
fi

echo "SUCCESS: Environment ready. Starting clipboard redactor..."
echo "Press Ctrl+C to stop."
echo

# Run the main script
python main.py 