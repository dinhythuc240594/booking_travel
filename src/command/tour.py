from command.component import DatabaseCommand
from command.booking import CreateBookingCommand
import datetime

from database import (
    TourRejection,
    Payment, 
    BookingStatus, 
    PaymentStatus,
    TourStatus,
    NewsletterSubscription,
    Tour)

#######
# Command Pattern sẽ quản lý các giao dịch (transactions) thông qua SQLAlchemy Session. 
# Nó giúp lưu dữ liệu xuống bảng Bookings và Payment, đồng thời xử lý undo() bằng cách cập nhật trạng thái 
# (ví dụ: chuyển từ pending sang cancelled hoặc refunded dựa trên Enum của bạn).
#######


class ProcessPaymentCommand(DatabaseCommand):

    """Lệnh thanh toán cho Booking"""
    def __init__(self, booking_command: CreateBookingCommand, amount: float, payment_method):
        self.booking_command = booking_command
        self.amount = amount
        self.payment_method = payment_method # PaymentMethod
        self.payment_record = None

    def execute(self, session) -> None:
        booking_id = self.booking_command.booking_record.booking_id
        
        self.payment_record = Payment(
            booking_id=booking_id,
            amount=self.amount,
            payment_method=self.payment_method,
            payment_status=PaymentStatus.SUCCESSFUL
        )
        session.add(self.payment_record)
        session.flush()
        
        # Cập nhật trạng thái Bookings thành confirmed
        self.booking_command.booking_record.booking_status = BookingStatus.CONFIRMED

    def undo(self, session) -> None:
        if self.payment_record:
            # Đổi trạng thái sang Refunded
            self.payment_record.payment_status = PaymentStatus.REFUNDED


class ChangetourtatusCommand(DatabaseCommand):

    """Lệnh thay đổi trạng thái bài viết (Duyệt/Xuất bản/Từ chối)"""
    def __init__(self, tour_id: int, new_status: TourStatus, reviewer_id: int = None):
        self.tour_id = tour_id
        self.new_status = new_status
        self.reviewer_id = reviewer_id
        self.old_status = None
        self.tour_record = None

    def execute(self, session) -> None:
        self.tour_record = session.query(Tour).get(self.tour_id)
        if self.tour_record:
            self.old_status = self.tour_record.status # Lưu lại trạng thái cũ để undo
            self.tour_record.status = self.new_status
            
            if self.reviewer_id:
                self.tour_record.reviewer_id = self.reviewer_id
                
            if self.new_status == TourStatus.approved:
                self.tour_record.published_at = datetime.datetime.now()

            session.flush()

    def undo(self, session) -> None:
        if self.tour_record and self.old_status:
            # Khôi phục lại trạng thái cũ trước khi thay đổi
            self.tour_record.status = self.old_status


class SubscribeNewsletterCommand(DatabaseCommand):

    """Lệnh khách hàng đăng ký nhận tin Newsletter"""
    def __init__(self, email: str, unsubscribe_token: str, user_id: int = None):
        self.email = email
        self.unsubscribe_token = unsubscribe_token
        self.user_id = user_id
        self.subscription_record = None

    def execute(self, session) -> None:
        self.subscription_record = NewsletterSubscription(
            email=self.email,
            unsubscribe_token=self.unsubscribe_token,
            user_id=self.user_id,
            is_active=True
        )
        session.add(self.subscription_record)
        session.flush()

    def undo(self, session) -> None:
        if self.subscription_record:
            self.subscription_record.is_active = False
            self.subscription_record.unsubscribed_at = datetime.datetime.utcnow()


class CreateTourCommand(DatabaseCommand):

    """Lệnh tạo Tour du lịch/Bài viết mới"""
    def __init__(self, tour_data: dict):
        self.data = tour_data
        self.tour_record = None

    def execute(self, session) -> None:
        self.tour_record = Tour(**self.data)
        session.add(self.tour_record)
        session.flush()

    def undo(self, session) -> None:
        if self.tour_record:
            session.delete(self.tour_record)


