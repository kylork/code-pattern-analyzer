# Documentation Reorganization Plan

This document outlines a plan to reorganize the documentation files in the Code Pattern Analyzer project to improve clarity, reduce redundancy, and provide better structure.

## Current Issues

1. **Too Many Documentation Files**: There are currently 19 .md files in the root directory
2. **Redundant Content**: Several files contain overlapping information
3. **Inconsistent Naming**: All-caps filenames make it hard to identify the purpose at a glance
4. **Fragmented Information**: Related content is spread across multiple files
5. **Missing Hierarchy**: Documentation lacks clear organization

## Proposed Structure

```
docs/
├── overview/
│   ├── README.md               # Project overview (from current README.md)
│   ├── philosophy.md           # Philosophical foundations (from PHILOSOPHY.md)
│   ├── project-summary.md      # Project summary (merge PROJECT_SUMMARY.md & SUMMARY.md)
│   └── structure.md            # Project structure (from PROJECT_STRUCTURE.md)
│
├── user-guide/
│   ├── getting-started.md      # Getting started guide (from GETTING_STARTED.md)
│   ├── installation.md         # Installation instructions (extracted from USAGE.md)
│   ├── usage.md                # Usage guide (from USAGE.md, minus installation)
│   └── examples.md             # Usage examples (extracted from USAGE.md)
│
├── developer-guide/
│   ├── architecture.md         # System architecture (extracted from CLAUDE.md)
│   ├── extending.md            # Extension guide (from EXTENDING.md)
│   ├── tree-sitter.md          # Tree-sitter integration (from TREE_SITTER_INTEGRATION.md)
│   ├── onboarding.md           # New developer onboarding (from ONBOARDING.md)
│   └── contribution.md         # Contribution guidelines (new file)
│
├── features/
│   ├── patterns/
│   │   ├── design-patterns.md  # Design pattern detection (new file)
│   │   └── code-smells.md      # Code smell detection (new file)
│   ├── architecture-detection/
│   │   ├── overview.md         # Architecture detection overview (from ARCHITECTURE_DETECTION.md)
│   │   ├── intents.md          # Architectural intents (from ARCHITECTURAL_PATTERNS_SUMMARY.md)
│   │   └── styles.md           # Architectural styles (from src/patterns/nexus.md)
│   ├── visualization.md        # Visualization capabilities (from VISUALIZATION.md)
│   └── web-ui/
│       ├── overview.md         # Web UI overview (from WEB_UI_PLAN.md intro)
│       ├── design.md           # Web UI design (from WEB_UI_PLAN.md mockups & architecture)
│       └── implementation.md   # Web UI implementation (from WEB_UI_IMPLEMENTATION.md)
│
└── project/
    ├── roadmap.md              # Development roadmap (from ROADMAP.md)
    ├── achievements.md         # Project achievements (from ACHIEVEMENTS.md)
    ├── claude.md               # Claude implementation guide (from CLAUDE.md)
    └── changelog.md            # Project changelog (new file)
```

## Implementation Strategy

### Phase 1: Create the Structure

1. Create the directory structure in the `docs/` folder
2. Keep all original files in the root directory initially

### Phase 2: Consolidate Content

1. Merge redundant files:
   - Combine PROJECT_SUMMARY.md and SUMMARY.md into a single project-summary.md
   - Extract installation content from USAGE.md into separate installation.md

2. Move specialized content to appropriate locations:
   - Move src/patterns/nexus.md to docs/features/architecture-detection/styles.md
   - Copy relevant parts of CLAUDE.md to docs/developer-guide/architecture.md

### Phase 3: Create Root README

1. Update the root README.md to:
   - Keep core project description
   - Add links to key documentation
   - Simplify structure

### Phase 4: Clean Up

1. Add redirects from old files to new ones
2. Eventually remove redundant root files, but only after ensuring all content is preserved

## Benefits

1. **Improved Organization**: Clear hierarchy makes navigation easier
2. **Reduced Redundancy**: Merged overlapping content
3. **Better Discoverability**: Documentation organized by purpose
4. **Scalability**: Structure supports future documentation
5. **Maintainability**: Easier to update specific aspects of documentation

## Preservation Strategy

To ensure no data is lost:

1. Keep original files in place initially and add links to new locations
2. Use git to track all changes carefully
3. Only remove original files after verification that all content is preserved
4. Consider adding a "legacy-docs" branch to preserve the original structure