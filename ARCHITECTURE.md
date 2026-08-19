# AgentBenchX Architecture

## System Overview

AgentBenchX follows a modular, layered architecture designed for extensibility, reproducibility, and clear separation of concerns. The system is organized around the core evaluation flow:

```
Task
  ↓
Agent
  ↓
Controlled Environment
  ↓
Tools
  ↓
Trace Collection
  ↓
Evaluation Engine
  ↓
Metrics
  ↓
Failure Taxonomy
  ↓
Benchmark Results
  ↓
Research Analysis
```

## Major Components

### 1. Backend API (`backend/`)
Built with FastAPI, provides RESTful interfaces for managing the evaluation lifecycle.

**Responsibilities:**
- Agent registration, configuration, and versioning
- Task and benchmark definition management
- Environment provisioning and control
- Experiment orchestration and tracking
- Trace storage and retrieval
- Evaluation result aggregation
- Authentication and authorization (future)
- API documentation and validation

**Sub-components:**
- **API Layer**: Route handlers and request/response models
- **Core**: Configuration, logging, security utilities
- **Domain**: Business logic entities and use cases
- **Services**: Application services orchestrating domain logic
- **Infrastructure**: Database providers, external service integrations
- **Schemas**: Pydantic models for data validation and serialization

### 2. Evaluator Library (`evaluator/`)
Specialized evaluation logic for assessing agent performance across dimensions.

**Responsibilities:**
- Deterministic evaluation (task success, accuracy, completeness)
- Model-based evaluation (planning quality, coherence, creativity)
- Safety evaluation (harmful content, prompt injection resistance)
- Robustness evaluation (noise tolerance, edge case handling)
- Reliability evaluation (consistency across runs, failure recovery)
- Efficiency evaluation (token usage, step count, time)
- Metric computation and aggregation
- Failure taxonomy application

**Sub-components:**
- **Runner**: Experiment execution and result collection
- **Evaluators**: Dimension-specific evaluation logic
- **Metrics**: Computation of quantitative measures
- **Scoring**: Aggregation and normalization of results
- **Taxonomy**: Failure categorization and analysis
- **Aggregation**: Cross-run and cross-experiment result synthesis

### 3. Environment Library (`environment/`)
Controlled execution environments for agent-tool interactions.

**Responsibilities:**
- Providing isolated execution contexts
- Managing tool availability and permissions
- Logging all interactions and state changes
- Ensuring reproducibility through seeded randomness
- Supporting various environment types (filesystem, database, web, API)
- Cleaning up resources after execution

**Sub-components:**
- **Base**: Abstract environment interfaces and common utilities
- **State**: Environment state management and snapshots
- **Filesystem**: Sandboxed file system operations
- **Database**: Controlled database interactions
- **Web**: Simulated web browsing and API interactions
- **Agentbenchx_env**: Concrete environment implementations
- **Tools**: Individual tool implementations and wrappers

### 4. Benchmark Library (`benchmark/`)
Versioned benchmark definitions and task generation.

**Responsibilities:**
- Defining benchmark schemas and versions
- Generating task instances from templates
- Validating benchmark definitions
- Categorizing benchmarks by domain and difficulty
- Providing benchmark metadata and documentation
- Enabling benchmark sharing and reproduction

**Sub-components:**
- **Tasks**: Individual task definitions organized by category
- **Schemas**: Validation schemas for tasks and benchmarks
- **Generators**: Task instance generation from templates
- **Validation**: Benchmark definition validation logic
- **VERSION**: Current benchmark version tracking

### 5. Agent Adapters (`agents/`)
Provider-specific interfaces for connecting different AI agents.

**Responsibilities:**
- Abstracting provider-specific agent APIs
- Normalizing agent inputs and outputs
- Handling provider authentication and rate limiting
- Implementing provider-specific tool calling conventions
- Providing example agent implementations
- Supporting custom agent implementations

**Sub-components:**
- **Base**: Abstract agent interface definition
- **Adapters**: Provider-specific implementations (OpenAI, Anthropic, Google, etc.)
- **Examples**: Reference agent implementations

### 6. Experiments (`experiments/`)
Configuration, execution, and analysis of evaluation experiments.

**Responsibilities:**
- Storing experiment configurations
- Tracking experiment runs and results
- Facilitating experiment reproduction
- Supporting parameter sweeps and A/B testing
- Storing and organizing experimental results
- Providing analysis tools and scripts

**Sub-components:**
- **Configs**: Experiment configuration templates
- **Runs**: Individual experiment execution records
- **Results**: Raw and processed experimental results
- **Analysis**: Post-experiment analysis scripts and notebooks

### 7. Dashboard (`dashboard/`)
Future web interface for visualization and monitoring (planned).

**Responsibilities:**
- Visualizing experiment results and metrics
- Monitoring active evaluations
- Browsing traces and agent behaviors
- Comparing agent performance across benchmarks
- Managing benchmark definitions
- Configuring and launching experiments

## Data Flow

### Agent Execution Flow
1. Experiment configuration specifies agent, task, and environment
2. Backend provisions environment and loads agent adapter
3. Agent receives task prompt and begins execution
4. Agent requests tool usage through standardized interface
5. Environment executes tool in sandboxed context
6. Tool results returned to agent
7. All interactions logged as trace events
8. Agent completes task or reaches iteration limit
9. Trace collection completes
10. Evaluators process trace to compute metrics
11. Results stored and made available for analysis

