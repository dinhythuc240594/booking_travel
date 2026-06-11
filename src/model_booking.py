
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
from tour_client_service import TourClientService


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
        # Lấy thông tin tour để hiển thị đẹp ở frontend
        tour_title = None
        tour_image = None
        if booking.booking_type == db.BookingTypeEnum.TOUR:
            tour = self.db.query(db.Tour).get(booking.reference_id)
            if tour:
                tour_title = tour.title
                tour_image = tour.thumbnail

        booking_dict = {
            'id': booking.booking_id,
            'user_id': booking.user_id,
            'booking_type': booking.booking_type.value if booking.booking_type else None,
            'reference_id': booking.reference_id,
            'check_in_date': booking.check_in_date.strftime('%Y-%m-%d') if booking.check_in_date else None,
            'check_out_date': booking.check_out_date.strftime('%Y-%m-%d') if booking.check_out_date else None,
            'total_price': float(booking.total_price) if booking.total_price else 0.0,
            'booking_status': booking.booking_status.value if booking.booking_status else None,
            'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M:%S') if booking.created_at else None,
            
            # Map sang các trường React frontend tương thích
            'tourId': booking.reference_id if booking.booking_type == db.BookingTypeEnum.TOUR else None,
            'tourTitle': tour_title,
            'tourImage': tour_image,
            'departureDate': booking.check_in_date.strftime('%Y-%m-%d') if booking.check_in_date else None,
            'status': booking.booking_status.value if booking.booking_status else None,
        }
        return booking_dict