class UpdateTourCommand(DatabaseCommand):

    """Lệnh cập nhật thông tin Tour"""
    def __init__(self, tour_id: int, update_data: dict):
        self.tour_id = tour_id
        self.update_data = update_data
        self.tour_record = None
        self.old_data = {}

    def execute(self, session) -> None:
        self.tour_record = session.query(Tour).get(self.tour_id)
        if self.tour_record:
            for key, value in self.update_data.items():
                if hasattr(self.tour_record, key):
                    self.old_data[key] = getattr(self.tour_record, key) # Lưu lại giá trị cũ
                    setattr(self.tour_record, key, value)
            self.tour_record.updated_at = datetime.datetime.utcnow()
            session.flush()

    def undo(self, session) -> None:
        if self.tour_record and self.old_data:
            # Khôi phục lại từng trường dữ liệu
            for key, value in self.old_data.items():
                setattr(self.tour_record, key, value)


class SoftDeleteTourCommand(DatabaseCommand):

    """Lệnh xóa mềm Tour (Ẩn khỏi hệ thống)"""
    def __init__(self, tour_id: int):
        self.tour_id = tour_id
        self.tour_record = None
        self.was_deleted = False

    def execute(self, session) -> None:
        self.tour_record = session.query(Tour).get(self.tour_id)
        if self.tour_record:
            self.was_deleted = self.tour_record.is_deleted
            self.tour_record.is_deleted = True
            self.tour_record.updated_at = datetime.datetime.utcnow()
            session.flush()

    def undo(self, session) -> None:
        if self.tour_record and not self.was_deleted:
            self.tour_record.is_deleted = False


class ApproveTourCommand(DatabaseCommand):

    """Lệnh Admin duyệt Tour"""
    def __init__(self, tour_id: int, reviewer_id: int):
        self.tour_id = tour_id
        self.reviewer_id = reviewer_id
        self.tour_record = None
        self.old_status = None

    def execute(self, session) -> None:
        self.tour_record = session.query(Tour).get(self.tour_id)
        if self.tour_record:
            self.old_status = self.tour_record.status
            self.tour_record.status = TourStatus.PUBLISHED
            self.tour_record.reviewer_id = self.reviewer_id
            self.tour_record.published_at = datetime.datetime.utcnow()
            session.flush()

    def undo(self, session) -> None:
        if self.tour_record and self.old_status:
            self.tour_record.status = self.old_status
            self.tour_record.reviewer_id = None
            self.tour_record.published_at = None


class RejectTourCommand(DatabaseCommand):

    """Lệnh Admin từ chối Tour (Đổi trạng thái + Ghi log lý do)"""
    def __init__(self, tour_id: int, rejected_by: int, reason: str):
        self.tour_id = tour_id
        self.rejected_by = rejected_by
        self.reason = reason
        self.tour_record = None
        self.rejection_record = None
        self.old_status = None

    def execute(self, session) -> None:
        self.tour_record = session.query(Tour).get(self.tour_id)
        if self.tour_record:
            self.old_status = self.tour_record.status
            self.tour_record.status = TourStatus.REJECTED
            self.tour_record.reviewer_id = self.rejected_by
            
            # Lưu log lý do từ chối
            self.rejection_record = TourRejection(
                tour_id=self.tour_id,
                rejected_by=self.rejected_by,
                reason=self.reason
            )
            session.add(self.rejection_record)
            session.flush()

    def undo(self, session) -> None:
        if self.tour_record and self.old_status:
            self.tour_record.status = self.old_status
            self.tour_record.reviewer_id = None
        if self.rejection_record:
            session.delete(self.rejection_record)


class ChangeTourStatusCommand(DatabaseCommand):

    """Lệnh thay đổi trạng thái tự do (Hỗ trợ Tool Admin)"""
    def __init__(self, tour_id: int, new_status: TourStatus, reviewer_id: int = None):
        self.tour_id = tour_id
        self.new_status = new_status
        self.reviewer_id = reviewer_id
        self.old_status = None
        self.tour_record = None

    def execute(self, session) -> None:
        self.tour_record = session.query(Tour).get(self.tour_id)
        if self.tour_record:
            self.old_status = self.tour_record.status 
            self.tour_record.status = self.new_status
            
            if self.reviewer_id:
                self.tour_record.reviewer_id = self.reviewer_id # Sửa mapping
                
            if self.new_status == TourStatus.PUBLISHED:
                self.tour_record.published_at = datetime.datetime.now()

            session.flush()

    def undo(self, session) -> None:
        if self.tour_record and self.old_status:
            self.tour_record.status = self.old_status