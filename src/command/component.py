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
            # Chạy undo logic cho các command đã execute thành công từ dưới lên trên
            for command in reversed(self._history):
                command.undo(session)
            
            # Commit các trạng thái Rollback (như Hủy/Hoàn tiền) xuống DB
            session.commit()
            raise e # Ném lỗi ra ngoài cho Controller/Service xử lý