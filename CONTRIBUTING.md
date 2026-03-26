# Contributing to BioStructure DB

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🎯 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Environment** (OS, Node version, etc.)

**Example:**
```markdown
**Bug**: API returns 500 error when searching

**Steps to Reproduce:**
1. Go to search page
2. Search for 'TP53'
3. See error

**Expected:** Search results
**Actual:** 500 Internal Server Error

**Environment:**
- OS: Ubuntu 20.04
- Node: v20.10.0
```

### Suggesting Features

Feature suggestions are welcome! Please provide:

- **Use case**: Why is this feature needed?
- **Proposed solution**: How should it work?
- **Alternatives**: What other solutions have you considered?

### Pull Requests

1. Fork the repository
2. Create your branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Ensure tests pass
6. Submit pull request

---

## 📋 Development Guidelines

### Code Style

- Use ESLint and Prettier
- Follow existing code style
- Write meaningful comments
- Use descriptive variable names

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: Add new search feature
fix: Fix database connection issue
docs: Update README
test: Add unit tests for API
refactor: Refactor database queries
```

### Testing

- Write tests for new features
- Maintain >70% code coverage
- Run tests before submitting PR

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage
```

---

## 🚀 Development Workflow

### 1. Setup Development Environment

```bash
# Clone repository
git clone https://github.com/knight-zmz/biostructure-db.git
cd biostructure-db

# Install dependencies
npm install

# Setup database
npm run db:setup

# Start development server
npm run dev
```

### 2. Make Changes

- Create feature branch
- Make changes
- Write tests
- Run tests

### 3. Submit PR

- Push to your fork
- Create pull request
- Wait for review
- Address feedback

---

## 📚 Additional Resources

- [Project Structure](docs/developer/architecture.md)
- [API Documentation](docs/api/)
- [Coding Standards](docs/developer/coding-standards.md)

---

## 🙏 Thank You!

Every contribution, no matter how small, makes a difference.

**🦞 Happy coding!**
