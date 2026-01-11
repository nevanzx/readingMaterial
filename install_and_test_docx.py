import subprocess
import sys

# Install python-docx
result = subprocess.run([sys.executable, "-m", "pip", "install", "python-docx"], capture_output=True, text=True)
print("Installation completed with return code:", result.returncode)
if result.stdout:
    print("Stdout:", result.stdout)
if result.stderr:
    print("Stderr:", result.stderr)

# Test import
try:
    import docx
    print("SUCCESS: python-docx imported successfully")
    
    # Create a simple document to test functionality
    doc = docx.Document()
    doc.add_paragraph("Test document created successfully!")
    doc.save("test_doc.docx")
    print("SUCCESS: Test document created successfully!")
    
except ImportError as e:
    print(f"FAILED: Import error: {e}")
except Exception as e:
    print(f"FAILED: Other error: {e}")