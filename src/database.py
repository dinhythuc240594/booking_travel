
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, TypeDecorator
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
import enum
import datetime

from config import envConfig as ecf

DEFAULT_CATEGORIES = [
    {
        'name': 'Công Nghệ',
        'slug': 'cong-nghe',
        'icon': 'phone',
        'order_display': 1,
        'parent_id': None,
    },
    {
        'name': 'Kinh tế',
        'slug': 'kinh-te',
        'icon': 'economy',
        'order_display': 2,
        'parent_id': None,
    },
    {
        'name': 'Thể thao',
        'slug': 'the-thao',
        'icon': 'sports',
        'order_display': 3,
        'parent_id': None,
    },
    {
        'name': 'Giải trí',
        'slug': 'giai-tri',
        'icon': 'entertainment',
        'order_display': 4,
        'parent_id': None,
    },
    {
        'name': 'Giáo dục',
        'slug': 'giao-duc',
        'icon': 'education',
        'order_display': 5,
        'parent_id': None,
    },
    {
        'name': 'Sức khỏe',
        'slug': 'suc-khoe',
        'icon': 'health',
        'order_display': 6,
        'parent_id': None,
    }
]


class Base(DeclarativeBase):
    pass


class NewsStatus(enum.Enum):
    
    DRAFT = "draft"
    PENDING = "pending"
    PUBLISHED = "published"
    HIDDEN = "hidden"
    REJECTED = "rejected"

    def __str__(self):
        return self.value
    
    @classmethod
    def from_string(cls, value):
        """Convert string to NewsStatus enum"""
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


class NewsStatusType(TypeDecorator):
    """Custom type decorator for NewsStatus enum"""
    impl = String(20)
    cache_ok = True
    
    def __init__(self):
        super(NewsStatusType, self).__init__(length=20)
    
    def process_bind_param(self, value, dialect):
        """Convert enum to string when saving to database"""
        if value is None:
            return None
        if isinstance(value, NewsStatus):
            return value.value
        if isinstance(value, str):
            return value
        return str(value)
    
    def process_result_value(self, value, dialect):
        """Convert string to enum when reading from database"""
        if value is None:
            return None
        if isinstance(value, NewsStatus):
            return value
        # Convert string to enum
        if isinstance(value, str):
            # Try to find enum by value
            value_lower = value.lower()
            for status in NewsStatus:
                if status.value.lower() == value_lower:
                    return status
            # If not found, try NewsStatus.from_string
            result = NewsStatus.from_string(value)
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


class Category(Base):
    """Table category news"""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    order_display = Column(Integer, default=0)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    level = Column(Integer, default=1)  # menu level: 1, 2
    visible = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    
    # Relationships
    parent = relationship("Category", remote_side=[id], backref="children")
    news = relationship("News", back_populates="category")


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


class News(Base):
    """table news"""
    __tablename__ = 'news'
    
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
    status = Column(NewsStatusType(), default=NewsStatus.DRAFT)
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
    category = relationship("Category", back_populates="news")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_news")
    approver = relationship("User", foreign_keys=[approved_by], back_populates="approved_news")


class Tag(Base):
    """table tag"""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    slug = Column(String(50), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.now())


class NewsTag(Base):
    """table relationship many-to-many between News and Tag"""
    __tablename__ = 'news_tags'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    news_id = Column(Integer, ForeignKey('news.id'), nullable=False)
    tag_id = Column(Integer, ForeignKey('tags.id'), nullable=False)


class SavedNews(Base):
    """table saved news of user"""
    __tablename__ = 'saved_news'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    news_id = Column(Integer, ForeignKey('news.id'), nullable=True)
    news_international_id = Column(Integer, ForeignKey('news_international.id'), nullable=True)
    site = Column(String(10), default='vn')
    created_at = Column(DateTime, default=datetime.datetime.now())
    
    # Relationships
    user = relationship("User", back_populates="saved_news")
    news = relationship("News", foreign_keys=[news_id])
    news_international = relationship("NewsInternational", foreign_keys=[news_international_id])


class ViewedNews(Base):
    """table viewed news of user"""
    __tablename__ = 'viewed_news'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    news_id = Column(Integer, ForeignKey('news.id'), nullable=True)
    news_international_id = Column(Integer, ForeignKey('news_international.id'), nullable=True)
    site = Column(String(10), default='vn')
    viewed_at = Column(DateTime, default=datetime.datetime.now())
    
    # Relationships
    user = relationship("User", back_populates="viewed_news")
    news = relationship("News", foreign_keys=[news_id])
    news_international = relationship("NewsInternational", foreign_keys=[news_international_id])


class Comment(Base):
    """table comment of user"""
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    news_id = Column(Integer, ForeignKey('news.id'), nullable=True)
    news_international_id = Column(Integer, ForeignKey('news_international.id'), nullable=True)
    content = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey('comments.id'), nullable=True)  # For reply comments
    site = Column(String(10), default='vn')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    
    # Relationships
    user = relationship("User", back_populates="comments")
    news = relationship("News", foreign_keys=[news_id])
    news_international = relationship("NewsInternational", foreign_keys=[news_international_id])
    parent = relationship("Comment", remote_side=[id], backref="replies")


class NewsInternational(Base):
    """table international news"""
    __tablename__ = 'news_international'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    thumbnail = Column(String(255), nullable=True)
    images = Column(Text, nullable=True)  # JSON array of image URLs
    category_id = Column(Integer, ForeignKey('categories_international.id'), nullable=False)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Author info (for API articles)
    author = Column(String(255), nullable=True)
    
    status = Column(NewsStatusType(), default=NewsStatus.DRAFT)
    is_featured = Column(Boolean, default=False)
    is_hot = Column(Boolean, default=False)
    is_api = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    meta_keywords = Column(String(255), nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    
    is_deleted = Column(Boolean, default=False)
    tags_string = Column(Text, nullable=True)

    # Relationships
    category = relationship("CategoryInternational", back_populates="news")
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])


class CategoryInternational(Base):
    """table category international"""
    __tablename__ = 'categories_international'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    order_display = Column(Integer, default=0)
    parent_id = Column(Integer, ForeignKey('categories_international.id'), nullable=True)
    level = Column(Integer, default=1)  # menu level: 1, 2
    visible = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now())
    
    # Relationships
    parent = relationship("CategoryInternational", remote_side=[id], backref="children")
    news = relationship("NewsInternational", back_populates="category")


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


class NewsRejection(Base):
    """table save news has been reject"""
    __tablename__ = 'news_rejections'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    news_id = Column(Integer, ForeignKey('news.id'), nullable=False)
    rejected_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    
    # Relationships
    news = relationship("News", foreign_keys=[news_id])
    rejector = relationship("User", foreign_keys=[rejected_by])


class NewsInternationalRejection(Base):
    """table save international news has been reject"""
    __tablename__ = 'news_international_rejections'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    news_international_id = Column(Integer, ForeignKey('news_international.id'), nullable=False)
    rejected_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now())
    
    # Relationships
    news_international = relationship("NewsInternational", foreign_keys=[news_international_id])
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