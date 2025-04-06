"""
Tree-sitter language manager for fetching, building, and loading language grammars.
"""

import os
import shutil
import subprocess
import importlib.util
import sys
import logging
from pathlib import Path
from typing import Dict, Optional, Set, Union

import tree_sitter
from tree_sitter import Language, Parser

logger = logging.getLogger(__name__)

class TreeSitterManager:
    """Manages tree-sitter language grammars and parsers."""
    
    # Default languages to support
    DEFAULT_LANGUAGES = {
        'python': 'https://github.com/tree-sitter/tree-sitter-python',
        'javascript': 'https://github.com/tree-sitter/tree-sitter-javascript',
        'typescript': 'https://github.com/tree-sitter/tree-sitter-typescript',
        'ruby': 'https://github.com/tree-sitter/tree-sitter-ruby',
        'go': 'https://github.com/tree-sitter/tree-sitter-go',
        'java': 'https://github.com/tree-sitter/tree-sitter-java',
        'c': 'https://github.com/tree-sitter/tree-sitter-c',
        'cpp': 'https://github.com/tree-sitter/tree-sitter-cpp',
        'rust': 'https://github.com/tree-sitter/tree-sitter-rust',
    }
    
    def __init__(self, languages_dir: Optional[str] = None):
        """Initialize the tree-sitter manager.
        
        Args:
            languages_dir: Directory to store language definitions. If None,
                uses the 'tree_sitter_languages' directory in the src directory.
        """
        # Set up directories
        if languages_dir is None:
            self.languages_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                'tree_sitter_languages'
            )
        else:
            self.languages_dir = languages_dir
            
        self.build_dir = os.path.join(self.languages_dir, 'build')
        
        # Create directories if they don't exist
        os.makedirs(self.languages_dir, exist_ok=True)
        os.makedirs(self.build_dir, exist_ok=True)
        
        # Initialize language cache
        self.language_cache: Dict[str, Language] = {}
        self.parser_cache: Dict[str, Parser] = {}
        
        # File extension to language mapping
        self.extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.rb': 'ruby',
            '.go': 'go',
            '.java': 'java',
            '.c': 'c',
            '.h': 'c',
            '.cpp': 'cpp',
            '.hpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.rs': 'rust',
        }
    
    def get_language_by_extension(self, file_path: Union[str, Path]) -> Optional[str]:
        """Determine the language based on file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            The language name or None if the extension is not recognized
        """
        ext = os.path.splitext(str(file_path))[1].lower()
        return self.extension_map.get(ext)
    
    def ensure_language_installed(self, language_name: str) -> bool:
        """Ensure a language grammar is installed.
        
        Args:
            language_name: Name of the language (e.g., 'python')
            
        Returns:
            True if the language is available, False otherwise
        """
        if language_name in self.language_cache:
            return True
            
        # Check if the language is already built
        library_path = os.path.join(self.build_dir, f"{language_name}.so")
        if os.path.exists(library_path):
            try:
                self.load_language(language_name, library_path)
                return True
            except Exception as e:
                logger.warning(f"Failed to load existing language {language_name}: {e}")
                # Continue to rebuild
                
        # Try to build the language
        return self.build_language(language_name)
    
    def build_language(self, language_name: str) -> bool:
        """Build a language grammar.
        
        Args:
            language_name: Name of the language (e.g., 'python')
            
        Returns:
            True if the build was successful, False otherwise
        """
        if language_name not in self.DEFAULT_LANGUAGES:
            logger.error(f"Unknown language: {language_name}")
            return False
            
        repo_url = self.DEFAULT_LANGUAGES[language_name]
        repo_dir = os.path.join(self.languages_dir, language_name)
        
        # Clone the repository if it doesn't exist
        if not os.path.exists(repo_dir):
            try:
                logger.info(f"Cloning {repo_url} to {repo_dir}")
                subprocess.run(
                    ['git', 'clone', repo_url, repo_dir],
                    check=True, capture_output=True
                )
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to clone {repo_url}: {e}")
                return False
        
        # Build the grammar
        try:
            # Special case for TypeScript which has multiple grammars
            if language_name == 'typescript':
                return self._build_typescript()
                
            # For other languages, build normally
            logger.info(f"Building {language_name} grammar")
            
            # Determine the source path based on language specifics
            src_path = self._get_src_path(language_name, repo_dir)
            
            # Build the language
            Language.build_library(
                os.path.join(self.build_dir, f"{language_name}.so"),
                [src_path]
            )
            
            # Load the language
            return self.load_language(language_name)
            
        except Exception as e:
            logger.error(f"Failed to build {language_name}: {e}")
            return False
    
    def _get_src_path(self, language_name: str, repo_dir: str) -> str:
        """Get the source path for a language grammar.
        
        Args:
            language_name: Name of the language
            repo_dir: Directory of the language repository
            
        Returns:
            The path to the grammar source directory
        """
        # Check for a 'src' directory
        src_dir = os.path.join(repo_dir, 'src')
        if os.path.exists(src_dir):
            return src_dir
            
        # Otherwise, use the repo directory
        return repo_dir
    
    def _build_typescript(self) -> bool:
        """Special case for building TypeScript which has multiple grammars.
        
        Returns:
            True if the build was successful, False otherwise
        """
        repo_dir = os.path.join(self.languages_dir, 'typescript')
        
        try:
            # TypeScript has multiple parsers in different subdirectories
            ts_src_path = os.path.join(repo_dir, 'typescript', 'src')
            tsx_src_path = os.path.join(repo_dir, 'tsx', 'src')
            
            # Build TypeScript grammar
            Language.build_library(
                os.path.join(self.build_dir, "typescript.so"),
                [ts_src_path]
            )
            
            # Build TSX grammar
            Language.build_library(
                os.path.join(self.build_dir, "tsx.so"),
                [tsx_src_path]
            )
            
            # Load the languages
            self.load_language('typescript')
            self.load_language('tsx', os.path.join(self.build_dir, "tsx.so"))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to build TypeScript: {e}")
            return False
    
    def load_language(self, language_name: str, library_path: Optional[str] = None) -> bool:
        """Load a language from a compiled grammar.
        
        Args:
            language_name: Name of the language (e.g., 'python')
            library_path: Path to the compiled grammar. If None, uses the
                default path in the build directory.
                
        Returns:
            True if the language was loaded successfully, False otherwise
        """
        if language_name in self.language_cache:
            return True
            
        if library_path is None:
            library_path = os.path.join(self.build_dir, f"{language_name}.so")
            
        try:
            language = Language(library_path, language_name)
            self.language_cache[language_name] = language
            return True
        except Exception as e:
            logger.error(f"Failed to load {language_name}: {e}")
            return False
    
    def get_parser(self, language_name: str) -> Optional[Parser]:
        """Get a parser for a language.
        
        Args:
            language_name: Name of the language (e.g., 'python')
            
        Returns:
            A tree-sitter Parser or None if the language is not available
        """
        # Check if parser is already cached
        if language_name in self.parser_cache:
            return self.parser_cache[language_name]
            
        # Ensure the language is available
        if not self.ensure_language_installed(language_name):
            return None
            
        # Create a new parser
        parser = Parser()
        parser.set_language(self.language_cache[language_name])
        
        # Cache the parser
        self.parser_cache[language_name] = parser
        return parser
    
    def parse_code(self, code: str, language_name: str) -> Optional[tree_sitter.Tree]:
        """Parse code with a specific language.
        
        Args:
            code: Code to parse
            language_name: Name of the language (e.g., 'python')
            
        Returns:
            A tree-sitter Tree or None if parsing failed
        """
        parser = self.get_parser(language_name)
        if parser is None:
            return None
            
        return parser.parse(bytes(code, 'utf-8'))
    
    def parse_file(self, file_path: Union[str, Path]) -> Optional[tree_sitter.Tree]:
        """Parse a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            A tree-sitter Tree or None if parsing failed
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        language_name = self.get_language_by_extension(file_path)
        if language_name is None:
            raise ValueError(f"Unsupported file type: {file_path}")
            
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
            
        return self.parse_code(code, language_name)
    
    def query(self, tree: tree_sitter.Tree, query_string: str, language_name: str) -> tree_sitter.Query:
        """Create a Query for a specific language.
        
        Args:
            tree: The tree-sitter Tree to query
            query_string: The query string in tree-sitter query language
            language_name: Name of the language (e.g., 'python')
            
        Returns:
            A tree-sitter Query
        """
        if language_name not in self.language_cache:
            if not self.ensure_language_installed(language_name):
                raise ValueError(f"Language {language_name} is not available")
                
        language = self.language_cache[language_name]
        query = language.query(query_string)
        
        return query
    
    def get_node_text(self, node: tree_sitter.Node, code: Union[str, bytes]) -> str:
        """Get the text of a node from the original source code.
        
        Args:
            node: A tree-sitter node
            code: The original source code
            
        Returns:
            The text corresponding to the node
        """
        if isinstance(code, str):
            code_bytes = bytes(code, 'utf-8')
        else:
            code_bytes = code
            
        return node.text.decode('utf-8')
    
    def get_available_languages(self) -> Set[str]:
        """Get a list of available languages.
        
        Returns:
            A set of language names
        """
        return set(self.DEFAULT_LANGUAGES.keys())