

from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
import database as db
import utils
from service.user_service import UserService
from service.tour_admin_service import TourAdminService
from service.tour_client_service import TourClientService


class UserModel:
    """Model class management User"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def authenticate(self, username: str, password: str) -> db.User:
        """
        Valid user with username and password
        
        Args:
            username: username or password
            password: password
            
        Returns:
            User object if true, None if wrong
        """
        
        # Try username first
        user = self.get_by_username(username)
        
        # If not found, try email
        if not user:
            user = self.get_by_email(username)
        
        # Check account locked before check password
        if user and not user.is_active:
            return None  # account locked, deny sign-in
        
        if user and user.is_active and utils.verify_password(user.password_hash, password):
            return user
        
        return None

    def get_by_username(self, username: str) -> db.User:
        """Get user follow username"""
        return self.db.query(db.User).filter(db.User.username == username).first()
    
    def get_by_email(self, email: str) -> db.User:
        """Get user follow email"""
        return self.db.query(db.User).filter(db.User.email == email).first()
    
    def get_by_id(self, user_id: int) -> db.User:
        """Get user follow ID"""
        return UserService.get_user_by_id(user_id)

    def is_locked_user(self, username: str) -> bool:
        """
        check account locked
        
        Args:
            username: user name or email
            
        Returns:
            True nếu if locked, else False
        """
        # Try username first
        user = self.get_by_username(username)
        
        # If not found, try email
        if not user:
            user = self.get_by_email(username)
        
        if user and not user.is_active:
            return True
        
        return False

    def create(self, username: str, email: str, password: str, 
               full_name: str = None, phone: str = None, 
               role: db.UserRole = db.UserRole.CUSTOMER) -> db.User:
        """
        Create new user
        
        Args:
            username: user name
            email: Email
            password: Password hashed
            full_name: Get full name
            phone: Phone
            role: Role (default is CUSTOMER)
            
        Returns:
            User object
        """

        user = UserService.create_user(
                username=username,
                email=email,
                password_hash=password,
                full_name=full_name if full_name else None,
                phone_number=phone,
                role=role
            )

        return user

class AdminModel(UserModel):
    
    def update(self, user_id: int, data: dict) -> db.User:
        """
        Update user
        
        Args:
            user_id: User ID
            data: Data to update
            
        Returns:
            User object
        """
        return UserService.update_user(user_id, data)

    def create_tour(self, data_dict: dict) -> db.Tour:

        # Gọi Service thực thi (Xử lý Command + File)
        tour_id = TourAdminService.create_tour(data_dict)
        if tour_id:
            return {'success': True, 'message': 'Tạo bài viết thành công', 'tour_id': tour_id}
        return {'success': False, 'message': 'Tạo bài viết thất bại', 'tour_id': None}

    def edit_tour(self, tour_id: int, data: dict) -> dict:

        # Gọi Service xử lý Update (Sẽ tự quét file và execute Command)
        success, message, tour_record = TourAdminService.update_tour(tour_id, data)
        if success:
            return {'success': True, 'message': 'Cập nhật bài viết thành công', 'data': tour_record}
        return {'success': False, 'message': 'Cập nhật bài viết thất bại', 'data': None}

    def delete_tour(self, tour_id: int) -> dict:
        """Xóa bài viết"""
        
        success, message, tour_record = TourAdminService.delete_tour(tour_id)
        if success:
            return {'success': True, 'message': 'Xóa bài viết thành công', 'data': tour_record}
        return {'success': False, 'message': 'Xóa bài viết thất bại', 'data': None}

    def approve_tour(self, tour_id: int, user_id: int) -> dict:
        """Duyệt bài viết"""
        
        success, message, tour_record = TourAdminService.api_approved_atour(tour_id, user_id)
        if success:
            return {'success': True, 'message': 'Duyệt bài viết thành công', 'data': tour_record}
        return {'success': False, 'message': 'Duyệt bài viết thất bại', 'data': None}

    def reject_tour(self, tour_id: int, user_id: int, reason: str = None) -> dict:
        """Từ chối bài viết"""
        
        success, message, tour_record = TourAdminService.api_rejected_atour(tour_id, user_id, reason)
        if success:
            return {'success': True, 'message': 'Từ chối bài viết thành công', 'data': tour_record}
        return {'success': False, 'message': 'Từ chối bài viết thất bại', 'data': None}

    def statistics_editor(self, user_id: int):
        """Thống kê bài viết"""
        
        data = TourClientService.api_statistics_editor(user_id)
        if data:
            return {'success': True, 'data': data}
        return {'success': False, 'message': 'Thống kê bài viết thất bại'}

    # ==========================================
    # CÁC API QUẢN LÝ USER (Đã dọn dẹp)
    # ==========================================

    def user_toggle_status(self, user_id: int):
        # Sử dụng Command Pattern
        data = TourAdminService.user_toggle_status(user_id)
        if data['success'] == True:
            return True, "Cập nhật thành công"
        return False, "Không thể cập nhật"


class CustomerModel(UserModel):
    pass


