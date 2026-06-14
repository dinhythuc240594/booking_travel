
from abc import ABC, abstractmethod


class DatabaseCommand(ABC):

    """Interface Command tương tác với SQLAlchemy Session"""
    @abstractmethod
    def execute(self, session) -> None:
        pass

    @abstractmethod
    def undo(self, session) -> None:
        pass


class DBTransactionInvoker:

    """Invoker quản lý transaction. Thực thi và tự động Rollback (Undo) nếu lỗi"""
    def __init__(self):
        self._history = []

    def execute_transaction(self, session, commands: list[DatabaseCommand]):
        try:
            for command in commands:
                command.execute(session)
                self._history.append(command)
            
            session.commit() # Commit tất cả nếu mọi thứ suôn sẻ
            self._history.clear()
            
        except Exception as e:
            # Rollback transaction in the database
            try:
                session.rollback()
            except Exception:
                pass
                
            # Run in-memory undo logic for commands that executed successfully
            for command in reversed(self._history):
                try:
                    command.undo(session)
                except Exception:
                    pass
            
            raise e # Raise original exception for Controller/Service handling