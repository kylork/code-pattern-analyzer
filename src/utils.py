"""
Utility functions for the Code Pattern Analyzer.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union, Set, Tuple
from pathlib import Path
import difflib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime

from .analyzer import CodeAnalyzer

logger = logging.getLogger(__name__)

class AnalysisComparer:
    """Compare analysis results between different files or analyzers."""
    
    def __init__(self, analyzer: Optional[CodeAnalyzer] = None):
        """Initialize the comparer.
        
        Args:
            analyzer: Optional analyzer to use. If None, creates a new one.
        """
        self.analyzer = analyzer or CodeAnalyzer()
    
    def compare_files(self, 
                     file_paths: List[Union[str, Path]],
                     pattern_name: Optional[str] = None,
                     category: Optional[str] = None,
                     output_format: str = "text") -> str:
        """Compare pattern detection between multiple files.
        
        Args:
            file_paths: List of file paths to compare
            pattern_name: If provided, only look for this specific pattern
            category: If provided, only look for patterns in this category
            output_format: Output format (json, text, html)
            
        Returns:
            Comparison report in the specified format
        """
        # Analyze each file
        results = []
        for file_path in file_paths:
            result = self.analyzer.analyze_file(file_path, pattern_name, category)
            results.append(result)
        
        # Generate the comparison report
        if output_format == "json":
            return json.dumps({
                "comparison_type": "files",
                "files": [r.get("file") for r in results],
                "results": results,
                "summary": self._generate_comparison_summary(results)
            }, indent=2)
        
        elif output_format == "text":
            report = ["# File Comparison Report"]
            report.append("\nFiles compared:")
            for i, result in enumerate(results):
                report.append(f"  {i+1}. {result.get('file')}")
            
            # Add summary
            summary = self._generate_comparison_summary(results)
            report.append("\n## Summary")
            
            # Common patterns
            report.append("\nCommon patterns:")
            if summary["common_patterns"]:
                for pattern in summary["common_patterns"]:
                    report.append(f"  - {pattern}")
            else:
                report.append("  (None)")
            
            # Unique patterns by file
            report.append("\nUnique patterns by file:")
            for i, result in enumerate(results):
                file_name = Path(result.get("file", f"File {i+1}")).name
                unique_patterns = summary["unique_patterns_by_file"].get(i, [])
                
                if unique_patterns:
                    report.append(f"  {file_name}:")
                    for pattern in unique_patterns:
                        report.append(f"    - {pattern}")
                else:
                    report.append(f"  {file_name}: (None)")
            
            # Pattern counts
            report.append("\n## Pattern Counts")
            for i, result in enumerate(results):
                file_name = Path(result.get("file", f"File {i+1}")).name
                
                if "summary" in result and "pattern_counts" in result["summary"]:
                    counts = result["summary"]["pattern_counts"]
                    report.append(f"\n{file_name}:")
                    
                    for pattern, count in counts.items():
                        report.append(f"  {pattern}: {count}")
                else:
                    report.append(f"\n{file_name}: No patterns detected")
            
            return "\n".join(report)
            
        elif output_format == "html":
            from .visualization import HTMLReport
            report_generator = HTMLReport(
                title="Code Pattern Comparison Report",
                include_charts=True
            )
            return report_generator.generate(results)
        
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _generate_comparison_summary(self, results: List[Dict]) -> Dict:
        """Generate a summary of the comparison.
        
        Args:
            results: List of analysis results
            
        Returns:
            Dictionary with comparison summary
        """
        # Extract pattern names from each result
        patterns_by_file = []
        for result in results:
            if "patterns" in result:
                patterns_by_file.append(set(result["patterns"].keys()))
            else:
                patterns_by_file.append(set())
        
        # Find common patterns (present in all files)
        common_patterns = set.intersection(*patterns_by_file) if patterns_by_file else set()
        
        # Find unique patterns for each file
        unique_patterns_by_file = {}
        for i, patterns in enumerate(patterns_by_file):
            # Patterns in this file but not in any other file
            other_patterns = set.union(*(patterns_by_file[j] for j in range(len(patterns_by_file)) if j != i))
            unique_patterns = patterns - other_patterns
            
            if unique_patterns:
                unique_patterns_by_file[i] = sorted(list(unique_patterns))
        
        return {
            "common_patterns": sorted(list(common_patterns)),
            "unique_patterns_by_file": unique_patterns_by_file
        }


class BatchAnalyzer:
    """Run pattern analysis on multiple files in parallel."""
    
    def __init__(self, 
                 analyzer: Optional[CodeAnalyzer] = None, 
                 max_workers: int = 4):
        """Initialize the batch analyzer.
        
        Args:
            analyzer: Optional analyzer to use. If None, creates a new one.
            max_workers: Maximum number of parallel workers
        """
        self.analyzer = analyzer or CodeAnalyzer()
        self.max_workers = max_workers
    
    def analyze_files(self, 
                     file_paths: List[Union[str, Path]],
                     pattern_name: Optional[str] = None,
                     category: Optional[str] = None) -> List[Dict]:
        """Analyze multiple files in parallel.
        
        Args:
            file_paths: List of file paths to analyze
            pattern_name: If provided, only look for this specific pattern
            category: If provided, only look for patterns in this category
            
        Returns:
            List of analysis results
        """
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {
                executor.submit(self.analyzer.analyze_file, path, pattern_name, category): path
                for path in file_paths
            }
            
            for future in as_completed(future_to_path):
                results.append(future.result())
                
        # Sort results by filename
        results.sort(key=lambda r: str(r.get('file', '')))
        
        return results
    
    def analyze_directories(self, 
                           directories: List[Union[str, Path]],
                           pattern_name: Optional[str] = None,
                           category: Optional[str] = None,
                           exclude_dirs: Optional[List[str]] = None,
                           file_extensions: Optional[List[str]] = None) -> List[Dict]:
        """Analyze multiple directories in parallel.
        
        Args:
            directories: List of directory paths to analyze
            pattern_name: If provided, only look for this specific pattern
            category: If provided, only look for patterns in this category
            exclude_dirs: List of directory names to exclude
            file_extensions: If provided, only analyze files with these extensions
            
        Returns:
            List of analysis results
        """
        all_results = []
        
        for directory in directories:
            # Analyze each directory
            results = self.analyzer.analyze_directory(
                directory,
                pattern_name=pattern_name,
                category=category,
                exclude_dirs=exclude_dirs,
                file_extensions=file_extensions,
                max_workers=self.max_workers
            )
            
            all_results.extend(results)
        
        return all_results


class ReportGenerator:
    """Generate comprehensive reports from analysis results."""
    
    def __init__(self, 
                 analyzer: Optional[CodeAnalyzer] = None,
                 output_dir: Optional[Union[str, Path]] = None):
        """Initialize the report generator.
        
        Args:
            analyzer: Optional analyzer to use. If None, creates a new one.
            output_dir: Directory to save reports. If None, uses current dir.
        """
        self.analyzer = analyzer or CodeAnalyzer()
        self.output_dir = output_dir or os.getcwd()
    
    def generate_report(self, 
                       results: List[Dict],
                       output_format: str = "html",
                       title: str = "Code Pattern Analysis Report",
                       filename: Optional[str] = None) -> str:
        """Generate a report from analysis results.
        
        Args:
            results: List of analysis results
            output_format: Output format (json, text, html)
            title: Title for the report
            filename: Optional filename to save the report. If None, generates one.
            
        Returns:
            Path to the saved report file
        """
        # Generate the report content
        if output_format == "html":
            from .visualization import HTMLReport
            report_generator = HTMLReport(title=title, include_charts=True)
            content = report_generator.generate(results)
        else:
            content = self.analyzer.generate_report(results, output_format)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"pattern-analysis-{timestamp}.{output_format}"
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Save the report
        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path