# AgentBenchX Development Guide

## Local Setup

### Prerequisites
- Python 3.9+
- Node.js 16+ (for frontend development)
- Docker and Docker Compose
- Git
- PostgreSQL (optional, for local development)

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agentbenchx
   ```

2. **Set up Python virtual environment**
   ```bash
   # Backend setup
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   pip install -r requirements/dev.txt
   ```

3. **Set up Node.js environment** (for future frontend work)
   ```bash
   cd ../dashboard
   npm install
   ```

4. **Environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database** (PostgreSQL)
   ```bash
   # Start PostgreSQL using Docker Compose
   docker-compose up -d db
   
   # Run migrations
   alembic upgrade head
   ```

### Development Workflow

#### Backend Development
1. Create feature branch: `git checkout -b feature/your-feature-name`
2. Make changes following coding standards
3. Write tests for new functionality
4. Run local tests: `pytest`
5. Commit changes: `git commit -m "feat: your descriptive message"`
6. Push branch and create pull request

#### Frontend Development (Future)
1. Create feature branch: `git checkout -b feature/your-feature-name`
2. Make changes in `/dashboard/src`
3. Follow TypeScript and React best practices
4. Run development server: `npm run dev`
5. Test changes locally
6. Commit and push as with backend

## Testing Workflow

### Running Tests
```bash
# Backend tests
pytest

# Backend tests with coverage
pytest --cov=app --cov-report=html

# Specific test module
pytest tests/unit/test_agents.py

# Frontend tests (when implemented)
npm test
```

### Test Types
- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete user workflows (future)
- **Property-based tests**: Test invariants and edge cases

### Test Organization
```
backend/tests/
├── unit/           # Isolated unit tests
├── integration/    # Cross-component tests
└── fixtures/       # Test data and mocks
```

## Linting and Formatting

### Python
- **Formatter**: Black
- **Linter**: Ruff
- **Type checking**: MyPy

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy app/

# Combined check (pre-commit)
pre-commit run
```

### JavaScript/TypeScript (Future)
- **Formatter**: Prettier
- **Linter**: ESLint
- **Type checking**: TypeScript compiler

```bash
# Format code
npm run format

# Lint code
npm run lint

# Type checking
npm run type-check
```

## Git Workflow

### Branch Naming
- `feature/` - New features
- `bugfix/` - Bug fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation changes
- `test/` - Test additions or modifications
- `chore/` - Maintenance tasks

### Commit Messages
Follow conventional commits format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Formatting changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Maintenance

Example: `feat: add agent runner service`

### Pull Request Process
1. Ensure branch is up-to-date with main: `git pull origin main`
2. Run all tests and checks locally
3. Push branch: `git push origin feature/your-feature-name`
4. Create pull request against main branch
5. Request review from team members
6. Address review feedback
7. Squash and merge after approval

## Environment Variables

See `.env.example` for required variables:

### Backend Variables
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - For JWT and cryptographic operations
- `DEBUG` - Enable debug mode (development only)
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `API_HOST` - Host for API binding
- `API_PORT` - Port for API binding
- `OPENAI_API_KEY` - OpenAI API key (when implemented)
- `ANTHROPIC_API_KEY` - Anthropic API key (when implemented)
- `GOOGLE_API_KEY` - Google API key (when implemented)

### Docker Variables
- `POSTGRES_USER` - PostgreSQL username
- `POSTGRES_PASSWORD` - PostgreSQL password
- `POSTGRES_DB` - PostgreSQL database name
- `POSTGRES_PORT` - PostgreSQL port

## Docker Workflow

### Development
```bash
# Start all services
docker-compose up

# Start services in background
docker-compose up -d

# Stop and remove containers
docker-compose down

# Rebuild containers after changes
docker-compose up --build

# View logs
docker-compose logs -f
```

### Services
- `api` - FastAPI backend service
- `db` - PostgreSQL database
- `redis` - Redis cache (future)
- `frontend` - Next.js dashboard (future)

## Code Style Guidelines

### Python
- Follow PEP 8 for style guidelines
- Use type hints for all public functions and classes
- Limit line length to 88 characters (Black default)
- Use descriptive variable and function names
- Write docstrings for all public modules, classes, and functions
- Use absolute imports within the project
- Prefer composition over inheritance
- Keep functions small and focused

### JavaScript/TypeScript (Future)
- Follow Airbnb JavaScript Style Guide with TypeScript extensions
- Use functional components and hooks
- Use TypeScript interfaces for props and state
- Limit line length to 100 characters
- Write JSDoc comments for exported functions and components
- Use meaningful variable and function names
- Keep components small and focused

## Documentation

### Inline Documentation
- Docstrings for all public APIs using Google or NumPy style
- Comments for complex logic or non-obvious implementations
- README files in each major directory
- Architecture decision records in DECISIONS.md

### External Documentation
- User guides in `/docs` directory
- API documentation generated from code
- Tutorials and examples in `/docs/tutorials`
- Research documentation in `/docs/research`

## Dependencies Management

### Python
- Use `pyproject.toml` for dependency management
- Use `poetry` or `pip-tools` for dependency resolution
- Separate dependencies:
  - Production: `pyproject.toml`
  - Development: `requirements/dev.txt`
  - Testing: Included in dev requirements
- Regularly update dependencies with security patches

### JavaScript/TypeScript (Future)
- Use `package.json` for dependency management
- Use `npm` or `yarn` for installation
- Separate dependencies:
  - Production: `dependencies`
  - Development: `devDependencies`
- Regularly audit for vulnerabilities: `npm audit`

## Release Process

### Versioning
Follow Semantic Versioning (MAJOR.MINOR.PATCH):
- MAJOR: Incompatible API changes
- MINOR: Backward-compatible functionality
- PATCH: Backward-compatible bug fixes

### Pre-release Checklist
1. Ensure all tests pass
2. Update CHANGELOG.md with changes
3. Update version in appropriate files
4. Tag release: `git tag vX.Y.Z`
5. Push tags: `git push origin --tags`
6. Build and publish Docker images
7. Create GitHub release with release notes

### Post-release
1. Monitor for issues and feedback
2. Address critical bugs promptly
3. Plan next iteration based on roadmap

## Troubleshooting

### Common Issues
1. **Database connection fails**
   - Check PostgreSQL is running: `docker-compose ps db`
   - Verify DATABASE_URL in .env
   - Check database migrations: `alembic current`

2. **Tests fail intermittently**
   - Check for proper test isolation
   - Ensure no shared state between tests
   - Use unique temporary resources per test

3. **Docker container fails to start**
   - Check logs: `docker-compose logs <service>`
   - Verify port conflicts
   - Check resource limitations

4. **Import errors**
   - Verify virtual environment is activated
   - Check PYTHONPATH settings
   - Ensure package is installed in development mode

### Getting Help
- Check existing documentation in `/docs`
- Search issue tracker for similar problems
- Ask in project communication channels
- Create detailed issue with reproduction steps