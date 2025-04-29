"""
Sample code that shows an opportunity for applying the Factory Method pattern.

This file contains code that creates different types of objects based on
a condition (if-else statements), which is a good candidate for refactoring
using the Factory Method pattern.
"""

from abc import ABC, abstractmethod

# Abstract Product
class Product(ABC):
    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def save(self):
        pass

class PDFDocument(Product):
    def open(self):
        return "Opening PDF document"
    
    def save(self):
        return "Saving PDF document"


class WordDocument(Product):
    def open(self):
        return "Opening Word document"
    
    def save(self):
        return "Saving Word document"


class TextDocument(Product):
    def open(self):
        return "Opening text document"
    
    def save(self):
        return "Saving text document"


class CSVDocument(Product):
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

# Creator (Factory) interface
class Creator(ABC):
    @abstractmethod
    def create_document(self):
        pass

# Concrete Creator for TextDocument
class TextDocumentCreator(Creator):
    def create_document(self):
        return TextDocument()

# Concrete Creator for PDFDocument
class PDFDocumentCreator(Creator):
    def create_document(self):
        return PDFDocument()

# Concrete Creator for CSVDocument
class CSVDocumentCreator(Creator):
    def create_document(self):
        return CSVDocument()

# Concrete Creator for WordDocument
class WordDocumentCreator(Creator):
    def create_document(self):
        return WordDocument()



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

# Client code example
def client_code(creator: Creator):
    # Use the factory method to create a product
    product = creator.create_document()
    # Use the product
    return product

# Usage example
if __name__ == '__main__':
    # Create and use a TextDocumentCreator
    creator = TextDocumentCreator()
    product = client_code(creator)
    print(product)

    # Create and use a PDFDocumentCreator
    creator = PDFDocumentCreator()
    product = client_code(creator)
    print(product)

    # Create and use a CSVDocumentCreator
    creator = CSVDocumentCreator()
    product = client_code(creator)
    print(product)

    # Create and use a WordDocumentCreator
    creator = WordDocumentCreator()
    product = client_code(creator)
    print(product)
