# Changelog

All notable changes to AgentBenchX will be documented in this file.

## [Unreleased]
### Added
- Trace serialization functionality for Phase 2.3
- Comprehensive serialization tests for Trace and TraceEvent models
- Verified round-trip serialization preserves all data including UUIDs, timestamps, enums, and complex payloads

## [0.2.1] - 2026-08-19
### Added
- Trace serialization functionality for Phase 2.3
  - Trace and TraceEvent models can be safely serialized to JSON and deserialized
  - All information survives the round trip: trace ID, run ID, task ID, agent ID, timestamps, event IDs, event sequence numbers, event types, event payloads, event metadata, trace metadata
  - Uses Pydantic's native serialization methods (model_dump_json, model_validate_json)
  - Properly handles UUIDs, datetime values (with timezone preservation), enums, nested dictionaries, lists, and None/null values
- Comprehensive serialization tests
  - Tests for empty traces, multi-event traces, complex payloads, and invalid data
  - Verifies invalid event types, missing required fields, and invalid UUIDs are properly rejected
  - Confirms timezone information is preserved in datetime serialization

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

## [0.1.0] - 2026-08-19
### Added
- Initial repository setup with complete architectural foundation
- All required documentation files
- Directory structure matching specifications
- Licensing and contribution guidelines
- README with project overview
- CITATION.cff for proper attribution