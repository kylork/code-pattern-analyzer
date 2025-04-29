"""
Control Flow Analysis module.

This module implements control flow graph generation and analysis,
which enables tracking the possible execution paths through code.
"""

from typing import Dict, List, Set, Tuple, Optional, Any, Union
import logging
from enum import Enum
import networkx as nx
import tree_sitter

logger = logging.getLogger(__name__)

class NodeType(Enum):
    """Types of nodes in a control flow graph."""
    ENTRY = "entry"
    EXIT = "exit"
    STATEMENT = "statement"
    BRANCH = "branch"
    LOOP = "loop"
    RETURN = "return"
    EXCEPTION = "exception"
    FUNCTION_CALL = "function_call"

class ControlFlowGraph:
    """Representation of a control flow graph.
    
    This class uses a NetworkX directed graph to represent control flow,
    with nodes representing code blocks and edges representing possible
    execution paths.
    """
    
    def __init__(self, name: str = "anonymous"):
        """Initialize a control flow graph.
        
        Args:
            name: Name of the function or method this CFG represents
        """
        self.name = name
        self.graph = nx.DiGraph()
        self.entry_node = None
        self.exit_nodes = set()
        self.next_node_id = 0
        
    def add_node(self, 
                node_type: NodeType, 
                code: Optional[str] = None, 
                node_data: Optional[Dict[str, Any]] = None) -> int:
        """Add a node to the control flow graph.
        
        Args:
            node_type: Type of the node
            code: Source code represented by this node
            node_data: Additional data for the node
            
        Returns:
            The ID of the created node
        """
        node_id = self.next_node_id
        self.next_node_id += 1
        
        # Create node data dictionary
        data = {
            "type": node_type,
            "code": code or "",
            **(node_data or {})
        }
        
        # Add the node to the graph
        self.graph.add_node(node_id, **data)
        
        # Update entry/exit nodes if needed
        if node_type == NodeType.ENTRY:
            self.entry_node = node_id
        elif node_type == NodeType.EXIT:
            self.exit_nodes.add(node_id)
            
        return node_id
    
    def add_edge(self, 
                from_node: int, 
                to_node: int,
                edge_type: Optional[str] = None,
                edge_data: Optional[Dict[str, Any]] = None) -> None:
        """Add an edge between nodes in the control flow graph.
        
        Args:
            from_node: Source node ID
            to_node: Target node ID
            edge_type: Type of the edge (e.g., 'true_branch', 'false_branch', 'loop')
            edge_data: Additional data for the edge
        """
        # Create edge data dictionary
        data = {**(edge_data or {})}
        if edge_type:
            data["type"] = edge_type
            
        # Add the edge to the graph
        self.graph.add_edge(from_node, to_node, **data)
    
    def get_node_data(self, node_id: int) -> Dict[str, Any]:
        """Get data for a specific node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            Dictionary of node data
        """
        return self.graph.nodes[node_id]
    
    def get_entry_paths(self) -> List[List[int]]:
        """Get all paths from entry to exit nodes.
        
        Returns:
            List of paths, where each path is a list of node IDs
        """
        if self.entry_node is None or not self.exit_nodes:
            return []
            
        paths = []
        for exit_node in self.exit_nodes:
            for path in nx.all_simple_paths(self.graph, self.entry_node, exit_node):
                paths.append(path)
                
        return paths
    
    def detect_unreachable_code(self) -> List[int]:
        """Detect unreachable code blocks in the graph.
        
        Returns:
            List of node IDs that are unreachable from the entry node
        """
        if self.entry_node is None:
            return list(self.graph.nodes)
            
        reachable_nodes = set(nx.descendants(self.graph, self.entry_node))
        reachable_nodes.add(self.entry_node)
        
        all_nodes = set(self.graph.nodes)
        unreachable_nodes = all_nodes - reachable_nodes
        
        return sorted(list(unreachable_nodes))
    
    def detect_cycles(self) -> List[List[int]]:
        """Detect cycles in the control flow graph.
        
        Returns:
            List of cycles, where each cycle is a list of node IDs
        """
        return list(nx.simple_cycles(self.graph))
    
    def find_dominators(self) -> Dict[int, Set[int]]:
        """Find dominator relationships in the control flow graph.
        
        A node D dominates a node N if every path from the entry node to N
        must go through D.
        
        Returns:
            Dictionary mapping each node to the set of nodes that dominate it
        """
        if self.entry_node is None:
            return {}
            
        return nx.immediate_dominators(self.graph, self.entry_node)
    
    def calculate_cyclomatic_complexity(self) -> int:
        """Calculate the cyclomatic complexity of the control flow graph.
        
        Cyclomatic complexity is defined as E - N + 2P, where:
        - E is the number of edges
        - N is the number of nodes
        - P is the number of connected components (usually 1)
        
        Returns:
            The cyclomatic complexity value
        """
        edges = self.graph.number_of_edges()
        nodes = self.graph.number_of_nodes()
        components = nx.number_weakly_connected_components(self.graph)
        
        return edges - nodes + 2 * components
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the control flow graph to a dictionary representation.
        
        Returns:
            Dictionary representation of the graph
        """
        nodes = []
        for node_id in self.graph.nodes:
            node_data = self.get_node_data(node_id)
            nodes.append({
                "id": node_id,
                "type": node_data["type"].value if isinstance(node_data["type"], NodeType) else node_data["type"],
                "code": node_data.get("code", ""),
                "data": {k: v for k, v in node_data.items() if k not in ["type", "code"]}
            })
            
        edges = []
        for from_node, to_node, data in self.graph.edges(data=True):
            edges.append({
                "from": from_node,
                "to": to_node,
                "type": data.get("type", "normal"),
                "data": {k: v for k, v in data.items() if k != "type"}
            })
            
        return {
            "name": self.name,
            "nodes": nodes,
            "edges": edges,
            "entry_node": self.entry_node,
            "exit_nodes": list(self.exit_nodes)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ControlFlowGraph':
        """Create a ControlFlowGraph from a dictionary representation.
        
        Args:
            data: Dictionary representation of the graph
            
        Returns:
            A new ControlFlowGraph instance
        """
        cfg = cls(name=data.get("name", "anonymous"))
        
        # Set next_node_id to avoid conflicts
        if data.get("nodes"):
            cfg.next_node_id = max(node["id"] for node in data["nodes"]) + 1
        
        # Add nodes
        for node_data in data.get("nodes", []):
            # Create the node with the specific ID
            node_id = node_data["id"]
            node_type = NodeType(node_data["type"]) if isinstance(node_data["type"], str) else node_data["type"]
            code = node_data.get("code", "")
            additional_data = node_data.get("data", {})
            
            # Add to graph directly since we're using a specific ID
            cfg.graph.add_node(node_id, type=node_type, code=code, **additional_data)
            
            # Update entry/exit nodes if needed
            if node_type == NodeType.ENTRY:
                cfg.entry_node = node_id
            elif node_type == NodeType.EXIT:
                cfg.exit_nodes.add(node_id)
        
        # Add edges
        for edge_data in data.get("edges", []):
            from_node = edge_data["from"]
            to_node = edge_data["to"]
            edge_type = edge_data.get("type", "normal")
            additional_data = edge_data.get("data", {})
            
            cfg.graph.add_edge(from_node, to_node, type=edge_type, **additional_data)
        
        return cfg
    
    def visualize(self, output_file: Optional[str] = None) -> Optional[str]:
        """Generate a visualization of the control flow graph.
        
        Args:
            output_file: Path to save the visualization. If None, the visualization
                         will be displayed interactively (if in a supported environment).
                         
        Returns:
            Path to the saved visualization file, or None if displayed interactively
        """
        try:
            import matplotlib.pyplot as plt
            from matplotlib.colors import LinearSegmentedColormap
            
            # Create position layout for nodes
            pos = nx.spring_layout(self.graph, seed=42)
            
            # Create figure
            plt.figure(figsize=(12, 8))
            
            # Define node colors based on type
            node_colors = []
            for node in self.graph.nodes:
                node_type = self.graph.nodes[node].get("type")
                if node_type == NodeType.ENTRY:
                    node_colors.append("green")
                elif node_type == NodeType.EXIT:
                    node_colors.append("red")
                elif node_type == NodeType.BRANCH:
                    node_colors.append("orange")
                elif node_type == NodeType.LOOP:
                    node_colors.append("purple")
                elif node_type == NodeType.RETURN:
                    node_colors.append("blue")
                elif node_type == NodeType.EXCEPTION:
                    node_colors.append("yellow")
                else:
                    node_colors.append("skyblue")
            
            # Draw nodes
            nx.draw_networkx_nodes(self.graph, pos, node_size=700, node_color=node_colors, alpha=0.8)
            
            # Draw edges
            edge_colors = []
            for u, v, data in self.graph.edges(data=True):
                edge_type = data.get("type", "normal")
                if edge_type == "true_branch":
                    edge_colors.append("green")
                elif edge_type == "false_branch":
                    edge_colors.append("red")
                elif edge_type == "loop":
                    edge_colors.append("purple")
                elif edge_type == "exception":
                    edge_colors.append("orange")
                else:
                    edge_colors.append("black")
                    
            nx.draw_networkx_edges(self.graph, pos, edge_color=edge_colors, 
                                  width=1.5, arrowsize=15, arrowstyle="->")
            
            # Draw labels
            labels = {}
            for node in self.graph.nodes:
                node_data = self.graph.nodes[node]
                node_type = node_data.get("type")
                code = node_data.get("code", "")
                
                # Create a shortened label
                if isinstance(node_type, NodeType):
                    type_str = node_type.value
                else:
                    type_str = str(node_type)
                    
                if code:
                    # Shorten code for the label
                    code_short = code[:20] + "..." if len(code) > 20 else code
                    code_short = code_short.replace("\n", "↵")
                    labels[node] = f"{type_str}: {code_short}"
                else:
                    labels[node] = type_str
                    
            nx.draw_networkx_labels(self.graph, pos, labels=labels, font_size=10)
            
            # Set title and adjust layout
            plt.title(f"Control Flow Graph: {self.name}")
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


class ControlFlowAnalyzer:
    """Analyzer for generating and analyzing control flow graphs."""
    
    def __init__(self):
        """Initialize the control flow analyzer."""
        # Language-specific configurations for control flow
        self.language_config = {
            "python": {
                "queries": {
                    "functions": """
                        (function_definition
                            name: (identifier) @function_name
                            body: (block) @function_body) @function
                        
                        (class_definition
                            name: (identifier) @class_name
                            body: (block
                                (function_definition
                                    name: (identifier) @method_name
                                    body: (block) @method_body) @method)) @class
                    """,
                    "statements": """
                        (expression_statement) @expr
                        (assignment) @assign
                        (return_statement) @return
                        (if_statement) @if
                        (elif_clause) @elif
                        (else_clause) @else
                        (for_statement) @for
                        (while_statement) @while
                        (try_statement) @try
                        (except_clause) @except
                        (finally_clause) @finally
                        (raise_statement) @raise
                        (assert_statement) @assert
                        (break_statement) @break
                        (continue_statement) @continue
                        (pass_statement) @pass
                        (call) @call
                    """
                }
            },
            "javascript": {
                "queries": {
                    "functions": """
                        (function_declaration
                            name: (identifier) @function_name
                            body: (statement_block) @function_body) @function
                        
                        (method_definition
                            name: (property_identifier) @method_name
                            body: (statement_block) @method_body) @method
                        
                        (arrow_function
                            body: [(statement_block) @arrow_body, (expression) @arrow_expr]) @arrow
                    """,
                    "statements": """
                        (expression_statement) @expr
                        (variable_declaration) @var
                        (lexical_declaration) @lex_decl
                        (return_statement) @return
                        (if_statement) @if
                        (else_clause) @else
                        (for_statement) @for
                        (for_in_statement) @for_in
                        (while_statement) @while
                        (do_statement) @do
                        (switch_statement) @switch
                        (case_statement) @case
                        (try_statement) @try
                        (catch_clause) @catch
                        (finally_clause) @finally
                        (throw_statement) @throw
                        (break_statement) @break
                        (continue_statement) @continue
                        (call_expression) @call
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
    
    def create_cfg_from_tree(self, 
                           tree: tree_sitter.Tree, 
                           code: str, 
                           language: str,
                           func_name: Optional[str] = None) -> Dict[str, ControlFlowGraph]:
        """Create control flow graphs from a tree-sitter AST.
        
        Args:
            tree: The tree-sitter AST
            code: The source code that was parsed
            language: The language of the source code
            func_name: Optional function name to only create a CFG for a specific function
            
        Returns:
            Dictionary mapping function names to their control flow graphs
        """
        if not self.supports_language(language):
            logger.warning(f"Control flow analysis not supported for language: {language}")
            return {}
            
        try:
            from tree_sitter import Query, Language, Parser
            
            # Get the language module
            from src.tree_sitter_manager import LanguageManager
            manager = LanguageManager()
            lang_module = manager.get_language(language)
            
            # Get queries for this language
            lang_config = self.language_config[language]
            functions_query = lang_config["queries"]["functions"]
            statements_query = lang_config["queries"]["statements"]
            
            # Query for functions/methods
            function_query = Query(lang_module, functions_query)
            function_matches = function_query.captures(tree.root_node)
            
            # Extract functions and methods
            functions = {}
            function_nodes = {}
            
            for match, tag in function_matches:
                if tag in ['function', 'method', 'arrow']:
                    function_nodes[match.id] = match
            
            # Create CFGs for each function
            cfgs = {}
            
            for node_id, node in function_nodes.items():
                # Get function name
                name = "anonymous"
                for match, tag in function_matches:
                    if tag in ['function_name', 'method_name'] and match.parent.id == node_id:
                        name = code[match.start_byte:match.end_byte]
                        break
                
                # Skip if a specific function was requested and this isn't it
                if func_name is not None and name != func_name:
                    continue
                
                # Get function body
                body = None
                for match, tag in function_matches:
                    if tag in ['function_body', 'method_body', 'arrow_body', 'arrow_expr'] and match.parent.id == node_id:
                        body = match
                        break
                
                if body:
                    # Create CFG for this function
                    cfg = self._build_cfg_for_function(name, body, code, language, lang_module, statements_query)
                    cfgs[name] = cfg
            
            return cfgs
            
        except Exception as e:
            logger.error(f"Error creating control flow graphs: {e}")
            return {}
    
    def _build_cfg_for_function(self, 
                              name: str, 
                              body_node: tree_sitter.Node, 
                              code: str, 
                              language: str,
                              lang_module,
                              statements_query: str) -> ControlFlowGraph:
        """Build a control flow graph for a single function.
        
        Args:
            name: Function name
            body_node: The AST node representing the function body
            code: The source code
            language: The language of the source code
            lang_module: The tree-sitter language module
            statements_query: Query for statements
            
        Returns:
            A ControlFlowGraph for the function
        """
        # Create a new CFG
        cfg = ControlFlowGraph(name=name)
        
        # Create entry and exit nodes
        entry_node = cfg.add_node(NodeType.ENTRY, "ENTRY")
        exit_node = cfg.add_node(NodeType.EXIT, "EXIT")
        
        # Query for statements in the function body
        query = Query(lang_module, statements_query)
        statement_matches = query.captures(body_node)
        
        # Build the CFG
        current_node = entry_node
        
        # Group matches by their parent (to handle nested structures)
        statements_by_parent = {}
        for match, tag in statement_matches:
            parent_id = match.parent.id if match.parent else None
            if parent_id not in statements_by_parent:
                statements_by_parent[parent_id] = []
            statements_by_parent[parent_id].append((match, tag))
        
        # Process top-level statements in the function body
        self._process_statements(cfg, body_node.id, statements_by_parent, entry_node, exit_node, code)
        
        return cfg
    
    def _process_statements(self, 
                          cfg: ControlFlowGraph, 
                          parent_id: int, 
                          statements_by_parent: Dict[int, List[Tuple[tree_sitter.Node, str]]],
                          current_node: int,
                          exit_node: int,
                          code: str) -> int:
        """Process a block of statements to build the CFG.
        
        Args:
            cfg: The control flow graph being built
            parent_id: ID of the parent node
            statements_by_parent: Dictionary mapping parent node IDs to their statements
            current_node: Current CFG node to connect from
            exit_node: Exit node of the function
            code: The source code
            
        Returns:
            The last node in this block of statements
        """
        if parent_id not in statements_by_parent:
            return current_node
            
        # Get statements for this parent
        statements = sorted(
            statements_by_parent[parent_id], 
            key=lambda x: (x[0].start_point[0], x[0].start_point[1])
        )
        
        # Process each statement
        for stmt_node, stmt_type in statements:
            # Extract the code for this statement
            stmt_code = code[stmt_node.start_byte:stmt_node.end_byte]
            
            # Handle different statement types
            if stmt_type in ['expr', 'assign', 'var', 'lex_decl', 'pass']:
                # Simple statement - create a node and connect it
                stmt_node_id = cfg.add_node(NodeType.STATEMENT, stmt_code)
                cfg.add_edge(current_node, stmt_node_id)
                current_node = stmt_node_id
                
            elif stmt_type in ['return']:
                # Return statement - connect to the exit node
                return_node = cfg.add_node(NodeType.RETURN, stmt_code)
                cfg.add_edge(current_node, return_node)
                cfg.add_edge(return_node, exit_node)
                # No further nodes will be executed after return
                return None
                
            elif stmt_type in ['break']:
                # Break statement - handled by the loop processing
                break_node = cfg.add_node(NodeType.STATEMENT, stmt_code, {"is_break": True})
                cfg.add_edge(current_node, break_node)
                # Signal that this is a break
                return break_node
                
            elif stmt_type in ['continue']:
                # Continue statement - handled by the loop processing
                continue_node = cfg.add_node(NodeType.STATEMENT, stmt_code, {"is_continue": True})
                cfg.add_edge(current_node, continue_node)
                # Signal that this is a continue
                return continue_node
                
            elif stmt_type in ['if']:
                # If statement - create a branch node
                if_node = cfg.add_node(NodeType.BRANCH, f"if {stmt_code.split(':', 1)[0]}")
                cfg.add_edge(current_node, if_node)
                
                # Process the 'if' body
                if_body_id = stmt_node.child_by_field_name("consequence").id
                if_body_end = self._process_statements(cfg, if_body_id, statements_by_parent, if_node, exit_node, code)
                
                # Process the 'else' clause if it exists
                else_body_node = stmt_node.child_by_field_name("alternative")
                
                if else_body_node:
                    else_body_id = else_body_node.id
                    else_body_end = self._process_statements(cfg, else_body_id, statements_by_parent, if_node, exit_node, code)
                    
                    # If both branches can continue, merge them
                    if if_body_end and else_body_end:
                        merge_node = cfg.add_node(NodeType.STATEMENT, "if-else merge")
                        cfg.add_edge(if_body_end, merge_node, "true_branch")
                        cfg.add_edge(else_body_end, merge_node, "false_branch")
                        current_node = merge_node
                    else:
                        # If one branch can't continue (has return/break), use the other
                        current_node = if_body_end or else_body_end
                else:
                    # No else, if body rejoins main flow or if it's None, if condition becomes current node
                    merge_node = cfg.add_node(NodeType.STATEMENT, "if merge")
                    if if_body_end:
                        cfg.add_edge(if_body_end, merge_node, "true_branch")
                    cfg.add_edge(if_node, merge_node, "false_branch")
                    current_node = merge_node
                    
            elif stmt_type in ['for', 'while']:
                # Loop - create a loop node
                loop_node = cfg.add_node(NodeType.LOOP, stmt_code.split(':', 1)[0])
                cfg.add_edge(current_node, loop_node)
                
                # Process the loop body
                loop_body_id = stmt_node.child_by_field_name("body").id
                loop_body_end = self._process_statements(cfg, loop_body_id, statements_by_parent, loop_node, exit_node, code)
                
                # Connect loop back to loop node
                if loop_body_end:
                    if hasattr(loop_body_end, "is_break"):
                        # Break statement - exit the loop
                        pass
                    elif hasattr(loop_body_end, "is_continue"):
                        # Continue statement - go back to loop condition
                        cfg.add_edge(loop_body_end, loop_node, "loop")
                    else:
                        # Normal end of loop body - go back to loop condition
                        cfg.add_edge(loop_body_end, loop_node, "loop")
                
                # Loop exit - create a node for code after the loop
                loop_exit = cfg.add_node(NodeType.STATEMENT, "loop exit")
                cfg.add_edge(loop_node, loop_exit, "loop_exit")
                current_node = loop_exit
                
            elif stmt_type in ['try']:
                # Try statement - create a try node
                try_node = cfg.add_node(NodeType.STATEMENT, "try")
                cfg.add_edge(current_node, try_node)
                
                # Process the try body
                try_body_id = stmt_node.child_by_field_name("body").id
                try_body_end = self._process_statements(cfg, try_body_id, statements_by_parent, try_node, exit_node, code)
                
                # Process except clauses
                except_clauses = [child for child in stmt_node.children if child.type == "except_clause"]
                except_ends = []
                
                for except_node in except_clauses:
                    except_id = except_node.id
                    except_node_id = cfg.add_node(NodeType.EXCEPTION, code[except_node.start_byte:except_node.end_byte].split(':', 1)[0])
                    cfg.add_edge(try_node, except_node_id, "exception")
                    
                    # Process the except body
                    except_body_id = except_node.child_by_field_name("body").id
                    except_end = self._process_statements(cfg, except_body_id, statements_by_parent, except_node_id, exit_node, code)
                    if except_end:
                        except_ends.append(except_end)
                
                # Process finally clause if it exists
                finally_clause = None
                for child in stmt_node.children:
                    if child.type == "finally_clause":
                        finally_clause = child
                        break
                        
                finally_end = None
                if finally_clause:
                    finally_id = finally_clause.id
                    finally_node_id = cfg.add_node(NodeType.STATEMENT, "finally")
                    
                    # Connect try body to finally if it doesn't end with return/break
                    if try_body_end:
                        cfg.add_edge(try_body_end, finally_node_id)
                        
                    # Connect each except clause to finally if it doesn't end with return/break
                    for except_end in except_ends:
                        if except_end:
                            cfg.add_edge(except_end, finally_node_id)
                            
                    # Process the finally body
                    finally_body_id = finally_clause.child_by_field_name("body").id
                    finally_end = self._process_statements(cfg, finally_body_id, statements_by_parent, finally_node_id, exit_node, code)
                    
                # Determine the final current node after try-except-finally
                if finally_end:
                    current_node = finally_end
                elif except_ends:
                    # Create a merge node for all except clauses
                    merge_node = cfg.add_node(NodeType.STATEMENT, "except merge")
                    for except_end in except_ends:
                        if except_end:
                            cfg.add_edge(except_end, merge_node)
                    
                    # If try body doesn't end with return/break, connect it to merge too
                    if try_body_end:
                        cfg.add_edge(try_body_end, merge_node)
                        
                    current_node = merge_node
                else:
                    # No except clauses, just try body
                    current_node = try_body_end
                    
            elif stmt_type in ['call']:
                # Function call
                call_node = cfg.add_node(NodeType.FUNCTION_CALL, stmt_code)
                cfg.add_edge(current_node, call_node)
                current_node = call_node
                
            elif stmt_type in ['raise', 'throw']:
                # Exception raising - connect to exit
                raise_node = cfg.add_node(NodeType.EXCEPTION, stmt_code)
                cfg.add_edge(current_node, raise_node)
                cfg.add_edge(raise_node, exit_node)
                # No further nodes will be executed after an uncaught exception
                return None
        
        # Return the last node in this block
        return current_node

    def find_dead_code(self, cfg: ControlFlowGraph) -> List[Dict[str, Any]]:
        """Find dead code in a control flow graph.
        
        Args:
            cfg: The control flow graph to analyze
            
        Returns:
            List of dead code nodes with their information
        """
        unreachable_nodes = cfg.detect_unreachable_code()
        
        dead_code = []
        for node_id in unreachable_nodes:
            node_data = cfg.get_node_data(node_id)
            dead_code.append({
                "node_id": node_id,
                "type": node_data["type"].value if isinstance(node_data["type"], NodeType) else str(node_data["type"]),
                "code": node_data.get("code", "")
            })
            
        return dead_code
    
    def detect_possible_infinite_loops(self, cfg: ControlFlowGraph) -> List[List[int]]:
        """Detect potentially infinite loops in a control flow graph.
        
        This is a heuristic detection that looks for cycles in the CFG
        that don't have any obvious exit conditions.
        
        Args:
            cfg: The control flow graph to analyze
            
        Returns:
            List of potential infinite loops, where each loop is a list of node IDs
        """
        # Find all cycles in the graph
        cycles = cfg.detect_cycles()
        
        # Filter for potentially infinite loops (cycles without obvious exit paths)
        potential_infinite_loops = []
        
        for cycle in cycles:
            has_exit_condition = False
            
            # Check for nodes in the cycle that have edges leading outside the cycle
            cycle_set = set(cycle)
            for node_id in cycle:
                # Get all neighbors of this node
                neighbors = list(cfg.graph.successors(node_id))
                
                # Check if any neighbors are outside the cycle
                for neighbor in neighbors:
                    if neighbor not in cycle_set:
                        # Found a potential exit path
                        has_exit_condition = True
                        break
                        
                if has_exit_condition:
                    break
            
            # If no exit conditions found, this could be an infinite loop
            if not has_exit_condition:
                potential_infinite_loops.append(cycle)
                
        return potential_infinite_loops
    
    def analyze_function_complexity(self, cfg: ControlFlowGraph) -> Dict[str, Any]:
        """Analyze the complexity of a function using its control flow graph.
        
        Args:
            cfg: The control flow graph to analyze
            
        Returns:
            Dictionary containing complexity metrics
        """
        # Calculate cyclomatic complexity
        cyclomatic_complexity = cfg.calculate_cyclomatic_complexity()
        
        # Calculate nesting depth (simplified approach)
        nesting_depth = 0
        for node_id in cfg.graph.nodes:
            node_data = cfg.get_node_data(node_id)
            if "nesting_level" in node_data:
                nesting_depth = max(nesting_depth, node_data["nesting_level"])
                
        # Detect code quality issues
        unreachable_code = len(cfg.detect_unreachable_code())
        potential_infinite_loops = len(self.detect_possible_infinite_loops(cfg))
        
        return {
            "function_name": cfg.name,
            "cyclomatic_complexity": cyclomatic_complexity,
            "nesting_depth": nesting_depth,
            "unreachable_code_blocks": unreachable_code,
            "potential_infinite_loops": potential_infinite_loops
        }
    
    def get_function_exit_paths(self, cfg: ControlFlowGraph) -> Dict[str, List[List[int]]]:
        """Get all possible exit paths from a function.
        
        Args:
            cfg: The control flow graph to analyze
            
        Returns:
            Dictionary mapping exit types to lists of paths
        """
        # Get all paths from entry to exit
        all_paths = cfg.get_entry_paths()
        
        # Categorize paths by their exit type
        exit_paths = {
            "normal": [],   # Normal return from function
            "exception": [] # Exit via exception
        }
        
        for path in all_paths:
            # Check the node before the exit node
            if len(path) >= 2:
                pre_exit_node = path[-2]
                node_data = cfg.get_node_data(pre_exit_node)
                node_type = node_data["type"]
                
                if node_type == NodeType.EXCEPTION or node_type == "exception":
                    exit_paths["exception"].append(path)
                else:
                    exit_paths["normal"].append(path)
                    
        return exit_paths