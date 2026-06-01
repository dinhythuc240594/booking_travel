from abc import ABC, abstractmethod
import datetime

from database import (
    TourRejection,
    Setting,
    Bookings, 
    Payment, 
    BookingStatusEnum, 
    User, 
    PaymentStatusEnum,
    TourStatus,
    NewsletterSubscription,
    Tour)

#######
# Command Pattern sẽ quản lý các giao dịch (transactions) thông qua SQLAlchemy Session. 
# Nó giúp lưu dữ liệu xuống bảng Bookings và Payment, đồng thời xử lý undo() bằng cách cập nhật trạng thái 
# (ví dụ: chuyển từ pending sang cancelled hoặc refunded dựa trên Enum của bạn).
#######


class DatabaseCommand(ABC):

    """Interface Command tương tác với SQLAlchemy Session"""
    @abstractmethod
    def execute(self, session) -> None:
        pass

    @abstractmethod
    def undo(self, session) -> None:
        pass


class DBTransactionInvoker:

    """Invoker quản lý transaction. Thực thi và tự động Rollback (Undo) nếu lỗi"""
    def __init__(self):
        self._history = []

    def execute_transaction(self, session, commands: list[DatabaseCommand]):
        try:
            for command in commands:
                command.execute(session)
                self._history.append(command)
            
            session.commit() # Commit tất cả nếu mọi thứ suôn sẻ
            self._history.clear()
            
        except Exception as e:
            # Chạy undo logic cho các command đã execute thành công từ dưới lên trên
            for command in reversed(self._history):
                command.undo(session)
            
            # Commit các trạng thái Rollback (như Hủy/Hoàn tiền) xuống DB
            session.commit()
            raise e # Ném lỗi ra ngoài cho Controller/Service xử lý


class CreateBookingCommand(DatabaseCommand):

    """Lệnh tạo Booking (Hotel hoặc Tour) cho Khách hàng"""
    def __init__(self, user_id: int, booking_type, reference_id: int, total_price: float, check_in_date: datetime = None, check_out_date: datetime = None):
        self.user_id = user_id
        self.booking_type = booking_type # BookingTypeEnum.hotel hoặc tour
        self.reference_id = reference_id
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.total_price = total_price
        self.booking_record = None # Lưu lại record để undo

    def execute(self, session) -> None:
        self.booking_record = Bookings(
            user_id=self.user_id,
            booking_type=self.booking_type,
            reference_id=self.reference_id,
            check_in_date=self.check_in_date,
            check_out_date=self.check_out_date,
            total_price=self.total_price,
            booking_status=BookingStatusEnum.pending
        )
        session.add(self.booking_record)
        session.flush() # Lấy ID tạm thời mà chưa commit hẳn

    def undo(self, session) -> None:
        if self.booking_record:
            # Hủy vé thay vì xóa record (để giữ lịch sử)
            self.booking_record.booking_status = BookingStatusEnum.cancelled


class ProcessPaymentCommand(DatabaseCommand):

    """Lệnh thanh toán cho Booking"""
    def __init__(self, booking_command: CreateBookingCommand, amount: float, payment_method):
        self.booking_command = booking_command
        self.amount = amount
        self.payment_method = payment_method # PaymentMethodEnum
        self.payment_record = None

    def execute(self, session) -> None:
        booking_id = self.booking_command.booking_record.booking_id
        
        self.payment_record = Payment(
            booking_id=booking_id,
            amount=self.amount,
            payment_method=self.payment_method,
            payment_status=PaymentStatusEnum.successful
        )
        session.add(self.payment_record)
        session.flush()
        
        # Cập nhật trạng thái Bookings thành confirmed
        self.booking_command.booking_record.booking_status = BookingStatusEnum.confirmed

    def undo(self, session) -> None:
        if self.payment_record:
            # Đổi trạng thái sang Refunded
            self.payment_record.payment_status = PaymentStatusEnum.refunded


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
    def __init__(self, tour_id: int, approved_by: int):
        self.tour_id = tour_id
        self.approved_by = approved_by
        self.tour_record = None
        self.old_status = None

    def execute(self, session) -> None:
        self.tour_record = session.query(Tour).get(self.tour_id)
        if self.tour_record:
            self.old_status = self.tour_record.status
            self.tour_record.status = TourStatus.PUBLISHED
            self.tour_record.approved_by = self.approved_by
            self.tour_record.published_at = datetime.datetime.utcnow()
            session.flush()

    def undo(self, session) -> None:
        if self.tour_record and self.old_status:
            self.tour_record.status = self.old_status
            self.tour_record.approved_by = None
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
            self.tour_record.approved_by = self.rejected_by
            
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
            self.tour_record.approved_by = None
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
                self.tour_record.reviewer_id = self.reviewer_id
            session.flush()

    def undo(self, session) -> None:
        if self.tour_record and self.old_status:
            self.tour_record.status = self.old_status


class BulkUpdateSettingsCommand(DatabaseCommand):

    """Lệnh cập nhật cấu hình hệ thống (Settings) hàng loạt"""
    def __init__(self, settings_data: dict):
        self.settings_data = settings_data
        self.old_values = {}
        self.newly_created_keys = []

    def execute(self, session) -> None:
        for key, value in self.settings_data.items():
            setting = session.query(Setting).filter(Setting.key == key).first()
            if setting:
                self.old_values[key] = setting.value
                setting.value = value if value else None
                setting.updated_at = datetime.datetime.utcnow()
            else:
                category = 'api' if 'api' in key.lower() or 'token' in key.lower() else ('smtp' if 'mail' in key.lower() or 'smtp' in key.lower() else 'general')
                new_setting = Setting(key=key, value=value if value else None, category=category)
                session.add(new_setting)
                self.newly_created_keys.append(key)
        session.flush()

    def undo(self, session) -> None:
        for key, old_val in self.old_values.items():
            setting = session.query(Setting).filter(Setting.key == key).first()
            if setting:
                setting.value = old_val
        for key in self.newly_created_keys:
            setting = session.query(Setting).filter(Setting.key == key).first()
            if setting:
                session.delete(setting)


class CreateAdminUserCommand(DatabaseCommand):

    """Lệnh tạo User mới từ Admin Panel"""
    def __init__(self, user_data: dict):
        self.data = user_data
        self.user_record = None

    def execute(self, session) -> None:
        self.user_record = User(**self.data)
        session.add(self.user_record)
        session.flush()

    def undo(self, session) -> None:
        if self.user_record:
            session.delete(self.user_record)


class ToggleUserStatusCommand(DatabaseCommand):

    """Lệnh Khóa/Mở Khóa User"""
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.user_record = None

    def execute(self, session) -> None:
        self.user_record = session.query(User).get(self.user_id)
        if self.user_record:
            self.user_record.is_active = not self.user_record.is_active
            self.user_record.updated_at = datetime.datetime.utcnow()
            session.flush()

    def undo(self, session) -> None:
        if self.user_record:
            self.user_record.is_active = not self.user_record.is_active