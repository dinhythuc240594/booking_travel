
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, TypeDecorator
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
import enum
import datetime

from config import envConfig as ecf


class Base(DeclarativeBase):
    pass


class TourStatus(enum.Enum):

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


class UserRole(enum.Enum):
    
    ADMIN = "admin"
    EDITOR = "editor"
    USER = "user"

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
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    avatar = Column(String(255), nullable=True)  # URL to avatar image
    role = Column(UserRoleType(), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    
    # Relationships
    created_news = relationship("News", foreign_keys="News.created_by", back_populates="creator")
    approved_news = relationship("News", foreign_keys="News.approved_by", back_populates="approver")
    saved_news = relationship("SavedNews", back_populates="user", cascade="all, delete-orphan")
    viewed_news = relationship("ViewedNews", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")


class Tours(Base):
    """table tours"""
    __tablename__ = 'tours'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    thumbnail = Column(String(255), nullable=True)
    images = Column(Text, nullable=True)  # JSON array of image URLs
    
    # Foreign keys
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Author info (for API articles)
    author = Column(String(255), nullable=True)
    
    # Status and visibility
    status = Column(TourStatusType(), default=TourStatus.DRAFT)
    is_featured = Column(Boolean, default=False)
    is_hot = Column(Boolean, default=False)
    is_api = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    
    # SEO
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    meta_keywords = Column(String(255), nullable=True)
    
    is_deleted = Column(Boolean, default=False)
    tags_string = Column(Text, nullable=True)
    
    # Timestamps
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    
    # Relationships
    category = relationship("Category", back_populates="tours")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_tours")
    approver = relationship("User", foreign_keys=[approved_by], back_populates="approved_tours")


class SavedTours(Base):
    """table saved tours of user"""
    __tablename__ = 'saved_tours'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    tour_id = Column(Integer, ForeignKey('tours.id'), nullable=True)
    site = Column(String(10), default='vn')
    created_at = Column(DateTime, default=datetime.datetime.now())
    
    # Relationships
    user = relationship("User", back_populates="saved_tours")
    tour = relationship("Tours", foreign_keys=[tour_id])


class ViewedTours(Base):
    """table viewed tours of user"""
    __tablename__ = 'viewed_tours'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    tour_id = Column(Integer, ForeignKey('tours.id'), nullable=True)
    site = Column(String(10), default='vn')
    viewed_at = Column(DateTime, default=datetime.datetime.now())
    
    # Relationships
    user = relationship("User", back_populates="viewed_tours")
    tour = relationship("Tours", foreign_keys=[tour_id])


class NewsletterSubscription(Base):
    """table register newsletter"""
    __tablename__ = 'newsletter_subscriptions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    unsubscribe_token = Column(String(255), nullable=False, unique=True)
    subscribed_at = Column(DateTime, default=datetime.datetime.now())
    unsubscribed_at = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class PasswordResetToken(Base):
    """table save token reset password"""
    __tablename__ = 'password_reset_tokens'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class ToursRejection(Base):
    """table save tours has been reject"""
    __tablename__ = 'tours_rejections'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tour_id = Column(Integer, ForeignKey('tours.id'), nullable=False)
    rejected_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    
    # Relationships
    tour = relationship("Tour", foreign_keys=[tour_id])
    rejector = relationship("User", foreign_keys=[rejected_by])


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