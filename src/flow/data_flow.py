"""
Data Flow Analysis module.

This module implements data flow analysis, which tracks how data values
flow through a program and how variables are used.
"""

from typing import Dict, List, Set, Tuple, Optional, Any, Union
import logging
import networkx as nx
import tree_sitter
from enum import Enum

from .control_flow import ControlFlowGraph, NodeType

logger = logging.getLogger(__name__)

class VariableAccess(Enum):
    """Types of variable accesses."""
    DEFINE = "define"  # Variable is defined/assigned
    USE = "use"        # Variable is used/read
    KILL = "kill"      # Variable is redefined or goes out of scope

class DataFlowAnalyzer:
    """Analyzer for tracking data flow in code.
    
    This class performs data flow analysis on a control flow graph,
    tracking variable definitions, uses, and potential issues.
    """
    
    def __init__(self):
        """Initialize the data flow analyzer."""
        # Language-specific configurations for variable operations
        self.language_config = {
            "python": {
                "queries": {
                    "variable_defines": """
                        (assignment
                            left: (identifier) @var_def)
                        
                        (assignment
                            left: (tuple_pattern
                                (identifier) @var_def))
                                
                        (for_statement
                            left: (identifier) @var_def)
                            
                        (for_statement
                            left: (tuple_pattern
                                (identifier) @var_def))
                                
                        (parameters
                            (identifier) @var_def)
                            
                        (with_statement
                            (with_item
                                alias: (identifier) @var_def))
                    """,
                    "variable_uses": """
                        (identifier) @var_use
                    """
                }
            },
            "javascript": {
                "queries": {
                    "variable_defines": """
                        (variable_declaration
                            (variable_declarator
                                name: (identifier) @var_def))
                                
                        (assignment_expression
                            left: (identifier) @var_def)
                            
                        (for_statement
                            initializer: (variable_declaration
                                (variable_declarator
                                    name: (identifier) @var_def)))
                                    
                        (formal_parameters
                            (identifier) @var_def)
                    """,
                    "variable_uses": """
                        (identifier) @var_use
                    """
                }
            }
        }
    
    def supports_language(self, language: str) -> bool:
        """Check if this analyzer supports a specific language.
        
        Args:
            language: The language to check
            
        Returns:
            True if the analyzer supports the language, False otherwise
        """
        return language in self.language_config
        
    def analyze_data_flow(self, 
                        cfg: ControlFlowGraph, 
                        tree: tree_sitter.Tree,
                        code: str,
                        language: str) -> Dict[str, Any]:
        """Analyze data flow in a control flow graph.
        
        Args:
            cfg: The control flow graph to analyze
            tree: The original tree-sitter AST
            code: The source code
            language: The language of the source code
            
        Returns:
            Dictionary containing data flow analysis results
        """
        if not self.supports_language(language):
            logger.warning(f"Data flow analysis not supported for language: {language}")
            return {"error": f"Language {language} not supported"}
            
        try:
            # Find variable definitions and uses in the CFG
            var_info = self._find_variable_operations(cfg, tree, code, language)
            
            # Perform reaching definitions analysis
            reaching_defs = self._compute_reaching_definitions(cfg, var_info)
            
            # Find potential issues
            issues = self._find_data_flow_issues(cfg, var_info, reaching_defs)
            
            # Generate the final results
            return {
                "function_name": cfg.name,
                "variables": list(var_info["all_variables"]),
                "definitions": var_info["definitions"],
                "uses": var_info["uses"],
                "def_use_chains": self._generate_def_use_chains(var_info, reaching_defs),
                "issues": issues
            }
            
        except Exception as e:
            logger.error(f"Error in data flow analysis: {e}")
            return {"error": str(e)}
    
    def _find_variable_operations(self, 
                               cfg: ControlFlowGraph, 
                               tree: tree_sitter.Tree,
                               code: str,
                               language: str) -> Dict[str, Any]:
        """Find variable definitions and uses in a CFG.
        
        Args:
            cfg: The control flow graph to analyze
            tree: The original tree-sitter AST
            code: The source code
            language: The language of the source code
            
        Returns:
            Dictionary containing variable information
        """
        try:
            from tree_sitter import Query, Language, Parser
            
            # Get the language module
            from src.tree_sitter_manager import LanguageManager
            manager = LanguageManager()
            lang_module = manager.get_language(language)
            
            # Get queries for this language
            lang_config = self.language_config[language]
            defines_query = lang_config["queries"]["variable_defines"]
            uses_query = lang_config["queries"]["variable_uses"]
            
            # Run the queries
            def_query = Query(lang_module, defines_query)
            def_matches = def_query.captures(tree.root_node)
            
            use_query = Query(lang_module, uses_query)
            use_matches = use_query.captures(tree.root_node)
            
            # Track variable information
            all_variables = set()
            definitions = {}  # node_id -> list of variables defined in that node
            uses = {}         # node_id -> list of variables used in that node
            var_definitions = {}  # var_name -> list of node IDs where it's defined
            var_uses = {}        # var_name -> list of node IDs where it's used
            
            # Process definitions
            for match, tag in def_matches:
                if tag == "var_def":
                    var_name = code[match.start_byte:match.end_byte]
                    all_variables.add(var_name)
                    
                    # Find which CFG node this definition belongs to
                    location = match.start_point
                    node_id = self._find_node_by_location(cfg, location)
                    
                    if node_id is not None:
                        if node_id not in definitions:
                            definitions[node_id] = []
                        definitions[node_id].append(var_name)
                        
                        if var_name not in var_definitions:
                            var_definitions[var_name] = []
                        var_definitions[var_name].append(node_id)
            
            # Process uses
            for match, tag in use_matches:
                if tag == "var_use":
                    var_name = code[match.start_byte:match.end_byte]
                    
                    # Skip if this is actually a definition
                    if any(match.id == m.id for m, t in def_matches if t == "var_def"):
                        continue
                        
                    all_variables.add(var_name)
                    
                    # Find which CFG node this use belongs to
                    location = match.start_point
                    node_id = self._find_node_by_location(cfg, location)
                    
                    if node_id is not None:
                        if node_id not in uses:
                            uses[node_id] = []
                        uses[node_id].append(var_name)
                        
                        if var_name not in var_uses:
                            var_uses[var_name] = []
                        var_uses[var_name].append(node_id)
            
            return {
                "all_variables": all_variables,
                "definitions": definitions,
                "uses": uses,
                "var_definitions": var_definitions,
                "var_uses": var_uses
            }
            
        except Exception as e:
            logger.error(f"Error finding variable operations: {e}")
            return {
                "all_variables": set(),
                "definitions": {},
                "uses": {},
                "var_definitions": {},
                "var_uses": {}
            }
    
    def _find_node_by_location(self, 
                             cfg: ControlFlowGraph, 
                             location: Tuple[int, int]) -> Optional[int]:
        """Find a CFG node corresponding to a source location.
        
        Args:
            cfg: The control flow graph
            location: Source location as (line, column)
            
        Returns:
            Node ID if found, None otherwise
        """
        # TODO: Implement a more accurate way to map source locations to CFG nodes
        # For now, this is a simplified approach
        for node_id in cfg.graph.nodes:
            # In a real implementation, we would track source locations in the CFG nodes
            # and perform a proper lookup here
            pass
            
        # Just return the first non-entry, non-exit node as a placeholder
        for node_id in cfg.graph.nodes:
            node_data = cfg.get_node_data(node_id)
            node_type = node_data["type"]
            if node_type != NodeType.ENTRY and node_type != NodeType.EXIT:
                return node_id
                
        return None
    
    def _compute_reaching_definitions(self, 
                                   cfg: ControlFlowGraph, 
                                   var_info: Dict[str, Any]) -> Dict[int, Dict[str, Set[int]]]:
        """Compute reaching definitions for each node in the CFG.
        
        A definition d "reaches" a point p if there exists a path from the point 
        immediately following d to p such that d is not "killed" along that path.
        
        Args:
            cfg: The control flow graph
            var_info: Variable information from _find_variable_operations
            
        Returns:
            Dictionary mapping node IDs to dictionaries mapping variable names to
            sets of node IDs where definitions reach this node
        """
        # Initialize reaching definitions for each node
        reaching_defs = {}
        for node_id in cfg.graph.nodes:
            reaching_defs[node_id] = {}
            
        # Initialize work list with all nodes
        work_list = list(cfg.graph.nodes)
        
        # Process nodes until the work list is empty
        while work_list:
            node_id = work_list.pop(0)
            
            # Compute in[node] = union of out[pred] for all predecessors
            in_defs = {}
            for pred_id in cfg.graph.predecessors(node_id):
                for var_name, def_nodes in reaching_defs.get(pred_id, {}).items():
                    if var_name not in in_defs:
                        in_defs[var_name] = set()
                    in_defs[var_name].update(def_nodes)
            
            # Compute out[node] = gen[node] + (in[node] - kill[node])
            out_defs = {}
            
            # Add definitions generated at this node
            for var_name in var_info["definitions"].get(node_id, []):
                if var_name not in out_defs:
                    out_defs[var_name] = set()
                out_defs[var_name].add(node_id)
            
            # Add definitions from in[node] that aren't killed at this node
            for var_name, def_nodes in in_defs.items():
                # If this node redefines the variable, previous definitions are killed
                if var_name in var_info["definitions"].get(node_id, []):
                    continue
                    
                if var_name not in out_defs:
                    out_defs[var_name] = set()
                out_defs[var_name].update(def_nodes)
            
            # If out[node] changed, add successors to the work list
            if out_defs != reaching_defs.get(node_id, {}):
                reaching_defs[node_id] = out_defs
                for succ_id in cfg.graph.successors(node_id):
                    if succ_id not in work_list:
                        work_list.append(succ_id)
        
        return reaching_defs
    
    def _generate_def_use_chains(self, 
                              var_info: Dict[str, Any],
                              reaching_defs: Dict[int, Dict[str, Set[int]]]) -> Dict[str, List[Tuple[int, int]]]:
        """Generate def-use chains from reaching definitions.
        
        A def-use chain connects a variable definition to all its uses.
        
        Args:
            var_info: Variable information from _find_variable_operations
            reaching_defs: Reaching definitions from _compute_reaching_definitions
            
        Returns:
            Dictionary mapping variable names to lists of (def_node, use_node) tuples
        """
        def_use_chains = {}
        
        # For each node where variables are used
        for node_id, used_vars in var_info["uses"].items():
            # For each variable used at this node
            for var_name in used_vars:
                # Find definitions that reach this node
                if var_name in reaching_defs.get(node_id, {}):
                    def_nodes = reaching_defs[node_id][var_name]
                    
                    # Add def-use chains for this variable
                    if var_name not in def_use_chains:
                        def_use_chains[var_name] = []
                        
                    for def_node in def_nodes:
                        def_use_chains[var_name].append((def_node, node_id))
        
        return def_use_chains
    
    def _find_data_flow_issues(self, 
                             cfg: ControlFlowGraph,
                             var_info: Dict[str, Any],
                             reaching_defs: Dict[int, Dict[str, Set[int]]]) -> Dict[str, List]:
        """Find potential data flow issues in the code.
        
        Args:
            cfg: The control flow graph
            var_info: Variable information from _find_variable_operations
            reaching_defs: Reaching definitions from _compute_reaching_definitions
            
        Returns:
            Dictionary mapping issue types to lists of problematic entities
        """
        issues = {
            "undefined_variables": [],      # Variables used without being defined
            "unused_variables": [],         # Variables defined but never used
            "uninitialized_variables": []   # Variables potentially used before initialization
        }
        
        # Check for undefined variables (used but never defined)
        for var_name in var_info["all_variables"]:
            if var_name not in var_info["var_definitions"]:
                issues["undefined_variables"].append(var_name)
        
        # Check for unused variables (defined but never used)
        for var_name in var_info["all_variables"]:
            if var_name not in var_info["var_uses"]:
                if var_name in var_info["var_definitions"]:
                    issues["unused_variables"].append(var_name)
        
        # Check for potentially uninitialized variables
        for node_id, used_vars in var_info["uses"].items():
            for var_name in used_vars:
                # If variable is used but no definition reaches this node
                if var_name not in reaching_defs.get(node_id, {}):
                    issues["uninitialized_variables"].append({
                        "variable": var_name,
                        "node_id": node_id
                    })
        
        return issues
    
    def visualize_data_flow(self, 
                          cfg: ControlFlowGraph,
                          data_flow_results: Dict[str, Any],
                          output_file: Optional[str] = None) -> Optional[str]:
        """Generate a visualization of the data flow.
        
        Args:
            cfg: The control flow graph
            data_flow_results: Results from analyze_data_flow
            output_file: Path to save the visualization. If None, the visualization
                         will be displayed interactively (if in a supported environment).
                         
        Returns:
            Path to the saved visualization file, or None if displayed interactively
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            from matplotlib.colors import LinearSegmentedColormap
            import numpy as np
            
            # Create position layout for nodes
            pos = nx.spring_layout(cfg.graph, seed=42)
            
            # Create figure
            plt.figure(figsize=(14, 10))
            
            # Define node colors based on type and data flow
            node_colors = []
            for node in cfg.graph.nodes:
                node_type = cfg.graph.nodes[node].get("type")
                
                # Basic coloring by node type
                if node_type == NodeType.ENTRY:
                    node_colors.append("green")
                elif node_type == NodeType.EXIT:
                    node_colors.append("red")
                elif node_type == NodeType.BRANCH:
                    node_colors.append("orange")
                elif node in data_flow_results.get("definitions", {}):
                    # Color nodes that define variables
                    node_colors.append("blue")
                elif node in data_flow_results.get("uses", {}):
                    # Color nodes that use variables
                    node_colors.append("purple")
                else:
                    node_colors.append("gray")
            
            # Draw nodes
            nx.draw_networkx_nodes(cfg.graph, pos, node_size=700, node_color=node_colors, alpha=0.8)
            
            # Draw edges
            nx.draw_networkx_edges(cfg.graph, pos, edge_color="black", width=1.5, 
                                  arrowsize=15, arrowstyle="->")
            
            # Draw labels
            labels = {}
            for node in cfg.graph.nodes:
                node_data = cfg.graph.nodes[node]
                node_type = node_data.get("type")
                code = node_data.get("code", "")
                
                # Add variable definitions and uses to the label
                var_info = []
                if node in data_flow_results.get("definitions", {}):
                    defs = data_flow_results["definitions"][node]
                    var_info.append(f"Def: {', '.join(defs)}")
                if node in data_flow_results.get("uses", {}):
                    uses = data_flow_results["uses"][node]
                    var_info.append(f"Use: {', '.join(uses)}")
                
                # Create the full label
                if isinstance(node_type, NodeType):
                    type_str = node_type.value
                else:
                    type_str = str(node_type)
                    
                if code:
                    # Shorten code for the label
                    code_short = code[:15] + "..." if len(code) > 15 else code
                    code_short = code_short.replace("\n", "↵")
                    label = f"{type_str}: {code_short}"
                else:
                    label = type_str
                    
                if var_info:
                    label += f"\n{' '.join(var_info)}"
                    
                labels[node] = label
                
            nx.draw_networkx_labels(cfg.graph, pos, labels=labels, font_size=8)
            
            # Highlight def-use chains
            def_use_chains = data_flow_results.get("def_use_chains", {})
            for var_name, chains in def_use_chains.items():
                for def_node, use_node in chains:
                    # Draw a curved edge between definition and use
                    nx.draw_networkx_edges(cfg.graph, pos, 
                                         edgelist=[(def_node, use_node)],
                                         edge_color="blue", width=2.0, 
                                         alpha=0.7, style="dashed",
                                         connectionstyle="arc3,rad=0.3")
            
            # Add legend
            legend_elements = [
                mpatches.Patch(color="green", label="Entry"),
                mpatches.Patch(color="red", label="Exit"),
                mpatches.Patch(color="orange", label="Branch"),
                mpatches.Patch(color="blue", label="Variable Definition"),
                mpatches.Patch(color="purple", label="Variable Use"),
                mpatches.Patch(color="gray", label="Other Statements")
            ]
            plt.legend(handles=legend_elements, loc="upper right")
            
            # Set title and adjust layout
            plt.title(f"Data Flow: {cfg.name}")
            plt.axis("off")
            plt.tight_layout()
            
            # Save or display the visualization
            if output_file:
                plt.savefig(output_file)
                plt.close()
                return output_file
            else:
                plt.show()
                return None
                
        except ImportError as e:
            logger.error(f"Visualization requires matplotlib: {e}")
            return None


class LiveVariableAnalyzer:
    """Analyzer for performing live variable analysis.
    
    Live variable analysis determines which variables are "live" at each
    program point, meaning their values may be used in the future.
    """
    
    def __init__(self):
        """Initialize the live variable analyzer."""
        pass
        
    def analyze(self, 
              cfg: ControlFlowGraph,
              var_info: Dict[str, Any]) -> Dict[int, Set[str]]:
        """Perform live variable analysis on a control flow graph.
        
        Args:
            cfg: The control flow graph to analyze
            var_info: Variable information from DataFlowAnalyzer._find_variable_operations
            
        Returns:
            Dictionary mapping node IDs to sets of live variables
        """
        # Initialize live variable sets
        live_vars = {}
        for node_id in cfg.graph.nodes:
            live_vars[node_id] = set()
            
        # Initialize work list with all nodes
        work_list = list(cfg.graph.nodes)
        
        # Process nodes until the work list is empty
        while work_list:
            node_id = work_list.pop(0)
            
            # Compute live_out[node] = union of live_in[succ] for all successors
            live_out = set()
            for succ_id in cfg.graph.successors(node_id):
                live_out.update(live_vars.get(succ_id, set()))
            
            # Compute live_in[node] = use[node] + (live_out[node] - def[node])
            live_in = set(var_info["uses"].get(node_id, []))
            
            # Add variables from live_out that aren't defined at this node
            for var_name in live_out:
                if var_name not in var_info["definitions"].get(node_id, []):
                    live_in.add(var_name)
            
            # If live_in[node] changed, add predecessors to the work list
            if live_in != live_vars.get(node_id, set()):
                live_vars[node_id] = live_in
                for pred_id in cfg.graph.predecessors(node_id):
                    if pred_id not in work_list:
                        work_list.append(pred_id)
        
        return live_vars
        
    def find_dead_stores(self, 
                       cfg: ControlFlowGraph,
                       var_info: Dict[str, Any],
                       live_vars: Dict[int, Set[str]]) -> List[Dict[str, Any]]:
        """Find dead stores (variables defined but never used).
        
        Args:
            cfg: The control flow graph to analyze
            var_info: Variable information from DataFlowAnalyzer._find_variable_operations
            live_vars: Live variable information from analyze
            
        Returns:
            List of dead store information
        """
        dead_stores = []
        
        # Check each node where variables are defined
        for node_id, defined_vars in var_info["definitions"].items():
            for var_name in defined_vars:
                # Get live variables after this node
                live_out = set()
                for succ_id in cfg.graph.successors(node_id):
                    live_out.update(live_vars.get(succ_id, set()))
                
                # If the variable isn't live after its definition, it's a dead store
                if var_name not in live_out:
                    # Check if it's used in the same node - if so, it's not a dead store
                    if var_name not in var_info["uses"].get(node_id, []):
                        dead_stores.append({
                            "variable": var_name,
                            "node_id": node_id
                        })
        
        return dead_stores


class AvailableExpressionAnalyzer:
    """Analyzer for performing available expressions analysis.
    
    Available expressions analysis determines which expressions have already
    been computed and not subsequently modified at each program point.
    """
    
    def __init__(self):
        """Initialize the available expressions analyzer."""
        pass
        
    def analyze(self, 
              cfg: ControlFlowGraph,
              tree: tree_sitter.Tree,
              code: str,
              language: str) -> Dict[int, Set[str]]:
        """Perform available expressions analysis on a control flow graph.
        
        Args:
            cfg: The control flow graph to analyze
            tree: The original tree-sitter AST
            code: The source code
            language: The language of the source code
            
        Returns:
            Dictionary mapping node IDs to sets of available expression strings
        """
        # Find expressions in the code
        expressions = self._find_expressions(tree, code, language)
        
        # Initialize available expressions for each node
        avail_exprs = {}
        for node_id in cfg.graph.nodes:
            avail_exprs[node_id] = set()
            
        # Initialize work list with all nodes
        work_list = list(cfg.graph.nodes)
        
        # Compute gen and kill sets for each node
        gen_sets = {}
        kill_sets = {}
        
        for node_id in cfg.graph.nodes:
            gen_sets[node_id] = set()
            kill_sets[node_id] = set()
            
            # Add expressions generated at this node
            for expr in expressions.get("expressions", {}).get(node_id, []):
                gen_sets[node_id].add(expr)
                
            # Add expressions killed at this node (ones that modify variables used in other expressions)
            for var in expressions.get("modified_vars", {}).get(node_id, []):
                for expr in expressions.get("all_expressions", []):
                    if var in expressions.get("expr_vars", {}).get(expr, []):
                        kill_sets[node_id].add(expr)
        
        # Process nodes until the work list is empty
        while work_list:
            node_id = work_list.pop(0)
            
            # Compute avail_in[node] = intersection of avail_out[pred] for all predecessors
            # If node has no predecessors, avail_in[node] = empty set
            preds = list(cfg.graph.predecessors(node_id))
            if preds:
                avail_in = set.intersection(*[avail_exprs.get(pred_id, set()) for pred_id in preds])
            else:
                avail_in = set()
            
            # Compute avail_out[node] = gen[node] + (avail_in[node] - kill[node])
            avail_out = set(gen_sets.get(node_id, set()))
            
            # Add expressions from avail_in that aren't killed at this node
            for expr in avail_in:
                if expr not in kill_sets.get(node_id, set()):
                    avail_out.add(expr)
            
            # If avail_out[node] changed, add successors to the work list
            if avail_out != avail_exprs.get(node_id, set()):
                avail_exprs[node_id] = avail_out
                for succ_id in cfg.graph.successors(node_id):
                    if succ_id not in work_list:
                        work_list.append(succ_id)
        
        return avail_exprs
        
    def _find_expressions(self, 
                       tree: tree_sitter.Tree,
                       code: str,
                       language: str) -> Dict[str, Any]:
        """Find expressions in the AST.
        
        Args:
            tree: The tree-sitter AST
            code: The source code
            language: The language of the source code
            
        Returns:
            Dictionary containing expression information
        """
        # This is a simplified implementation
        # A real implementation would use tree-sitter queries to extract expressions
        
        return {
            "all_expressions": [],
            "expressions": {},
            "modified_vars": {},
            "expr_vars": {}
        }
        
    def find_redundant_expressions(self, 
                                cfg: ControlFlowGraph,
                                avail_exprs: Dict[int, Set[str]],
                                expressions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find redundant expressions (expressions that are computed multiple times).
        
        Args:
            cfg: The control flow graph to analyze
            avail_exprs: Available expressions from analyze
            expressions: Expression information from _find_expressions
            
        Returns:
            List of redundant expression information
        """
        redundant_exprs = []
        
        # For each node where expressions are computed
        for node_id, node_exprs in expressions.get("expressions", {}).items():
            # Check if any of the expressions at this node are already available
            for expr in node_exprs:
                if expr in avail_exprs.get(node_id, set()):
                    redundant_exprs.append({
                        "expression": expr,
                        "node_id": node_id
                    })
        
        return redundant_exprs