
from typing import Optional

from flask import jsonify, session
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
import database as db
import datetime
import utils
import json
from booking_service import BookingService
from user_service import UserService
from setting_service import SettingService
from related_service import RelatedService
from tour_admin_service import TourAdminService

class UserModel:
    """Model class management User"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_by_username(self, username: str) -> db.User:
        """Get user follow username"""
        return self.db.query(db.User).filter(db.User.username == username).first()
    
    def get_by_email(self, email: str) -> db.User:
        """Get user follow email"""
        return self.db.query(db.User).filter(db.User.email == email).first()
    
    def get_by_id(self, user_id: int) -> db.User:
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

    def create_tour(self, data_dict: dict) -> db.Tour:

        # Gọi Service thực thi (Xử lý Command + File)
        success, message, result_data = TourAdminService.create_tour(data_dict)
        
        if success:
            return {'success': True, 'message': 'Tạo bài viết thành công', 'data': result_data}
        return {'success': False, 'message': 'Tạo bài viết thất bại', 'data': message}


    def edit_tour(self, tour_id: int, data: dict) -> tuple[bool, str]:

        # Gọi Service xử lý Update (Sẽ tự quét file và execute Command)
        success, message = TourAdminService.update_tour(tour_id, data)
        if success:
            return {'success': True, 'message': 'Cập nhật bài viết thành công'}
        return {'success': False, 'message': 'Cập nhật bài viết thất bại'}

    def delete_tour(self, tour_id: int) -> tuple[bool, str]:
        """Xóa bài viết"""
        
        success, message = TourAdminService.delete_tour(tour_id)
        if success:
            return {'success': True, 'message': 'Xóa bài viết thành công'}
        return {'success': False, 'message': 'Xóa bài viết thất bại'}

    def approve_tour(self, tour_id: int, user_id: int) -> tuple[bool, str]:
        """Duyệt bài viết"""
        
        success, message = TourAdminService.api_approved_atour(tour_id, user_id)
        if success:
            return {'success': True, 'message': 'Duyệt bài viết thành công'}
        return {'success': False, 'message': 'Duyệt bài viết thất bại'}

    def reject_tour(self, tour_id: int, user_id: int, reason: str = None) -> tuple[bool, str]:
        """Từ chối bài viết"""
        
        success, message = TourAdminService.api_rejected_atour(tour_id, user_id, reason)
        if success:
            return {'success': True, 'message': 'Từ chối bài viết thành công'}
        return {'success': False, 'message': 'Từ chối bài viết thất bại'}


    # ==========================================
    # CÁC API QUẢN LÝ USER (Đã dọn dẹp)
    # ==========================================

    def user_toggle_status(self, user_id: int):
        # Sử dụng Command Pattern
        data = TourAdminService.user_toggle_status(user_id)
        if data['success'] == True:
            return True, "Cập nhật thành công"
        return False, "Không thể cập nhật"


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

    def get_by_id(self, booking_id: int) -> db.Bookings:
        """Đọc thông tin Bookings qua ID"""
        return BookingService.get_booking_by_id(booking_id)

    def get_by_user_id(self, user_id: int) -> db.Bookings:
        """Đọc thông tin Bookings qua User ID"""
        return BookingService.get_bookings_by_user_id(user_id)

    def update_status(self, booking_id: int, new_status: db.BookingStatusEnum) -> bool:
        """Cập nhật trạng thái Bookings (VD: từ pending sang completed)"""
        return BookingService.update_booking_status(booking_id, new_status)

    def cancel_booking(self, booking_id: int) -> bool:
        """Hủy Bookings (Soft logic)"""
        return BookingService.cancel_booking(booking_id)

    def _booking_to_dict(self, booking: db.Bookings):
        booking_dict = {
            'id': booking.id,
            'user_id': booking.user_id,
            'tour_id': booking.tour_id,
            'hotel_id': booking.hotel_id,
            'nights': booking.nights,
            'persons': booking.persons,
            'payment_method': booking.payment_method,
            'status': booking.status,
            'created_at': booking.created_at,
            'updated_at': booking.updated_at
        }
        return booking_dict 
        

class TourModel:
    """Model class managers Tours follow OOP"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create(self, title: str, content: str, location_id: int, 
               author_id: int, duration_days: int = 1, 
               price_per_adult: float = 0.0, 
               price_per_child: float = 0.0,
               summary: str = None, thumbnail: str = None, images: str = None,
               slug: str = None, status: db.TourStatus = db.TourStatus.DRAFT) -> db.Tour:
        if slug is None:
            slug = self._generate_slug(title)
        
        tour = db.Tour(
            title=title,
            slug=slug,
            content=content,
            summary=summary,
            thumbnail=thumbnail,
            images=images,
            location_id=location_id,
            author_id=author_id,
            duration_days=duration_days,
            price_per_adult=price_per_adult,
            price_per_child=price_per_child,
            status=status
        )
        self.db.add(tour)
        self.db.commit()
        self.db.refresh(tour)
        return tour
    
    def get_by_id(self, tour_id: int, include_deleted: bool = False) -> db.Tour:
        query = self.db.query(db.Tour).filter(db.Tour.tour_id == tour_id)
        if not include_deleted:
            query = query.filter(db.Tour.is_deleted == False)
        return query.first()
    
    def get_by_slug(self, slug: str) -> db.Tour:
        return self.db.query(db.Tour).filter(
            db.Tour.slug == slug,
            db.Tour.is_deleted == False
        ).first()
    
    def get_by_category_name(self, category_name: str) -> db.Tour:
        if category_name == 'all':
            return self.db.query(db.Tour).filter(
                db.Tour.is_deleted == False
            ).all()
        return self.db.query(db.Tour).filter(
            db.Tour.category_name == category_name,
            db.Tour.is_deleted == False
        ).all()

    def get_all(self, limit: int = None, offset: int = 0, 
                status: db.TourStatus = None, include_deleted: bool = False) -> list[db.Tour]:
        query = self.db.query(db.Tour)
        if not include_deleted:
            query = query.filter(db.Tour.is_deleted == False)
        if status:
            query = query.filter(db.Tour.status == status)
        query = query.order_by(desc(db.Tour.created_at))
        if limit:
            query = query.limit(limit).offset(offset)
        return query.all()

    def get_by_author(self, author_id: int, limit: int = None, offset: int = 0,
                       status: db.TourStatus = None, search: str = None, 
                       include_deleted: bool = False) -> tuple[list[db.Tour], int]:
        query = self.db.query(db.Tour).filter(db.Tour.author_id == author_id) # Sửa từ created_by
        if not include_deleted:
            query = query.filter(db.Tour.is_deleted == False)
        if status:
            query = query.filter(db.Tour.status == status)
        if search:
            like_pattern = f"%{search}%"
            query = query.filter(or_(db.Tour.title.ilike(like_pattern), db.Tour.summary.ilike(like_pattern)))

        total = query.count()
        query = query.order_by(desc(db.Tour.created_at))
        if limit:
            query = query.limit(limit).offset(offset)
        return query.all(), total

    def update(self, tour_id: int, **kwargs) -> db.Tour:
        tour = self.get_by_id(tour_id)
        if not tour:
            return None
        for key, value in kwargs.items():
            if hasattr(tour, key):
                setattr(tour, key, value)
        tour.updated_at = datetime.datetime.utcnow()
        self.db.commit()
        self.db.refresh(tour)
        return tour

    def approve(self, tour_id: int, reviewer_id: int) -> db.Tour:
        return self.update(tour_id, status=db.TourStatus.PUBLISHED, 
                           reviewer_id=reviewer_id, published_at=datetime.datetime.utcnow())
    
    def reject(self, tour_id: int, reviewer_id: int, reason: str = None) -> db.Tour:
        result = self.update(tour_id, status=db.TourStatus.REJECTED, reviewer_id=reviewer_id)
        if result and reason:
            rejection = db.TourRejection(tour_id=tour_id, rejected_by=reviewer_id, reason=reason)
            self.db.add(rejection)
            self.db.commit()
        return result
    
    def delete(self, tour_id: int) -> bool:
        tour = self.get_by_id(tour_id)
        if not tour: return False
        tour.is_deleted = True
        tour.updated_at = datetime.datetime.utcnow()
        self.db.commit()
        return True
    
    def search(self, keyword: str, limit: int = None, offset: int = 0) -> list[db.Tour]:
        like_pattern = f"%{keyword}%"
        query = self.db.query(db.Tour).filter(
            db.Tour.is_deleted == False,
            or_(db.Tour.title.ilike(like_pattern), db.Tour.summary.ilike(like_pattern))
        ).order_by(desc(db.Tour.created_at))
        if limit:
            query = query.limit(limit).offset(offset)
        return query.all()

    def get_public_tours(self, limit: int = None, offset: int = 0) -> list[db.Tour]:
        query = self.db.query(db.Tour).filter(
            db.Tour.status == db.TourStatus.PUBLISHED,
            db.Tour.is_deleted == False
        ).order_by(desc(db.Tour.created_at))
        if limit:
            query = query.limit(limit).offset(offset)
        return query.all()

    def _tour_to_dict(self, tour: db.Tour, adult: int = 1, children: int = 0) -> dict:
        
        # Parse images JSON string nếu có
        images_list = []
        if tour.images:
            try:
                images_list = json.loads(tour.images)
            except:
                pass

        return {
            "tour_id": tour.tour_id,
            "location_id": tour.location_id,
            "title": tour.title,
            "slug": tour.slug,
            "summary": tour.summary,
            "content": tour.content,
            "duration_days": tour.duration_days,
            "price_per_adult": float(tour.price_per_adult)* (adult),
            "price_per_child": float(tour.price_per_child)* (children),
            "total_price": float(tour.price_per_adult)* (adult) + float(tour.price_per_child)* (children),
            "thumbnail": tour.thumbnail,
            "images": images_list, # Trả về list thay vì chuỗi JSON string
            "is_hot": tour.is_hot,
            "is_featured": tour.is_featured,
            "view_count": tour.view_count,
            "status": tour.status.value if tour.status else None, # Lấy giá trị của Enum
            # Convert DateTime -> String
            "published_at": tour.published_at.strftime('%Y-%m-%d %H:%M:%S') if tour.published_at else None,
            "created_at": tour.created_at.strftime('%Y-%m-%d %H:%M:%S') if tour.created_at else None,
            
            # Nếu muốn lấy thêm thông tin từ bảng liên kết (Relationship)
            "author_name": tour.author.username if tour.author else None,
            "location_name": tour.location.city if getattr(tour, 'location', None) else None
        }


    def _generate_slug(self, title: str) -> str:
        import re
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')


