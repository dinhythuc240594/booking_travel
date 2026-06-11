
import datetime

from command.component import DatabaseCommand
from database import User


class UserCommand(DatabaseCommand):

    """Lệnh tạo User mới từ Admin Panel"""
    def __init__(self, user_data: dict):
        self.data = user_data
        self.user_record = None

    def execute(self, session) -> None:
        self.user_record = User(**self.data)
        session.add(self.user_record)
        session.flush()

    def undo(self, session) -> None:
        if self.user_record:
            session.delete(self.user_record)


class ToggleUserStatusCommand(DatabaseCommand):

    """Lệnh Khóa/Mở Khóa User"""
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.user_record = None

    def execute(self, session) -> None:
        self.user_record = session.query(User).get(self.user_id)
        if self.user_record:
            self.user_record.is_active = not self.user_record.is_active
            self.user_record.updated_at = datetime.datetime.utcnow()
            session.flush()

    def undo(self, session) -> None:
        if self.user_record:
            self.user_record.is_active = not self.user_record.is_active