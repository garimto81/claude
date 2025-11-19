# Contributing to Claude Code Config

Welcome! We appreciate your interest in contributing to this Claude Code workflow system.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Plugin Development](#plugin-development)
- [Documentation](#documentation)
- [Translation](#translation)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

---

## Code of Conduct

This project follows the principle of respectful collaboration:

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Acknowledge contributions

---

## How Can I Contribute?

### 🐛 Reporting Bugs

**Before submitting a bug report:**
- Check existing issues to avoid duplicates
- Test with the latest version
- Collect relevant information (version, environment, steps to reproduce)

**Submit via GitHub Issues with:**
```markdown
**Environment:**
- OS: Windows/macOS/Linux
- Claude Code Version: X.Y.Z
- Repository Version: vX.Y.Z

**Steps to Reproduce:**
1. ...
2. ...

**Expected vs Actual:**
- Expected: ...
- Actual: ...

**Additional Context:**
Screenshots, logs, etc.
```

### 💡 Suggesting Enhancements

**Enhancement proposals should include:**
- Clear problem statement
- Proposed solution
- Use cases and benefits
- Potential drawbacks
- Alternative approaches considered

### 📝 Documentation Improvements

Documentation contributions are highly valued:
- Fix typos or unclear explanations
- Add examples or use cases
- Improve translation quality (Korean ↔ English)
- Create tutorials or guides

---

## Plugin Development

### Adding a New Plugin

**1. Create Plugin Structure:**
```bash
.claude/plugins/your-plugin/
├── README.md           # Plugin documentation
├── agents/
│   └── your-agent.md   # Agent definitions
├── commands/           # (optional)
│   └── your-cmd.md
└── skills/            # (optional)
    └── your-skill/
```

**2. Agent Template:**
```markdown
# Your Agent Name

## Purpose
[One-line description]

## Capabilities
- Capability 1
- Capability 2

## Usage
[When to use this agent]

## Example
[Code or usage example]

## Performance
- Success Rate: XX%
- Average Duration: X seconds
- Best For: [Use case]
```

**3. Register in marketplace.json:**
```json
{
  "name": "your-plugin",
  "version": "1.0.0",
  "description": "...",
  "author": {
    "name": "Your Name",
    "url": "https://github.com/yourusername"
  },
  "agents": ["./agents/your-agent.md"],
  "license": "MIT"
}
```

**4. Update VERSION:**
```yaml
plugins:
  your-plugin: "1.0.0"
```

### Plugin Guidelines

- **Single Responsibility**: Each plugin should have a clear, focused purpose
- **Documentation**: Include comprehensive README with examples
- **Testing**: Provide test scenarios or validation scripts
- **Performance**: Document expected success rates and timing
- **Dependencies**: Clearly list any external dependencies
- **License**: Ensure compatible license (preferably MIT)

---

## Documentation

### Language Strategy

**Primary Language: English**
- CLAUDE.md, README.md in English
- Korean translation: CLAUDE.ko.md, README.ko.md

**Translation Guidelines:**
- Keep technical terms in English (e.g., "agent", "plugin")
- Use clear, simple language
- Verify technical accuracy
- Test commands and examples

### Documentation Structure

```
docs/
├── phases/           # Phase-specific guides
│   ├── 00-prd.md
│   ├── 01-implementation.md
│   └── ...
├── agents/           # Agent documentation
│   └── by-domain/
├── guides/           # Tutorial guides
└── api/              # API reference
```

### Writing Style

- **Concise**: Keep explanations brief but complete
- **Examples**: Provide practical code examples
- **Visual**: Use diagrams, tables, code blocks
- **Actionable**: Include clear next steps
- **Searchable**: Use descriptive headings and keywords

---

## Translation

### How to Translate

**1. Create translation file:**
```bash
docs/your-doc.ko.md  # Korean
docs/your-doc.ja.md  # Japanese
```

**2. Follow template:**
```markdown
# [Document Title] (Korean/Japanese translation)

> **Original**: [Link to English version]
> **Last Updated**: YYYY-MM-DD

[Translated content...]
```

**3. Maintain consistency:**
- Use translation glossary (create if needed)
- Keep code examples unchanged
- Update links to translated versions when available
- Verify technical terms

### Translation Priority

1. **High**: CLAUDE.md, README.md, Quick Start Guide
2. **Medium**: Phase guides, Agent reference
3. **Low**: Advanced guides, Spec Kit documentation

---

## Testing

### Validation Scripts

**Test your changes:**
```bash
# Test Phase 0 validation
bash scripts/validate-phase-0.sh 9999

# Test plugin syntax
find .claude/plugins -name "*.md" -exec markdown-link-check {} \;

# Run Python linter
pylint scripts/*.py

# Run Shell linter
shellcheck scripts/*.sh
```

### Manual Testing

**For plugin changes:**
1. Load plugin in Claude Code
2. Test agent invocation
3. Verify expected behavior
4. Check token usage
5. Document success rate

**For workflow changes:**
1. Create test PRD
2. Run through Phase 0-6
3. Verify all validations pass
4. Test on different platforms (Windows/macOS/Linux)

---

## Submitting Changes

### Pull Request Process

**1. Fork and Branch:**
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

**2. Make Changes:**
- Follow existing code style
- Update documentation
- Add tests if applicable
- Update CHANGELOG.md
- Update VERSION if needed

**3. Commit Convention:**
```bash
git commit -m "type: subject (vX.Y.Z) [PRD-NNNN]"

# Types:
# feat: New feature
# fix: Bug fix
# docs: Documentation only
# refactor: Code refactoring
# perf: Performance improvement
# test: Adding tests
# chore: Maintenance
```

**4. Create Pull Request:**
```markdown
## Description
[Brief description of changes]

## Motivation
[Why these changes are needed]

## Changes Made
- Change 1
- Change 2

## Testing
- [ ] Manual testing completed
- [ ] Validation scripts pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No breaking changes (or documented in CHANGELOG)
```

### Review Process

**What reviewers look for:**
- Code quality and style
- Documentation completeness
- Test coverage
- Performance impact
- Breaking changes
- Security considerations

**Typical timeline:**
- Initial review: 1-3 days
- Revisions: As needed
- Merge: After approval + CI pass

---

## Development Setup

### Prerequisites

```bash
# Required
- Git
- Python 3.8+
- Node.js 16+ (for some validations)

# Optional
- Claude Code CLI
- GitHub CLI (gh)
```

### Local Setup

```bash
# 1. Clone repository
git clone https://github.com/garimto81/claude-code-config.git
cd claude-code-config

# 2. Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# 3. Run tests
pytest tests/ -v

# 4. Test validation scripts
bash scripts/validate-phase-0.sh 9999
```

---

## Release Process

**For maintainers only:**

```bash
# 1. Update VERSION
vim .claude/VERSION

# 2. Update CHANGELOG.md
vim CHANGELOG.md

# 3. Commit and tag
git commit -m "chore: Release vX.Y.Z"
git tag -a vX.Y.Z -m "Release vX.Y.Z"

# 4. Push
git push origin master --tags
```

---

## Questions?

- **General**: Open a GitHub Discussion
- **Bugs**: Create an Issue
- **Security**: Email maintainer privately

---

## Recognition

Contributors will be:
- Listed in CHANGELOG.md
- Credited in relevant documentation
- Recognized in release notes

Thank you for contributing! 🎉

---

**Maintainer**: 바이브 코더 (garimto81)
**License**: MIT
**Last Updated**: 2025-01-19
