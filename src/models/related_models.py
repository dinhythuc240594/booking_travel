
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
import database as db
import datetime
from service.setting_service import SettingService
from service.related_service import RelatedService


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
            "search_key": location.search_key,
        }

    def count_location_by_name_popular(self, location_id: int) -> int:
        """Get count location follow name and is popular"""
        count_tour = self.db.query(db.Tour).filter(
            db.Tour.location_id == location_id,
            db.Tour.status == db.TourStatus.PUBLISHED
        ).count()
        return count_tour

    def get_all(self, limit: int = None, offset: int = 0) -> list[db.Location]:
        """Get all location"""
        query = self.db.query(db.Location).filter(db.Location.is_deleted == False)
        query = query.order_by(desc(db.Location.created_at))
        if limit:
            query = query.limit(limit).offset(offset)
        return query.all()