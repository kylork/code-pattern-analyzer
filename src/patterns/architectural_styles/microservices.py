"""
Microservices Architecture pattern detector.

This module provides a pattern detector for identifying the Microservices
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

class MicroservicesPattern(ArchitecturalStylePattern):
    """Pattern for detecting Microservices Architecture.
    
    This pattern identifies codebases that follow the Microservices style,
    which emphasizes:
    
    1. Small, focused services with single responsibilities
    2. Service independence and loose coupling
    3. Service-specific databases and storage
    4. API-based communication
    5. Containerization and deployment isolation
    """
    
    def __init__(self):
        """Initialize the Microservices Architecture detector."""
        super().__init__(
            name="microservices_architecture",
            description="Identifies Microservices Architecture patterns",
            languages=["python", "javascript", "typescript", "java", "go"],
        )
        
        # Service tracking
        self.services = defaultdict(dict)
        self.service_boundary_confidence = defaultdict(float)
        
        # Service indicator patterns
        self.service_indicators = [
            r'service/', r'-service', r'_service',
            r'microservice', r'micro-service', r'api/',
            r'gateway', r'server',
        ]
        
        # API indicators
        self.api_indicators = [
            r'api', r'controller', r'endpoint', r'route',
            r'rest', r'graphql', r'grpc', r'handler',
            r'http', r'resource'
        ]
        
        # Database indicators
        self.db_indicators = [
            r'repository', r'dao', r'database', r'persistence',
            r'mongo', r'mysql', r'postgres', r'db', r'orm',
            r'sequelize', r'typeorm', r'knex'
        ]
        
        # Container indicators
        self.container_indicators = [
            r'docker', r'container', r'dockerfile', r'k8s',
            r'kubernetes', r'deployment', r'pod', r'service.yaml',
            r'helm', r'chart.yaml'
        ]
        
        # Communication indicators
        self.communication_indicators = [
            r'client', r'feign', r'rest', r'http', r'grpc',
            r'rabbitmq', r'kafka', r'pubsub', r'queue', r'message',
            r'request', r'response', r'eventbus'
        ]
    
    def _process_pattern_matches(self, 
                               pattern_name: str, 
                               matches: List[Dict],
                               file_path: str) -> None:
        """Process pattern matches to add to the component graph.
        
        For Microservices, we're looking for:
        1. Service boundaries
        2. API endpoints
        3. Database access
        4. Inter-service communication
        5. Container configuration
        
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
                
            # Extract info from the file path
            path_parts = self._get_path_parts(component_name)
            
            # Determine which service this belongs to
            service_name = self._identify_service(component_name, path_parts)
            
            # Determine component attributes
            is_api = self._is_api(component_name, match)
            is_db = self._is_database(component_name, match)
            is_container = self._is_container_config(component_name)
            is_inter_service = self._is_service_communication(component_name, match)
            
            # Add component node to graph
            self.component_graph.add_node(
                component_name,
                type='component',
                service=service_name,
                is_api=is_api,
                is_db=is_db,
                is_container=is_container,
                is_inter_service=is_inter_service,
                soc_score=match.get('info_hiding_score', 0.0),
                info_hiding_score=match.get('info_hiding_score', 0.0),
                di_score=match.get('dip_score', 0.0),
            )
            
            # Track service details
            if service_name not in self.services:
                self.services[service_name] = {
                    'api_count': 0,
                    'db_count': 0,
                    'container_config': False,
                    'inter_service_count': 0,
                    'component_count': 0,
                }
                
            self.services[service_name]['component_count'] += 1
            if is_api:
                self.services[service_name]['api_count'] += 1
            if is_db:
                self.services[service_name]['db_count'] += 1
            if is_container:
                self.services[service_name]['container_config'] = True
            if is_inter_service:
                self.services[service_name]['inter_service_count'] += 1
            
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
    
    def _get_path_parts(self, file_path: str) -> List[str]:
        """Extract meaningful parts from the file path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of path segments
        """
        # Convert to Path object for easier manipulation
        path = Path(file_path)
        
        # Get path parts excluding the filename itself
        parts = list(path.parts)
        
        # Filter out common non-meaningful parts
        filtered_parts = [p.lower() for p in parts if p not in [
            '/', '.', 'src', 'source', 'app', 'main'
        ]]
        
        return filtered_parts
    
    def _identify_service(self, file_path: str, path_parts: List[str]) -> str:
        """Identify which service a component belongs to.
        
        Args:
            file_path: Path to the file
            path_parts: List of path segments
            
        Returns:
            Service name or 'unknown'
        """
        file_path_str = str(file_path).lower()
        
        # Look for specific service indicators
        for part in path_parts:
            for indicator in self.service_indicators:
                if re.search(indicator, part, re.IGNORECASE):
                    # Extract service name
                    service_name = part.replace('service', '').replace('-', '').replace('_', '')
                    if service_name:
                        return service_name
                    return part
                    
        # Look for common microservice project structure
        # Examples: user-service/src/..., services/user/...
        for i, part in enumerate(path_parts):
            if part in ['services', 'microservices'] and i < len(path_parts) - 1:
                return path_parts[i+1]
                
        # Default to top-level directory if not found
        if path_parts:
            return path_parts[0]
            
        return 'unknown'
    
    def _is_api(self, file_path: str, match: Dict) -> bool:
        """Determine if a component is an API endpoint.
        
        Args:
            file_path: Path to the file
            match: Pattern match information
            
        Returns:
            True if the component is an API endpoint
        """
        file_path_str = str(file_path).lower()
        
        # Check for API indicators in the path
        for indicator in self.api_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE):
                return True
                
        # Check component imports for API frameworks
        imports = match.get('imports', [])
        api_framework_imports = [
            'flask', 'express', 'django', 'spring', 'fastapi',
            'nestjs', 'hapi', 'koa', 'gin', 'echo', 'gorilla',
            'graphql', 'grpc', 'controller', 'endpoint'
        ]
        
        for imp in imports:
            for framework in api_framework_imports:
                if framework in imp.lower():
                    return True
                    
        return False
    
    def _is_database(self, file_path: str, match: Dict) -> bool:
        """Determine if a component is database-related.
        
        Args:
            file_path: Path to the file
            match: Pattern match information
            
        Returns:
            True if the component is database-related
        """
        file_path_str = str(file_path).lower()
        
        # Check for database indicators in the path
        for indicator in self.db_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE):
                return True
                
        # Check component imports for database technologies
        imports = match.get('imports', [])
        db_imports = [
            'sql', 'jdbc', 'mongo', 'mongoose', 'sequelize',
            'typeorm', 'repository', 'dao', 'entity', 'model',
            'knex', 'orm', 'gorm', 'prisma', 'redis', 'dynamodb'
        ]
        
        for imp in imports:
            for db in db_imports:
                if db in imp.lower():
                    return True
                    
        return False
    
    def _is_container_config(self, file_path: str) -> bool:
        """Determine if a file is container-related configuration.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file is container-related
        """
        file_path_str = str(file_path).lower()
        
        # Check filename for container config indicators
        base_name = os.path.basename(file_path_str)
        if base_name in ['dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
                         'deployment.yaml', 'deployment.yml', 'service.yaml', 
                         'service.yml', 'chart.yaml', 'values.yaml']:
            return True
            
        # Check path for container indicators
        for indicator in self.container_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE):
                return True
                
        return False
    
    def _is_service_communication(self, file_path: str, match: Dict) -> bool:
        """Determine if a component is related to inter-service communication.
        
        Args:
            file_path: Path to the file
            match: Pattern match information
            
        Returns:
            True if the component is related to inter-service communication
        """
        file_path_str = str(file_path).lower()
        
        # Check for communication indicators in the path
        for indicator in self.communication_indicators:
            if re.search(indicator, file_path_str, re.IGNORECASE):
                return True
                
        # Check component imports for communication technologies
        imports = match.get('imports', [])
        comm_imports = [
            'http', 'axios', 'fetch', 'rest', 'client',
            'rabbitmq', 'kafka', 'pubsub', 'servicebus',
            'grpc', 'protobuf', 'amqp', 'feign', 'eventbus',
            'messaging', 'queue', 'stream'
        ]
        
        for imp in imports:
            for comm in comm_imports:
                if comm in imp.lower():
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
                
        # Service-to-service communication might use service names
        for service_name in self.services.keys():
            if service_name in dependency.lower():
                # This is likely a cross-service dependency
                return f"service://{service_name}"
                
        return None
    
    def _analyze_graph(self) -> Dict:
        """Analyze the component graph for Microservices Architecture.
        
        We detect:
        1. Service boundaries
        2. API presence in each service
        3. Database isolation
        4. Container configuration
        5. Service communication patterns
        
        Returns:
            A dictionary containing the microservices architecture analysis
        """
        # No components to analyze
        if len(self.component_graph.nodes) == 0:
            return {
                "type": self.name,
                "confidence": 0.0,
                "components": [],
                "description": "No components to analyze"
            }
        
        # Calculate service metrics
        services_count = len(self.services)
        services_with_api = sum(1 for s in self.services.values() if s['api_count'] > 0)
        services_with_db = sum(1 for s in self.services.values() if s['db_count'] > 0)
        services_with_container = sum(1 for s in self.services.values() if s['container_config'])
        services_with_inter_service = sum(1 for s in self.services.values() if s['inter_service_count'] > 0)
        
        # Calculate average size of services (by component count)
        component_counts = [s['component_count'] for s in self.services.values()]
        avg_components_per_service = sum(component_counts) / len(component_counts) if component_counts else 0
        
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
        
        # Calculate coupling between services
        cross_service_edges = 0
        for source, target in self.component_graph.edges:
            source_service = self.component_graph.nodes[source].get('service', 'unknown')
            target_service = self.component_graph.nodes[target].get('service', 'unknown')
            
            if source_service != target_service and source_service != 'unknown' and target_service != 'unknown':
                cross_service_edges += 1
                
        # Calculate service autonomy (lower coupling is better)
        total_edges = self.component_graph.number_of_edges()
        service_autonomy = 1.0 - (cross_service_edges / total_edges if total_edges > 0 else 0)
                
        # Compile metrics
        metrics = {
            "service_count": services_count,
            "services_with_api_ratio": services_with_api / services_count if services_count > 0 else 0,
            "services_with_db_ratio": services_with_db / services_count if services_count > 0 else 0,
            "services_with_container_ratio": services_with_container / services_count if services_count > 0 else 0,
            "services_with_communication_ratio": services_with_inter_service / services_count if services_count > 0 else 0,
            "avg_components_per_service": avg_components_per_service,
            "service_autonomy": service_autonomy,
            "cross_service_dependencies": cross_service_edges,
            "separation_of_concerns_score": soc_score,
            "information_hiding_score": info_hiding_score,
            "dependency_inversion_score": dip_score,
        }
        
        # Calculate microservices architecture confidence score
        confidence = self._calculate_microservices_confidence(metrics)
        
        # Generate description
        description = self._generate_description(metrics, confidence)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, confidence)
        
        # Extract service details
        service_details = []
        for service_name, details in self.services.items():
            if service_name != 'unknown':
                service_details.append({
                    "name": service_name,
                    "component_count": details['component_count'],
                    "has_api": details['api_count'] > 0,
                    "api_count": details['api_count'],
                    "has_database": details['db_count'] > 0,
                    "database_count": details['db_count'],
                    "has_container_config": details['container_config'],
                    "has_service_communication": details['inter_service_count'] > 0,
                    "service_communication_count": details['inter_service_count'],
                })
        
        return {
            "type": self.name,
            "confidence": confidence,
            "services": service_details,
            "metrics": metrics,
            "recommendations": recommendations,
            "description": description
        }
    
    def _calculate_microservices_confidence(self, metrics: Dict) -> float:
        """Calculate confidence score for microservices architecture.
        
        Args:
            metrics: Architecture metrics
            
        Returns:
            Confidence score (0.0-1.0)
        """
        # Key indicators for microservices
        factors = [
            # Must have multiple services
            0.1 * min(1.0, metrics["service_count"] / 3),
            
            # Services should have APIs
            0.2 * metrics["services_with_api_ratio"],
            
            # Services should have own databases
            0.2 * metrics["services_with_db_ratio"],
            
            # Services should have container configurations
            0.1 * metrics["services_with_container_ratio"],
            
            # Services should communicate with each other
            0.1 * metrics["services_with_communication_ratio"],
            
            # Service autonomy (low coupling between services)
            0.2 * metrics["service_autonomy"],
            
            # Services should be small and focused
            0.1 * (1.0 - min(1.0, metrics["avg_components_per_service"] / 50))
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
        desc = f"The codebase shows {confidence_desc} evidence of Microservices Architecture. "
        
        # Add service details
        desc += f"Analysis identified {metrics['service_count']} distinct services. "
        
        # Add API details
        api_ratio = metrics["services_with_api_ratio"]
        if api_ratio > 0.8:
            desc += "Most services have clear API interfaces. "
        elif api_ratio > 0.5:
            desc += "Some services have API interfaces. "
        else:
            desc += "Few services have clear API interfaces. "
        
        # Add database details
        db_ratio = metrics["services_with_db_ratio"]
        if db_ratio > 0.8:
            desc += "Most services have their own data persistence. "
        elif db_ratio > 0.5:
            desc += "Some services have their own data persistence. "
        else:
            desc += "Few services have their own data persistence. "
        
        # Add containerization details
        container_ratio = metrics["services_with_container_ratio"]
        if container_ratio > 0.8:
            desc += "Services are well containerized. "
        elif container_ratio > 0.5:
            desc += "Some services have containerization. "
        else:
            desc += "Limited containerization was detected. "
        
        # Add coupling details
        autonomy = metrics["service_autonomy"]
        if autonomy > 0.8:
            desc += "Services show high autonomy with low coupling. "
        elif autonomy > 0.6:
            desc += "Services have moderate coupling. "
        else:
            desc += "Services show high coupling, which is contrary to microservice principles. "
        
        # Add overall assessment
        if confidence > 0.7:
            desc += "The codebase demonstrates a deliberate implementation of Microservices Architecture."
        elif confidence > 0.4:
            desc += "The codebase shows partial implementation of Microservices concepts but could be improved."
        else:
            desc += "The codebase shows only superficial resemblance to Microservices Architecture."
            
        return desc
    
    def _generate_recommendations(self, metrics: Dict, confidence: float) -> List[str]:
        """Generate recommendations for improving microservices architecture.
        
        Args:
            metrics: The metrics dictionary
            confidence: Confidence score
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Only generate recommendations if confidence is below excellent
        if confidence < 0.8:
            # Service boundaries
            if metrics["service_count"] < 3:
                recommendations.append(
                    "Consider breaking down the application into more distinct services with clearer boundaries"
                )
                
            # API recommendations
            if metrics["services_with_api_ratio"] < 0.7:
                recommendations.append(
                    "Ensure each service has a well-defined API interface for inter-service communication"
                )
                
            # Database recommendations
            if metrics["services_with_db_ratio"] < 0.7:
                recommendations.append(
                    "Consider using service-specific databases to improve service autonomy"
                )
                
            # Container recommendations
            if metrics["services_with_container_ratio"] < 0.7:
                recommendations.append(
                    "Implement containerization for services to enable independent deployment"
                )
                
            # Coupling recommendations
            if metrics["service_autonomy"] < 0.7:
                recommendations.append(
                    "Reduce coupling between services to improve autonomy and resilience"
                )
                
            # Service size recommendations
            if metrics["avg_components_per_service"] > 30:
                recommendations.append(
                    "Consider further decomposing larger services to maintain focus and manageability"
                )
        
        return recommendations