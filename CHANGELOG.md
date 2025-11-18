# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [5.0.0] - 2025-01-18

### Added
- **Phase 2.5: Professional Reviews** - New workflow phase between testing and versioning
  - `/pragmatic-code-review` command - 7-tier hierarchical code review (Opus)
  - `/design-review` command - Playwright MCP-powered design review (Sonnet)
  - `/security-review` command - OWASP Top 10 security audit
  - Formal review workflow integration (Phase 2 → 2.5 → 3)
- **docs/PHASE_AGENT_MAPPING.md** - New comprehensive guide for Phase 3-6 agent selection
  - Detailed agent descriptions (success rates, timing, use cases)
  - Phase-agent summary table
  - Parallel execution strategies
  - Performance metrics
- **docs/AGENT_USAGE_BEST_PRACTICES.md** - New data-driven agent selection guide
  - Testing agents (unit vs E2E vs integration)
  - Implementation agents (debugger, typescript-expert, fullstack-developer)
  - Review & security agents (code-reviewer, pragmatic-code-review, security-auditor)
  - Performance targets table
  - Common mistakes and best practices

### Changed
- **CLAUDE.md** optimized to v5.0.0
  - Reduced from 1,368 lines to ~1,125 lines (35% reduction, ~1,900 tokens saved)
  - Agent-Task Mapping Rules: 96 lines → 27 lines (summary + link)
  - Phase 3-6 Agent Mapping: 194 lines → 20 lines (summary + link)
  - Updated Phase 0-6 cycle diagram to include Phase 2.5
  - Plugin Marketplace section updated (v4.16.0 → v5.0.0)
- **README.md** updated to v5.0.0
  - Added v5.0.0 update section
  - Documented Phase 2.5 workflow
  - Updated development cycle diagram
  - Highlighted 35% token savings

### Improved
- **Documentation Structure**: Modular architecture for better maintainability
  - Main workflow: CLAUDE.md (core concepts + quick reference)
  - Detailed guides: Separate docs for deep dives
  - Reduced duplication across documentation
- **Token Efficiency**: 35% reduction in CLAUDE.md
  - Agent mapping: Moved to dedicated docs
  - Phase-specific details: Separate reference guide
  - Quick reference tables retained in main doc
- **Workflow Clarity**: Phase 2.5 formalizes review process
  - Clear review types (code, design, security)
  - When to use each review type
  - Integration with existing Phase 0-6 cycle

### Technical Details
- **Files Added**: 2 new documentation files
  - `docs/PHASE_AGENT_MAPPING.md` (~120 lines)
  - `docs/AGENT_USAGE_BEST_PRACTICES.md` (~200 lines)
- **Lines Removed**: ~243 lines from CLAUDE.md (moved to dedicated docs)
- **Net Change**: +77 lines total (2 new docs - removed sections)
- **Token Savings**: ~1,900 tokens (35% reduction in CLAUDE.md)

### Breaking Changes
- **Documentation References**: Some internal links updated
  - Agent mapping details now in `docs/AGENT_USAGE_BEST_PRACTICES.md`
  - Phase 3-6 details now in `docs/PHASE_AGENT_MAPPING.md`
  - No workflow changes - only documentation restructuring

### Migration Guide
- **No action required**: Workflow remains backward compatible
- **Optional**: Review new Phase 2.5 workflow for enhanced quality
- **Recommended**: Use `/pragmatic-code-review` before merging PRs

### References
- **Phase 2.5 Documentation**: CLAUDE.md "Phase 2.5: Code & Design Review"
- **Agent Mapping**: docs/PHASE_AGENT_MAPPING.md
- **Best Practices**: docs/AGENT_USAGE_BEST_PRACTICES.md

---

## [4.18.0] - 2025-01-18

### Added
- **Workflow-Reviews Plugin** - Integrated OneRedOak/claude-code-workflows
  - 2 specialized agents for professional code and design reviews
  - `pragmatic-code-review` (Opus, 99 lines) - 7-tier hierarchical review framework
    - Architecture, Functionality, Security, Maintainability, Testing, Performance, Dependencies
    - Principal Engineer reviewer with Pragmatic Quality methodology
  - `design-review` (Sonnet, 107 lines) - Playwright MCP-powered design review
    - 7-phase process: Interaction, Responsiveness, Visual Polish, Accessibility, Robustness, Code Health, Console
    - WCAG 2.1 AA accessibility compliance
  - 3 slash commands for instant reviews
    - `/pragmatic-code-review` (42 lines) - Comprehensive PR code review
    - `/design-review` (38 lines) - UI/UX consistency validation
    - `/security-review` (191 lines) - OWASP Top 10 security audit