### Trace Lifecycle
1. **Generation**: Environment captures agent-tool interactions as TraceEvent objects
2. **Storage**: Trace events persisted to database with relational structure
3. **Retrieval**: Traces fetched for evaluation or analysis
4. **Processing**: Evaluators analyze traces to compute dimension scores
5. **Aggregation**: Results combined across runs and experiments
6. **Archival**: Long-term storage of trace data for research

## Component Responsibilities

### Agent Interface
- Receives task prompts and environmental observations
- Requests tool usage with parameters
- Processes tool results and continues execution
- Receives execution context containing history of previous actions and results
- Terminates when task complete or limits reached
- All actions must be traceable through standardized interface

### Environment Interface
- Provides initial state and task description
- Mediates all tool usage requests
- Logs tool inputs, outputs, timing, and side effects
- Enforces security boundaries and permissions
- Provides clean state for reproducible runs
- Supports snapshotting and restoration for debugging

### Tool Interface
- Executes specific functions (file ops, db queries, web requests, etc.)
- Returns structured results or errors
- May have state that persists across calls within environment
- Subject to permission checking and rate limiting
- Implemented in sandboxed context when possible

### Evaluator Interface
- Takes trace and returns evaluation results
- May be deterministic (rule-based) or model-based (LLM-judged)
- Produces explainable scores with failure categorization
- Supports batch evaluation of multiple traces
- Composable for complex multi-dimensional assessment

## Security Boundaries

1. **Host Protection**: Agent execution isolated from host filesystem and network
2. **Tool Sandboxing**: Tools execute in restricted environments with least privilege
3. **Data Isolation**: Experiment data separated and access-controlled
4. **Credential Management**: Provider credentials stored securely, never logged
5. **Network Controls**: Outbound network access restricted and monitored
6. **Process Isolation**: Each agent run in separate process/container
7. **Input Sanitization**: Agent outputs validated before tool execution
8. **Audit Logging**: Security-relevant events logged for review

## Future Scalability

1. **Horizontal Scaling**: Backend services designed for stateless horizontal scaling
2. **Distributed Execution**: Experiment running可分发到 worker 节点
3. **Caching Layer**: Redis for frequent database queries and computation results
4. **Message Queues**: Background task processing with Celery/RQ
5. **Microservices**: Optional decomposition of tightly coupled components
6. **Cloud Deployment**: Kubernetes/helm charts for cloud deployment
7. **Plugin System**: Dynamic loading of evaluators, tools, and agent adapters
8. **Event Streaming**: OpenTelemetry-compatible trace export for external analysis

## Database Entities (Proposed)

- **Agent**: Provider, configuration, version, credentials (encrypted)
- **AgentVersion**: Specific agent configuration snapshot
- **Task**: Definition, success criteria, category, difficulty
- **TaskVersion**: Immutable task definition snapshot
- **Environment**: Type, configuration, provisioning script
- **Tool**: Implementation, permissions, resource limits
- **EvaluationRun**: Agent-task-environment execution instance
- **Trace**: Linked list of trace events from an evaluation run
- **TraceEvent**: Individual agent action or observation
- **EvaluationResult**: Scores and metrics for an evaluation run
- **Metric**: Definition of computable measures
- **Benchmark**: Collection of tasks with versioning
- **BenchmarkVersion**: Immutable benchmark definition snapshot
- **Experiment**: Configuration for repeated evaluation runs
- **ExperimentResult**: Aggregated results from experiment runs

## Design Principles

1. **Separation of Concerns**: Each component has single, well-defined responsibility
2. **Replaceable Components**: Interfaces allow independent implementation swapping
3. **Reproducibility**: Environments and benchmarks versioned for exact replication
4. **Traceability**: Every action captured with sufficient context for analysis
5. **Explainability**: Evaluation results traceable to specific behaviors
6. **Security-First**: Boundaries and permissions designed in from start
7. **Extensibility**: Clear extension points for new capabilities
8. **Testability**: Components designed for unit and integration testing
9. **Performance-Conscious**: Design avoids unnecessary overhead where possible
10. **Research-Oriented**: Facilitates analysis, experimentation, and knowledge sharing

## ASCII Architecture Diagram

```
+----------------+     +----------------+     +------------------+
|    Agent       |     |  Environment   |     |     Tool         |
| (Adapter/      |<---->| (Sandboxed     |<---->| (File, DB, Web,  |
|  Implementation)|     |  Context)      |     |  API, Custom)    |
+----------------+     +----------------+     +------------------+
        ^                         ^                  ^
        |                         |                  |
        |  Tool Requests/Results  |  State Updates   |  Execution
        |                         |                  |
        v                         v                  v
+----------------+     +----------------+     +------------------+
|  Trace         |     |  Evaluator     |     |   Backend API    |
|  Collection    |     |  (Dimensions)  |     |  (Services, DB)  |
+----------------+     +----------------+     +------------------+
        ^                         ^                  ^
        |                         |                  |
        |  Trace Events           |  Evaluation      |  Config/Control
        |                         |  Results         |
        v                         v                  v
+----------------+     +----------------+     +------------------+
|   Storage      |     |  Results       |     |  Experiment      |
|  (Database)    |     |  Aggregation   |     |  Configuration   |
+----------------+     +----------------+     +------------------+
        ^                         ^                  ^
        |                         |                  |
        |  Persistence            |  Research        |  Definition/Launch
        |                         |  Analysis        |
        v                         v                  v
+----------------+     +----------------+     +------------------+
|  Research      |     |  Dashboard     |     |     CLI          |
|  Analysis      |<---->| (Future)      |     |  (Admin/Ops)     |
+----------------+     +----------------+     +------------------+
```