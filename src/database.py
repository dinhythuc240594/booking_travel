
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, TypeDecorator, Numeric
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
import enum
import datetime

from config import envConfig as ecf


class Base(DeclarativeBase):
    pass


class ArticleStatusEnum(enum.Enum):
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


class ArticleStatus(enum.Enum):

    DRAFT = "draft"
    PENDING = "pending"
    PUBLISHED = "published"
    HIDDEN = "hidden"
    REJECTED = "rejected"

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


class ArticleStatusType(TypeDecorator):
    """Custom type decorator for ArticleStatus enum"""
    impl = String(20)
    cache_ok = True
    
    def __init__(self):
        super(ArticleStatusType, self).__init__(length=20)
    
    def process_bind_param(self, value, dialect):
        """Convert enum to string when saving to database"""
        if value is None:
            return None
        if isinstance(value, ArticleStatus):
            return value.value
        if isinstance(value, str):
            return value
        return str(value)
    
    def process_result_value(self, value, dialect):
        """Convert string to enum when reading from database"""
        if value is None:
            return None
        if isinstance(value, ArticleStatus):
            return value
        # Convert string to enum
        if isinstance(value, str):
            # Try to find enum by value
            value_lower = value.lower()
            for status in ArticleStatus:
                if status.value.lower() == value_lower:
                    return status
            # If not found, try ArticleStatus.from_string
            result = ArticleStatus.from_string(value)
            if result:
                return result
        # If all else fails, return None or raise error
        return None


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


class BookingTypeEnum(enum.Enum):
    HOTEL = "hotel"
    TOUR = "tour"

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


class BookingStatusEnum(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"

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


class PaymentMethodEnum(enum.Enum):
    credit_card = "credit_card"
    paypal = "paypal"
    bank_transfer = "bank_transfer"
    cash = "cash"

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


class PaymentStatusEnum(enum.Enum):
    pending = "pending"
    successful = "successful"
    failed = "failed"
    refunded = "refunded"

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
    full_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    avatar = Column(String(255), nullable=True)  # URL to avatar image
    role = Column(UserRoleType(), default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())


class Customer(User):

    # Relationships Customer
    bookings = relationship("Bookings", back_populates="user", cascade="all, delete-orphan")
    newsletter_subscriptions = relationship("NewsletterSubscription", back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")


class Admin(User):
    pass


class Writer(User):

    writer_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    bio = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    social_links = Column(Text, nullable=True)  # JSON string containing social media links

    # Relationships Writer
    articles_authored = relationship("Article", foreign_keys="[Article.author_id]", back_populates="author")
    articles_reviewed = relationship("Article", foreign_keys="[Article.reviewer_id]", back_populates="reviewer")
    articles_approved = relationship("Article", foreign_keys="[Article.approved_by]", back_populates="approver")
    saved_articles = relationship("SavedArticles", back_populates="user", cascade="all, delete-orphan")
    viewed_articles = relationship("ViewedArticles", back_populates="user", cascade="all, delete-orphan")


class TourLocation(Base):
    __tablename__ = 'tour_locations'
    
    location_id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    slug = Column(String(255), nullable=False, unique=True)
    is_deleted = Column(Boolean, default=False)
    is_published = Column(Boolean, default=True)
    status = Column(Enum(ArticleStatusEnum), default=ArticleStatusEnum.DRAFT)

    # Relationships
    hotels = relationship("Hotels", back_populates="location", cascade="all, delete")
    tour = relationship("Tour", back_populates="location", cascade="all, delete")


class Hotels(Base):
    __tablename__ = 'hotels'
    
    hotel_id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey('tour_locations.location_id', ondelete="SET NULL"))
    name = Column(String(150), nullable=False)
    star_rating = Column(Integer)
    price_per_night = Column(Numeric(10, 2), nullable=False)
    address = Column(String(255))

    # Relationships
    location = relationship("TourLocation", back_populates="hotels")


class Tour(Base):
    """table tour"""
    __tablename__ = 'tour'
    
    tour_id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey('tour_locations.location_id', ondelete="SET NULL"))
    slug = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    duration_days = Column(Integer, nullable=False)
    is_published = Column(Boolean, default=False)
    status = Column(TourStatusType(), default=TourStatus.DRAFT)
    is_deleted = Column(Boolean, default=False)
    price_per_person = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())

    location = relationship("TourLocation", back_populates="tour")


