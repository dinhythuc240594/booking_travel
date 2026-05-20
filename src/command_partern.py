from abc import ABC, abstractmethod
import datetime

from database import Booking, Payment, BookingStatusEnum, BookingTypeEnum, PaymentMethodEnum, PaymentStatusEnum

#######
# Command Pattern sẽ quản lý các giao dịch (transactions) thông qua SQLAlchemy Session. 
# Nó giúp lưu dữ liệu xuống bảng Booking và Payment, đồng thời xử lý undo() bằng cách cập nhật trạng thái 
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


class CreateBookingCommand(DatabaseCommand):
    """Lệnh tạo Booking (Hotel hoặc Tour)"""
    def __init__(self, user_id: int, booking_type, reference_id: int, total_price: float):
        self.user_id = user_id
        self.booking_type = booking_type # BookingTypeEnum.hotel hoặc tour
        self.reference_id = reference_id
        self.total_price = total_price
        self.booking_record = None # Lưu lại record để undo

    def execute(self, session) -> None:
        # Sử dụng model Booking từ database.py
        self.booking_record = Booking(
            user_id=self.user_id,
            booking_type=self.booking_type,
            reference_id=self.reference_id,
            total_price=self.total_price,
            booking_status=BookingStatusEnum.pending
        )
        session.add(self.booking_record)
        session.flush() # Lấy ID tạm thời mà chưa commit hẳn
        print(f"✅ Đã tạo Booking (ID tạm: {self.booking_record.booking_id}) loại {self.booking_type.value}.")

    def undo(self, session) -> None:
        if self.booking_record:
            # Hủy vé thay vì xóa record (lịch sử)
            self.booking_record.booking_status = BookingStatusEnum.cancelled
            print(f"🔄 Đã HỦY Booking (ID: {self.booking_record.booking_id}). Trạng thái: {BookingStatusEnum.cancelled.value}")


class ProcessPaymentCommand(DatabaseCommand):
    """Lệnh thanh toán cho Booking"""
    def __init__(self, booking_command: CreateBookingCommand, amount: float, payment_method):
        self.booking_command = booking_command
        self.amount = amount
        self.payment_method = payment_method # PaymentMethodEnum
        self.payment_record = None

    def execute(self, session) -> None:
        # Lấy booking_id từ command trước đó
        booking_id = self.booking_command.booking_record.booking_id
        
        self.payment_record = Payment(
            booking_id=booking_id,
            amount=self.amount,
            payment_method=self.payment_method,
            payment_status=PaymentStatusEnum.successful
        )
        session.add(self.payment_record)
        session.flush()
        
        # Cập nhật trạng thái Booking thành confirmed
        self.booking_command.booking_record.booking_status = BookingStatusEnum.confirmed
        print(f"💳 Đã thanh toán ${self.amount} qua {self.payment_method.value}. Booking đã Confirm.")

    def undo(self, session) -> None:
        if self.payment_record:
            # Đổi trạng thái sang Refunded
            self.payment_record.payment_status = PaymentStatusEnum.refunded
            print(f"💸 Đã HOÀN TIỀN (Refunded) thanh toán (ID: {self.payment_record.payment_id}).")


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
            print("🚀 GIAO DỊCH THÀNH CÔNG VÀ ĐƯỢC LƯU VÀO DATABASE!")
            self._history.clear()
            
        except Exception as e:
            print(f"\n❌ LỖI HỆ THỐNG PHÁT SINH: {str(e)}")
            print("⏳ Đang tiến hành Rollback trạng thái qua Undo logic...")
            # Chạy undo logic cho các command đã execute thành công
            for command in reversed(self._history):
                command.undo(session)
            
            # Commit các trạng thái Hủy/Hoàn tiền xuống DB
            session.commit()
            print("✅ Đã xử lý Hủy/Hoàn tiền thành công.")