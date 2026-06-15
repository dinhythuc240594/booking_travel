
from sqlalchemy.orm import Session
import database as db
from service.booking_service import BookingService
from datetime import datetime, timedelta


class BookingModel:
    """Model class management Bookings"""
    
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_combo_booking(
        self, 
        user_id: int, hotel_id: int, nights: int, 
        tour_id: int, persons: int, adults: int, children: int,
        payment_method_str: str,
        check_in_date: datetime,
        total_price: float,
        check_out_date: datetime
    ) -> bool:
        """
        Create booking follow combo API. 
        Note: BookingService trả về boolean (True/False) cho giao dịch này.
        """
        # Convert string to Enum payment method
        payment_method = db.PaymentMethod.from_string(payment_method_str)
        if not payment_method:
            payment_method = db.PaymentMethod.CREDIT_CARD # Default fallback

        success = BookingService.create_combo_booking({
                    "user_id": user_id,
                    "booking_type": db.BookingType.TOUR,
                    # "hotel_id": hotel_id,
                    # "nights": nights,
                    "tour_id": tour_id,
                    "persons": persons,
                    "adults": adults,
                    "children": children,
                    "payment_method": payment_method,
                    "check_in_date": check_in_date,
                    "check_out_date": check_out_date,
                    "total_price": total_price,
                    "booking_status": db.BookingStatus.PENDING
                })

        return success

    def get_by_id(self, booking_id: int) -> db.Bookings:
        """Đọc thông tin Bookings qua ID"""
        return BookingService.get_booking_by_id(booking_id)

    def get_latest_by_user_id(self, user_id: int) -> db.Bookings:
        """Đọc thông tin Bookings qua User ID"""
        return BookingService.get_latest_booking_by_id(user_id)

    def get_by_user_id(self, user_id: int) -> list:
        """Đọc thông tin Bookings qua User ID"""
        return BookingService.get_bookings_by_user_id(user_id)

    def update_status(self, booking_id: int, new_status: db.BookingStatus) -> bool:
        """Cập nhật trạng thái Bookings (VD: từ pending sang completed)"""
        return BookingService.update_booking_status(booking_id, new_status)

    def cancel_booking(self, booking_id: int) -> bool:
        """Hủy Bookings (Soft logic)"""
        return BookingService.cancel_booking(booking_id)

    def get_booking_status(self):
        """Lấy số lượng booking theo trạng thái"""
        return BookingService.get_booking_status()

    def get_bookings_statistics(self, start_date) -> dict:
        """Lấy tất cả thống kê đặt tour sử dụng Command Pattern"""
        from command.booking import GetBookingsStatisticsCommand
        cmd = GetBookingsStatisticsCommand(start_date)
        cmd.execute(self.db)
        return cmd.result

    def _booking_to_dict(self, booking: db.Bookings):
        # Lấy thông tin tour để hiển thị đẹp ở frontend
        tour_title = None
        tour_image = None
        tour_slug = None
        if booking.booking_type == db.BookingType.TOUR:
            tour = self.db.query(db.Tour).get(booking.reference_id)
            if tour:
                tour_title = tour.title
                tour_image = tour.thumbnail
                tour_slug = tour.slug

        # Lấy thông tin thanh toán (nếu có)
        payment_method = None
        payment_status = None

        payment = self.db.query(db.Payment).filter(db.Payment.booking_id == booking.booking_id).first()
        if payment:
            payment_method = payment.payment_method.value if payment.payment_method else None
            payment_status = payment.payment_status.value if payment.payment_status else None

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
            'adults': booking.adults,
            'children': booking.children,
            
            # Map sang các trường React frontend tương thích
            'tourId': booking.reference_id if booking.booking_type == db.BookingType.TOUR else None,
            'tourTitle': tour_title,
            'tourImage': tour_image,
            'tourSlug': tour_slug,
            'departureDate': booking.check_in_date.strftime('%Y-%m-%d') if booking.check_in_date else None,
            'status': booking.booking_status.value if booking.booking_status else None,
            'payment_method': payment_method,
            'payment_status': payment_status,
        }
        return booking_dict