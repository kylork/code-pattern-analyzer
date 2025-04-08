"""
Analyzer for detecting patterns in source code files and directories.
"""

from typing import Dict, List, Optional, Set, Union
from pathlib import Path
import os
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .parser import CodeParser
from .pattern_recognizer import PatternRecognizer
from .mock_implementation import patch_analyzer
from .tree_sitter_impl import replace_mock_implementation

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """Analyzes source code files to identify patterns."""
    
    def __init__(self, use_mock: bool = False):
        """Initialize the analyzer with a parser and pattern recognizer.
        
        Args:
            use_mock: If True, use the mock implementation instead of tree-sitter
        """
        self.parser = CodeParser()
        self.pattern_recognizer = PatternRecognizer()
        self.use_mock = use_mock
        self._restore_func = None
        
        # Configure the implementation
        self._configure_implementation(use_mock)
    
    def _configure_implementation(self, use_mock: bool) -> None:
        """Configure the implementation to use (mock or real).
        
        Args:
            use_mock: If True, use the mock implementation
        """
        # Clean up any existing patch
        if self._restore_func:
            self._restore_func()
            self._restore_func = None
        
        # Apply the appropriate implementation
        if use_mock:
            logger.info("Using mock implementation")
            self._restore_func = patch_analyzer()
        else:
            logger.info("Using real tree-sitter implementation")
            self._restore_func = replace_mock_implementation()
    
    def set_implementation(self, use_mock: bool) -> None:
        """Set the implementation to use (mock or real).
        
        Args:
            use_mock: If True, use the mock implementation
        """
        if use_mock == self.use_mock:
            return  # Already using the requested implementation
        
        self.use_mock = use_mock
        self._configure_implementation(use_mock)
    
    def analyze_file(self, 
                     file_path: Union[str, Path], 
                     pattern_name: Optional[str] = None,
                     category: Optional[str] = None) -> Dict:
        """Analyze a single file for patterns.
        
        Args:
            file_path: Path to the file to analyze
            pattern_name: If provided, only look for this specific pattern
            category: If provided, only look for patterns in this category
            
        Returns:
            A dictionary with analysis results
        """
        file_path = Path(file_path)
        try:
            # Get the language
            language = self.parser._get_language_by_extension(file_path)
            if not language:
                return {"error": f"Unsupported file type: {file_path}", "file": str(file_path)}
            
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Parse the file
            ast = self.parser.parse_file(file_path)
            if not ast:
                return {"error": "Failed to parse file", "file": str(file_path)}
            
            # Recognize patterns
            patterns = self.pattern_recognizer.recognize(
                ast, code, language, pattern_name, category, str(file_path)
            )
            
            # Get summary stats
            summary = self._generate_summary(patterns)
            
            return {
                "file": str(file_path),
                "language": language,
                "patterns": patterns,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return {"error": str(e), "file": str(file_path)}
    
    def analyze_directory(self, 
                         directory: Union[str, Path], 
                         pattern_name: Optional[str] = None,
                         category: Optional[str] = None,
                         exclude_dirs: Optional[List[str]] = None,
                         file_extensions: Optional[List[str]] = None,
                         max_workers: int = 4) -> List[Dict]:
        """Analyze all files in a directory for patterns.
        
        Args:
            directory: Path to the directory to analyze
            pattern_name: If provided, only look for this specific pattern
            category: If provided, only look for patterns in this category
            exclude_dirs: List of directory names to exclude
            file_extensions: If provided, only analyze files with these extensions
            max_workers: Maximum number of worker threads for parallel processing
            
        Returns:
            A list of dictionaries with analysis results for each file
        """
        directory = Path(directory)
        if not directory.is_dir():
            raise NotADirectoryError(f"{directory} is not a directory")
            
        exclude_dirs = exclude_dirs or ['.git', 'node_modules', 'venv', '__pycache__']
        file_paths = []
        
        # Find all files to analyze
        for root, dirs, files in os.walk(directory):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # Skip files with unwanted extensions
                if file_extensions and not any(file.endswith(ext) for ext in file_extensions):
                    continue
                    
                # Skip files we can't parse
                if not self.parser._get_language_by_extension(file_path):
                    continue
                    
                file_paths.append(file_path)
        
        # Analyze files in parallel
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {
                executor.submit(self.analyze_file, path, pattern_name, category): path
                for path in file_paths
            }
            
            for future in as_completed(future_to_path):
                results.append(future.result())
                
        # Sort results by filename
        results.sort(key=lambda r: r.get('file', ''))
        
        return results
    
    def _generate_summary(self, patterns: Dict[str, List[Dict]]) -> Dict:
        """Generate a summary of the patterns found.
        
        Args:
            patterns: Pattern recognition results
            
        Returns:
            A dictionary with summary statistics
        """
        summary = {
            "total_patterns": sum(len(matches) for matches in patterns.values()),
            "pattern_counts": {name: len(matches) for name, matches in patterns.items()},
        }
        
        # Count patterns by type
        type_counts = {}
        for matches in patterns.values():
            for match in matches:
                if 'type' in match:
                    match_type = match['type']
                    type_counts[match_type] = type_counts.get(match_type, 0) + 1
        
        summary["type_counts"] = type_counts
        
        return summary
    
    def generate_report(self, results: List[Dict], output_format: str = "json") -> str:
        """Generate a report from analysis results.
        
        Args:
            results: List of analysis results from analyze_file or analyze_directory
            output_format: Format for the report (json, text, html)
            
        Returns:
            The report as a string in the specified format
        """
        if output_format == "json":
            return json.dumps(results, indent=2)
        
        elif output_format == "text":
            report = []
            for result in results:
                if "error" in result:
                    report.append(f"Error analyzing {result['file']}: {result['error']}")
                    continue
                
                report.append(f"File: {result['file']}")
                report.append(f"Language: {result['language']}")
                
                if "summary" in result:
                    summary = result["summary"]
                    report.append(f"Total patterns: {summary['total_patterns']}")
                    
                    if summary["pattern_counts"]:
                        report.append("Pattern counts:")
                        for pattern, count in summary["pattern_counts"].items():
                            report.append(f"  {pattern}: {count}")
                
                if "patterns" in result:
                    for pattern_name, matches in result["patterns"].items():
                        report.append(f"\nPattern: {pattern_name}")
                        for match in matches:
                            match_str = f"  {match.get('name', 'Unnamed')}"
                            if 'type' in match:
                                match_str += f" ({match['type']})"
                            if 'line' in match:
                                match_str += f" at line {match['line']}"
                            report.append(match_str)
                
                report.append("\n" + "-" * 80 + "\n")
            
            return "\n".join(report)
            
        elif output_format == "html":
            from .visualization import HTMLReport
            report_generator = HTMLReport(include_charts=True)
            return report_generator.generate(results)
            
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def get_available_patterns(self) -> List[str]:
        """Get a list of all available patterns.
        
        Returns:
            A list of pattern names
        """
        return self.pattern_recognizer.get_available_patterns()
    
    def get_available_categories(self) -> List[str]:
        """Get a list of all available pattern categories.
        
        Returns:
            A list of category names
        """
        return self.pattern_recognizer.get_available_categories()
    
    def get_patterns_by_category(self, category: str) -> List[str]:
        """Get a list of patterns in a category.
        
        Args:
            category: The category to look up
            
        Returns:
            A list of pattern names in the category
        """
        return self.pattern_recognizer.get_patterns_by_category(category)