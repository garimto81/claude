# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
