"""
Sample code that shows an opportunity for applying the Factory Method pattern.

This file contains code that creates different types of objects based on
a condition (if-else statements), which is a good candidate for refactoring
using the Factory Method pattern.
"""

class PDFDocument:
    def open(self):
        return "Opening PDF document"
    
    def save(self):
        return "Saving PDF document"


class WordDocument:
    def open(self):
        return "Opening Word document"
    
    def save(self):
        return "Saving Word document"


class TextDocument:
    def open(self):
        return "Opening text document"
    
    def save(self):
        return "Saving text document"


class CSVDocument:
    def open(self):
        return "Opening CSV document"
    
    def save(self):
        return "Saving CSV document"


# This function creates documents based on the file extension
# It could be refactored to use the Factory Method pattern
def create_document(file_path):
    """Create a document object based on the file extension."""
    # Extract the file extension
    extension = file_path.split('.')[-1].lower()
    
    # Create the appropriate document type
    if extension == 'pdf':
        return PDFDocument()
    elif extension == 'docx' or extension == 'doc':
        return WordDocument()
    elif extension == 'txt':
        return TextDocument()
    elif extension == 'csv':
        return CSVDocument()
    else:
        raise ValueError(f"Unsupported file type: {extension}")


# Usage example
def process_document(file_path):
    try:
        # Create the document using conditional logic
        document = create_document(file_path)
        
        # Use the document
        print(f"Processing {file_path}...")
        print(document.open())
        # Do some processing...
        print(document.save())
        
        return True
    except ValueError as e:
        print(f"Error: {e}")
        return False


# Test with different file types
if __name__ == "__main__":
    files = [
        "report.pdf",
        "letter.docx",
        "notes.txt",
        "data.csv",
        "image.png"  # This will raise an error
    ]
    
    for file in files:
        print(f"\nProcessing {file}:")
        process_document(file)