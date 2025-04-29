#!/usr/bin/env python3
"""
Architecture Evolution Simulator

This script simulates how software architecture evolves over time as requirements change,
technical debt accumulates, and refactoring occurs. It generates an interactive HTML
visualization showing the evolution stages.

Usage:
    python simulate_architecture_evolution.py --output ./evolution_simulation.html
"""

import os
import sys
import logging
import argparse
import shutil
from pathlib import Path
import time
import random
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

class ArchitectureState:
    """Represents a state of the architecture at a point in time."""
    
    def __init__(self, 
                 stage, 
                 year, 
                 architecture_type, 
                 name, 
                 components, 
                 dependencies,
                 complexity,
                 tech_debt,
                 maintainability,
                 scalability,
                 description):
        """Initialize the architecture state.
        
        Args:
            stage: Stage number in the evolution
            year: Year in the evolution timeline
            architecture_type: Type of architecture (layered, hexagonal, etc.)
            name: A descriptive name for this architecture state
            components: Number of components
            dependencies: Number of dependencies
            complexity: Complexity level (1-5)
            tech_debt: Technical debt level (1-5)
            maintainability: Maintainability level (1-5)
            scalability: Scalability level (1-5)
            description: Textual description of this architecture state
        """
        self.stage = stage
        self.year = year
        self.architecture_type = architecture_type
        self.name = name
        self.components = components
        self.dependencies = dependencies
        self.complexity = complexity
        self.tech_debt = tech_debt
        self.maintainability = maintainability
        self.scalability = scalability
        self.description = description
        self.changes = []
        self.decisions = []
        self.code_changes = []
        
    def add_change(self, change_type, description, impact):
        """Add a change from the previous stage.
        
        Args:
            change_type: Type of change (Added, Modified, Removed)
            description: Description of the change
            impact: Impact level of the change (Low, Medium, High)
        """
        self.changes.append({
            "type": change_type,
            "description": description,
            "impact": impact
        })
        
    def add_decision(self, decision_id, description, year):
        """Add an architectural decision.
        
        Args:
            decision_id: ID of the decision (e.g., ADR-001)
            description: Description of the decision
            year: Year the decision was made
        """
        self.decisions.append({
            "id": decision_id,
            "description": description,
            "year": year
        })
        
    def add_code_change(self, file_name, additions, deletions, example):
        """Add a code change example.
        
        Args:
            file_name: Name of the file that was changed
            additions: Number of lines added
            deletions: Number of lines deleted
            example: Example code showing the change
        """
        self.code_changes.append({
            "file_name": file_name,
            "additions": additions,
            "deletions": deletions,
            "example": example
        })
        
    def to_dict(self):
        """Convert to a dictionary for JSON serialization.
        
        Returns:
            Dictionary representation
        """
        return {
            "stage": self.stage,
            "year": self.year,
            "architecture_type": self.architecture_type,
            "name": self.name,
            "components": self.components,
            "dependencies": self.dependencies,
            "complexity": self.complexity,
            "tech_debt": self.tech_debt,
            "maintainability": self.maintainability,
            "scalability": self.scalability,
            "description": self.description,
            "changes": self.changes,
            "decisions": self.decisions,
            "code_changes": self.code_changes,
            "complexity_label": self._get_level_label(self.complexity),
            "tech_debt_label": self._get_level_label(self.tech_debt),
            "maintainability_label": self._get_level_label(self.maintainability),
            "scalability_label": self._get_level_label(self.scalability)
        }
        
    @staticmethod
    def _get_level_label(level):
        """Convert a numeric level to a label.
        
        Args:
            level: Numeric level (1-5)
            
        Returns:
            Textual label
        """
        labels = {
            1: "Very Low",
            2: "Low",
            3: "Medium",
            4: "High",
            5: "Very High"
        }
        return labels.get(level, "Unknown")


