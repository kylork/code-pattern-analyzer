root@swift:~/claude-code-demo/test# ls
root@swift:~/claude-code-demo/test# git clone https://github.com/kylork/code-pattern-analyzer.git
Cloning into 'code-pattern-analyzer'...
remote: Enumerating objects: 296, done.
remote: Counting objects: 100% (296/296), done.
remote: Compressing objects: 100% (242/242), done.
remote: Total 296 (delta 65), reused 274 (delta 43), pack-reused 0 (from 0)
Receiving objects: 100% (296/296), 692.50 KiB | 5.58 MiB/s, done.
Resolving deltas: 100% (65/65), done.
root@swift:~/claude-code-demo/test# ls
code-pattern-analyzer
root@swift:~/claude-code-demo/test# cd code-pattern-analyzer
root@swift:~/claude-code-demo/test/code-pattern-analyzer# tree
.
├── ACHIEVEMENTS.md
├── ARCHITECTURAL_PATTERNS_SUMMARY.md
├── ARCHITECTURE_DETECTION.md
├── CLAUDE.md
├── Dockerfile
├── EXTENDING.md
├── GETTING_STARTED.md
├── Makefile
├── ONBOARDING.md
├── PHILOSOPHY.md
├── PROJECT_SUMMARY.md
├── README.md
├── ROADMAP.md
├── SUMMARY.md
├── TREE_SITTER_INTEGRATION.md
├── USAGE.md
├── VISUALIZATION.md
├── WEB_UI_IMPLEMENTATION.md
├── WEB_UI_PLAN.md
├── code-patter-analyzer-file-tree.txt
├── code_pattern_analyzer.egg-info
│   ├── PKG-INFO
│   ├── SOURCES.txt
│   ├── dependency_links.txt
│   ├── entry_points.txt
│   ├── requires.txt
│   └── top_level.txt
├── debug_architecture.py
├── debug_dependency_inversion.py
├── debug_information_hiding.py
├── debug_layered_architecture.py
├── demo.sh
├── docker-compose.yml
├── docs
│   └── patterns
│       └── repository_strategy_pattern.md
├── examples
│   ├── ARCHITECTURE_PATTERNS.md
│   ├── dependency_inversion
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── factories.py
│   │   ├── high_level.py
│   │   ├── implementations.py
│   │   └── interfaces.py
│   ├── event_driven
│   │   ├── __init__.py
│   │   ├── consumers.py
│   │   ├── cqrs.py
│   │   ├── event_bus.py
│   │   ├── event_sourcing.py
│   │   ├── events.py
│   │   └── producers.py
│   ├── example_cmd.py
│   ├── information_hiding
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── data_access.py
│   │   └── service_layer.py
│   └── layered_architecture
│       ├── __init__.py
│       ├── controllers
│       │   ├── __init__.py
│       │   └── user_controller.py
│       ├── models
│       │   ├── __init__.py
│       │   └── user.py
│       ├── repositories
│       │   ├── __init__.py
│       │   └── user_repository.py
│       └── services
│           ├── __init__.py
│           └── user_service.py
├── pyproject.toml
├── reports
│   └── js_patterns_report.html
├── requirements.txt
├── run_architecture_analysis.py
├── run_demo.py
├── sample-code
│   └── sample.py
├── sample.py
├── samples
│   ├── adapter_sample.js
│   ├── adapter_sample.py
│   ├── code_smells.py
│   ├── command_sample.js
│   ├── command_sample.py
│   ├── decorator_sample.js
│   ├── decorator_sample.py
│   ├── facade_sample.js
│   ├── facade_sample.py
│   ├── factory_sample.py
│   ├── observer_sample.js
│   ├── observer_sample.py
│   ├── patterns.js
│   ├── repository_strategy_sample.js
│   ├── repository_strategy_sample.py
│   ├── singleton_sample.py
│   ├── strategy_sample.js
│   └── strategy_sample.py
├── scripts
│   ├── setup_web_ui.sh
│   └── start_web_ui.sh
├── setup.py
├── src
│   ├── __init__.py
│   ├── __main__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-310.pyc
│   │   ├── analyzer.cpython-310.pyc
│   │   ├── cli.cpython-310.pyc
│   │   ├── mock_implementation.cpython-310.pyc
│   │   ├── parser.cpython-310.pyc
│   │   ├── pattern_base.cpython-310.pyc
│   │   ├── pattern_recognizer.cpython-310.pyc
│   │   ├── pattern_registry.cpython-310.pyc
│   │   ├── tree_sitter_manager.cpython-310.pyc
│   │   ├── utils.cpython-310.pyc
│   │   └── visualization.cpython-310.pyc
│   ├── analyzer.py
│   ├── cli
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── parser.py
│   │   └── subcommands.py
│   ├── cli.py
│   ├── commands
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-310.pyc
│   │   │   ├── compare.cpython-310.pyc
│   │   │   └── report.cpython-310.pyc
│   │   ├── architecture.py
│   │   ├── compare.py
│   │   └── report.py
│   ├── mock_implementation.py
│   ├── parser.py
│   ├── pattern_base.py
│   ├── pattern_recognizer.py
│   ├── pattern_registry.py
│   ├── patterns
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-310.pyc
│   │   │   ├── class_patterns.cpython-310.pyc
│   │   │   ├── code_smells.cpython-310.pyc
│   │   │   ├── design_patterns.cpython-310.pyc
│   │   │   └── function_patterns.cpython-310.pyc
│   │   ├── architectural_intents
│   │   │   ├── __init__.py
│   │   │   ├── architectural_intent_base.py
│   │   │   ├── architectural_intent_detector.py
│   │   │   ├── dependency_inversion.py
│   │   │   ├── information_hiding.py
│   │   │   └── separation_of_concerns.py
│   │   ├── architectural_styles
│   │   │   ├── __init__.py
│   │   │   ├── architectural_style_base.py
│   │   │   ├── architectural_style_detector.py
│   │   │   ├── clean_architecture.py
│   │   │   ├── event_driven.py
│   │   │   ├── hexagonal.py
│   │   │   ├── layered.py
│   │   │   └── microservices.py
│   │   ├── class_patterns.py
│   │   ├── code_smells.py
│   │   ├── design_patterns.py
│   │   ├── enhanced
│   │   │   └── strategy_pattern_enhanced.py
│   │   ├── function_patterns.py
│   │   ├── nexus.md
│   │   └── python_patterns.py
│   ├── tree_sitter_impl.py
│   ├── tree_sitter_manager.py
│   ├── utils.py
│   ├── visualization
│   │   ├── __init__.py
│   │   └── architecture_visualizer.py
│   ├── visualization.py
│   └── web
│       ├── __init__.py
│       ├── app.py
│       ├── cli.py
│       └── static
│           └── index.html
├── test_implementations.py
├── tests
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── test_analyzer.cpython-310.pyc
│   │   └── test_parser.cpython-310.pyc
│   ├── test_analyzer.py
│   ├── test_enhanced_patterns.py
│   ├── test_files
│   │   └── test_python.py
│   ├── test_parser.py
│   └── test_pattern_detection.py
├── visualize_layered_architecture.py
└── web_ui
    └── frontend
        ├── README.md
        ├── package-lock.json
        ├── package.json
        ├── public
        │   ├── favicon.ico
        │   ├── index.html
        │   ├── logo192.png
        │   ├── logo512.png
        │   ├── manifest.json
        │   └── robots.txt
        └── src
            ├── App.css
            ├── App.js
            ├── App.test.js
            ├── components
            │   ├── FilePage.js
            │   ├── Header.js
            │   ├── HomePage.js
            │   ├── ProjectPage.js
            │   ├── ProjectsPage.js
            │   └── ResultsPage.js
            ├── index.css
            ├── index.js
            ├── logo.svg
            ├── reportWebVitals.js
            ├── services
            │   └── api.js
            └── setupTests.js

38 directories, 191 files