class Bookings(Base):
    __tablename__ = 'bookings'
    
    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    booking_type = Column(Enum(BookingTypeEnum), nullable=False)
    reference_id = Column(Integer, nullable=False) # Chứa ID của Hotels hoặc Tour
    check_in_date = Column(DateTime)
    check_out_date = Column(DateTime)
    total_price = Column(Numeric(10, 2), nullable=False)
    booking_status = Column(Enum(BookingStatusEnum), default=BookingStatusEnum.pending)
    created_at = Column(DateTime, default=datetime.datetime.now)

    # Relationships
    user = relationship("User", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking", cascade="all, delete-orphan")


class Payment(Base):
    __tablename__ = 'payments'
    
    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey('bookings.booking_id', ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(Enum(PaymentMethodEnum), nullable=False)
    payment_status = Column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.pending)
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

###### Bảng thẻ tag chung cho cả bài viết và tour, nếu cần có thể tách riêng ra 2 bảng Article ######

class Article(Base):
    __tablename__ = 'article'
    
    article_id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('users.user_id', ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(ArticleStatusEnum), default=ArticleStatusEnum.DRAFT)
    category_id = Column(Integer, ForeignKey('article_categories.category_id', ondelete="SET NULL"), nullable=True) 
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    summary = Column(String(500), nullable=True)
    slug = Column(String(255), nullable=False, unique=True)
    is_deleted = Column(Boolean, default=False)
    is_published = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    updated_by = Column(Integer, ForeignKey('users.user_id', ondelete="SET NULL"), nullable=True)
    published_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey('users.user_id'), nullable=True)

    author = relationship("User", foreign_keys=[author_id], back_populates="articles_authored")
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="articles_reviewed")
    category = relationship("ArticleCategory", back_populates="article")
    comments = relationship("ArticleComment", back_populates="article", cascade="all, delete-orphan")
    tags = relationship("ArticleTag", secondary="article_tag_links", backref="article")
    approver = relationship("User", foreign_keys=[approved_by], back_populates="articles_approved")


class ArticleRejection(Base):
    """table save article has been rejected"""
    __tablename__ = 'article_rejections'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey('article.article_id'), nullable=False)
    rejected_by = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    
    # Relationships
    article = relationship("Article", foreign_keys=[article_id])
    rejector = relationship("User", foreign_keys=[rejected_by])


class ArticleCategory(Base):

    __tablename__ = 'article_categories'
    
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey('article_categories.category_id'), nullable=True)
    visible = Column(Boolean, default=True)
    order_display = Column(Integer, default=0)  # Thuộc tính để sắp xếp danh mục trong menu
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # Relationships
    parent = relationship("ArticleCategory", remote_side=[category_id], backref="children")
    article = relationship("Article", back_populates="category")


class ArticleTag(Base):
    """Bảng thẻ tag cho bài viết"""
    __tablename__ = 'article_tags'
    
    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    slug = Column(String(50), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.now)


class ArticleTagLink(Base):
    """Bảng trung gian N-N giữa Article và Tag"""
    __tablename__ = 'article_tag_links'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey('article.article_id', ondelete="CASCADE"), nullable=False)
    tag_id = Column(Integer, ForeignKey('article_tags.tag_id', ondelete="CASCADE"), nullable=False)


class ArticleComment(Base):
    """Bảng bình luận cho bài viết"""
    __tablename__ = 'article_comments'
    
    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey('article.article_id', ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey('article_comments.comment_id', ondelete="CASCADE"), nullable=True)
    
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    article = relationship("Article", back_populates="comments")
    parent = relationship("ArticleComment", remote_side=[comment_id], backref="replies")


class SavedArticles(Base):
    """table saved article of user"""
    __tablename__ = 'saved_articles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    tour_id = Column(Integer, ForeignKey('tour.tour_id'), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    
    # Relationships
    user = relationship("User", back_populates="saved_articles")
    tour = relationship("Tour", foreign_keys=[tour_id])


class ViewedArticles(Base):
    """table viewed article of user"""
    __tablename__ = 'viewed_articles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    tour_id = Column(Integer, ForeignKey('tour.tour_id'), nullable=True)
    viewed_at = Column(DateTime, default=datetime.datetime.now())

    # Relationships
    user = relationship("User", back_populates="viewed_articles")
    tour = relationship("Tour", foreign_keys=[tour_id])


# Database connection
_engine = None
_SessionLocal = None

def get_database_url():
    """get URL connect database in config"""
    from flask import current_app
    try:
        return current_app.config.get('DATABASE_URL', ecf.DATABASE_URL)
    except RuntimeError:
        # if haven't Flask app context, using value default
        import os
        return os.environ.get('DATABASE_URL', ecf.DATABASE_URL)

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