class EvolutionSimulator:
    """Simulates the evolution of software architecture over time."""
    
    def __init__(self, 
                 project_size=3, 
                 initial_architecture="layered",
                 team_experience=3,
                 requirement_change_rate=3,
                 tech_debt_tolerance=3,
                 refactoring_frequency=3,
                 events=None):
        """Initialize the simulator with parameters.
        
        Args:
            project_size: Size of the project (1-5)
            initial_architecture: Initial architecture type
            team_experience: Team experience level (1-5)
            requirement_change_rate: Rate of requirement changes (1-5)
            tech_debt_tolerance: Tolerance for technical debt (1-5)
            refactoring_frequency: Frequency of refactoring (1-5)
            events: List of special events to include in the simulation
        """
        self.project_size = project_size
        self.initial_architecture = initial_architecture
        self.team_experience = team_experience
        self.requirement_change_rate = requirement_change_rate
        self.tech_debt_tolerance = tech_debt_tolerance
        self.refactoring_frequency = refactoring_frequency
        self.events = events or []
        
        # Initialize states list
        self.states = []
        
    def simulate(self, years=5):
        """Run the simulation for a specified number of years.
        
        Args:
            years: Number of years to simulate
            
        Returns:
            List of architecture states
        """
        # Create initial state
        initial_state = self._create_initial_state()
        self.states.append(initial_state)
        
        # Simulate evolution
        for year in range(1, years + 1):
            logger.info(f"Simulating year {year}...")
            
            # Get previous state
            prev_state = self.states[-1]
            
            # Create next state based on evolution factors
            next_state = self._evolve_architecture(prev_state, year)
            
            # Apply special events if any are scheduled for this year
            for event in self.events:
                if event["year"] == year:
                    next_state = self._apply_event(next_state, event)
            
            # Add to states
            self.states.append(next_state)
            
        return self.states
    
    def _create_initial_state(self):
        """Create the initial architecture state.
        
        Returns:
            Initial architecture state
        """
        # Map initial architecture type to parameters
        architecture_params = {
            "monolith": {
                "name": "Monolithic Architecture",
                "components": 5 * self.project_size,
                "dependencies": 8 * self.project_size,
                "complexity": 2,
                "tech_debt": 1,
                "maintainability": 4 if self.project_size <= 3 else 3,
                "scalability": 2,
                "description": "A simple monolithic architecture with all components in a single application. "
                            "This approach works well for the initial stages of the project but may face "
                            "scalability challenges as the system grows."
            },
            "layered": {
                "name": "Layered Architecture",
                "components": 6 * self.project_size,
                "dependencies": 10 * self.project_size,
                "complexity": 2,
                "tech_debt": 1,
                "maintainability": 4,
                "scalability": 3,
                "description": "A classic three-tier layered architecture with clear separation between "
                            "presentation, business logic, and data access concerns. Dependencies flow "
                            "downward, and each layer has a well-defined responsibility."
            },
            "hexagonal": {
                "name": "Hexagonal Architecture",
                "components": 8 * self.project_size,
                "dependencies": 12 * self.project_size,
                "complexity": 3,
                "tech_debt": 1,
                "maintainability": 4,
                "scalability": 4,
                "description": "A hexagonal (ports and adapters) architecture that isolates the core domain "
                            "from external concerns. The domain defines interfaces (ports) that adapters implement, "
                            "creating a clear separation between business logic and technical concerns."
            },
            "clean": {
                "name": "Clean Architecture",
                "components": 10 * self.project_size,
                "dependencies": 15 * self.project_size,
                "complexity": 4,
                "tech_debt": 1,
                "maintainability": 5,
                "scalability": 4,
                "description": "A clean architecture with entities at the core, surrounded by use cases, interface "
                            "adapters, and frameworks. Dependencies point inward toward the core, ensuring that "
                            "business rules are isolated from external concerns."
            },
            "microservices": {
                "name": "Microservices Architecture",
                "components": 12 * self.project_size,
                "dependencies": 18 * self.project_size,
                "complexity": 5,
                "tech_debt": 2,
                "maintainability": 4,
                "scalability": 5,
                "description": "A microservices architecture with independent services communicating via APIs. "
                            "Each service has its own data storage and can be developed, deployed, and scaled "
                            "independently. This approach offers high scalability but adds operational complexity."
            }
        }
        
        # Get parameters for the selected architecture
        params = architecture_params.get(self.initial_architecture, architecture_params["layered"])
        
        # Create initial state
        initial_state = ArchitectureState(
            stage=0,
            year=0,
            architecture_type=self.initial_architecture,
            name=params["name"],
            components=params["components"],
            dependencies=params["dependencies"],
            complexity=params["complexity"],
            tech_debt=params["tech_debt"],
            maintainability=params["maintainability"],
            scalability=params["scalability"],
            description=params["description"]
        )
        
        # Add initial architectural decision
        initial_state.add_decision(
            "ADR-001",
            f"Initial selection of {self.initial_architecture} architecture pattern",
            0
        )
        
        return initial_state
    
    def _evolve_architecture(self, prev_state, year):
        """Evolve the architecture based on evolution factors.
        
        Args:
            prev_state: Previous architecture state
            year: Current year
            
        Returns:
            New architecture state
        """
        # Start with previous values
        components = prev_state.components
        dependencies = prev_state.dependencies
        complexity = prev_state.complexity
        tech_debt = prev_state.tech_debt
        maintainability = prev_state.maintainability
        scalability = prev_state.scalability
        
        # Factor for random variation (0.8 to 1.2)
        rand_factor = lambda: random.uniform(0.8, 1.2)
        
        # Add components based on requirement change rate
        new_components = int(self.requirement_change_rate * rand_factor())
        components += new_components
        
        # Add dependencies
        new_dependencies = int(new_components * 1.5 * rand_factor())
        dependencies += new_dependencies
        
        # Increase complexity based on growth and team experience
        complexity_change = (new_components / 10) * (6 - self.team_experience) / 5
        complexity = min(5, complexity + complexity_change)
        
        # Increase technical debt based on tolerance and change rate
        debt_change = (self.tech_debt_tolerance / 5) * (self.requirement_change_rate / 3) * rand_factor()
        tech_debt = min(5, tech_debt + debt_change)
        
        # Apply refactoring effects
        if random.random() < (self.refactoring_frequency / 10):
            # Refactoring reduces tech debt and complexity but may temporarily decrease maintainability
            tech_debt = max(1, tech_debt - random.uniform(0.5, 1.5))
            complexity = max(1, complexity - random.uniform(0.2, 0.8))
            maintainability = max(1, maintainability - 0.5)  # Temporary decrease
        else:
            # Without refactoring, maintainability decreases with complexity and tech debt
            maintainability = max(1, maintainability - (complexity_change + debt_change) / 4)
        
        # Update scalability based on architecture and growth
        if prev_state.architecture_type in ["microservices", "hexagonal", "clean"]:
            # These architectures scale better
            scalability = min(5, scalability + 0.1)
        else:
            # Traditional architectures may struggle with growth
            scalability = max(1, scalability - 0.2 * (self.project_size / 3))
        
        # Determine if architecture type changes
        architecture_type = prev_state.architecture_type
        architecture_name = prev_state.name
        
        # Potential architecture evolution paths
        evolution_paths = {
            "monolith": {
                "next": "layered",
                "threshold": 4,  # Complexity threshold to evolve
                "name": "Structured Monolith"
            },
            "layered": {
                "next": "hexagonal",
                "threshold": 4,
                "name": "Enhanced Layered Architecture"
            },
            "hexagonal": {
                "next": "clean",
                "threshold": 4.5,
                "name": "Advanced Hexagonal Architecture"
            },
            "clean": {
                "next": "microservices",
                "threshold": 4.5,
                "name": "Modular Clean Architecture"
            }
        }
        
        # Check if should evolve architecture
        if (architecture_type in evolution_paths and 
            complexity > evolution_paths[architecture_type]["threshold"] and
            random.random() < 0.3):
            
            # Transition to next architecture type
            new_type = evolution_paths[architecture_type]["next"]
            
            # Create transition name
            architecture_name = f"Transitioning to {new_type.title()} Architecture"
            
            # After year 3, actually change the architecture type
            if year > 3:
                architecture_type = new_type
        else:
            # If not changing type, use evolved name
            if architecture_type in evolution_paths:
                architecture_name = evolution_paths[architecture_type]["name"]
        
        # Create description based on current state
        if tech_debt > 4:
            description = (
                f"The architecture shows signs of significant technical debt accumulation. "
                f"The {architecture_type} structure is still present, but code quality issues "
                f"and architectural violations are increasing. Refactoring is recommended to "
                f"avoid further deterioration."
            )
        elif complexity > 4:
            description = (
                f"The system has grown substantially in complexity. While the {architecture_type} "
                f"architecture is maintained, the increasing number of components and dependencies "
                f"is making the system harder to understand and maintain. Consider splitting into "
                f"more manageable subsystems."
            )
        else:
            description = (
                f"The architecture continues to evolve as a {architecture_type} design. "
                f"New components have been added to handle growing requirements, and the "
                f"overall structure remains coherent. Technical debt is being managed, "
                f"and the system remains maintainable and scalable."
            )
        
        # Create new state
        new_state = ArchitectureState(
            stage=year,
            year=year,
            architecture_type=architecture_type,
            name=architecture_name,
            components=int(components),
            dependencies=int(dependencies),
            complexity=round(complexity, 1),
            tech_debt=round(tech_debt, 1),
            maintainability=round(maintainability, 1),
            scalability=round(scalability, 1),
            description=description
        )
        
        # Add changes from previous state
        self._add_changes(prev_state, new_state)
        
        # Add architectural decisions
        self._add_decisions(new_state, year)
        
        # Add code changes
        self._add_code_changes(new_state, year)
        
        return new_state
    
    def _apply_event(self, state, event):
        """Apply a special event to the architecture state.
        
        Args:
            state: Current architecture state
            event: Event to apply
            
        Returns:
            Modified architecture state
        """
        event_type = event["type"]
        
        if event_type == "scaling":
            # Rapid user growth event
            state.scalability = max(1, state.scalability - 1)
            state.complexity += 0.5
            state.tech_debt += 0.5
            state.description = (
                "The system experienced rapid user growth, putting significant pressure on "
                "the architecture. Performance bottlenecks emerged, and quick fixes were "
                "implemented to handle the load, increasing technical debt."
            )
            state.add_change(
                "Modified",
                "Emergency scaling improvements to handle increased load",
                "High"
            )
            
        elif event_type == "security":
            # Security incident
            state.tech_debt += 1
            state.add_change(
                "Added",
                "Enhanced security controls following security incident",
                "High"
            )
            state.add_decision(
                f"ADR-{10 + state.year}",
                "Implementation of comprehensive security review and remediation process",
                state.year
            )
            
        elif event_type == "acquisition":
            # Company acquisition
            state.complexity += 1
            state.dependencies += int(state.dependencies * 0.3)
            state.components += int(state.components * 0.2)
            state.description = (
                "Following a company acquisition, the architecture needed to integrate with "
                "existing systems from the parent company. This introduced new dependencies "
                "and increased overall complexity."
            )
            
        elif event_type == "pivot":
            # Business pivot
            state.tech_debt += 1.5
            state.complexity += 1
            state.components = int(state.components * 0.7)  # Some components removed
            state.dependencies = int(state.dependencies * 0.6)  # Dependencies removed
            state.add_change(
                "Removed",
                "Removed several components no longer needed after business pivot",
                "High"
            )
            state.add_change(
                "Added",
                "Added new core components to support new business direction",
                "High"
            )
            state.description = (
                "A significant business pivot required rapid changes to the architecture. "
                "Many components were repurposed or replaced, leading to increased technical "
                "debt and architectural inconsistencies."
            )
        
        return state
    
    def _add_changes(self, prev_state, new_state):
        """Add changes from previous state to new state.
        
        Args:
            prev_state: Previous architecture state
            new_state: New architecture state
        """
        # Add component changes
        component_diff = new_state.components - prev_state.components
        if component_diff > 0:
            new_state.add_change(
                "Added",
                f"Added {component_diff} new components to support growing requirements",
                "Medium" if component_diff > 5 else "Low"
            )
        elif component_diff < 0:
            new_state.add_change(
                "Removed",
                f"Removed {abs(component_diff)} obsolete components",
                "Medium" if abs(component_diff) > 5 else "Low"
            )
        
        # Add refactoring if tech debt decreased
        if new_state.tech_debt < prev_state.tech_debt:
            new_state.add_change(
                "Modified",
                "Refactored components to reduce technical debt",
                "Medium"
            )
        
        # Add architecture changes
        if new_state.architecture_type != prev_state.architecture_type:
            new_state.add_change(
                "Modified",
                f"Began transition from {prev_state.architecture_type} to {new_state.architecture_type} architecture",
                "High"
            )
            
    def _add_decisions(self, state, year):
        """Add architectural decisions to the state.
        
        Args:
            state: Architecture state
            year: Current year
        """
        # Add decisions based on the current state and year
        
        # Decision for refactoring
        if state.tech_debt < 3 and random.random() < 0.7:
            state.add_decision(
                f"ADR-{year+1}",
                "Implementation of regular refactoring process to manage technical debt",
                year
            )
        
        # Decision for architecture evolution
        if state.architecture_type != self.initial_architecture:
            state.add_decision(
                f"ADR-{year+2}",
                f"Transition to {state.architecture_type} architecture to address scalability and maintainability concerns",
                year
            )
            
        # Add technology-specific decisions
        tech_decisions = [
            "Adoption of containerization for deployment",
            "Migration to cloud infrastructure",
            "Implementation of CI/CD pipeline",
            "Adoption of automated testing framework",
            "Implementation of monitoring and observability solution"
        ]
        
        if random.random() < 0.3:
            decision_idx = year % len(tech_decisions)
            state.add_decision(
                f"ADR-{year+3}",
                tech_decisions[decision_idx],
                year
            )
            
    def _add_code_changes(self, state, year):
        """Add code change examples to the state.
        
        Args:
            state: Architecture state
            year: Current year
        """
        # Template code changes based on architecture type
        code_changes = {
            "monolith": {
                "file_name": "Application.java",
                "example": """- public class Application {
-     private Database db;
-     private UserInterface ui;
-     
-     public void processRequest(Request req) {
-         // Doing everything in one method
-         ...
-     }
- }
+ public class Application {
+     private Database db;
+     private UserInterface ui;
+     private RequestProcessor processor;
+     
+     public void processRequest(Request req) {
+         // Delegating to specialized processor
+         processor.process(req);
+     }
+ }
+ 
+ class RequestProcessor {
+     public void process(Request req) {
+         // Processing logic moved here
+         ...
+     }
+ }"""
            },
            "layered": {
                "file_name": "UserService.java",
                "example": """- public class UserService {
-     private Connection dbConnection;
-     
-     public User getUserById(long id) {
-         // Direct database access from service
-         String sql = "SELECT * FROM users WHERE id = " + id;
-         ...
-     }
- }
+ public class UserService {
+     private UserRepository userRepository;
+     
+     public User getUserById(long id) {
+         // Using repository pattern
+         return userRepository.findById(id);
+     }
+ }
+ 
+ public interface UserRepository {
+     User findById(long id);
+ }
+ 
+ public class JdbcUserRepository implements UserRepository {
+     private Connection dbConnection;
+     
+     public User findById(long id) {
+         // Database access moved to repository
+         ...
+     }
+ }"""
            },
            "hexagonal": {
                "file_name": "UserService.java",
                "example": """- public class UserService {
-     private UserRepository userRepository;
-     
-     public User getUserById(long id) {
-         return userRepository.findById(id);
-     }
- }
+ public interface UserService {
+     User getUserById(long id);
+ }
+ 
+ public class UserServiceImpl implements UserService {
+     private UserPort userPort;
+     
+     public User getUserById(long id) {
+         return userPort.findById(id);
+     }
+ }
+ 
+ public interface UserPort {
+     User findById(long id);
+ }
+ 
+ public class UserJdbcAdapter implements UserPort {
+     private Connection dbConnection;
+     
+     public User findById(long id) {
+         // Implementation details
+         ...
+     }
+ }"""
            },
            "clean": {
                "file_name": "GetUserUseCase.java",
                "example": """- public class UserController {
-     private UserService userService;
-     
-     public UserResponse getUser(long id) {
-         User user = userService.getUserById(id);
-         return new UserResponse(user);
-     }
- }
+ public class GetUserUseCase {
+     private UserRepository userRepository;
+     
+     public GetUserResponse execute(GetUserRequest request) {
+         // Domain logic in use case
+         User user = userRepository.findById(request.getUserId());
+         
+         if (user == null) {
+             throw new UserNotFoundException(request.getUserId());
+         }
+         
+         return new GetUserResponse(user);
+     }
+ }
+ 
+ public class UserController {
+     private GetUserUseCase getUserUseCase;
+     
+     public UserResponse getUser(long id) {
+         GetUserRequest request = new GetUserRequest(id);
+         GetUserResponse response = getUserUseCase.execute(request);
+         return new UserResponse(response);
+     }
+ }"""
            },
            "microservices": {
                "file_name": "UserService.java",
                "example": """- public class UserController {
-     private UserRepository userRepository;
-     private OrderRepository orderRepository;
-     
-     public UserWithOrdersResponse getUserWithOrders(long id) {
-         User user = userRepository.findById(id);
-         List<Order> orders = orderRepository.findByUserId(id);
-         return new UserWithOrdersResponse(user, orders);
-     }
- }
+ public class UserController {
+     private UserRepository userRepository;
+     private OrderServiceClient orderServiceClient;
+     
+     public UserWithOrdersResponse getUserWithOrders(long id) {
+         User user = userRepository.findById(id);
+         
+         // Remote call to Order microservice
+         List<Order> orders = orderServiceClient.getOrdersForUser(id);
+         
+         return new UserWithOrdersResponse(user, orders);
+     }
+ }
+ 
+ public class OrderServiceClient {
+     private WebClient webClient;
+     
+     public List<Order> getOrdersForUser(long userId) {
+         // HTTP call to Order service
+         return webClient.get()
+                 .uri("/orders?userId=" + userId)
+                 .retrieve()
+                 .bodyToFlux(Order.class)
+                 .collectList()
+                 .block();
+     }
+ }"""
            }
        }
        
        # Get code change for the current architecture
        architecture_type = state.architecture_type
        if architecture_type in code_changes:
            change = code_changes[architecture_type]
            
            # Count additions and deletions
            additions = change["example"].count('\n+') - 1
            deletions = change["example"].count('\n-') - 1
            
            state.add_code_change(
                change["file_name"],
                additions,
                deletions,
                change["example"]
            )
    
    def generate_html(self, output_path):
        """Generate an HTML visualization of the architecture evolution.
        
        Args:
            output_path: Path to save the HTML file
            
        Returns:
            Path to the generated HTML file
        """
        if not self.states:
            logger.warning("No simulation states to visualize. Run simulate() first.")
            return None
            
        # Get template path
        template_path = Path(__file__).parent / "src" / "templates" / "architecture_evolution.html"
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get states data as JSON
        states_json = json.dumps([state.to_dict() for state in self.states])
        
        # Load template
        with open(template_path, 'r') as f:
            template = f.read()
            
        # Replace placeholder with actual data
        template = template.replace(
            '// Timeline stages will be generated here',
            f'// Timeline stages data\nconst simulationData = {states_json};\n\n// Render timeline stages\nrenderTimeline(simulationData);'
        )
        
        # Add function to render timeline
        render_function = """
function renderTimeline(data) {
    const timelineContainer = document.getElementById('timeline');
    timelineContainer.innerHTML = '';
    
    data.forEach((state, index) => {
        const stage = document.createElement('div');
        stage.className = 'timeline-stage';
        if (index === 0) stage.classList.add('active');
        
        stage.innerHTML = `
            <div class="stage-header">Year ${state.year}</div>
            <div class="stage-image">
                <div>Stage ${state.stage}</div>
            </div>
            <div class="stage-details">
                <div class="stage-name">${state.name}</div>
                <div class="stage-metrics">
                    <div>Complexity: ${state.complexity_label}</div>
                    <div>Tech Debt: ${state.tech_debt_label}</div>
                </div>
            </div>
        `;
        
        // Add click handler in JavaScript
        stage.addEventListener('click', function() {
            // Update active stage
            document.querySelectorAll('.timeline-stage').forEach(s => s.classList.remove('active'));
            this.classList.add('active');
            
            // Update visualization
            updateVisualization(state);
        });
        
        timelineContainer.appendChild(stage);
    });
}

function updateVisualization(state) {
    // Update visualization title
    document.querySelector('.visualization-title').textContent = `${state.name} (Year ${state.year})`;
    
    // Update metrics
    const metricsHtml = `
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">Components</div>
                <div class="metric-value">${state.components}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Dependencies</div>
                <div class="metric-value">${state.dependencies}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Complexity</div>
                <div class="metric-value">${state.complexity_label}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Technical Debt</div>
                <div class="metric-value">${state.tech_debt_label}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Maintainability</div>
                <div class="metric-value">${state.maintainability_label}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Scalability</div>
                <div class="metric-value">${state.scalability_label}</div>
            </div>
        </div>
        
        <h3 style="margin-top: 30px;">Architecture Description</h3>
        <p>${state.description}</p>
    `;
    
    // Update right panel
    const rightPanel = document.querySelector('.right-panel');
    rightPanel.innerHTML = `<h3>Architecture Metrics</h3>${metricsHtml}`;
    
    // Update changes
    if (state.changes.length > 0) {
        const changesHtml = state.changes.map(change => `
            <div class="change-item">
                <div class="change-type">${change.type}</div>
                <div class="change-description">${change.description}</div>
                <div class="change-impact impact-${change.impact.toLowerCase()}">${change.impact} Impact</div>
            </div>
        `).join('');
        
        document.querySelector('.changes-list').innerHTML = changesHtml;
    }
    
    // Update decisions
    if (state.decisions.length > 0) {
        const decisionsHtml = state.decisions.map(decision => `
            <div class="change-item">
                <div class="change-type">${decision.id}</div>
                <div class="change-description">${decision.description}</div>
                <div class="change-impact">Year ${decision.year}</div>
            </div>
        `).join('');
        
        document.querySelectorAll('.changes-list')[1].innerHTML = decisionsHtml;
    }
    
    // Update code changes
    if (state.code_changes.length > 0) {
        const codeChange = state.code_changes[0]; // Just use the first one
        
        const codeHtml = `
            <div class="code-diff">
                <div class="diff-header">
                    <span>${codeChange.file_name}</span>
                    <span>+${codeChange.additions} -${codeChange.deletions}</span>
                </div>
                <div class="diff-content">
                    ${codeChange.example.split('\\n').map(line => {
                        let className = 'diff-line';
                        if (line.startsWith('+')) className += ' diff-added';
                        else if (line.startsWith('-')) className += ' diff-removed';
                        return `<div class="${className}">${line}</div>`;
                    }).join('')}
                </div>
            </div>
        `;
        
        const codeContainer = document.querySelector('.detail-section:last-child .code-diff');
        if (codeContainer) {
            codeContainer.outerHTML = codeHtml;
        }
    }
    
    // Update architecture diagram
    updateArchitectureDiagram(state);
}

function updateArchitectureDiagram(state) {
    // Different diagram for each architecture type
    const diagrams = {
        'monolith': `
            <svg width="100%" height="100%" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
                <rect x="200" y="100" width="400" height="200" fill="#e1e1e1" stroke="#333" stroke-width="2" />
                <text x="400" y="180" text-anchor="middle" font-size="24">Monolithic</text>
                <text x="400" y="210" text-anchor="middle" font-size="24">Application</text>
                
                <rect x="300" y="320" width="200" height="50" fill="#f7e5d1" stroke="#f39c12" stroke-width="2" />
                <text x="400" y="350" text-anchor="middle" font-size="16">Database</text>
                
                <path d="M400,300 L400,320" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)" />
                
                <defs>
                    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
                    </marker>
                </defs>
            </svg>
        `,
        'layered': `
            <svg width="100%" height="100%" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
                <rect x="50" y="50" width="700" height="80" fill="#d1e7f7" stroke="#3498db" stroke-width="2" />
                <text x="400" y="90" text-anchor="middle" font-size="16">Presentation Layer</text>
                
                <rect x="50" y="160" width="700" height="80" fill="#d1f7e3" stroke="#2ecc71" stroke-width="2" />
                <text x="400" y="200" text-anchor="middle" font-size="16">Business Logic Layer</text>
                
                <rect x="50" y="270" width="700" height="80" fill="#f7e5d1" stroke="#f39c12" stroke-width="2" />
                <text x="400" y="310" text-anchor="middle" font-size="16">Data Access Layer</text>
                
                <path d="M400,130 L400,160" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)" />
                <path d="M400,240 L400,270" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)" />
            </svg>
        `,
        'hexagonal': `
            <svg width="100%" height="100%" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
                <!-- Core Domain Hexagon -->
                <polygon points="400,80 550,150 550,250 400,320 250,250 250,150" 
                         fill="#d1f7e3" stroke="#2ecc71" stroke-width="2" />
                <text x="400" y="200" text-anchor="middle" font-size="16">Core Domain</text>
                
                <!-- Ports -->
                <circle cx="250" cy="160" r="20" fill="#d1e7f7" stroke="#3498db" stroke-width="2" />
                <circle cx="250" cy="240" r="20" fill="#d1e7f7" stroke="#3498db" stroke-width="2" />
                <circle cx="550" cy="160" r="20" fill="#f7e5d1" stroke="#f39c12" stroke-width="2" />
                <circle cx="550" cy="240" r="20" fill="#f7e5d1" stroke="#f39c12" stroke-width="2" />
                
                <!-- Adapters -->
                <rect x="50" y="140" width="100" height="40" fill="#d1e7f7" stroke="#3498db" stroke-width="2" />
                <text x="100" y="165" text-anchor="middle" font-size="14">UI Adapter</text>
                
                <rect x="50" y="220" width="100" height="40" fill="#d1e7f7" stroke="#3498db" stroke-width="2" />
                <text x="100" y="245" text-anchor="middle" font-size="14">API Adapter</text>
                
                <rect x="650" y="140" width="100" height="40" fill="#f7e5d1" stroke="#f39c12" stroke-width="2" />
                <text x="700" y="165" text-anchor="middle" font-size="14">DB Adapter</text>
                
                <rect x="650" y="220" width="100" height="40" fill="#f7e5d1" stroke="#f39c12" stroke-width="2" />
                <text x="700" y="245" text-anchor="middle" font-size="14">Cache Adapter</text>
                
                <!-- Connections -->
                <path d="M150,160 L230,160" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)" />
                <path d="M150,240 L230,240" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)" />
                <path d="M570,160 L650,160" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)" />
                <path d="M570,240 L650,240" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)" />
            </svg>
        `,
        'clean': `
            <svg width="100%" height="100%" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
                <!-- Entities Circle -->
                <circle cx="400" cy="200" r="60" fill="#f7d1e3" stroke="#9b59b6" stroke-width="2" />
                <text x="400" y="200" text-anchor="middle" font-size="16">Entities</text>
                
                <!-- Use Cases Circle -->
                <circle cx="400" cy="200" r="120" fill="none" stroke="#3498db" stroke-width="2" />
                <text x="400" y="100" text-anchor="middle" font-size="16">Use Cases</text>
                
                <!-- Interface Adapters Circle -->
                <circle cx="400" cy="200" r="180" fill="none" stroke="#2ecc71" stroke-width="2" />
                <text x="400" y="40" text-anchor="middle" font-size="16">Interface Adapters</text>
                
                <!-- Frameworks Circle -->
                <circle cx="400" cy="200" r="240" fill="none" stroke="#f39c12" stroke-width="2" />
                <text x="400" y="380" text-anchor="middle" font-size="16">Frameworks & Drivers</text>
                
                <!-- Dependency Direction -->
                <defs>
                    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
                    </marker>
                </defs>
                <path d="M280,200 L340,200" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)" />
                <text x="310" y="190" text-anchor="middle" font-size="12">Dependencies</text>
            </svg>
        `,
        'microservices': `
            <svg width="100%" height="100%" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
                <!-- Microservices -->
                <rect x="100" y="60" width="150" height="80" rx="10" ry="10" fill="#d1e7f7" stroke="#3498db" stroke-width="2" />
                <text x="175" y="100" text-anchor="middle" font-size="16">User Service</text>
                
                <rect x="550" y="60" width="150" height="80" rx="10" ry="10" fill="#d1e7f7" stroke="#3498db" stroke-width="2" />
                <text x="625" y="100" text-anchor="middle" font-size="16">Order Service</text>
                
                <rect x="100" y="260" width="150" height="80" rx="10" ry="10" fill="#d1e7f7" stroke="#3498db" stroke-width="2" />
                <text x="175" y="300" text-anchor="middle" font-size="16">Product Service</text>
                
                <rect x="550" y="260" width="150" height="80" rx="10" ry="10" fill="#d1e7f7" stroke="#3498db" stroke-width="2" />
                <text x="625" y="300" text-anchor="middle" font-size="16">Payment Service</text>
                
                <!-- API Gateway -->
                <rect x="325" y="160" width="150" height="80" rx="10" ry="10" fill="#d1f7e3" stroke="#2ecc71" stroke-width="2" />
                <text x="400" y="200" text-anchor="middle" font-size="16">API Gateway</text>
                
                <!-- Connections -->
                <path d="M175,140 L325,180" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)" />
                <path d="M625,140 L475,180" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)" />
                <path d="M175,260 L325,220" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)" />
                <path d="M625,260 L475,220" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)" />
                
                <!-- Databases -->
                <circle cx="175" y="180" r="15" fill="#f7e5d1" stroke="#f39c12" stroke-width="2" />
                <circle cx="625" y="180" r="15" fill="#f7e5d1" stroke="#f39c12" stroke-width="2" />
                <circle cx="175" y="380" r="15" fill="#f7e5d1" stroke="#f39c12" stroke-width="2" />
                <circle cx="625" y="380" r="15" fill="#f7e5d1" stroke="#f39c12" stroke-width="2" />
                
                <path d="M175,140 L175,165" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)" />
                <path d="M625,140 L625,165" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)" />
                <path d="M175,340 L175,365" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)" />
                <path d="M625,340 L625,365" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)" />
            </svg>
        `
    };
    
    // Get the visualization container
    const container = document.getElementById('architecture-visualization');
    
    // Update with the appropriate diagram
    container.innerHTML = diagrams[state.architecture_type] || diagrams['layered'];
}

// Initialize the first stage
document.addEventListener('DOMContentLoaded', function() {
    if (simulationData && simulationData.length > 0) {
        updateVisualization(simulationData[0]);
    }
});
"""
        
        # Add render function to template
        template = template.replace('// Simulation button', render_function + '\n\n// Simulation button')
        
        # Write HTML file
        with open(output_path, 'w') as f:
            f.write(template)
            
        logger.info(f"Generated HTML visualization at {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Simulate the evolution of software architecture over time"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="./output/architecture_evolution.html",
        help="Path to save the evolution HTML file"
    )
    
    parser.add_argument(
        "--years", "-y",
        type=int,
        default=5,
        help="Number of years to simulate"
    )
    
    parser.add_argument(
        "--project-size",
        type=int,
        choices=range(1, 6),
        default=3,
        help="Project size (1=Very Small, 5=Very Large)"
    )
    
    parser.add_argument(
        "--initial-architecture",
        choices=["monolith", "layered", "hexagonal", "clean", "microservices"],
        default="layered",
        help="Initial architecture type"
    )
    
    parser.add_argument(
        "--team-experience",
        type=int,
        choices=range(1, 6),
        default=3,
        help="Team experience level (1=Beginner, 5=Expert)"
    )
    
    parser.add_argument(
        "--requirement-change-rate",
        type=int,
        choices=range(1, 6),
        default=3,
        help="Rate of requirement changes (1=Very Low, 5=Very High)"
    )
    
    parser.add_argument(
        "--tech-debt-tolerance",
        type=int,
        choices=range(1, 6),
        default=3,
        help="Tolerance for technical debt (1=Very Low, 5=Very High)"
    )
    
    parser.add_argument(
        "--refactoring-frequency",
        type=int,
        choices=range(1, 6),
        default=3,
        help="Frequency of refactoring (1=Very Low, 5=Very High)"
    )
    
    parser.add_argument(
        "--event-scaling",
        action="store_true",
        help="Include rapid user growth event in year 2"
    )
    
    parser.add_argument(
        "--event-security",
        action="store_true",
        help="Include security incident event in year 3"
    )
    
    parser.add_argument(
        "--event-acquisition",
        action="store_true",
        help="Include company acquisition event in year 4"
    )
    
    parser.add_argument(
        "--event-pivot",
        action="store_true",
        help="Include business pivot event in year 2"
    )
    
    args = parser.parse_args()
    
    try:
        # Prepare events list
        events = []
        if args.event_scaling:
            events.append({"type": "scaling", "year": 2})
        if args.event_security:
            events.append({"type": "security", "year": 3})
        if args.event_acquisition:
            events.append({"type": "acquisition", "year": 4})
        if args.event_pivot:
            events.append({"type": "pivot", "year": 2})
        
        # Create simulator
        simulator = EvolutionSimulator(
            project_size=args.project_size,
            initial_architecture=args.initial_architecture,
            team_experience=args.team_experience,
            requirement_change_rate=args.requirement_change_rate,
            tech_debt_tolerance=args.tech_debt_tolerance,
            refactoring_frequency=args.refactoring_frequency,
            events=events
        )
        
        # Run simulation
        logger.info(f"Starting architecture evolution simulation for {args.years} years...")
        states = simulator.simulate(args.years)
        logger.info(f"Simulation completed with {len(states)} states")
        
        # Generate HTML visualization
        output_path = Path(args.output)
        html_path = simulator.generate_html(output_path)
        
        if html_path:
            print(f"\nSimulation completed successfully!")
            print(f"HTML visualization generated at: {html_path}")
            print("Open this file in a browser to explore the architecture evolution.")
            
    except Exception as e:
        logger.error(f"Error during simulation: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())