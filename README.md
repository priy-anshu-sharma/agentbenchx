# AgentBenchX

A model/provider-agnostic research-grade platform for evaluating autonomous AI agents.

## Problem Statement

As AI agents become more capable and autonomous, there is a growing need for rigorous, standardized evaluation frameworks that can assess agent performance across multiple dimensions including task success, accuracy, tool use, planning quality, efficiency, latency, cost, reliability, robustness, safety, and resistance to various failure modes. Existing evaluation tools are often provider-specific, lack standardization, or focus narrowly on certain capabilities.

## Why AgentBenchX Exists

AgentBenchX aims to fill this gap by providing a comprehensive, modular, and extensible platform that enables researchers and developers to:

- Evaluate agents from any provider (OpenAI, Anthropic, Google, etc.) using the same benchmarks
- Collect detailed traces of agent behavior for analysis
- Measure performance across 15+ dimensions of agent capability
- Ensure reproducible experiments through controlled environments and versioned benchmarks
- Assess safety, security, and robustness properties
- Share benchmark definitions and results for community collaboration

## Architecture Overview

AgentBenchX follows a modular architecture with clearly separated concerns:

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

Key components include:
- **Backend API** (FastAPI): Core services for managing agents, tasks, environments, and evaluations
- **Evaluator Library**: Specialized evaluators for different assessment dimensions
- **Environment Library**: Controlled execution environments for agent-tool interactions
- **Benchmark Library**: Versioned benchmark definitions and task generators
- **Agent Adapters**: Provider-specific interfaces for connecting different AI agents
- **Dashboard** (Next.js): Visualization and monitoring interface (planned)

## Technology Stack

- **Backend**: Python, FastAPI, Pydantic, SQLAlchemy, PostgreSQL
- **Evaluation**: Python, Pytest
- **Frontend**: Next.js, TypeScript, Tailwind CSS (future)
- **Infrastructure**: Docker, Docker Compose
- **Future**: Redis, background workers, OpenTelemetry tracing, sandboxed execution

## Project Status

**Phase 0: Foundation** - Architecture, directory structure, and foundational documentation complete
- Core directories and configuration files established
- Architectural decisions documented
- Development workflow defined

## Research Goals

AgentBenchX is designed to support research in:
- Comparative analysis of agent architectures
- Emergent capabilities in autonomous agents
- Failure mode identification and mitigation
- Safety and alignment in agent systems
- Tool use and reasoning capabilities
- Long-term agent reliability and consistency

## Contributing

We welcome contributions from the research community. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

AgentBenchX is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Citation

If you use AgentBenchX in your research, please cite it using the information in [CITATION.cff](CITATION.cff).