
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from datetime import datetime
from typing import List, Optional
import database as db
from booking_service import BookingService
from tour_service import TourService
from user_service import UserService
import utils
from related_service import RelatedService

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import database as db


class UserModel:
    """Model class management User"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_by_username(self, username: str) -> Optional[db.User]:
        """Get user follow username"""
        return self.db.query(db.User).filter(db.User.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[db.User]:
        """Get user follow email"""
        return self.db.query(db.User).filter(db.User.email == email).first()
    
    def get_by_id(self, user_id: int) -> Optional[db.User]:
        """Get user follow ID"""
        return UserService.get_user_by_id(user_id)
    
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
    
    def authenticate(self, username: str, password: str) -> Optional[db.User]:
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


class BookingModel:
    """Model class management Bookings"""
    
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_combo_booking(self, user_id: int, hotel_id: int, nights: int, tour_id: int, persons: int, payment_method_str: str) -> bool:
        """
        Create booking follow combo API. 
        Note: BookingService trả về boolean (True/False) cho giao dịch này.
        """
        # Convert string to Enum payment method
        payment_method = db.PaymentMethodEnum.from_string(payment_method_str)
        if not payment_method:
            payment_method = db.PaymentMethodEnum.credit_card # Default fallback

        success = BookingService.create_combo_booking(
            user_id=user_id, 
            hotel_id=hotel_id, 
            nights=nights,
            tour_id=tour_id, 
            persons=persons, 
            payment_method=payment_method
        )
        return success

    def get_by_id(self, booking_id: int) -> Optional[db.Bookings]:
        """Đọc thông tin Bookings qua ID"""
        return BookingService.get_booking_by_id(booking_id)

    def update_status(self, booking_id: int, new_status: db.BookingStatusEnum) -> bool:
        """Cập nhật trạng thái Bookings (VD: từ pending sang completed)"""
        return BookingService.update_booking_status(booking_id, new_status)

    def cancel_booking(self, booking_id: int) -> bool:
        """Hủy Bookings (Soft logic)"""
        return BookingService.cancel_booking(booking_id)


class TourModel:
    """Model class quản lý Tour du lịch, sử dụng Command & Composite Pattern"""
    
    def __init__(self, db_session: Session):
        self.db = db_session

    def create(self, location_id: int, name: str, description: str, duration_days: int, price_per_person: float) -> bool:
        """
        Tạo Tour mới thông qua Command Pattern để đảm bảo an toàn giao dịch.
        """
        success = TourService.create_tour(
            location_id=location_id, 
            name=name, 
            description=description, 
            duration_days=duration_days, 
            price_per_person=price_per_person
        )

        return success


    def update_price(self, tour_id: int, new_price: float) -> bool:
        """
        Cập nhật giá Tour sử dụng Command Pattern (hỗ trợ Undo nếu có lỗi chuỗi).
        """
        success = TourService.update_tour_price(tour_id=tour_id, new_price=new_price)
        return success

    def get_tours_by_location_tree(self, location_id: int) -> Optional[Dict[str, Any]]:
        """
        Lấy danh sách Tour theo Địa điểm dưới dạng Cây (Composite Pattern),
        kèm theo tổng số lượng Tour.
        """

        return TourService.get_tours_by_location_tree(location_id=location_id)

    def get_by_id(self, tour_id: int) -> Optional[db.Tour]:
        """Đọc thông tin một Tour cụ thể qua ID"""
        return self.db.query(db.Tour).filter(db.Tour.tour_id == tour_id).first()
    
    def get_all(self, limit: int = 20, offset: int = 0) -> List[db.Tour]:
        """Lấy danh sách tất cả các Tour (có phân trang)"""
        return self.db.query(db.Tour).order_by(db.Tour.tour_id.desc()).limit(limit).offset(offset).all()
    
    def delete(self, tour_id: int) -> bool:
        """Xóa cứng một Tour"""
        tour = self.get_by_id(tour_id)
        if not tour:
            return False
        try:
            self.db.delete(tour)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Lỗi khi xóa Tour: {e}")
            return False

    def get_public_tours(self, limit: int = 20, offset: int = 0) -> List[db.Tour]:
        """Lấy danh sách Tour công khai (is_published=True) có phân trang"""
        return self.db.query(db.Tour).filter(db.Tour.is_published == True).order_by(db.Tour.tour_id.desc()).limit(limit).offset(offset).all()

    def search_tour(self, keyword: str, page: int = 1, per_page: int = 10) -> List[db.Tour]:
        """Tìm kiếm Tour theo từ khóa trên tên và mô tả, có phân trang"""
        offset = (page - 1) * per_page
        return self.db.query(db.Tour).filter(
            db.Tour.is_published == True,
            or_(
                db.Tour.name.ilike(f'%{keyword}%'),
                db.Tour.description.ilike(f'%{keyword}%')
            )
        ).order_by(db.Tour.tour_id.desc()).limit(per_page).offset(offset).all()


class RelatedActivityModel:
    """Model class management Related user activities (History, Saved, Viewed)"""
    
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_booking_history(self, user_id: int) -> List[db.Bookings]:
        """
        Lấy toàn bộ lịch sử Bookings của một người dùng kèm theo chi tiết thanh toán
        """
        return RelatedService.get_user_booking_history(user_id)

    def save_tour(self, user_id: int, tour_id: int) -> bool:
        """
        Chức năng 'Yêu thích/Lưu lại' Tour
        """
        return RelatedService.save_tour_for_later(user_id, tour_id)

    def record_tour_view(self, user_id: int, tour_id: int) -> None:
        """
        Ghi nhận lịch sử xem Tour của người dùng
        """
        RelatedService.record_viewed_tour(user_id, tour_id)


