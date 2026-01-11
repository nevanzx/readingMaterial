import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    from docx import Document
    print("SUCCESS: Successfully imported Document from docx")
    doc = Document()
    print("SUCCESS: Created a Document object")
except ImportError as e:
    print(f"FAILED: ImportError - {e}")
    print("This means the python-docx package is not installed properly.")
except Exception as e:
    print(f"FAILED: Unexpected error - {e}")