# CLAUDE.md

## 1. 🛑 Critical Instructions (AI Must Read)

### Core Rules
1.  **Language**:
    *   **User-facing**: Korean (한글) - 답변, 문서, 커밋 메시지 설명 등.
    *   **Technical**: English - 코드, 변수명, 기술 용어(GitHub, API 등).
2.  **Path Handling**:
    *   ALWAYS use **Absolute Paths** for file operations.
    *   Verify file existence before reading/writing.
3.  **Validation**:
    *   **NEVER skip validation**. Each phase has a strict validator.
    *   If validation fails, **STOP** and fix the issue. Do not proceed to the next phase.

### Project Context
*   **Root**: `c:\claude\claude-code-config`
*   **Plugin Registry**: `.claude-plugin/registry.json`
*   **Identity**: Meta-workflow system (Not a product codebase).

---

## 2. 🌊 Causal Workflow Pipeline

Follow this pipeline strictly. Each phase is the **Cause** for the next phase's **Effect**.

| Phase | Input (Cause) | Action (Process) | Output (Effect) | Validator (Gatekeeper) |
| :--- | :--- | :--- | :--- | :--- |
| **0** | User Request | **Requirement Analysis**<br>Create PRD with 8 core sections. | `tasks/prds/NNNN-*.md` | `scripts/validate-phase-0.ps1 NNNN` |
| **0.5** | PRD | **Task Breakdown**<br>Convert PRD to actionable tasks. | `tasks/NNNN-tasks-*.md` | `scripts/validate-phase-0.5.ps1 NNNN` |
| **1** | Task List | **Implementation**<br>Write code & 1:1 paired tests. | `src/*`, `tests/*` | `scripts/validate-phase-1.ps1` |
| **2** | Impl Code | **Verification**<br>Run tests & check coverage. | Pass All Tests | `scripts/validate-phase-2.ps1` |
| **2.5** | Verified Code | **Review**<br>Code/Design/Security review. | Review Approval | `/pragmatic-code-review` |
| **3** | Approval | **Versioning**<br>Bump version & update changelog. | `CHANGELOG.md` | `scripts/validate-phase-3.ps1` |
| **4** | Versioned Code | **Git Ops**<br>Commit & Create PR. | Git Commit / PR | `scripts/validate-phase-5.ps1` |
| **5** | PR | **E2E & Security**<br>Full system check. | Security Report | `scripts/validate-phase-5.ps1` |
| **6** | Passed PR | **Deployment**<br>Production release. | Deployed Artifact | `scripts/validate-phase-6.ps1` |

> **Feedback Loop**: If Validation fails, return to the **Action** step of the *current* phase. Do not regress to previous phases unless requirements change.

---

## 3. ⚡ Quick Actions

Select the tool based on your current mode.

### 🧠 Planning (Phase 0 - 0.5)
*   **New Feature**: `/create-prd` → Interactive PRD creation.
*   **Plan Update**: `/aiden-plan` → Update implementation plan.

### 💻 Coding (Phase 1)
*   **TDD Start**: `/tdd` → Generate test boilerplate first.
*   **Bug Fix**: `/fix-issue` → Structured issue resolution.
*   **Refactor**: `/check` → Run quality checks before refactoring.

### ✅ Verifying (Phase 2 - 2.5)
*   **Run Tests**: `pytest tests/ -v`
*   **Code Review**: `/pragmatic-code-review`
*   **UI Review**: `/design-review`

### 🚀 Ops (Phase 3 - 6)
*   **Commit**: `/commit` → Create conventional commit.
*   **Changelog**: `/changelog` → Update changelog.
*   **Analyze**: `/analyze-code` → Generate Mermaid class diagram.

---

## 4. 🛠️ Toolchain Reference

*   **Plugin Manager**: `python scripts/plugin_manager.py`
*   **Universal Validator**: `python scripts/validate_phase_universal.py`
*   **Windows Native**: `scripts/*.ps1` (Preferred on Windows)
*   **Bypass Mode**: `.\start-claude-bypass.bat` (Runs with `--dangerously-skip-permissions`)
