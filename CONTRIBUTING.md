# Contributing to InfraGenie AgentCore Infrastructure

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/infragenie_agentcore_infrastructure.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit with clear messages: `git commit -m "Add feature: description"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install AgentCore CLI
pip install bedrock-agentcore
```

## Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose
- Add comments for complex logic

## Adding New Gateways

When adding support for a new MCP gateway:

1. Create deployment script: `deploy_{service}_gateway.py`
2. Create OAuth provider script if needed: `create_{service}_oauth_provider.py`
3. Create target script: `create_{service}_target.py`
4. Add testing script: `test_{service}_gateway_http.py`
5. Update README.md with gateway details
6. Follow naming convention: `{service}-mcp-gateway`

## Testing

Before submitting a PR:

1. Test gateway deployment in your AWS account
2. Verify OAuth authentication works
3. Test gateway connectivity with `test_gateway_http.py`
4. Ensure no credentials are committed

## Security

- Never commit credentials or secrets
- Use AWS Parameter Store for sensitive data
- Review .gitignore before committing
- Use environment variables for configuration

## Pull Request Guidelines

- Provide clear description of changes
- Reference any related issues
- Include testing steps
- Update documentation as needed
- Ensure code follows project style

## Questions?

Open an issue for:
- Bug reports
- Feature requests
- Documentation improvements
- General questions

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Focus on what's best for the community

Thank you for contributing! 🚀