class RelatedActivityModel:
    """Model class management Related user activities (History, Saved, Viewed)"""
    
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_booking_history(self, user_id: int) -> list:
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


class SettingModel:
    """Model quản lý cấu hình hệ thống"""
    
    def __init__(self, db_session):
        self.db = db_session

    def get_all_settings(self, category: str = None) -> dict:
        """Đọc toàn bộ setting (Hỗ trợ lọc theo category)"""
        return SettingService.get_settings_grouped(category)

    def update_settings(self, data_dict: dict) -> bool:
        """Cập nhật nhiều setting cùng lúc"""
        return SettingService.bulk_update(data_dict)


class LocationModel:

    """Model quản lý location"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def create_location_bulk(self, locations: list) -> bool:
        """Tạo nhiều location cùng lúc"""
        return RelatedService.create_location_bulk(locations)

    def update_location(self, location: dict) -> db.Location:
        """Cập nhật thông tin location"""
        if not location:
            return False
        location_id = location.get('location_id')
        if not location_id:
            return False
        location_obj = self.db.query(db.Location).filter(db.Location.location_id == location_id).first()
        if not location_obj:
            return False
        
        for attr in location:
            if hasattr(location_obj, attr):
                setattr(location_obj, attr, location[attr])
                
        location_obj.updated_at = datetime.datetime.utcnow()
        self.db.commit()
        self.db.refresh(location_obj)
        return True

    def delete_location(self, location_id: int) -> bool:
        """Xóa thông tin location"""
        if not location_id:
            return False
        location = self.db.query(db.Location).filter(db.Location.location_id == location_id).first()
        if not location:
            return False
        self.db.delete(location)
        self.db.commit()
        return True

    def get_by_id(self, location_id: int) -> db.Location:
        """Get location follow ID"""
        return RelatedService.get_location_by_id(location_id)

    def get_location(self, is_popular=False, limit=25, offset=0) -> list[db.Location]:
        """Get all location"""
        query = self.db.query(db.Location).filter(db.Location.is_deleted == False)
        if is_popular:
            query = query.filter(db.Location.is_popular == True)
        query = query.order_by(desc(db.Location.created_at))
        if limit:
            query = query.limit(limit).offset(offset)
        return query.all()

    def get_location_by_name(self, name: str) -> db.Location:
        """Get location follow name"""
        if not name:
            return None
        name_like = f"%{name}%"
        return self.db.query(db.Location).filter(db.Location.name.like(name_like)).first()

    def _location_to_dict(self, location: db.Location) -> dict:
        """Convert Location object to dictionary"""
        return {
            "location_id": location.location_id,
            "name": location.name,
            "city": location.city,
            "country": location.country,
            "is_deleted": location.is_deleted,
            "created_at": location.created_at,
            "updated_at": location.updated_at,
            "toursCount": self.count_location_by_name_popular(location.location_id),
            "image_url": location.image_url,
        }

    def count_location_by_name_popular(self, location_id: int) -> int:
        """Get count location follow name and is popular"""
        count_tour = self.db.query(db.Tour).filter(
            db.Tour.location_id == location_id,
            db.Tour.status == db.TourStatus.PUBLISHED
        ).count()
        return count_tour

    