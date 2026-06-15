
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, TypeDecorator, Numeric, Date
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
import enum
import datetime

from config import envConfig as ecf


class Base(DeclarativeBase):
    pass


class TourStatus(enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"

    def __str__(self):
        return self.value
    
    @classmethod
    def from_string(cls, value):
        """Convert string to TourStatus enum"""
        if value is None:
            return None
        if isinstance(value, cls):
            return value
        try:
            # Try to get enum by value
            for status in cls:
                if status.value == value:
                    return status
        except (ValueError, AttributeError):
            pass
        return None


class TourStatusType(TypeDecorator):
    """Custom type decorator for TourStatus enum"""
    impl = String(20)
    cache_ok = True
    
    def __init__(self):
        super(TourStatusType, self).__init__(length=20)
    
    def process_bind_param(self, value, dialect):
        """Convert enum to string when saving to database"""
        if value is None:
            return None
        if isinstance(value, TourStatus):
            return value.value
        if isinstance(value, str):
            return value
        return str(value)
    
    def process_result_value(self, value, dialect):
        """Convert string to enum when reading from database"""
        if value is None:
            return None
        if isinstance(value, TourStatus):
            return value
        # Convert string to enum
        if isinstance(value, str):
            # Try to find enum by value
            value_lower = value.lower()
            for status in TourStatus:
                if status.value.lower() == value_lower:
                    return status
            # If not found, try TourStatus.from_string
            result = TourStatus.from_string(value)
            if result:
                return result
        # If all else fails, return None or raise error
        return None


class BookingType(enum.Enum):
    TOUR = "tour"
    HOTEL = "hotel"

    def __str__(self):
        return self.value
    
    @classmethod
    def from_string(cls, value):
        """Convert string to TourStatus enum"""
        if value is None:
            return None
        if isinstance(value, cls):
            return value
        try:
            # Try to get enum by value
            for status in cls:
                if status.value == value:
                    return status
        except (ValueError, AttributeError):
            pass
        return None


class BookingTypeType(TypeDecorator):
    """Custom type decorator for TourStatus enum"""
    impl = String(20)
    cache_ok = True
    
    def __init__(self):
        super(BookingTypeType, self).__init__(length=20)
    
    def process_bind_param(self, value, dialect):
        """Convert enum to string when saving to database"""
        if value is None:
            return None
        if isinstance(value, BookingType):
            return value.value
        if isinstance(value, str):
            return value
        return str(value)
    
    def process_result_value(self, value, dialect):
        """Convert string to enum when reading from database"""
        if value is None:
            return None
        if isinstance(value, BookingType):
            return value
        # Convert string to enum
        if isinstance(value, str):
            # Try to find enum by value
            value_lower = value.lower()
            for status in BookingType:
                if status.value.lower() == value_lower:
                    return status
            # If not found, try BookingType.from_string
            result = BookingType.from_string(value)
            if result:
                return result
        # If all else fails, return None or raise error
        return None


class BookingStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

    def __str__(self):
        return self.value
    
    @classmethod
    def from_string(cls, value):
        """Convert string to TourStatus enum"""
        if value is None:
            return None
        if isinstance(value, cls):
            return value
        try:
            # Try to get enum by value
            for status in cls:
                if status.value == value:
                    return status
        except (ValueError, AttributeError):
            pass
        return None


class BookingStatusType(TypeDecorator):
    """Custom type decorator for TourStatus enum"""
    impl = String(20)
    cache_ok = True
    
    def __init__(self):
        super(BookingStatusType, self).__init__(length=20)
    
    def process_bind_param(self, value, dialect):
        """Convert enum to string when saving to database"""
        if value is None:
            return None
        if isinstance(value, BookingStatus):
            return value.value
        if isinstance(value, str):
            return value
        return str(value)
    
    def process_result_value(self, value, dialect):
        """Convert string to enum when reading from database"""
        if value is None:
            return None
        if isinstance(value, BookingStatus):
            return value
        # Convert string to enum
        if isinstance(value, str):
            # Try to find enum by value
            value_lower = value.lower()
            for status in BookingStatus:
                if status.value.lower() == value_lower:
                    return status
            # If not found, try BookingStatus.from_string
            result = TourStatus.from_string(value)
            if result:
                return result
        # If all else fails, return None or raise error
        return None


class PaymentMethod(enum.Enum):
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"

    def __str__(self):
        return self.value
    
    @classmethod
    def from_string(cls, value):
        """Convert string to TourStatus enum"""
        if value is None:
            return None
        if isinstance(value, cls):
            return value
        try:
            # Try to get enum by value
            for status in cls:
                if status.value == value:
                    return status
        except (ValueError, AttributeError):
            pass
        return None


class PaymentMethodType(TypeDecorator):
    """Custom type decorator for PaymentMethod enum"""
    impl = String(20)
    cache_ok = True
    
    def __init__(self):
        super(PaymentMethodType, self).__init__(length=20)
    
    def process_bind_param(self, value, dialect):
        """Convert enum to string when saving to database"""
        if value is None:
            return None
        if isinstance(value, PaymentMethod):
            return value.value
        if isinstance(value, str):
            return value
        return str(value)
    
    def process_result_value(self, value, dialect):
        """Convert string to enum when reading from database"""
        if value is None:
            return None
        if isinstance(value, PaymentMethod):
            return value
        # Convert string to enum
        if isinstance(value, str):
            # Try to find enum by value
            value_lower = value.lower()
            for method in PaymentMethod:
                if method.value.lower() == value_lower:
                    return method
            # If not found, try PaymentMethod.from_string
            result = PaymentMethod.from_string(value)
            if result:
                return result
        # If all else fails, return None or raise error
        return None


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    REFUNDED = "refunded"

    def __str__(self):
        return self.value
    
    @classmethod
    def from_string(cls, value):
        """Convert string to TourStatus enum"""
        if value is None:
            return None
        if isinstance(value, cls):
            return value
        try:
            # Try to get enum by value
            for status in cls:
                if status.value == value:
                    return status
        except (ValueError, AttributeError):
            pass
        return None


class PaymentStatusType(TypeDecorator):
    """Custom type decorator for PaymentStatus enum"""
    impl = String(20)
    cache_ok = True
    
    def __init__(self):
        super(PaymentStatusType, self).__init__(length=20)
    
    def process_bind_param(self, value, dialect):
        """Convert enum to string when saving to database"""
        if value is None:
            return None
        if isinstance(value, PaymentStatus):
            return value.value
        if isinstance(value, str):
            return value
        return str(value)
    
    def process_result_value(self, value, dialect):
        """Convert string to enum when reading from database"""
        if value is None:
            return None
        if isinstance(value, PaymentStatus):
            return value
        # Convert string to enum
        if isinstance(value, str):
            # Try to find enum by value
            value_lower = value.lower()
            for status in PaymentStatus:
                if status.value.lower() == value_lower:
                    return status
            # If not found, try PaymentStatus.from_string
            result = PaymentStatus.from_string(value)
            if result:
                return result
        # If all else fails, return None or raise error
        return None
    

class UserRole(enum.Enum):

    CUSTOMER = "customer"
    ADMIN = "admin"
    STAFF = "staff"

    def __str__(self):
        return self.value

    @classmethod
    def from_string(cls, value):
        """Convert string to UserRole enum"""
        if value is None:
            return None
        if isinstance(value, cls):
            return value
        try:
            # Try to get enum by value
            for role in cls:
                if role.value == value:
                    return role
        except (ValueError, AttributeError):
            pass
        return None


class UserRoleType(TypeDecorator):
    """Custom type decorator for UserRole enum"""
    impl = String(20)
    cache_ok = True
    
    def __init__(self):
        super(UserRoleType, self).__init__(length=20)
    
    def process_bind_param(self, value, dialect):
        """Convert enum to string when saving to database"""
        if value is None:
            return None
        if isinstance(value, UserRole):
            return value.value
        if isinstance(value, str):
            return value
        return str(value)
    
    def process_result_value(self, value, dialect):
        """Convert string to enum when reading from database"""
        if value is None:
            return None
        if isinstance(value, UserRole):
            return value
        # Convert string to enum
        if isinstance(value, str):
            # Try to find enum by value
            value_lower = value.lower()
            for role in UserRole:
                if role.value.lower() == value_lower:
                    return role
            # If not found, try UserRole.from_string
            result = UserRole.from_string(value)
            if result:
                return result
        # If all else fails, return None or raise error
        return None


class User(Base):
    """table user"""
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)

    # extra info
    full_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    avatar = Column(String(255), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    address = Column(String(500), nullable=True)

    role = Column(UserRoleType(), default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    bookings = relationship("Bookings", back_populates="user", cascade="all, delete-orphan")
    newsletter_subscriptions = relationship("NewsletterSubscription", back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")
    tour_authored = relationship("Tour", foreign_keys="[Tour.author_id]", back_populates="author")
    tour_reviewed = relationship("Tour", foreign_keys="[Tour.reviewer_id]", back_populates="reviewer")
    saved_tour = relationship("Savedtour", back_populates="user", cascade="all, delete-orphan")
    viewed_tour = relationship("Viewedtour", back_populates="user", cascade="all, delete-orphan")

class Location(Base):
    __tablename__ = 'locations'
    
    location_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    search_key = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    slug = Column(String(255), nullable=False, unique=True)
    is_deleted = Column(Boolean, default=False)
    is_published = Column(Boolean, default=True)
    status = Column(TourStatusType(), default=TourStatus.DRAFT)
    is_popular = Column(Boolean, default=False)
    image_url = Column(Text, nullable=True)

    # Relationships
    hotels = relationship("Hotels", back_populates="location", cascade="all, delete")
    tour = relationship("Tour", back_populates="location", cascade="all, delete")


class Hotels(Base):
    __tablename__ = 'hotels'
    
    hotel_id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey('locations.location_id', ondelete="SET NULL"))
    name = Column(String(150), nullable=False)
    star_rating = Column(Integer)
    price_per_night = Column(Numeric(15, 2), nullable=False)
    address = Column(String(255))

    # Relationships
    location = relationship("Location", back_populates="hotels")


class Bookings(Base):
    __tablename__ = 'bookings'
    
    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    booking_type = Column(BookingTypeType(), nullable=False)
    reference_id = Column(Integer, nullable=False) # Chứa ID của Hotels hoặc Tour
    check_in_date = Column(DateTime)
    check_out_date = Column(DateTime)
    total_price = Column(Numeric(15, 2), nullable=False)
    booking_status = Column(BookingStatusType(), default=BookingStatus.PENDING)
    created_at = Column(DateTime, default=datetime.datetime.now)
    persons = Column(Integer, default=1)
    adults = Column(Integer, default=1)
    children = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking", cascade="all, delete-orphan")


class Payment(Base):
    __tablename__ = 'payments'
    
    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey('bookings.booking_id', ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(PaymentMethodType(), nullable=False)
    payment_status = Column(PaymentStatusType(), default=PaymentStatus.PENDING)
    payment_date = Column(DateTime, default=datetime.datetime.now)

    # Relationships
    booking = relationship("Bookings", back_populates="payments")


class Tag(Base):
    """Bảng thẻ tag"""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    slug = Column(String(50), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class NewsletterSubscription(Base):
    """table register news letter"""
    __tablename__ = 'newsletter_subscriptions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    unsubscribe_token = Column(String(255), nullable=False, unique=True)
    subscribed_at = Column(DateTime, default=datetime.datetime.now())
    unsubscribed_at = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class PasswordResetToken(Base):
    """table save token reset password"""
    __tablename__ = 'password_reset_tokens'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    token = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class Setting(Base):
    """table setting for system"""
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), nullable=False, unique=True)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # 'api', 'smtp', 'general', etc.
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

###### Bảng thẻ tag chung cho cả bài viết và tour, nếu cần có thể tách riêng ra 2 bảng Tour ######

class Tour(Base):
    """Bảng Tour (Đã đồng bộ hoàn toàn với SQL và Service)"""
    __tablename__ = 'tour'

    tour_id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey('locations.location_id', ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    author_id = Column(Integer, ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('users.user_id', ondelete="SET NULL"), nullable=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    duration_days = Column(Integer, nullable=False, default=1)
    category_name = Column(String(250), nullable=True)
    price_per_adult = Column(Numeric(15, 2), nullable=False, default=0.0)
    price_per_child = Column(Numeric(15, 2), nullable=False, default=0.0)
    discount_price = Column(Numeric(15, 2), nullable=True)

    thumbnail = Column(String(255), nullable=True)
    images = Column(Text, nullable=True)  # JSON Array lưu ảnh
    is_published = Column(Boolean, default=False)
    is_hot = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    slug = Column(String(255), nullable=False, unique=True)
    view_count = Column(Integer, default=0)
    status = Column(TourStatusType(), default=TourStatus.DRAFT)
    is_deleted = Column(Boolean, default=False)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    # Relationships
    author = relationship("User", foreign_keys=[author_id], back_populates="tour_authored", lazy="joined")
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="tour_reviewed", lazy="joined")
    comments = relationship("TourComment", back_populates="tour", cascade="all, delete-orphan")
    location = relationship("Location", back_populates="tour", lazy="joined")


class TourRejection(Base):
    """table save tour has been rejected"""
    __tablename__ = 'tour_rejections'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tour_id = Column(Integer, ForeignKey('tour.tour_id'), nullable=False)
    rejected_by = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    
    # Relationships
    tour = relationship("Tour", foreign_keys=[tour_id])
    rejector = relationship("User", foreign_keys=[rejected_by])


class TourComment(Base):
    """Bảng bình luận cho tour"""
    __tablename__ = 'tour_comments'
    
    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    tour_id = Column(Integer, ForeignKey('tour.tour_id', ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey('tour_comments.comment_id', ondelete="CASCADE"), nullable=True)
    
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    tour = relationship("Tour", back_populates="comments")
    parent = relationship("TourComment", remote_side=[comment_id], backref="replies")


class Savedtour(Base):
    """table saved tour of user"""
    __tablename__ = 'saved_tour'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    tour_id = Column(Integer, ForeignKey('tour.tour_id'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now())

    # Relationships
    user = relationship("User", back_populates="saved_tour")
    tour = relationship("Tour", foreign_keys=[tour_id])


class Viewedtour(Base):
    """table viewed tour of user"""
    __tablename__ = 'viewed_tour'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    tour_id = Column(Integer, ForeignKey('tour.tour_id'), nullable=True)
    viewed_at = Column(DateTime, default=datetime.datetime.now())

    # Relationships
    user = relationship("User", back_populates="viewed_tour")
    tour = relationship("Tour", foreign_keys=[tour_id])


# Database connection
_engine = None
_SessionLocal = None

def get_database_url():
    return ecf.DATABASE_URL
    # """get URL connect database in config"""
    # from flask import current_app
    # try:
    #     return current_app.config.get('DATABASE_URL', ecf.DATABASE_URL)
    # except RuntimeError:
    #     # if haven't Flask app context, using value default
    #     import os
    #     return os.environ.get('DATABASE_URL', ecf.DATABASE_URL)

def create_engine_instance():
    """create engine connect database"""
    global _engine
    if _engine is None:
        _engine = create_engine(get_database_url(), pool_size=20, max_overflow=20, pool_recycle=3600)
    return _engine

def get_session():
    global _SessionLocal
    if _SessionLocal is None:
        engine = create_engine_instance()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal()

def init_db():
    engine = create_engine_instance()
    Base.metadata.create_all(engine)
    
    # Check if discount_price column exists in tour table, and add it if missing
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    try:
        columns = [col['name'] for col in inspector.get_columns('tour')]
        if 'discount_price' not in columns:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE tour ADD COLUMN discount_price DECIMAL(15, 2) NULL"))
                conn.commit()
    except Exception as e:
        print(f"Error checking/adding discount_price column: {e}")

    # Alter column precisions to DECIMAL(15, 2) to prevent out of range errors for VND currency
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE bookings MODIFY COLUMN total_price DECIMAL(15, 2) NOT NULL"))
            conn.execute(text("ALTER TABLE payments MODIFY COLUMN amount DECIMAL(15, 2) NOT NULL"))
            conn.execute(text("ALTER TABLE tour MODIFY COLUMN price_per_adult DECIMAL(15, 2) NOT NULL DEFAULT 0.0"))
            conn.execute(text("ALTER TABLE tour MODIFY COLUMN price_per_child DECIMAL(15, 2) NOT NULL DEFAULT 0.0"))
            conn.execute(text("ALTER TABLE tour MODIFY COLUMN discount_price DECIMAL(15, 2) NULL"))
            conn.execute(text("ALTER TABLE hotels MODIFY COLUMN price_per_night DECIMAL(15, 2) NOT NULL"))
            conn.commit()
            print("Successfully updated database columns to DECIMAL(15, 2)")
    except Exception as e:
        print(f"Error updating column precisions to DECIMAL(15, 2): {e}")