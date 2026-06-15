from command.component import DatabaseCommand
from database import (
    Bookings, 
    BookingStatus, 
)
from datetime import datetime


class CreateBookingCommand(DatabaseCommand):

    """Lệnh tạo Booking (Hotel hoặc Tour) cho Khách hàng"""
    def __init__(self, data: dict):
        self.data = data
        self.booking_record = None

        self.user_id = data.get('user_id')
        self.booking_type = data.get('booking_type')
        self.reference_id = data.get('reference_id')
        self.check_in_date = data.get('check_in_date')
        self.check_out_date = data.get('check_out_date')
        self.persons = data.get('persons')
        self.adults = data.get('adults')
        self.children = data.get('children')
        self.total_price = data.get('total_price')

    def execute(self, session) -> None:
        self.booking_record = Bookings(
            user_id=self.user_id,
            booking_type=self.booking_type,
            reference_id=self.reference_id,
            check_in_date=self.check_in_date,
            check_out_date=self.check_out_date,
            persons=self.persons,
            adults=self.adults,
            children=self.children,
            total_price=self.total_price,
            booking_status=BookingStatus.PENDING
        )
        session.add(self.booking_record)
        session.flush()

    def undo(self, session) -> None:
        if self.booking_record:
            self.booking_record.booking_status = BookingStatus.CANCELLED


class GetBookingsStatisticsCommand(DatabaseCommand):
    """Lệnh lấy thống kê bookings không sử dụng hàm func"""
    def __init__(self, start_date=None):
        self.start_date = start_date
        self.result = {}

    def execute(self, session) -> None:
        # Lấy tất cả bookings
        bookings = session.query(Bookings).all()
        
        total_bookings = len(bookings)
        total_revenue = 0.0
        pending_count = 0
        confirmed_count = 0
        completed_count = 0
        cancelled_count = 0
        
        for b in bookings:
            status = b.booking_status
            if status == BookingStatus.PENDING:
                pending_count += 1
            elif status == BookingStatus.CONFIRMED:
                confirmed_count += 1
                total_revenue += float(b.total_price or 0)
            elif status == BookingStatus.COMPLETED:
                completed_count += 1
                total_revenue += float(b.total_price or 0)
            elif status == BookingStatus.CANCELLED:
                cancelled_count += 1

        # Tính dữ liệu biểu đồ xu hướng 7 ngày gần nhất
        daily_dict = {}
        if self.start_date:
            for b in bookings:
                if b.created_at and b.created_at >= self.start_date:
                    d_str = b.created_at.date().strftime('%Y-%m-%d')
                    if d_str not in daily_dict:
                        daily_dict[d_str] = {'count': 0, 'revenue': 0.0}
                    daily_dict[d_str]['count'] += 1
                    if b.booking_status in [BookingStatus.CONFIRMED, BookingStatus.COMPLETED]:
                        daily_dict[d_str]['revenue'] += float(b.total_price or 0)

        # Lấy 5 Bookings gần nhất
        sorted_bookings = sorted(
            [b for b in bookings if b.created_at is not None],
            key=lambda x: x.created_at,
            reverse=True
        )
        recent_bookings = sorted_bookings[:5]
        
        self.result = {
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'pending_count': pending_count,
            'confirmed_count': confirmed_count,
            'completed_count': completed_count,
            'cancelled_count': cancelled_count,
            'daily_dict': daily_dict,
            'recent_bookings': recent_bookings
        }

    def undo(self, session) -> None:
        pass