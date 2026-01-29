from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

class OMCSkill(Enum):
    RALPLAN = "oh-my-claudecode:ralplan"
    ULTRAWORK = "oh-my-claudecode:ultrawork"
    RALPH = "oh-my-claudecode:ralph"
    ARCHITECT = "oh-my-claudecode:architect"
    REVIEW = "oh-my-claudecode:review"
    BUILD_FIX = "oh-my-claudecode:build-fix"

class ModelTier(Enum):
    HAIKU = "haiku"
    SONNET = "sonnet"
    OPUS = "opus"

@dataclass
class AgentConfig:
    agent_type: str
    model: ModelTier
    prompt: str
    background: bool = False

@dataclass
class AgentResult:
    agent_type: str
    success: bool
    output: str
    error: Optional[str] = None

@dataclass
class PlanResult:
    success: bool
    plan_path: str
    iterations: int
    consensus_reached: bool

@dataclass
class ExecutionResult:
    success: bool
    completed_tasks: List[str]
    failed_tasks: List[str]
    agents_spawned: int

@dataclass
class RalphResult:
    success: bool
    iterations: int
    architect_approved: bool
    final_status: str

@dataclass
class VerificationResult:
    approved: bool
    feedback: str
    issues: List[str]


class OMCBridge:
    """OMC 스킬 및 에이전트 호출 브리지"""

    # 커맨드 → OMC 에이전트 매핑
    COMMAND_AGENT_MAP: Dict[str, tuple] = {
        "/debug": ("architect", ModelTier.OPUS),
        "/check --fix": ("build-fixer", ModelTier.SONNET),
        "/check --security": ("security-reviewer", ModelTier.OPUS),
        "/issue fix": ("executor", ModelTier.SONNET),
        "/pr auto": ("code-reviewer", ModelTier.OPUS),
        "/tdd": ("tdd-guide", ModelTier.SONNET),
        "/research": ("researcher", ModelTier.SONNET),
        "/audit quick": ("explore", ModelTier.HAIKU),
    }

    def get_agent_for_command(self, command: str) -> Optional[AgentConfig]:
        """커맨드에 적합한 OMC 에이전트 반환"""
        if command in self.COMMAND_AGENT_MAP:
            agent_type, model = self.COMMAND_AGENT_MAP[command]
            return AgentConfig(
                agent_type=f"oh-my-claudecode:{agent_type}",
                model=model,
                prompt=""  # 호출 시 설정
            )
        return None

    def build_task_call(self, agent_config: AgentConfig) -> str:
        """Task tool 호출 코드 생성"""
        return f'''Task(
    subagent_type="{agent_config.agent_type}",
    model="{agent_config.model.value}",
    prompt="""{agent_config.prompt}""",
    run_in_background={str(agent_config.background).lower()}
)'''

    def build_ralplan_call(self, task_description: str) -> str:
        """Ralplan 호출 코드 생성"""
        return f'''Task(
    subagent_type="oh-my-claudecode:planner",
    model="opus",
    prompt="""다음 작업에 대한 구현 계획을 수립하세요:

{task_description}

계획 수립 후 Architect와 합의를 진행합니다."""
)'''

    def build_ultrawork_call(self, tasks: List[str]) -> str:
        """Ultrawork 병렬 실행 호출 코드 생성"""
        task_list = "\n".join(f"- {t}" for t in tasks)
        return f'''# Ultrawork 병렬 실행
# 다음 작업들을 병렬로 실행:
{task_list}

# 독립적인 작업들은 병렬 Task 호출
Task(subagent_type="oh-my-claudecode:executor", model="sonnet", prompt="...")
Task(subagent_type="oh-my-claudecode:executor", model="sonnet", prompt="...")
'''

    def build_architect_verify_call(self, task_summary: str) -> str:
        """Architect 검증 호출 코드 생성"""
        return f'''Task(
    subagent_type="oh-my-claudecode:architect",
    model="opus",
    prompt="""다음 구현이 완료되었는지 검증하세요:

{task_summary}

검증 항목:
1. 원래 요청을 완전히 충족하는가?
2. 명백한 버그가 있는가?
3. 누락된 엣지 케이스가 있는가?
4. 코드 품질이 수용 가능한가?

APPROVED 또는 REJECTED 중 하나로 응답하세요."""
)'''


# 편의 함수
def get_omc_bridge() -> OMCBridge:
    return OMCBridge()


if __name__ == "__main__":
    bridge = OMCBridge()

    # 커맨드 → 에이전트 매핑 테스트
    config = bridge.get_agent_for_command("/debug")
    print(f"Agent for /debug: {config}")

    # Ralplan 호출 코드 생성
    print(bridge.build_ralplan_call("로그인 기능 구현"))
