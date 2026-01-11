#!/usr/bin/env python3
"""Test script to verify python-docx installation."""

import sys

print("Python executable:", sys.executable)
print("Python version:", sys.version)

try:
    import docx
    print("python-docx imported successfully")
    print(f"Module location: {docx.__file__ if hasattr(docx, '__file__') else 'N/A'}")

    # Create a simple document to test functionality
    doc = docx.Document()
    doc.add_paragraph("Test document created successfully!")
    doc.save("test_doc.docx")
    print("Test document created successfully!")

except ImportError as e:
    print(f"Import error: {e}")
    import subprocess
    result = subprocess.run([sys.executable, "-m", "pip", "install", "python-docx"], capture_output=True, text=True)
    print("Installation result:", result.returncode)
    print("Installation stdout:", result.stdout)
    print("Installation stderr:", result.stderr)

    # Try importing again after installation
    try:
        import docx
        print("After installation - python-docx imported successfully")
    except ImportError as e2:
        print(f"After installation - Import error: {e2}")

except Exception as e:
    print(f"Other error: {e}")