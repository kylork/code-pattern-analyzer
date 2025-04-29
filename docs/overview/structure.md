# Code Pattern Analyzer - Project Structure

This document provides a structured overview of the core components of the Code Pattern Analyzer project.

## Core Architecture

```
src/
├── __init__.py              # Package initialization
├── __main__.py              # Entry point for running as a module
├── analyzer.py              # Main analyzer class for code analysis
├── parser.py                # Code parser interface
├── pattern_base.py          # Base classes for patterns
├── pattern_recognizer.py    # Pattern recognition engine
├── pattern_registry.py      # Registry of available patterns
├── tree_sitter_impl.py      # Tree-sitter implementation
├── tree_sitter_manager.py   # Manager for tree-sitter grammars
├── mock_implementation.py   # Mock implementation for demo purposes
├── utils.py                 # Utility functions
└── visualization.py         # Visualization components
```

## Pattern Definitions

```
src/patterns/
├── __init__.py                      # Package initialization
├── class_patterns.py                # Class-related patterns
├── code_smells.py                   # Code smell patterns
├── design_patterns.py               # Design pattern detection
├── function_patterns.py             # Function-related patterns
├── python_patterns.py               # Python-specific patterns
├── nexus.md                         # Nexus architectural philosophy
├── architectural_intents/           # Architectural intent patterns
│   ├── __init__.py                  # Package initialization
│   ├── architectural_intent_base.py # Base class for intents
│   ├── architectural_intent_detector.py # Intent detector
│   ├── dependency_inversion.py      # Dependency inversion principle
│   ├── information_hiding.py        # Information hiding principle
│   └── separation_of_concerns.py    # Separation of concerns principle
├── architectural_styles/            # Architectural style patterns
│   ├── __init__.py                  # Package initialization
│   ├── architectural_style_base.py  # Base class for styles
│   ├── architectural_style_detector.py # Style detector
│   ├── clean_architecture.py        # Clean architecture detection
│   ├── event_driven.py              # Event-driven architecture
│   ├── hexagonal.py                 # Hexagonal architecture
│   ├── layered.py                   # Layered architecture
│   └── microservices.py             # Microservices architecture
└── enhanced/                        # Enhanced pattern detectors
    └── strategy_pattern_enhanced.py # Enhanced strategy detection
```

## Command-Line Interface

```
src/cli/
├── __init__.py                      # Package initialization
├── main.py                          # Main CLI entry point
├── parser.py                        # CLI argument parser
└── subcommands.py                   # Subcommand implementations

src/commands/
├── __init__.py                      # Package initialization
├── architecture.py                  # Architecture analysis command
├── compare.py                       # File comparison command
└── report.py                        # Report generation command
```

## Visualization Components

```
src/visualization/
├── __init__.py                      # Package initialization
└── architecture_visualizer.py       # Architecture visualization

reports/                             # Generated reports directory
├── js_patterns_report.html          # JavaScript patterns report
├── layered_architecture.html        # Layered architecture report
└── samples_report.html              # Sample code report
```

## Web Interface

```
src/web/
├── __init__.py                      # Package initialization
├── app.py                           # FastAPI application
├── cli.py                           # Web CLI integration
└── static/                          # Static web assets
    └── index.html                   # Base HTML template

web_ui/
└── frontend/                        # React frontend
    ├── public/                      # Public assets
    │   ├── index.html               # HTML entry point
    │   └── ...                      # Other assets
    └── src/                         # React source code
        ├── components/              # React components
        │   ├── FilePage.js          # File analysis page
        │   ├── Header.js            # Header component
        │   ├── HomePage.js          # Home page
        │   ├── ProjectPage.js       # Project page
        │   ├── ProjectsPage.js      # Projects list page
        │   └── ResultsPage.js       # Results visualization page
        ├── services/                # Service modules
        │   └── api.js               # API integration
        ├── App.js                   # Main React component
        └── index.js                 # React entry point
```