- **Plugin Count**: 25 total (24 → 25)
  - 17 wshobson plugins (16 → 17)
  - 8 Phase-based legacy plugins
- **Use Cases**: Professional reviews inspired by Anthropic's own process
  - Automated PR reviews with dual-loop architecture
  - Live environment testing with Playwright MCP
  - High-confidence vulnerability detection (>80% certainty)
  - World-class design standards (Stripe, Airbnb, Linear)

### Changed
- **CLAUDE.md** updated to v4.18.0
  - Added workflow-reviews plugin documentation
  - Updated plugin count (24 → 25)
- **README.md** updated with v4.18.0 highlights
  - Added v4.18.0 update section
  - Documented 2 agents + 3 commands
  - Updated version references and plugin counts
- **marketplace.json** expanded
  - 68 plugins → 69 plugins
  - Added workflow-reviews plugin definition

### Improved
- **Review Automation**: Comprehensive review capabilities
  - 7-tier hierarchical code review (Architecture → Dependencies)
  - 7-phase design review (Interaction → Console)
  - OWASP Top 10 security scanning
  - Playwright MCP integration for live testing
- **Quality Standards**: Industry-leading review methodologies
  - Pragmatic Quality framework (balance speed with standards)
  - WCAG 2.1 AA accessibility compliance
  - High-confidence vulnerability detection
  - Evidence-based feedback with screenshots

### Technical Details
- **Files Added**: 5 files in `.claude/plugins/workflow-reviews/`
  - 2 agents (206 lines total)
  - 3 commands (271 lines total)
- **Total Lines Added**: ~477 lines (review workflow definitions)
- **Source**: OneRedOak/claude-code-workflows
- **Plugin Type**: Professional review workflows
- **Models**: Opus (code review), Sonnet (design review)

### References
- **Source Repository**: https://github.com/OneRedOak/claude-code-workflows
- **Video Tutorials**: Patrick Ellis' YouTube channel
- **Documentation**: CLAUDE.md "Available Plugins" section
- **Installation**: Agents and commands in `.claude/plugins/workflow-reviews/`

---

## [4.17.0] - 2025-01-18

### Added
- **Meta-Development Plugin** - Integrated davila7/claude-code-templates
  - 6 meta agents for building Claude Code components
  - `agent-expert` (476 lines) - Agent development meta guide
  - `command-expert` (420 lines) - Slash command development guide
  - `mcp-expert` (257 lines) - MCP integration development guide
  - `cli-ui-designer` (404 lines) - CLI UI design specialist
  - `docusaurus-expert` (173 lines) - Documentation site specialist
  - `frontend-developer` (32 lines) - Frontend development specialist
- **Plugin Count**: 24 total (23 → 24)
  - 16 wshobson plugins (15 → 16)
  - 8 Phase-based legacy plugins
- **Use Cases**: Claude Code system development and extension
  - Creating new agents for Claude Code
  - Developing custom slash commands
  - Integrating MCP servers
  - Building CLI interfaces
  - Documentation site management

### Changed
- **CLAUDE.md** updated to v4.17.0
  - Added meta-development plugin documentation
  - Updated plugin count (23 → 24)
- **README.md** updated with v4.17.0 highlights
  - Added v4.17.0 update section
  - Documented 6 meta agents
  - Updated version references
- **marketplace.json** expanded
  - 66 plugins → 68 plugins
  - Added meta-development plugin definition

### Improved
- **Meta-Development Capabilities**: Can now develop Claude Code extensions
  - Agent creation with proper YAML frontmatter
  - Command creation with Markdown templates
  - MCP integration with best practices
  - CLI UI design with terminal aesthetics

### Technical Details
- **Files Added**: 6 agent files in `.claude/plugins/meta-development/agents/`
- **Total Lines Added**: ~1,762 lines (agent definitions)
- **Source**: davila7/claude-code-templates
- **Plugin Type**: Meta-development (tools for building tools)

