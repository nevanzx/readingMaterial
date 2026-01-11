#!/usr/bin/env python
"""Test script to check if docx module can be imported"""

try:
    from docx import Document
    print("SUCCESS: python-docx imported successfully")
    print(f"Document class: {Document}")
    
    # Try creating a simple document to test functionality
    doc = Document()
    doc.add_paragraph("Test paragraph")
    print("SUCCESS: Created a sample document object")
    
except ImportError as e:
    print(f"ERROR: Import failed with ImportError: {e}")
except Exception as e:
    print(f"ERROR: Import failed with unexpected error: {e}")