## Examples and Samples

```
examples/                            # Example implementations
├── ARCHITECTURE_PATTERNS.md         # Architecture pattern docs
├── dependency_inversion/            # Dependency inversion examples
├── event_driven/                    # Event-driven architecture examples
├── information_hiding/              # Information hiding examples
└── layered_architecture/            # Layered architecture examples

samples/                             # Sample pattern implementations
├── adapter_sample.js                # Adapter pattern (JS)
├── adapter_sample.py                # Adapter pattern (Python)
├── code_smells.py                   # Code smell examples
├── command_sample.js                # Command pattern (JS)
├── command_sample.py                # Command pattern (Python)
├── decorator_sample.js              # Decorator pattern (JS)
├── decorator_sample.py              # Decorator pattern (Python)
├── facade_sample.js                 # Facade pattern (JS)
├── facade_sample.py                 # Facade pattern (Python)
├── factory_sample.py                # Factory pattern
├── observer_sample.js               # Observer pattern (JS)
├── observer_sample.py               # Observer pattern (Python)
├── patterns.js                      # Combined patterns (JS)
├── repository_strategy_sample.js    # Repository strategy (JS)
├── repository_strategy_sample.py    # Repository strategy (Python)
├── singleton_sample.py              # Singleton pattern
├── strategy_sample.js               # Strategy pattern (JS)
└── strategy_sample.py               # Strategy pattern (Python)
```

## Tests

```
tests/
├── __init__.py                      # Package initialization
├── test_analyzer.py                 # Analyzer tests
├── test_enhanced_patterns.py        # Enhanced pattern tests
├── test_parser.py                   # Parser tests
├── test_pattern_detection.py        # Pattern detection tests
└── test_files/                      # Test files
    └── test_python.py               # Python test file
```

## Debugging and Development

```
debug_architecture.py                # Debug architecture detection
debug_dependency_inversion.py        # Debug dependency inversion
debug_information_hiding.py          # Debug information hiding
debug_layered_architecture.py        # Debug layered architecture
run_architecture_analysis.py         # Run architecture analysis
run_demo.py                          # Run demo analysis
test_implementations.py              # Test implementations
visualize_layered_architecture.py    # Visualize layered architecture
```

## Configuration and Build

```
Dockerfile                           # Docker container definition
Makefile                             # Build automation
docker-compose.yml                   # Docker Compose configuration
pyproject.toml                       # Project metadata
requirements.txt                     # Python dependencies
setup.py                             # Package installation script
scripts/                             # Utility scripts
├── setup_web_ui.sh                  # Set up web UI
└── start_web_ui.sh                  # Start web UI
```

## Documentation

```
docs/                               # Project documentation
├── overview/                       # Project overview
│   ├── README.md                    # Main overview
│   ├── philosophy.md                # Project philosophy
│   ├── project-summary.md           # Project summary
│   └── structure.md                 # This document
├── user-guide/                     # User documentation
│   └── getting-started.md           # Getting started guide
├── developer-guide/                # Developer documentation
│   ├── extending.md                 # Extension guide
│   └── tree-sitter.md               # Tree-sitter integration
├── features/                       # Feature documentation
│   ├── architecture-detection/      # Architecture detection
│   │   ├── overview.md              # Architecture detection overview
│   │   ├── intents.md               # Architectural intents
│   │   └── styles.md                # Architectural styles
│   ├── visualization.md             # Visualization capabilities
│   └── web-ui/                      # Web UI documentation
│       ├── overview.md              # Web UI overview
│       ├── design.md                # Web UI design
│       └── implementation.md        # Web UI implementation
├── project/                        # Project documentation
│   ├── achievements.md              # Project achievements
│   ├── claude.md                    # Claude implementation guide
│   └── roadmap.md                   # Development roadmap
└── patterns/                       # Pattern documentation
    └── repository_strategy_pattern.md # Repository strategy pattern
```