### References
- **Source Repository**: https://github.com/davila7/claude-code-templates
- **Documentation**: CLAUDE.md "Available Plugins" section
- **Installation**: Agents available in `.claude/plugins/meta-development/`

---

## [4.16.0] - 2025-01-18

### Added
- **Plugin Marketplace System** - Integrated wshobson/agents plugin architecture
  - 23 plugins total (15 wshobson + 8 Phase-based legacy)
  - 120+ agents (87 new + 33 existing)
  - 27 skills with progressive disclosure
  - `.claude-plugin/marketplace.json` with 66 plugin definitions
- **10 Slash Commands** from hesreallyhim/awesome-claude-code
  - Git & Version Control (3): `/commit`, `/create-pr`, `/fix-issue`
  - Code Quality (3): `/tdd`, `/check`, `/optimize`
  - Documentation (2): `/create-docs`, `/changelog`
  - Project Management (2): `/create-prd`, `/todo`
- **PRD-0006** documentation
  - `tasks/prds/0006-prd-global-workflow-improvements.md` (253 lines)
  - `tasks/0006-tasks-global-workflow-improvements.md` (189 lines, 17 tasks)

### Changed
- **CLAUDE.md** updated to v4.16.0
  - Plugin system architecture documented
  - Agent count updated (33 → 120+)
  - Token efficiency metrics updated (80-90% → 85-95%)
- **README.md** updated with v4.16.0 highlights
  - Added plugin system section
  - Updated folder structure diagram
  - Added performance metrics

### Improved
- **Token Efficiency**: 85-95% savings (up from 80-90%)
  - Reduced token usage by 62% per conversation
  - Progressive disclosure for 27 skills
  - On-demand loading instead of upfront loading
- **Agent Availability**: +264% increase (33 → 120+ agents)
- **Automation**: 10 slash commands for Phase 0-6 workflow

### Fixed
- `.gitignore` updated to exclude project folders (sso-nextjs, ojt-platform)
- `.gitignore` updated to exclude agent tracking data (.agent-quality-v2.jsonl)

### Technical Details
- **Files Changed**: 176 files
- **Additions**: +54,389 lines
- **Deletions**: -1,225 lines
- **Pull Request**: #21 (merged to master)
- **Branch**: feature/PRD-0006-global-workflow-improvements

### References
- **wshobson/agents**: https://github.com/wshobson/agents
- **awesome-claude-code**: https://github.com/hesreallyhim/awesome-claude-code
- **PRD**: tasks/prds/0006-prd-global-workflow-improvements.md
- **Task List**: tasks/0006-tasks-global-workflow-improvements.md

---

## [4.15.0] - 2025-01-14

### Added
- Agent Evolution System with Langfuse (Phase 1)
- Conversation-First Simplification
  - Task generation via conversation (no API calls)
  - Automatic agent selection (no manual scripts)
  - On-demand agent analysis

### Changed
- Removed unnecessary complexity from workflow
- Simplified task generation process

### Improved
- Developer experience with streamlined workflows
- Reduced setup complexity (no API keys required)

---

## [4.14.0] - 2025-01-14

### Added
- Agent Quality Tracking v2.0 system
- Data-driven agent-task mapping rules
- Performance targets for all agents

### Changed
- Agent selection based on success rate data
- Improved agent-task mapping documentation

---

## [4.13.0] - 2025-01-14

### Added
- PhaseFlow AI task generation system
- Two-Phase task generation process
- Mandatory 1:1 test file pairing

### Changed
- Task generation workflow (parent tasks → sub-tasks)

---

## [4.12.0] - 2025-01-14

### Added
- Initial wshobson/agents plugin system integration (15 agents)
- Plugin marketplace foundation

---

## [4.11.0] - 2025-01-14

### Added
- cc-sdd validation gates integration
- Phase validation scripts (validate-phase-0.sh, validate-phase-0.5.sh)

---

## [4.10.0] - 2025-01-13

### Added
- Global workflow system documentation
- Phase 0-6 development cycle
- 33 core agents

### Changed
- Repository structure to support meta-workflow system

---

## Earlier Versions

See git history for versions prior to v4.10.0.

---

**Maintained By**: Claude Code + garimto81
**Repository**: https://github.com/garimto81/claude-code-config
