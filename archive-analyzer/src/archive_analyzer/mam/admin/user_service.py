"""
Worker F: User Service

사용자 관리

🔒 규칙:
- users 테이블만 수정 가능
- core/interfaces.py의 IUserService 구현
"""

from archive_analyzer.core.interfaces import IUserService, User


class UserService(IUserService):
    """사용자 관리 서비스"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def get_user(self, user_id: str) -> User | None:
        """사용자 조회"""
        # TODO: 구현
        raise NotImplementedError

    async def get_user_by_email(self, email: str) -> User | None:
        """이메일로 사용자 조회"""
        # TODO: 구현
        raise NotImplementedError

    async def create_user(self, email: str, **kwargs) -> User:
        """사용자 생성"""
        # TODO: 구현
        raise NotImplementedError

    async def update_user_role(self, user_id: str, role: str) -> bool:
        """역할 변경"""
        # TODO: 구현
        raise NotImplementedError

    async def list_users(self) -> list[User]:
        """사용자 목록"""
        # TODO: 구현
        raise NotImplementedError
