"""
Refactoring Suggestion module.

This module provides functionality to generate refactoring suggestions
based on pattern detection, code smells, architectural analysis, flow analysis,
and complexity metrics.
"""

from enum import Enum
from typing import Dict, List, Optional, Set, Any, Union
import os
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RefactoringType(Enum):
    """Types of code refactorings."""
    EXTRACT_METHOD = "extract_method"
    EXTRACT_CLASS = "extract_class"
    INLINE_METHOD = "inline_method"
    RENAME = "rename"
    MOVE = "move"
    PULL_UP = "pull_up"
    PUSH_DOWN = "push_down"
    ENCAPSULATE_FIELD = "encapsulate_field"
    REPLACE_CONDITIONAL_WITH_POLYMORPHISM = "replace_conditional_with_polymorphism"
    INTRODUCE_PARAMETER_OBJECT = "introduce_parameter_object"
    INTRODUCE_NULL_OBJECT = "introduce_null_object"
    FACTORY_METHOD = "factory_method"
    STRATEGY = "strategy"
    OBSERVER = "observer"
    DECORATOR = "decorator"
    SINGLETON = "singleton"
    ARCHITECTURAL = "architectural"
    CUSTOM = "custom"

class SuggestionImpact(Enum):
    """Impact level of a refactoring suggestion."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RefactoringSuggestion:
    """Represents a code refactoring suggestion."""
    
    def __init__(
        self,
        refactoring_type: RefactoringType,
        description: str,
        file_path: str,
        line_range: tuple,
        impact: SuggestionImpact,
        source: str,
        details: Dict[str, Any] = None,
        before_code: str = None,
        after_code: str = None,
        benefits: List[str] = None,
        effort: int = 3,  # 1-5 scale
        affected_components: List[str] = None
    ):
        """Initialize a refactoring suggestion.
        
        Args:
            refactoring_type: Type of refactoring
            description: Description of the refactoring
            file_path: Path to the file to refactor
            line_range: Range of lines to refactor
            impact: Impact level of the refactoring
            source: Source of the suggestion (pattern, smell, flow, etc.)
            details: Additional details specific to the refactoring type
            before_code: Example code before refactoring
            after_code: Example code after refactoring
            benefits: List of benefits from applying this refactoring
            effort: Estimated effort level (1-5)
            affected_components: List of components affected by this refactoring
        """
        self.refactoring_type = refactoring_type
        self.description = description
        self.file_path = file_path
        self.line_range = line_range
        self.impact = impact
        self.source = source
        self.details = details or {}
        self.before_code = before_code
        self.after_code = after_code
        self.benefits = benefits or []
        self.effort = max(1, min(5, effort))  # Clamp to 1-5
        self.affected_components = affected_components or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the refactoring suggestion to a dictionary.
        
        Returns:
            Dictionary representation of the suggestion
        """
        return {
            "refactoring_type": self.refactoring_type.value,
            "description": self.description,
            "file_path": self.file_path,
            "line_range": self.line_range,
            "impact": self.impact.value,
            "source": self.source,
            "details": self.details,
            "before_code": self.before_code,
            "after_code": self.after_code,
            "benefits": self.benefits,
            "effort": self.effort,
            "affected_components": self.affected_components
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RefactoringSuggestion':
        """Create a RefactoringSuggestion from a dictionary.
        
        Args:
            data: Dictionary representation of a suggestion
            
        Returns:
            A new RefactoringSuggestion instance
        """
        return cls(
            refactoring_type=RefactoringType(data["refactoring_type"]),
            description=data["description"],
            file_path=data["file_path"],
            line_range=tuple(data["line_range"]),
            impact=SuggestionImpact(data["impact"]),
            source=data["source"],
            details=data.get("details"),
            before_code=data.get("before_code"),
            after_code=data.get("after_code"),
            benefits=data.get("benefits"),
            effort=data.get("effort", 3),
            affected_components=data.get("affected_components")
        )

class SuggestionGenerator:
    """Base class for refactoring suggestion generators."""
    
    def __init__(self):
        """Initialize the suggestion generator."""
        pass
    
    def generate_suggestions(self, target: str) -> List[RefactoringSuggestion]:
        """Generate refactoring suggestions for a target file or directory.
        
        Args:
            target: File or directory to analyze
            
        Returns:
            List of refactoring suggestions
        """
        raise NotImplementedError("Subclasses must implement generate_suggestions()")
    
    def save_suggestions(self, suggestions: List[RefactoringSuggestion], output_path: str) -> None:
        """Save refactoring suggestions to a file.
        
        Args:
            suggestions: List of refactoring suggestions
            output_path: Path to save suggestions to
        """
        serializable = [suggestion.to_dict() for suggestion in suggestions]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, indent=2)
        
        logger.info(f"Saved {len(suggestions)} refactoring suggestions to {output_path}")
    
    @staticmethod
    def load_suggestions(input_path: str) -> List[RefactoringSuggestion]:
        """Load refactoring suggestions from a file.
        
        Args:
            input_path: Path to load suggestions from
            
        Returns:
            List of refactoring suggestions
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        suggestions = [RefactoringSuggestion.from_dict(item) for item in data]
        logger.info(f"Loaded {len(suggestions)} refactoring suggestions from {input_path}")
        
        return suggestions

class ComplexityBasedSuggestionGenerator(SuggestionGenerator):
    """Generates refactoring suggestions based on complexity metrics."""
    
    def __init__(self, complexity_threshold=20, cognitive_threshold=30):
        """Initialize the generator with thresholds.
        
        Args:
            complexity_threshold: Cyclomatic complexity threshold for suggestions
            cognitive_threshold: Cognitive complexity threshold for suggestions
        """
        super().__init__()
        self.complexity_threshold = complexity_threshold
        self.cognitive_threshold = cognitive_threshold
    
    def generate_suggestions(self, complexity_results) -> List[RefactoringSuggestion]:
        """Generate refactoring suggestions from complexity analysis results.
        
        Args:
            complexity_results: Results from complexity analysis
            
        Returns:
            List of refactoring suggestions
        """
        suggestions = []
        
        # Process each function's complexity metrics
        for func_result in complexity_results:
            file_path = func_result.get("file_path", "unknown")
            
            # Process all functions
            for func in func_result.get("functions", []):
                # Skip functions with low complexity
                if (func.get("complexity", 0) < self.complexity_threshold and
                    func.get("cognitive_complexity", 0) < self.cognitive_threshold):
                    continue
                
                function_name = func.get("name", "anonymous")
                line_start = func.get("line", 1)
                line_end = func.get("end_line", line_start + 10)  # Estimate if not provided
                
                # Determine impact based on complexity
                if func.get("complexity", 0) > self.complexity_threshold * 1.5:
                    impact = SuggestionImpact.HIGH
                elif func.get("complexity", 0) > self.complexity_threshold:
                    impact = SuggestionImpact.MEDIUM
                else:
                    impact = SuggestionImpact.LOW
                
                # Create suggestion based on complexity type
                if func.get("complexity", 0) >= self.complexity_threshold:
                    suggestions.append(RefactoringSuggestion(
                        refactoring_type=RefactoringType.EXTRACT_METHOD,
                        description=f"Extract methods from complex function '{function_name}'",
                        file_path=file_path,
                        line_range=(line_start, line_end),
                        impact=impact,
                        source="complexity_metrics",
                        details={
                            "function_name": function_name,
                            "complexity": func.get("complexity", 0),
                            "threshold": self.complexity_threshold
                        },
                        benefits=[
                            "Reduce cyclomatic complexity",
                            "Improve readability",
                            "Make function more maintainable"
                        ],
                        effort=3
                    ))
                
                if func.get("cognitive_complexity", 0) >= self.cognitive_threshold:
                    suggestions.append(RefactoringSuggestion(
                        refactoring_type=RefactoringType.EXTRACT_METHOD,
                        description=f"Simplify cognitive complexity in function '{function_name}'",
                        file_path=file_path,
                        line_range=(line_start, line_end),
                        impact=impact,
                        source="complexity_metrics",
                        details={
                            "function_name": function_name,
                            "cognitive_complexity": func.get("cognitive_complexity", 0),
                            "threshold": self.cognitive_threshold
                        },
                        benefits=[
                            "Reduce cognitive complexity",
                            "Improve code understandability",
                            "Reduce nested structures"
                        ],
                        effort=4
                    ))
        
        return suggestions

class FlowAnalysisSuggestionGenerator(SuggestionGenerator):
    """Generates refactoring suggestions based on flow analysis."""
    
    def __init__(self):
        """Initialize the flow analysis suggestion generator."""
        super().__init__()
    
    def generate_suggestions(self, flow_results) -> List[RefactoringSuggestion]:
        """Generate refactoring suggestions from flow analysis results.
        
        Args:
            flow_results: Results from flow analysis
            
        Returns:
            List of refactoring suggestions
        """
        suggestions = []
        
        # Process control flow issues
        if "control_flow_graphs" in flow_results:
            suggestions.extend(self._process_control_flow_issues(flow_results))
        
        # Process data flow issues
        if "data_flow_results" in flow_results:
            suggestions.extend(self._process_data_flow_issues(flow_results))
        
        return suggestions
    
    def _process_control_flow_issues(self, flow_results) -> List[RefactoringSuggestion]:
        """Process control flow issues to generate suggestions.
        
        Args:
            flow_results: Flow analysis results
            
        Returns:
            List of refactoring suggestions
        """
        suggestions = []
        
        for func_name, issues in flow_results.get("issues", {}).items():
            file_path = "unknown"  # In a real implementation, we'd get this from the flow results
            
            # Check for dead code
            dead_code = issues.get("dead_code", [])
            if dead_code:
                # Get the line range from the dead code
                line_ranges = []
                for code_block in dead_code:
                    if "start_line" in code_block and "end_line" in code_block:
                        line_ranges.append((code_block["start_line"], code_block["end_line"]))
                
                # Use the first line range if available
                line_range = line_ranges[0] if line_ranges else (1, 10)
                
                suggestions.append(RefactoringSuggestion(
                    refactoring_type=RefactoringType.CUSTOM,
                    description=f"Remove unreachable code in function '{func_name}'",
                    file_path=file_path,
                    line_range=line_range,
                    impact=SuggestionImpact.MEDIUM,
                    source="control_flow_analysis",
                    details={
                        "function_name": func_name,
                        "dead_code_count": len(dead_code)
                    },
                    benefits=[
                        "Eliminate unreachable code",
                        "Reduce code size",
                        "Improve maintainability"
                    ],
                    effort=2
                ))
            
            # Check for infinite loops
            infinite_loops = issues.get("infinite_loops", [])
            if infinite_loops:
                suggestions.append(RefactoringSuggestion(
                    refactoring_type=RefactoringType.CUSTOM,
                    description=f"Fix potential infinite loops in function '{func_name}'",
                    file_path=file_path,
                    line_range=(1, 10),  # Placeholder
                    impact=SuggestionImpact.HIGH,
                    source="control_flow_analysis",
                    details={
                        "function_name": func_name,
                        "loop_count": len(infinite_loops)
                    },
                    benefits=[
                        "Prevent infinite loops",
                        "Ensure code terminates properly",
                        "Avoid runtime errors"
                    ],
                    effort=3
                ))
            
            # Check complex conditions
            complexity = issues.get("complexity", {})
            if complexity.get("cyclomatic_complexity", 0) > 15:
                suggestions.append(RefactoringSuggestion(
                    refactoring_type=RefactoringType.REPLACE_CONDITIONAL_WITH_POLYMORPHISM,
                    description=f"Replace complex conditionals with polymorphism in '{func_name}'",
                    file_path=file_path,
                    line_range=(1, 10),  # Placeholder
                    impact=SuggestionImpact.MEDIUM,
                    source="control_flow_analysis",
                    details={
                        "function_name": func_name,
                        "complexity": complexity.get("cyclomatic_complexity", 0)
                    },
                    benefits=[
                        "Simplify complex conditional logic",
                        "Make code more maintainable",
                        "Enable adding new variants without modifying existing code"
                    ],
                    effort=4
                ))
        
        return suggestions
    
    def _process_data_flow_issues(self, flow_results) -> List[RefactoringSuggestion]:
        """Process data flow issues to generate suggestions.
        
        Args:
            flow_results: Flow analysis results
            
        Returns:
            List of refactoring suggestions
        """
        suggestions = []
        
        for func_name, issues in flow_results.get("issues", {}).items():
            file_path = "unknown"  # In a real implementation, we'd get this from the flow results
            
            # Check unused variables
            unused_vars = issues.get("unused_variables", [])
            if unused_vars:
                suggestions.append(RefactoringSuggestion(
                    refactoring_type=RefactoringType.CUSTOM,
                    description=f"Remove unused variables in function '{func_name}'",
                    file_path=file_path,
                    line_range=(1, 10),  # Placeholder
                    impact=SuggestionImpact.LOW,
                    source="data_flow_analysis",
                    details={
                        "function_name": func_name,
                        "unused_variables": unused_vars
                    },
                    benefits=[
                        "Reduce code clutter",
                        "Improve readability",
                        "Avoid confusion about variable usage"
                    ],
                    effort=1
                ))
            
            # Check uninitialized variables
            uninitialized = issues.get("uninitialized_variables", [])
            if uninitialized:
                suggestions.append(RefactoringSuggestion(
                    refactoring_type=RefactoringType.CUSTOM,
                    description=f"Initialize variables before use in function '{func_name}'",
                    file_path=file_path,
                    line_range=(1, 10),  # Placeholder
                    impact=SuggestionImpact.HIGH,
                    source="data_flow_analysis",
                    details={
                        "function_name": func_name,
                        "uninitialized_variables": [v.get("variable") for v in uninitialized]
                    },
                    benefits=[
                        "Prevent runtime errors",
                        "Ensure variables have expected values",
                        "Make code more robust"
                    ],
                    effort=2
                ))
        
        return suggestions

class PatternBasedSuggestionGenerator(SuggestionGenerator):
    """Generates refactoring suggestions based on design pattern opportunities."""
    
    def __init__(self):
        """Initialize the pattern-based suggestion generator."""
        super().__init__()
    
    def generate_suggestions(self, pattern_opportunities) -> List[RefactoringSuggestion]:
        """Generate refactoring suggestions from pattern opportunities.
        
        Args:
            pattern_opportunities: Dictionary of pattern opportunities by file
            
        Returns:
            List of refactoring suggestions
        """
        suggestions = []
        
        for file_path, opportunities in pattern_opportunities.items():
            for opportunity in opportunities:
                pattern_name = opportunity.get("pattern_name")
                
                # Skip if no pattern name
                if not pattern_name:
                    continue
                
                # Map pattern name to refactoring type
                refactoring_type = RefactoringType.CUSTOM
                if pattern_name == "Factory Method":
                    refactoring_type = RefactoringType.FACTORY_METHOD
                elif pattern_name == "Strategy":
                    refactoring_type = RefactoringType.STRATEGY
                elif pattern_name == "Observer":
                    refactoring_type = RefactoringType.OBSERVER
                elif pattern_name == "Decorator":
                    refactoring_type = RefactoringType.DECORATOR
                elif pattern_name == "Singleton":
                    refactoring_type = RefactoringType.SINGLETON
                
                # Extract line range
                line_range = opportunity.get("line_range", (1, 10))
                
                # Determine impact based on confidence
                confidence = opportunity.get("confidence", 0.5)
                if confidence > 0.8:
                    impact = SuggestionImpact.HIGH
                elif confidence > 0.6:
                    impact = SuggestionImpact.MEDIUM
                else:
                    impact = SuggestionImpact.LOW
                
                # Create suggestion
                description = f"Apply {pattern_name} pattern"
                if "description" in opportunity:
                    description = opportunity["description"]
                    
                suggestions.append(RefactoringSuggestion(
                    refactoring_type=refactoring_type,
                    description=description,
                    file_path=file_path,
                    line_range=line_range,
                    impact=impact,
                    source="pattern_opportunity",
                    details={
                        "pattern_name": pattern_name,
                        "confidence": confidence
                    },
                    before_code=opportunity.get("code_snippet"),
                    benefits=opportunity.get("benefits", []),
                    effort=3
                ))
        
        return suggestions

class ArchitecturalSuggestionGenerator(SuggestionGenerator):
    """Generates refactoring suggestions based on architectural analysis."""
    
    def __init__(self):
        """Initialize the architectural suggestion generator."""
        super().__init__()
    
    def generate_suggestions(self, architectural_results) -> List[RefactoringSuggestion]:
        """Generate refactoring suggestions from architectural analysis.
        
        Args:
            architectural_results: Results from architectural analysis
            
        Returns:
            List of refactoring suggestions
        """
        suggestions = []
        
        # Check for dependency cycles
        cycles = architectural_results.get("dependency_cycles", [])
        if cycles:
            for cycle in cycles:
                # Create suggestion for each cycle
                components = cycle.get("components", [])
                if not components:
                    continue
                    
                # Get first component as an example
                file_path = components[0].get("file", "unknown")
                
                suggestions.append(RefactoringSuggestion(
                    refactoring_type=RefactoringType.ARCHITECTURAL,
                    description=f"Break dependency cycle between {len(components)} components",
                    file_path=file_path,
                    line_range=(1, 10),  # Placeholder
                    impact=SuggestionImpact.HIGH,
                    source="architectural_analysis",
                    details={
                        "cycle": [comp.get("name", "unknown") for comp in components],
                        "cycle_length": len(components)
                    },
                    benefits=[
                        "Eliminate circular dependencies",
                        "Improve code maintainability",
                        "Enable independent testing and deployment"
                    ],
                    effort=4,
                    affected_components=[comp.get("name", "unknown") for comp in components]
                ))
        
        # Check for architectural anti-patterns
        antipatterns = architectural_results.get("anti_patterns", [])
        for antipattern in antipatterns:
            name = antipattern.get("name", "Unknown")
            severity = antipattern.get("severity", "medium")
            
            # Map severity to impact
            impact = SuggestionImpact.MEDIUM
            if severity == "high":
                impact = SuggestionImpact.HIGH
            elif severity == "critical":
                impact = SuggestionImpact.CRITICAL
            elif severity == "low":
                impact = SuggestionImpact.LOW
                
            # Extract affected files
            affected_files = antipattern.get("affected_files", [])
            file_path = affected_files[0] if affected_files else "unknown"
            
            suggestions.append(RefactoringSuggestion(
                refactoring_type=RefactoringType.ARCHITECTURAL,
                description=f"Fix architectural anti-pattern: {name}",
                file_path=file_path,
                line_range=(1, 10),  # Placeholder
                impact=impact,
                source="architectural_analysis",
                details={
                    "anti_pattern": name,
                    "severity": severity,
                    "affected_files": affected_files
                },
                benefits=antipattern.get("remediation_benefits", [
                    "Improve architectural integrity",
                    "Reduce technical debt",
                    "Make codebase easier to maintain"
                ]),
                effort=antipattern.get("remediation_effort", 3),
                affected_components=antipattern.get("affected_components", [])
            ))
        
        return suggestions

class CompositeSuggestionGenerator(SuggestionGenerator):
    """Generates refactoring suggestions from multiple sources."""
    
    def __init__(self):
        """Initialize the composite suggestion generator."""
        super().__init__()
        self.generators = [
            ComplexityBasedSuggestionGenerator(),
            FlowAnalysisSuggestionGenerator(),
            PatternBasedSuggestionGenerator(),
            ArchitecturalSuggestionGenerator()
        ]
    
    def add_generator(self, generator: SuggestionGenerator) -> None:
        """Add a suggestion generator to the composite.
        
        Args:
            generator: SuggestionGenerator instance to add
        """
        self.generators.append(generator)
    
    def generate_suggestions(self, analysis_results) -> List[RefactoringSuggestion]:
        """Generate refactoring suggestions from all analysis results.
        
        Args:
            analysis_results: Dictionary containing results from different analyses
            
        Returns:
            List of refactoring suggestions
        """
        all_suggestions = []
        
        # Use each generator with its corresponding analysis results
        if "complexity_results" in analysis_results:
            complexity_generator = ComplexityBasedSuggestionGenerator()
            all_suggestions.extend(
                complexity_generator.generate_suggestions(analysis_results["complexity_results"])
            )
        
        if "flow_results" in analysis_results:
            flow_generator = FlowAnalysisSuggestionGenerator()
            all_suggestions.extend(
                flow_generator.generate_suggestions(analysis_results["flow_results"])
            )
        
        if "pattern_opportunities" in analysis_results:
            pattern_generator = PatternBasedSuggestionGenerator()
            all_suggestions.extend(
                pattern_generator.generate_suggestions(analysis_results["pattern_opportunities"])
            )
        
        if "architectural_results" in analysis_results:
            arch_generator = ArchitecturalSuggestionGenerator()
            all_suggestions.extend(
                arch_generator.generate_suggestions(analysis_results["architectural_results"])
            )
        
        # Sort suggestions by impact
        impact_order = {
            SuggestionImpact.CRITICAL: 0,
            SuggestionImpact.HIGH: 1,
            SuggestionImpact.MEDIUM: 2,
            SuggestionImpact.LOW: 3
        }
        
        all_suggestions.sort(key=lambda s: impact_order[s.impact])
        
        return all_suggestions
    
    def generate_all_suggestions(self, target: str) -> List[RefactoringSuggestion]:
        """Run all analysis types and generate suggestions from the results.
        
        Args:
            target: File or directory to analyze
            
        Returns:
            List of refactoring suggestions
        """
        try:
            # Import tools at runtime to avoid circular imports
            from src.analyzer import CodeAnalyzer
            from src.metrics.complexity import ComplexityAnalyzer
            from src.flow.control_flow import ControlFlowAnalyzer
            from src.flow.data_flow import DataFlowAnalyzer
            
            # Initialize analyzers
            code_analyzer = CodeAnalyzer()
            complexity_analyzer = ComplexityAnalyzer()
            control_flow_analyzer = ControlFlowAnalyzer()
            data_flow_analyzer = DataFlowAnalyzer()
            
            # Run code analysis
            analysis_results = {}
            
            # Analyze the files
            if os.path.isfile(target):
                file_results = [code_analyzer.analyze_file(target)]
            else:
                file_results = code_analyzer.analyze_directory(target)
            
            # Run complexity analysis
            complexity_results = []
            for file_result in file_results:
                if "error" in file_result:
                    continue
                
                result = complexity_analyzer.analyze(
                    file_result["ast"],
                    file_result["code"],
                    file_result["language"],
                    file_result["file"]
                )
                complexity_results.append(result)
            analysis_results["complexity_results"] = complexity_results
            
            # Run flow analysis
            flow_results = {"control_flow_graphs": {}, "issues": {}}
            for file_result in file_results:
                if "error" in file_result:
                    continue
                
                # Generate CFGs
                cfgs = control_flow_analyzer.create_cfg_from_tree(
                    file_result["ast"],
                    file_result["code"],
                    file_result["language"]
                )
                
                # Analyze each CFG
                for func_name, cfg in cfgs.items():
                    # Add to flow results
                    flow_results["control_flow_graphs"][func_name] = cfg.to_dict()
                    
                    # Find control flow issues
                    dead_code = control_flow_analyzer.find_dead_code(cfg)
                    infinite_loops = control_flow_analyzer.detect_possible_infinite_loops(cfg)
                    complexity = control_flow_analyzer.analyze_function_complexity(cfg)
                    exit_paths = control_flow_analyzer.get_function_exit_paths(cfg)
                    
                    # Store issues
                    flow_results["issues"][func_name] = {
                        "dead_code": dead_code,
                        "infinite_loops": infinite_loops,
                        "complexity": complexity,
                        "exit_paths": exit_paths
                    }
                    
                    # Run data flow analysis if possible
                    if data_flow_analyzer.supports_language(file_result["language"]):
                        df_result = data_flow_analyzer.analyze_data_flow(
                            cfg,
                            file_result["ast"],
                            file_result["code"],
                            file_result["language"]
                        )
                        
                        # Add to flow results
                        if "data_flow_results" not in flow_results:
                            flow_results["data_flow_results"] = {}
                        
                        flow_results["data_flow_results"][func_name] = df_result
                        
                        # Add data flow issues
                        if "issues" in df_result:
                            flow_results["issues"][func_name].update(df_result["issues"])
            
            analysis_results["flow_results"] = flow_results
            
            # Run pattern opportunity detection
            try:
                from recommendation_detector import detect_pattern_opportunities
                
                pattern_opportunities = {}
                for file_result in file_results:
                    if "error" in file_result:
                        continue
                    
                    file_path = file_result["file"]
                    opportunities = detect_pattern_opportunities(file_path)
                    if opportunities:
                        pattern_opportunities[file_path] = opportunities
                
                analysis_results["pattern_opportunities"] = pattern_opportunities
            except ImportError:
                logger.warning("Pattern opportunity detection not available")
            
            # Run architectural analysis if available
            try:
                from src.architecture.analyzer import ArchitecturalAnalyzer
                
                arch_analyzer = ArchitecturalAnalyzer()
                architectural_results = arch_analyzer.analyze(target)
                analysis_results["architectural_results"] = architectural_results
            except ImportError:
                logger.warning("Architectural analysis not available")
            
            # Generate suggestions from all analysis results
            return self.generate_suggestions(analysis_results)
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            return []

def generate_refactoring_report(
    suggestions: List[RefactoringSuggestion],
    output_path: str,
    format_type: str = "html"
) -> None:
    """Generate a report of refactoring suggestions.
    
    Args:
        suggestions: List of refactoring suggestions
        output_path: Path to save the report
        format_type: Format of the report (html, json, text)
    """
    if format_type == "json":
        # Save as JSON
        serializable = [suggestion.to_dict() for suggestion in suggestions]
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, indent=2)
    
    elif format_type == "text":
        # Generate text report
        lines = ["# Refactoring Suggestions Report\n"]
        
        lines.append(f"Total suggestions: {len(suggestions)}\n")
        
        # Group by impact
        critical = [s for s in suggestions if s.impact == SuggestionImpact.CRITICAL]
        high = [s for s in suggestions if s.impact == SuggestionImpact.HIGH]
        medium = [s for s in suggestions if s.impact == SuggestionImpact.MEDIUM]
        low = [s for s in suggestions if s.impact == SuggestionImpact.LOW]
        
        lines.append(f"- Critical: {len(critical)}")
        lines.append(f"- High: {len(high)}")
        lines.append(f"- Medium: {len(medium)}")
        lines.append(f"- Low: {len(low)}\n")
        
        # Group by type
        types = {}
        for s in suggestions:
            if s.refactoring_type.value not in types:
                types[s.refactoring_type.value] = 0
            types[s.refactoring_type.value] += 1
        
        lines.append("## Suggestion Types")
        for t, count in types.items():
            lines.append(f"- {t}: {count}")
        
        lines.append("\n## Detailed Suggestions\n")
        
        # Add all suggestions
        for i, suggestion in enumerate(suggestions, 1):
            lines.append(f"### {i}. {suggestion.description}")
            lines.append(f"- **Type:** {suggestion.refactoring_type.value}")
            lines.append(f"- **Impact:** {suggestion.impact.value}")
            lines.append(f"- **File:** {suggestion.file_path}")
            lines.append(f"- **Lines:** {suggestion.line_range[0]}-{suggestion.line_range[1]}")
            lines.append(f"- **Source:** {suggestion.source}")
            lines.append(f"- **Effort:** {suggestion.effort} (1-5 scale)")
            
            if suggestion.benefits:
                lines.append("\n**Benefits:**")
                for benefit in suggestion.benefits:
                    lines.append(f"- {benefit}")
            
            if suggestion.before_code:
                lines.append("\n**Before:**")
                lines.append("```")
                lines.append(suggestion.before_code)
                lines.append("```")
            
            if suggestion.after_code:
                lines.append("\n**After:**")
                lines.append("```")
                lines.append(suggestion.after_code)
                lines.append("```")
            
            lines.append("\n" + "-" * 80 + "\n")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
    
    else:  # HTML format
        # Generate HTML report
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Refactoring Suggestions Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3, h4 {{
            color: #2c3e50;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            padding: 20px;
        }}
        .suggestion {{
            border-left: 5px solid #3498db;
            padding-left: 15px;
            margin-bottom: 30px;
        }}
        .critical {{
            border-left-color: #e74c3c;
        }}
        .high {{
            border-left-color: #e67e22;
        }}
        .medium {{
            border-left-color: #f39c12;
        }}
        .low {{
            border-left-color: #3498db;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            color: white;
        }}
        .badge.critical {{
            background-color: #e74c3c;
        }}
        .badge.high {{
            background-color: #e67e22;
        }}
        .badge.medium {{
            background-color: #f39c12;
        }}
        .badge.low {{
            background-color: #3498db;
        }}
        .details {{
            margin-top: 10px;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .detail {{
            background-color: #f8f9fa;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 14px;
        }}
        .benefits {{
            margin-top: 15px;
        }}
        .benefit {{
            margin-bottom: 5px;
            display: flex;
            align-items: flex-start;
        }}
        .benefit::before {{
            content: '✓';
            color: #2ecc71;
            margin-right: 5px;
            font-weight: bold;
        }}
        pre {{
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }}
        .code-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 15px;
        }}
        .code-block {{
            flex: 1;
            min-width: 300px;
        }}
        .summary {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            flex: 1;
            min-width: 150px;
            padding: 15px;
            border-radius: 8px;
            color: white;
            text-align: center;
        }}
        .summary-card.critical {{
            background-color: #e74c3c;
        }}
        .summary-card.high {{
            background-color: #e67e22;
        }}
        .summary-card.medium {{
            background-color: #f39c12;
        }}
        .summary-card.low {{
            background-color: #3498db;
        }}
        .summary-card h3 {{
            margin: 0;
            color: white;
        }}
        .summary-card p {{
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0 0;
        }}
        .filters {{
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
        }}
        .filter-group {{
            margin-bottom: 10px;
        }}
        .filter-group label {{
            font-weight: bold;
            margin-right: 10px;
        }}
        button {{
            padding: 5px 10px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}
        button:hover {{
            background-color: #2980b9;
        }}
    </style>
</head>
<body>
    <h1>Refactoring Suggestions Report</h1>
    
    <div class="summary">
        <div class="summary-card critical">
            <h3>Critical</h3>
            <p>{len([s for s in suggestions if s.impact == SuggestionImpact.CRITICAL])}</p>
        </div>
        <div class="summary-card high">
            <h3>High</h3>
            <p>{len([s for s in suggestions if s.impact == SuggestionImpact.HIGH])}</p>
        </div>
        <div class="summary-card medium">
            <h3>Medium</h3>
            <p>{len([s for s in suggestions if s.impact == SuggestionImpact.MEDIUM])}</p>
        </div>
        <div class="summary-card low">
            <h3>Low</h3>
            <p>{len([s for s in suggestions if s.impact == SuggestionImpact.LOW])}</p>
        </div>
    </div>
    
    <div class="filters">
        <div class="filter-group">
            <label>Filter by Impact:</label>
            <button onclick="filterByImpact('all')">All</button>
            <button onclick="filterByImpact('critical')">Critical</button>
            <button onclick="filterByImpact('high')">High</button>
            <button onclick="filterByImpact('medium')">Medium</button>
            <button onclick="filterByImpact('low')">Low</button>
        </div>
        <div class="filter-group">
            <label>Filter by Type:</label>
            <button onclick="filterByType('all')">All</button>
            {"".join([f'<button onclick="filterByType(\'{t}\')">{t}</button>' for t in set(s.refactoring_type.value for s in suggestions)])}
        </div>
    </div>
    
    <div class="card">
        <h2>Refactoring Suggestions</h2>
        
        <div id="suggestions-container">
"""
        
        # Add each suggestion
        for suggestion in suggestions:
            impact_class = suggestion.impact.value
            
            html += f"""
            <div class="suggestion {impact_class}" data-impact="{impact_class}" data-type="{suggestion.refactoring_type.value}">
                <h3>{suggestion.description}</h3>
                
                <div class="details">
                    <span class="badge {impact_class}">{impact_class.upper()}</span>
                    <span class="detail">{suggestion.refactoring_type.value}</span>
                    <span class="detail">File: {os.path.basename(suggestion.file_path)}</span>
                    <span class="detail">Lines: {suggestion.line_range[0]}-{suggestion.line_range[1]}</span>
                    <span class="detail">Effort: {"●" * suggestion.effort}{"○" * (5 - suggestion.effort)}</span>
                </div>
"""
            
            # Add benefits
            if suggestion.benefits:
                html += """
                <div class="benefits">
                    <h4>Benefits:</h4>
"""
                for benefit in suggestion.benefits:
                    html += f"""
                    <div class="benefit">{benefit}</div>
"""
                html += """
                </div>
"""
            
            # Add code samples
            if suggestion.before_code or suggestion.after_code:
                html += """
                <div class="code-container">
"""
                if suggestion.before_code:
                    html += f"""
                    <div class="code-block">
                        <h4>Before:</h4>
                        <pre><code>{suggestion.before_code}</code></pre>
                    </div>
"""
                if suggestion.after_code:
                    html += f"""
                    <div class="code-block">
                        <h4>After:</h4>
                        <pre><code>{suggestion.after_code}</code></pre>
                    </div>
"""
                html += """
                </div>
"""
            
            html += """
            </div>
"""
        
        # Close the HTML document
        html += """
        </div>
    </div>
    
    <script>
        function filterByImpact(impact) {
            const suggestions = document.querySelectorAll('.suggestion');
            suggestions.forEach(sugg => {
                if (impact === 'all' || sugg.dataset.impact === impact) {
                    sugg.style.display = 'block';
                } else {
                    sugg.style.display = 'none';
                }
            });
        }
        
        function filterByType(type) {
            const suggestions = document.querySelectorAll('.suggestion');
            suggestions.forEach(sugg => {
                if (type === 'all' || sugg.dataset.type === type) {
                    sugg.style.display = 'block';
                } else {
                    sugg.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
"""
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    logger.info(f"Generated refactoring report with {len(suggestions)} suggestions at {output_path}")

def get_refactoring_suggestions(target: str, output_path: Optional[str] = None, format_type: str = "html") -> List[RefactoringSuggestion]:
    """Generate refactoring suggestions for a target file or directory.
    
    Args:
        target: File or directory to analyze
        output_path: Path to save the report (optional)
        format_type: Format of the report (html, json, text)
        
    Returns:
        List of refactoring suggestions
    """
    generator = CompositeSuggestionGenerator()
    suggestions = generator.generate_all_suggestions(target)
    
    if output_path:
        generate_refactoring_report(suggestions, output_path, format_type)
    
    return suggestions