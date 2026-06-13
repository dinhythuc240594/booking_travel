
from command.user import UserCommand
from database import get_session, User, UserRole
import datetime

class UserService:
    
    @staticmethod
    def create_user(username: str, email: str, password_hash: str, full_name: str = None, phone_number: str = None, role=UserRole.CUSTOMER):
        """Tạo tài khoản người dùng mới"""
        session = get_session()
        try:

            command = UserCommand({
                'username': username,
                'email': email,
                'password_hash': password_hash, 
                'full_name': full_name,
                'phone_number': phone_number,
                'role': role
            })
            command.execute(session)
            session.commit()
            session.refresh(command.user_record)
            return command.user_record
        except Exception as e:
            session.rollback()
            return None
        finally:
            session.close()

    @staticmethod
    def get_user_by_id(user_id: int):
        """Lấy thông tin người dùng theo ID"""
        session = get_session()
        try:
            return session.query(User).filter(User.user_id == user_id).first()
        finally:
            session.close()

    @staticmethod
    def update_user(user_id: int, data_dict):
        """Cập nhật thông tin người dùng"""
        session = get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return False
            
            for key, value in data_dict.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            user.updated_at = datetime.datetime.now()
            session.commit()
            return True
        except Exception as e:
            print(e)
            session.rollback()
            return False
        finally:
            session.close()

    @staticmethod
    def delete_user(user_id: int):
        """Xóa người dùng (Soft delete hoặc Hard delete)"""
        session = get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                session.delete(user) # Hard delete. Nếu soft delete thì set is_active = False
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()