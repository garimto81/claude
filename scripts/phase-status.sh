#!/bin/bash
# Phase Status Dashboard
# Usage: bash scripts/phase-status.sh [PRD_NUM]

PRD_NUM=$1

if [ -z "$PRD_NUM" ]; then
  echo "Usage: $0 <PRD_NUMBER>"
  echo "Example: $0 0001"
  exit 1
fi

echo "======================================================================"
echo "Phase Status Dashboard - PRD-${PRD_NUM}"
echo "======================================================================"

# Phase 0: PRD
echo ""
echo "Phase 0: Requirements (PRD)"
PRD_FILE=$(ls tasks/prds/${PRD_NUM}-prd-*.md 2>/dev/null | head -1)
if [ -n "$PRD_FILE" ]; then
  LINES=$(wc -l < "$PRD_FILE" 2>/dev/null || echo "0")
  echo "   [DONE] $PRD_FILE (${LINES} lines)"
else
  echo "   [TODO] Create PRD in tasks/prds/${PRD_NUM}-prd-*.md"
fi

# Phase 0.5: Task List
echo ""
echo "Phase 0.5: Task Generation"
TASK_FILE=$(ls tasks/${PRD_NUM}-tasks-*.md 2>/dev/null | head -1)
if [ -n "$TASK_FILE" ]; then
  TOTAL=$(grep -c "\[ \]" "$TASK_FILE" 2>/dev/null || echo "0")
  DONE=$(grep -c "\[x\]" "$TASK_FILE" 2>/dev/null || echo "0")
  PROGRESS=$((TOTAL + DONE))
  if [ "$PROGRESS" -gt 0 ]; then
    PCT=$((DONE * 100 / PROGRESS))
    echo "   [DONE] $TASK_FILE (${DONE}/${PROGRESS} tasks, ${PCT}%)"
  else
    echo "   [DONE] $TASK_FILE (no tasks)"
  fi
else
  echo "   [TODO] Generate task list: tasks/${PRD_NUM}-tasks-*.md"
fi

# Phase 1: Implementation
echo ""
echo "Phase 1: Implementation"
if [ -d "src" ]; then
  SRC_COUNT=$(find src -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" \) ! -name "__init__.py" 2>/dev/null | wc -l)
  echo "   [IN PROGRESS] ${SRC_COUNT} implementation files"
else
  echo "   [TODO] Create src/ directory and implement features"
fi

# Phase 2: Testing
echo ""
echo "Phase 2: Testing"
if [ -d "tests" ]; then
  TEST_COUNT=$(find tests -type f \( -name "test_*.py" -o -name "*.test.ts" -o -name "*.test.js" \) 2>/dev/null | wc -l)
  echo "   [IN PROGRESS] ${TEST_COUNT} test files"

  # Run tests if available
  if command -v pytest &> /dev/null && [ -f "pytest.ini" ]; then
    if pytest tests/ > /dev/null 2>&1; then
      echo "   [PASS] All tests passing"
    else
      echo "   [FAIL] Some tests failing"
    fi
  elif command -v npm &> /dev/null && [ -f "package.json" ]; then
    if npm test > /dev/null 2>&1; then
      echo "   [PASS] All tests passing"
    else
      echo "   [FAIL] Some tests failing"
    fi
  fi
else
  echo "   [TODO] Create tests/ directory and write tests"
fi

# Phase 3: Versioning
echo ""
echo "Phase 3: Semantic Versioning"
LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "none")
if [ "$LATEST_TAG" != "none" ]; then
  echo "   [DONE] Latest tag: $LATEST_TAG"
else
  echo "   [TODO] Create version tag (e.g., git tag -a v1.0.0)"
fi

# Phase 4: Git + PR
echo ""
echo "Phase 4: Git + Auto PR"
BRANCH=$(git branch --show-current)
if [[ "$BRANCH" =~ ^feature/PRD- ]]; then
  echo "   [IN PROGRESS] Current branch: $BRANCH"

  # Check if PR exists
  if command -v gh &> /dev/null; then
    PR_NUM=$(gh pr list --head "$BRANCH" --json number --jq '.[0].number' 2>/dev/null)
    if [ -n "$PR_NUM" ]; then
      echo "   [DONE] PR #$PR_NUM created"
    else
      echo "   [TODO] Push to create PR"
    fi
  fi
else
  echo "   [TODO] Create feature branch (feature/PRD-${PRD_NUM}-name)"
fi

# Phase 5: E2E & Security
echo ""
echo "Phase 5: E2E & Security Testing"
E2E_EXISTS=false
if [ -f "playwright.config.ts" ] || [ -f "cypress.config.ts" ]; then
  echo "   [IN PROGRESS] E2E framework configured"
  E2E_EXISTS=true
else
  echo "   [TODO] Configure E2E testing (Playwright/Cypress)"
fi

# Phase 6: Deployment
echo ""
echo "Phase 6: Deployment"
if [ -f "Dockerfile" ]; then
  echo "   [IN PROGRESS] Dockerfile exists"
else
  echo "   [TODO] Create Dockerfile for deployment"
fi

if [ -f ".env.example" ]; then
  echo "   [DONE] .env.example documented"
else
  echo "   [TODO] Create .env.example"
fi

echo ""
echo "======================================================================"
echo "Next Steps:"
echo "  1. Run validation: bash scripts/validate-phase-X.sh"
echo "  2. View token usage: python scripts/measure-token-usage.py --all"
echo "  3. Check agent quality: python .claude/evolution/scripts/analyze_quality2.py --summary"
echo "======================================================================"
