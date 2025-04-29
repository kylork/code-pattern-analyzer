"""
Event-Driven Architecture pattern detector.

This module provides a pattern detector for identifying the Event-Driven
architectural style in codebases.
"""

from typing import Dict, List, Optional, Set, Counter
import logging
import os
import re
import networkx as nx
from pathlib import Path
from collections import defaultdict

from ...pattern_base import Pattern, CompositePattern
from .architectural_style_base import ArchitecturalStylePattern

logger = logging.getLogger(__name__)

class EventDrivenPattern(ArchitecturalStylePattern):
    """Pattern for detecting Event-Driven Architecture.
    
    This pattern identifies codebases that follow the Event-Driven style,
    which emphasizes:
    
    1. Event production and consumption
    2. Message passing and event handling
    3. Loose coupling through event brokers
    4. Asynchronous processing
    5. Optional event sourcing and CQRS
    """
    
    def __init__(self):
        """Initialize the Event-Driven Architecture detector."""
        super().__init__(
            name="event_driven_architecture",
            description="Identifies Event-Driven Architecture patterns",
            languages=["python", "javascript", "typescript", "java", "go"],
        )
        
        # Component tracking
        self.event_producers = set()
        self.event_consumers = set()
        self.event_brokers = set()
        self.event_handlers = set()
        self.command_handlers = set()  # For CQRS
        self.query_handlers = set()    # For CQRS
        self.event_stores = set()      # For Event Sourcing
        
        # Event-related indicators
        self.event_indicators = [
            r'event', r'message', r'notification', r'signal',
            r'publish', r'subscribe', r'emit', r'dispatch',
            r'payload', r'topic', r'channel', r'queue'
        ]
        
        # Producer indicators
        self.producer_indicators = [
            r'producer', r'publisher', r'dispatcher', r'sender',
            r'emit', r'publish', r'raise_event', r'dispatch_event',
            r'send_message', r'trigger'
        ]
        
        # Consumer indicators
        self.consumer_indicators = [
            r'consumer', r'subscriber', r'listener', r'receiver',
            r'handler', r'process', r'on_event', r'on_message',
            r'subscribe', r'consume', r'listen'
        ]
        
        # Broker indicators
        self.broker_indicators = [
            r'broker', r'bus', r'mediator', r'queue', r'channel',
            r'exchange', r'topic', r'hub', r'distributor',
            r'rabbitmq', r'kafka', r'pubsub', r'servicebus', 
            r'eventhub', r'sns', r'sqs', r'eventbridge'
        ]
        
        # CQRS indicators
        self.cqrs_indicators = [
            r'command', r'query', r'cqrs', r'command_handler',
            r'query_handler', r'command_bus', r'query_bus',
            r'command_dispatcher', r'query_dispatcher'
        ]
        
        # Event Sourcing indicators
        self.event_sourcing_indicators = [
            r'event_store', r'event_sourcing', r'aggregate',
            r'projection', r'aggregate_root', r'event_stream',
            r'replay', r'snapshot', r'journal'
        ]
    
    def _process_pattern_matches(self, 
                               pattern_name: str, 
                               matches: List[Dict],
                               file_path: str) -> None:
        """Process pattern matches to add to the component graph.
        
        For Event-Driven Architecture, we're looking for:
        1. Event producers
        2. Event consumers/handlers
        3. Event brokers
        4. CQRS and Event Sourcing components
        
        Args:
            pattern_name: The name of the pattern
            matches: List of pattern matches
            file_path: Path to the file
        """
        # Skip patterns that aren't relevant for architectural style detection
        if pattern_name not in ["separation_of_concerns", "information_hiding", 
                               "dependency_inversion", "architectural_intent"]:
            return
            
        for match in matches:
            # Each match represents a component
            component_name = match.get('path', file_path)
            
            # Skip if already processed
            if self.component_graph.has_node(component_name):
                continue
                
            # Extract info from the file path and content
            component_type = self._classify_component(component_name, match)
            
            # Add component node to graph
            self.component_graph.add_node(
                component_name,
                type='component',
                event_component_type=component_type,
                message_passing=self._has_message_passing(component_name, match),
                asynchronous=self._is_asynchronous(component_name, match),
                uses_cqrs=self._uses_cqrs(component_name, match),
                uses_event_sourcing=self._uses_event_sourcing(component_name, match),
            )
            
            # Track component by type
            if component_type == 'producer':
                self.event_producers.add(component_name)
            elif component_type == 'consumer':
                self.event_consumers.add(component_name)
            elif component_type == 'broker':
                self.event_brokers.add(component_name)
            elif component_type == 'handler':
                self.event_handlers.add(component_name)
            elif component_type == 'command_handler':
                self.command_handlers.add(component_name)
            elif component_type == 'query_handler':
                self.query_handlers.add(component_name)
            elif component_type == 'event_store':
                self.event_stores.add(component_name)
            
            # Add dependencies if available
            if 'imports' in match:
                for dependency in match['imports']:
                    # Try to resolve relative paths or package references
                    dependency_path = self._resolve_dependency(component_name, dependency)
                    if dependency_path:
                        if not self.component_graph.has_node(dependency_path):
                            # Add placeholder node for now
                            self.component_graph.add_node(dependency_path, type='component')
                        
                        # Add dependency edge
                        self.component_graph.add_edge(component_name, dependency_path)
    
    def _classify_component(self, file_path: str, match: Dict) -> str:
        """Classify the component as an Event-Driven Architecture component.
        
        Args:
            file_path: Path to the file
            match: The pattern match data
            
        Returns:
            Component type classification
        """
        file_path_str = str(file_path).lower()
        imports = match.get('imports', [])
        imports_str = ' '.join(imports).lower()
        
        # First, check for event brokers since they're most distinctive
        for indicator in self.broker_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE) or re.search(indicator, imports_str, re.IGNORECASE):
                return 'broker'
        
        # Check for event stores (for Event Sourcing)
        for indicator in self.event_sourcing_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE) or re.search(indicator, imports_str, re.IGNORECASE):
                return 'event_store'
        
        # Check for CQRS command/query handlers
        if any(re.search(r'command_handler', s, re.IGNORECASE) for s in [file_path_str, imports_str]):
            return 'command_handler'
        if any(re.search(r'query_handler', s, re.IGNORECASE) for s in [file_path_str, imports_str]):
            return 'query_handler'
        
        # Check for event producers
        for indicator in self.producer_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE) or re.search(indicator, imports_str, re.IGNORECASE):
                return 'producer'
        
        # Check for event consumers/handlers
        for indicator in self.consumer_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE) or re.search(indicator, imports_str, re.IGNORECASE):
                return 'consumer'
        
        # Check if it contains event-related terms but isn't a specific component
        for indicator in self.event_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE) or re.search(indicator, imports_str, re.IGNORECASE):
                return 'handler'  # Generic event-related component
        
        # Default to "unknown" if we can't classify
        return 'unknown'
    
    def _has_message_passing(self, file_path: str, match: Dict) -> bool:
        """Determine if a component uses message passing.
        
        Args:
            file_path: Path to the file
            match: The pattern match information
            
        Returns:
            True if the component uses message passing
        """
        file_path_str = str(file_path).lower()
        imports = match.get('imports', [])
        imports_str = ' '.join(imports).lower()
        
        message_indicators = [
            r'send', r'publish', r'emit', r'dispatch', r'consume',
            r'subscribe', r'listen', r'receive', r'on_message',
            r'message', r'event', r'notification'
        ]
        
        for indicator in message_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE) or re.search(indicator, imports_str, re.IGNORECASE):
                return True
        
        return False
    
    def _is_asynchronous(self, file_path: str, match: Dict) -> bool:
        """Determine if a component uses asynchronous processing.
        
        Args:
            file_path: Path to the file
            match: The pattern match information
            
        Returns:
            True if the component uses asynchronous processing
        """
        file_path_str = str(file_path).lower()
        imports = match.get('imports', [])
        imports_str = ' '.join(imports).lower()
        
        async_indicators = [
            r'async', r'await', r'promise', r'future', r'callback',
            r'reactive', r'observable', r'subscribe', r'completable',
            r'parallel', r'non-blocking', r'rxjava', r'rxjs', r'reactor'
        ]
        
        for indicator in async_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE) or re.search(indicator, imports_str, re.IGNORECASE):
                return True
        
        return False
    
    def _uses_cqrs(self, file_path: str, match: Dict) -> bool:
        """Determine if a component uses CQRS.
        
        Args:
            file_path: Path to the file
            match: The pattern match information
            
        Returns:
            True if the component uses CQRS
        """
        file_path_str = str(file_path).lower()
        imports = match.get('imports', [])
        imports_str = ' '.join(imports).lower()
        
        for indicator in self.cqrs_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE) or re.search(indicator, imports_str, re.IGNORECASE):
                return True
        
        return False
    
    def _uses_event_sourcing(self, file_path: str, match: Dict) -> bool:
        """Determine if a component uses Event Sourcing.
        
        Args:
            file_path: Path to the file
            match: The pattern match information
            
        Returns:
            True if the component uses Event Sourcing
        """
        file_path_str = str(file_path).lower()
        imports = match.get('imports', [])
        imports_str = ' '.join(imports).lower()
        
        for indicator in self.event_sourcing_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE) or re.search(indicator, imports_str, re.IGNORECASE):
                return True
        
        return False
    
    def _resolve_dependency(self, source_path: str, dependency: str) -> Optional[str]:
        """Resolve a dependency string to a file path.
        
        Args:
            source_path: Path to the source file
            dependency: Dependency string (import or package)
            
        Returns:
            Resolved file path or None if can't resolve
        """
        # This is a simplified implementation
        # In a real system, this would have more complex import resolution
        
        # For now, just check if the dependency is a node in our graph
        for node in self.component_graph.nodes:
            if dependency in node:
                return node
                
        # Look for event-related libraries commonly used in imported names
        event_libraries = [
            'rabbitmq', 'kafka', 'pubsub', 'eventbus', 'rxjs', 'rxjava',
            'reactor', 'events', 'eventemitter', 'observer', 'reactive',
            'publisher', 'subscriber', 'emitter'
        ]
        
        for lib in event_libraries:
            if lib in dependency.lower():
                return f"external://{lib}"
                
        return None
    
    def _analyze_graph(self) -> Dict:
        """Analyze the component graph for Event-Driven Architecture.
        
        We detect:
        1. Event production and consumption
        2. Message-passing patterns
        3. Presence of event brokers
        4. Asynchronous processing
        5. CQRS and Event Sourcing patterns
        
        Returns:
            A dictionary containing the event-driven architecture analysis
        """
        # No components to analyze
        if len(self.component_graph.nodes) == 0:
            return {
                "type": self.name,
                "confidence": 0.0,
                "components": [],
                "description": "No components to analyze"
            }
        
        # Calculate component type counts
        total_components = len(self.component_graph.nodes)
        producer_count = len(self.event_producers)
        consumer_count = len(self.event_consumers)
        broker_count = len(self.event_brokers)
        handler_count = len(self.event_handlers)
        command_handler_count = len(self.command_handlers)
        query_handler_count = len(self.query_handlers)
        event_store_count = len(self.event_stores)
        
        # Count components with message passing and asynchronous processing
        message_passing_count = sum(
            1 for node in self.component_graph.nodes
            if self.component_graph.nodes[node].get('message_passing', False)
        )
        
        async_count = sum(
            1 for node in self.component_graph.nodes
            if self.component_graph.nodes[node].get('asynchronous', False)
        )
        
        # Calculate CQRS and Event Sourcing usage
        cqrs_count = sum(
            1 for node in self.component_graph.nodes
            if self.component_graph.nodes[node].get('uses_cqrs', False)
        )
        
        event_sourcing_count = sum(
            1 for node in self.component_graph.nodes
            if self.component_graph.nodes[node].get('uses_event_sourcing', False)
        )
        
        # Calculate architectural intent scores from previously analyzed results
        soc_score = 0.0
        if 'separation_of_concerns' in self.architectural_intents:
            soc_score = self.architectural_intents['separation_of_concerns'].get('confidence', 0.0)
            
        info_hiding_score = 0.0
        if 'information_hiding' in self.architectural_intents:
            info_hiding_score = self.architectural_intents['information_hiding'].get('confidence', 0.0)
            
        dip_score = 0.0
        if 'dependency_inversion' in self.architectural_intents:
            dip_score = self.architectural_intents['dependency_inversion'].get('confidence', 0.0)
        
        # Compile metrics
        metrics = {
            "total_components": total_components,
            "event_producer_count": producer_count,
            "event_consumer_count": consumer_count,
            "event_broker_count": broker_count,
            "event_handler_count": handler_count,
            "message_passing_component_count": message_passing_count,
            "async_component_count": async_count,
            "message_passing_ratio": message_passing_count / total_components if total_components > 0 else 0,
            "async_ratio": async_count / total_components if total_components > 0 else 0,
            "uses_cqrs": cqrs_count > 0,
            "cqrs_component_count": cqrs_count,
            "command_handler_count": command_handler_count,
            "query_handler_count": query_handler_count,
            "uses_event_sourcing": event_sourcing_count > 0,
            "event_sourcing_component_count": event_sourcing_count,
            "event_store_count": event_store_count,
            "separation_of_concerns_score": soc_score,
            "information_hiding_score": info_hiding_score,
            "dependency_inversion_score": dip_score,
        }
        
        # Calculate event-driven architecture confidence score
        confidence = self._calculate_event_driven_confidence(metrics)
        
        # Generate description
        description = self._generate_description(metrics, confidence)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, confidence)
        
        # Extract component details
        components = []
        for node in self.component_graph.nodes:
            component_type = self.component_graph.nodes[node].get('event_component_type', 'unknown')
            
            # Only include event-related components
            if component_type != 'unknown':
                components.append({
                    "name": node,
                    "type": component_type,
                    "message_passing": self.component_graph.nodes[node].get('message_passing', False),
                    "asynchronous": self.component_graph.nodes[node].get('asynchronous', False),
                    "uses_cqrs": self.component_graph.nodes[node].get('uses_cqrs', False),
                    "uses_event_sourcing": self.component_graph.nodes[node].get('uses_event_sourcing', False),
                })
        
        return {
            "type": self.name,
            "confidence": confidence,
            "components": components,
            "metrics": metrics,
            "recommendations": recommendations,
            "description": description
        }
    
    def _calculate_event_driven_confidence(self, metrics: Dict) -> float:
        """Calculate confidence score for event-driven architecture.
        
        Args:
            metrics: Architecture metrics
            
        Returns:
            Confidence score (0.0-1.0)
        """
        # Key indicators for event-driven architecture
        factors = [
            # Must have message passing
            0.3 * metrics["message_passing_ratio"],
            
            # Should have event producers
            0.15 * min(1.0, metrics["event_producer_count"] / 2),
            
            # Should have event consumers
            0.15 * min(1.0, metrics["event_consumer_count"] / 2),
            
            # Should have event brokers
            0.15 * min(1.0, metrics["event_broker_count"] / 1),
            
            # Should have asynchronous processing
            0.15 * metrics["async_ratio"],
            
            # CQRS is a bonus
            0.05 * (1.0 if metrics["uses_cqrs"] else 0.0),
            
            # Event Sourcing is a bonus
            0.05 * (1.0 if metrics["uses_event_sourcing"] else 0.0)
        ]
        
        # Calculate weighted score
        confidence = sum(factors)
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def _generate_description(self, metrics: Dict, confidence: float) -> str:
        """Generate a description of the architectural style.
        
        Args:
            metrics: The metrics dictionary
            confidence: Confidence score
            
        Returns:
            Human-readable description
        """
        # Determine confidence level
        if confidence > 0.8:
            confidence_desc = "strong"
        elif confidence > 0.6:
            confidence_desc = "good"
        elif confidence > 0.4:
            confidence_desc = "moderate"
        elif confidence > 0.2:
            confidence_desc = "weak"
        else:
            confidence_desc = "minimal"
            
        # Build description
        desc = f"The codebase shows {confidence_desc} evidence of Event-Driven Architecture. "
        
        # Add component details
        desc += f"Analysis identified {metrics['event_producer_count']} event producers, "
        desc += f"{metrics['event_consumer_count']} event consumers, and "
        desc += f"{metrics['event_broker_count']} event brokers. "
        
        # Add message passing details
        message_ratio = metrics["message_passing_ratio"]
        if message_ratio > 0.7:
            desc += "The codebase heavily relies on message passing for communication. "
        elif message_ratio > 0.4:
            desc += "Message passing is used in some parts of the codebase. "
        else:
            desc += "Message passing is not widely used, which is unusual for an event-driven system. "
        
        # Add asynchronous processing details
        async_ratio = metrics["async_ratio"]
        if async_ratio > 0.7:
            desc += "Components are predominantly asynchronous. "
        elif async_ratio > 0.4:
            desc += "Some components use asynchronous processing. "
        else:
            desc += "Asynchronous processing is limited, which is unusual for an event-driven system. "
        
        # Add CQRS and Event Sourcing details
        uses_cqrs = metrics["uses_cqrs"]
        uses_event_sourcing = metrics["uses_event_sourcing"]
        
        if uses_cqrs and uses_event_sourcing:
            desc += "The codebase implements both CQRS and Event Sourcing patterns, indicating advanced event-driven techniques. "
        elif uses_cqrs:
            desc += "The codebase implements the CQRS pattern, separating command and query responsibilities. "
        elif uses_event_sourcing:
            desc += "The codebase implements Event Sourcing, storing state as a sequence of events. "
        
        # Add overall assessment
        if confidence > 0.7:
            desc += "The codebase demonstrates a deliberate implementation of Event-Driven Architecture."
        elif confidence > 0.4:
            desc += "The codebase shows partial implementation of Event-Driven Architecture concepts but could be improved."
        else:
            desc += "The codebase shows only superficial resemblance to Event-Driven Architecture."
            
        return desc
    
    def _generate_recommendations(self, metrics: Dict, confidence: float) -> List[str]:
        """Generate recommendations for improving event-driven architecture.
        
        Args:
            metrics: The metrics dictionary
            confidence: Confidence score
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Only generate recommendations if confidence is below excellent
        if confidence < 0.8:
            # Message passing recommendations
            if metrics["message_passing_ratio"] < 0.5:
                recommendations.append(
                    "Increase the use of message passing for communication between components"
                )
                
            # Event producers/consumers recommendations
            if metrics["event_producer_count"] < 2:
                recommendations.append(
                    "Create more explicit event producers that publish events to the system"
                )
                
            if metrics["event_consumer_count"] < 2:
                recommendations.append(
                    "Implement more event consumers/handlers to respond to events"
                )
                
            # Event broker recommendations
            if metrics["event_broker_count"] < 1:
                recommendations.append(
                    "Introduce an event broker to decouple event producers from consumers"
                )
                
            # Asynchronous processing recommendations
            if metrics["async_ratio"] < 0.5:
                recommendations.append(
                    "Increase the use of asynchronous processing to fully benefit from event-driven architecture"
                )
                
            # Advanced pattern recommendations
            if not metrics["uses_cqrs"] and confidence > 0.4:
                recommendations.append(
                    "Consider implementing CQRS to separate command and query responsibilities"
                )
                
            if not metrics["uses_event_sourcing"] and confidence > 0.5:
                recommendations.append(
                    "Consider implementing Event Sourcing for critical business entities to maintain a complete history"
                )
        
        return recommendations