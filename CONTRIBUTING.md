# Contributing to AgentBenchX

Thank you for considering contributing to AgentBenchX! We welcome contributions from the community to help build a better platform for evaluating AI agents.

## How to Contribute

There are many ways to contribute to AgentBenchX:

1. **Report bugs** - Use the GitHub issue tracker to report bugs
2. **Suggest features** - Share your ideas for new features or improvements
3. **Improve documentation** - Help us make our documentation clearer and more comprehensive
4. **Write code** - Contribute new features, fix bugs, or improve performance
5. **Create benchmarks** - Develop new benchmarks or improve existing ones
6. **Write evaluators** - Create new evaluation dimensions or improve existing evaluators
7. **Build agent adapters** - Add support for new AI providers or platforms
8. **Review code** - Help review pull requests from other contributors

## Getting Started

### Setting Up Your Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/agentbenchx.git
   cd agentbenchx
   ```
3. Set up the development environment following the instructions in [DEVELOPMENT.md](DEVELOPMENT.md)
4. Create a branch for your changes:
   ```bash
   git checkout -b feature-or-fix-description
   ```

### Making Changes

1. Follow the coding standards outlined in [DEVELOPMENT.md](DEVELOPMENT.md)
2. Write tests for any new functionality
3. Ensure all tests pass before submitting
4. Update documentation as needed
5. Write clear, descriptive commit messages

### Submitting Changes

1. Push your changes to your fork:
   ```bash
   git push origin feature-or-fix-description
   ```
2. Open a pull request against the `main` branch of the main repository
3. Fill out the pull request template completely
4. Respond to any review feedback promptly
5. Keep your branch updated with the main branch if needed

## Contribution Guidelines

### Code Standards
- Follow PEP 8 for Python code
- Use type hints for all public functions and classes
- Write comprehensive docstrings
- Keep functions and classes focused and readable
- Write unit tests for new functionality
- Follow the project's linting and formatting rules

### Commit Messages
Use conventional commits format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Formatting changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Maintenance

Example: `feat: add OpenAI agent adapter`

### Pull Request Requirements
- Description must clearly explain what the PR does and why
- Reference any related issues
- Include screenshots for UI changes (when applicable)
- All tests must pass
- Code must follow project style guidelines
- Documentation must be updated if needed

### Issue Reporting
When reporting issues, please include:
- Clear and descriptive title
- Steps to reproduce the behavior
- Expected vs actual behavior
- Screenshots or logs if applicable
- Environment details (OS, Python version, etc.)
- Any relevant configuration details

## Development Process

We use a standard GitHub flow workflow:
1. Main branch (`main`) is always deployable
2. Feature branches are created from `main`
3. Pull requests are made to `main`
4. Code review is required for all PRs
5. After approval, PRs are merged using squash merge
6. Tags are created for releases

## Communities and Communication

- **GitHub Issues**: For bug reports, feature requests, and discussions
- **GitHub Discussions**: For questions, ideas, and general conversation
- **Pull Requests**: For code contributions and review
- **Documentation**: For in-depth guides and references

## Getting Help

If you need help with your contribution:
1. Check the existing documentation
2. Search existing issues for similar questions
3. Ask in GitHub Discussions
4. Reach out to maintainers if needed

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details.

## Licensing

By contributing to AgentBenchX, you agree that your contributions will be licensed under the MIT License. See [LICENSE](LICENSE) for details.

Thank you again for your contribution!