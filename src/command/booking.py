from command.component import DatabaseCommand
from database import (
    Bookings, 
    BookingStatusEnum, 
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
        self.total_price = data.get('total_price')

    def execute(self, session) -> None:
        self.booking_record = Bookings(
            user_id=self.user_id,
            booking_type=self.booking_type,
            reference_id=self.reference_id,
            check_in_date=self.check_in_date,
            check_out_date=self.check_out_date,
            total_price=self.total_price,
            booking_status=BookingStatusEnum.PENDING
        )
        session.add(self.booking_record)
        session.flush()

    def undo(self, session) -> None:
        if self.booking_record:
            self.booking_record.booking_status = BookingStatusEnum.CANCELLED