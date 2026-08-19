# Changelog

All notable changes to AgentBenchX will be documented in this file.

## [Unreleased]
### Added
- Initial project structure and architecture
- Foundational documentation (SPEC.md, ARCHITECTURE.md, ROADMAP.md, DEVELOPMENT.md, DECISIONS.md, SECURITY.md)
- Core directory structure for all components
- License, contribution guidelines, and code of conduct
- README with project overview
- CITATION.cff for proper attribution

## [0.1.0] - 2026-08-19
### Added
- Initial repository setup with complete architectural foundation
- All required documentation files
- Directory structure matching specifications
- Licensing and contribution guidelines

## [0.2.0] - 2026-08-19
### Added
- Execution context mechanism for agent learning from tool results
- Structured ExecutionContext and ActionExecution models in traces domain
- Updated orchestrator service to maintain execution history and provide context to agents
- Modified Agent interface to accept structured execution context
- Updated mock agent in tests to learn from context and adapt behavior
- Comprehensive unit tests for execution context functionality
- Integration tests verifying end-to-end flow with context-based learning
- Trace event system properly linking action IDs across ACTION_REQUESTED, TOOL_EXECUTED, and ACTION_COMPLETED events
- Fixed trace model helper functions to include required timestamp and sequence_number fields
- Established canonical ActionResult definition (without action_id, as Action owns identity)
- Updated all service layer implementations (task, agent, environment services)
- Created API route structure with proper module organization

### Changed
- Updated ARCHITECTURE.md to document execution context flow in Agent Interface section
- Added ADR 016: Execution Context for Agent Learning to DECISIONS.md

### Fixed
- Trace model test failures due to missing timestamp and sequence_number fields
- ActionResult inconsistency between domain and environment modules
- Orchestrator test failures due to agent not learning from tool results
- Import issues in orchestrator service for ExecutionContext and ActionExecution models