from abc import ABC, abstractmethod
import datetime

from database import (
    Bookings, 
    Payment, 
    BookingStatusEnum, 
    BookingTypeEnum, 
    PaymentMethodEnum, 
    PaymentStatusEnum,
    Article,
    ArticleStatusEnum,
    NewsletterSubscription)

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


class CreateBookingCommand(DatabaseCommand):
    """Lệnh tạo Bookings (Hotels hoặc Tours)"""
    def __init__(self, user_id: int, booking_type, reference_id: int, total_price: float):
        self.user_id = user_id
        self.booking_type = booking_type # BookingTypeEnum.hotel hoặc tour
        self.reference_id = reference_id
        self.total_price = total_price
        self.booking_record = None # Lưu lại record để undo

    def execute(self, session) -> None:
        # Sử dụng model Bookings từ database.py
        self.booking_record = Bookings(
            user_id=self.user_id,
            booking_type=self.booking_type,
            reference_id=self.reference_id,
            total_price=self.total_price,
            booking_status=BookingStatusEnum.pending
        )
        session.add(self.booking_record)
        session.flush() # Lấy ID tạm thời mà chưa commit hẳn
        print(f"✅ Đã tạo Bookings (ID tạm: {self.booking_record.booking_id}) loại {self.booking_type.value}.")

    def undo(self, session) -> None:
        if self.booking_record:
            # Hủy vé thay vì xóa record (lịch sử)
            self.booking_record.booking_status = BookingStatusEnum.cancelled
            print(f"🔄 Đã HỦY Bookings (ID: {self.booking_record.booking_id}). Trạng thái: {BookingStatusEnum.cancelled.value}")


class ProcessPaymentCommand(DatabaseCommand):
    """Lệnh thanh toán cho Bookings"""
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
        
        # Cập nhật trạng thái Bookings thành confirmed
        self.booking_command.booking_record.booking_status = BookingStatusEnum.confirmed
        print(f"💳 Đã thanh toán ${self.amount} qua {self.payment_method.value}. Bookings đã Confirm.")

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


class CreateArticleCommand(DatabaseCommand):
    """Lệnh tạo bài viết mới (Draft)"""
    def __init__(self, author_id: int, category_id: int, title: str, slug: str, content: str):
        self.author_id = author_id
        self.category_id = category_id
        self.title = title
        self.slug = slug
        self.content = content
        self.article_record = None

    def execute(self, session) -> None:
        self.article_record = Article(
            author_id=self.author_id,
            category_id=self.category_id,
            title=self.title,
            slug=self.slug,
            content=self.content,
            status=ArticleStatusEnum.draft
        )
        session.add(self.article_record)
        session.flush()
        print(f"📝 Đã tạo bài viết Nháp: '{self.title}' (ID tạm: {self.article_record.article_id}).")

    def undo(self, session) -> None:
        if self.article_record:
            # Undo việc tạo bài viết có thể là đánh dấu rejected hoặc xóa mềm
            self.article_record.status = ArticleStatusEnum.rejected
            print(f"🔄 Đã HỦY quá trình tạo bài viết (ID: {self.article_record.article_id}). Chuyển sang Rejected.")


class ChangeArticleStatusCommand(DatabaseCommand):
    """Lệnh thay đổi trạng thái bài viết (Duyệt/Xuất bản/Từ chối)"""
    def __init__(self, article_id: int, new_status: ArticleStatusEnum, reviewer_id: int = None):
        self.article_id = article_id
        self.new_status = new_status
        self.reviewer_id = reviewer_id
        self.old_status = None
        self.article_record = None

    def execute(self, session) -> None:
        self.article_record = session.query(Article).get(self.article_id)
        if self.article_record:
            self.old_status = self.article_record.status # Lưu lại trạng thái cũ để undo
            self.article_record.status = self.new_status
            
            if self.reviewer_id:
                self.article_record.reviewer_id = self.reviewer_id
                
            if self.new_status == ArticleStatusEnum.approved:
                self.article_record.published_at = datetime.datetime.now()

            session.flush()
            print(f"✅ Đã chuyển trạng thái bài viết {self.article_id} thành {self.new_status.value}.")

    def undo(self, session) -> None:
        if self.article_record and self.old_status:
            # Khôi phục lại trạng thái cũ trước khi thay đổi
            self.article_record.status = self.old_status
            print(f"🔄 Đã ROLLBACK trạng thái bài viết {self.article_id} về {self.old_status.value}.")


class SubscribeNewsletterCommand(DatabaseCommand):
    """Lệnh đăng ký nhận tin Newsletter"""
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
        print(f"📧 Đã đăng ký Newsletter cho email: {self.email}.")

    def undo(self, session) -> None:
        if self.subscription_record:
            self.subscription_record.is_active = False
            self.subscription_record.unsubscribed_at = datetime.datetime.now()
            print(f"🔄 Đã HỦY đăng ký Newsletter cho email: {self.email}.")