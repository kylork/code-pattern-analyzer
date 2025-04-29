"""
Sample implementation of the Factory Method pattern in Python.
"""

from abc import ABC, abstractmethod


# Product interface
class Document(ABC):
    @abstractmethod
    def open(self):
        pass
    
    @abstractmethod
    def save(self):
        pass


# Concrete products
class PDFDocument(Document):
    def open(self):
        return "Opening PDF document"
    
    def save(self):
        return "Saving PDF document"


class WordDocument(Document):
    def open(self):
        return "Opening Word document"
    
    def save(self):
        return "Saving Word document"


class TextDocument(Document):
    def open(self):
        return "Opening text document"
    
    def save(self):
        return "Saving text document"


# Creator (Factory) class
class DocumentFactory:
    @staticmethod
    def create_document(doc_type):
        """
        Factory method to create documents based on type.
        """
        if doc_type == "pdf":
            return PDFDocument()
        elif doc_type == "word":
            return WordDocument()
        elif doc_type == "text":
            return TextDocument()
        else:
            raise ValueError(f"Unknown document type: {doc_type}")


# Usage example
if __name__ == "__main__":
    # Create documents using the factory
    pdf = DocumentFactory.create_document("pdf")
    word = DocumentFactory.create_document("word")
    text = DocumentFactory.create_document("text")
    
    # Use the documents
    print(pdf.open())
    print(word.save())
    print(text.open())


# Another example with specialized factories
class PDFFactory:
    def create_document(self):
        return PDFDocument()


class WordFactory:
    def create_document(self):
        return WordDocument()


class TextFactory:
    def create_document(self):
        return TextDocument()


# Function factory
def create_document(doc_type):
    """
    Factory function for creating documents.
    """
    if doc_type == "pdf":
        return PDFDocument()
    elif doc_type == "word":
        return WordDocument()
    elif doc_type == "text":
        return TextDocument()
    else:
        raise ValueError(f"Unknown document type: {doc_type}")