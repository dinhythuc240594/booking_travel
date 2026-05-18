"""
Model classes để quản lý các thao tác thêm, xóa, sửa, lấy dữ liệu của web tin tức
và sử dụng thư viện SQLAlchemy ORM
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_
from datetime import datetime
from typing import List, Optional
import database as db
import utils


class NewsModel:
    """Model class managers News follow OOP"""
    
    def __init__(self, db_session: Session):
        """
        Initialization NewsModel
        
        Args:
            db_session: SQLAlchemy session
        """
        self.db = db_session
    
    def create(self, title: str, content: str, category_id: int, 
               created_by: int, summary: str = None, thumbnail: str = None,
               slug: str = None, status: db.NewsStatus = db.NewsStatus.DRAFT) -> db.News:
        """
        Create news
        
        Args:
            title: Title article
            content: Content article
            category_id: ID category
            created_by: ID creator
            summary: Summary article
            thumbnail: URL avatar
            slug: URL slug (auto generate if None)
            status: Status article
            
        Returns:
            News object
        """
        if slug is None:
            slug = self._generate_slug(title)
        
        news = db.News(
            title=title,
            slug=slug,
            content=content,
            summary=summary,
            thumbnail=thumbnail,
            category_id=category_id,
            created_by=created_by,
            status=status
        )
        
        self.db.add(news)
        self.db.commit()
        self.db.refresh(news)
        return news
    
    def get_by_id(self, news_id: int, include_deleted: bool = False) -> Optional[db.News]:
        """
        Get article follow ID
        
        Args:
            news_id: ID article
            include_deleted: if True, include article deleted (for admin)
        """
        query = self.db.query(db.News).filter(db.News.id == news_id)
        if not include_deleted:
            query = query.filter(db.News.is_deleted == False)
        return query.first()
    
    def get_by_slug(self, slug: str) -> Optional[db.News]:
        """Get article follow slug (instead get article deleted)"""
        return self.db.query(db.News).filter(
            db.News.slug == slug,
            db.News.is_deleted == False
        ).first()
    
    def get_all(self, limit: int = None, offset: int = 0, 
                status: db.NewsStatus = None, include_deleted: bool = False) -> List[db.News]:
        """
        List article
        
        Args:
            limit: amount article
            offset: position start
            status: filter status
            include_deleted: If True, get article deleted (for admin)
            
        Returns:
            List of News objects
        """
        query = self.db.query(db.News)
        
        if not include_deleted:
            query = query.filter(db.News.is_deleted == False)
        
        if status:
            query = query.filter(db.News.status == status)
        
        query = query.order_by(desc(db.News.created_at))
        
        if limit:
            query = query.limit(limit).offset(offset)
        
        return query.all()

    def get_by_creator(
        self,
        creator_id: int,
        limit: int | None = None,
        offset: int = 0,
        status: db.NewsStatus | None = None,
        search: str | None = None,
        include_deleted: bool = False,
    ) -> tuple[list[db.News], int]:
        """
        List article follow creator (editor), support pagging and search.

        Args:
            creator_id: ID creator (editor)
            limit: Amount article for a page
            offset: Position start
            status: Filter status
            search: Keyword / summary
            include_deleted: If True, include article deleted (for admin)

        Returns:
            (items, total) - list article and total
        """
        query = self.db.query(db.News).filter(db.News.created_by == creator_id)

        if not include_deleted:
            query = query.filter(db.News.is_deleted == False)

        if status:
            query = query.filter(db.News.status == status)

        if search:
            like_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    db.News.title.ilike(like_pattern),
                    db.News.summary.ilike(like_pattern),
                )
            )

        # Tính tổng trước khi limit/offset
        total = query.count()

        query = query.order_by(desc(db.News.created_at))

        if limit:
            query = query.limit(limit).offset(offset)

        items = query.all()
        return items, total
    
    def get_published(self, limit: int = None, offset: int = 0) -> List[db.News]:
        """List article published (just only article don't deleted)"""
        return self.get_all(
            limit=limit, 
            offset=offset, 
            status=db.NewsStatus.PUBLISHED
        )
    
    def get_by_category(self, category_id: int, limit: int = None, 
                       offset: int = 0) -> List[db.News]:
        """List article of category (just only article don't deleted)"""
        query = self.db.query(db.News).filter(
            db.News.category_id == category_id,
            db.News.status == db.NewsStatus.PUBLISHED,
            db.News.is_deleted == False
        ).order_by(desc(db.News.created_at))
        
        if limit:
            query = query.limit(limit).offset(offset)
        
        return query.all()
    
    def get_by_categories(
        self,
        category_ids: list[int],
        limit: int | None = None,
        offset: int = 0,
    ) -> list[db.News]:
        """List article of all child category (just only article don't deleted)"""
        if not category_ids:
            return []

        query = (
            self.db.query(db.News)
            .filter(
                db.News.category_id.in_(category_ids),
                db.News.status == db.NewsStatus.PUBLISHED,
                db.News.is_deleted == False,
            )
            .order_by(desc(db.News.created_at))
        )

        if limit:
            query = query.limit(limit).offset(offset)

        return query.all()
    
    def get_featured(self, limit: int = 10) -> List[db.News]:
        """List article is featured (just only article don't deleted)"""
        return self.db.query(db.News).filter(
            db.News.is_featured == True,
            db.News.status == db.NewsStatus.PUBLISHED,
            db.News.is_deleted == False
        ).order_by(desc(db.News.created_at)).limit(limit).all()
    
    def get_hot(self, limit: int = 10) -> List[db.News]:
        """List article is hot (just only article don't deleted)"""
        return self.db.query(db.News).filter(
            db.News.is_hot == True,
            db.News.status == db.NewsStatus.PUBLISHED,
            db.News.is_deleted == False
        ).order_by(desc(db.News.view_count)).limit(limit).all()
    
    def search(self, keyword: str, limit: int = 20) -> List[db.News]:
        """List article by keyword (just only article don't deleted)"""
        return self.db.query(db.News).filter(
            or_(
                db.News.title.ilike(f'%{keyword}%'),
                db.News.content.ilike(f'%{keyword}%'),
                db.News.summary.ilike(f'%{keyword}%')
            ),
            db.News.status == db.NewsStatus.PUBLISHED,
            db.News.is_deleted == False
        ).order_by(desc(db.News.created_at)).limit(limit).all()
    
    def update(self, news_id: int, **kwargs) -> Optional[db.News]:
        """
        Update article
        
        Args:
            news_id: Article ID
            **kwargs: Fields need update
            
        Returns:
            Updated News object or None
        """
        news = self.get_by_id(news_id)
        if not news:
            return None
        
        for key, value in kwargs.items():
            if hasattr(news, key):
                setattr(news, key, value)
        
        news.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(news)
        return news
    
    def approve(self, news_id: int, approved_by: int) -> Optional[db.News]:
        """Article approved"""
        return self.update(
            news_id, 
            status=db.NewsStatus.PUBLISHED,
            approved_by=approved_by,
            published_at=datetime.utcnow()
        )
    
    def reject(self, news_id: int, approved_by: int, reason: str = None) -> Optional[db.News]:
        """
        Article reject
        
        Args:
            news_id: Article ID
            approved_by: ID user rejected
            reason: Content reject
        """
        result = self.update(
            news_id,
            status=db.NewsStatus.REJECTED,
            approved_by=approved_by
        )
        
        # Save content reject of news_rejections
        if result and reason:
            rejection = db.NewsRejection(
                news_id=news_id,
                rejected_by=approved_by,
                reason=reason
            )
            self.db.add(rejection)
            self.db.commit()
        
        return result
    
    def delete(self, news_id: int) -> bool:
        """
        delete article (soft delete) - set is_deleted = True
        """
        news = self.get_by_id(news_id)
        if not news:
            return False
        
        news.is_deleted = True
        news.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def increment_view(self, news_id: int) -> None:
        """increase views"""
        news = self.get_by_id(news_id)
        if news:
            news.view_count += 1
            self.db.commit()
    
    def _generate_slug(self, title: str) -> str:
        """create slug from title"""
        import re
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')


class CategoryModel:
    """Model class management Category"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create(self, name: str, slug: str, parent_id: int = None, 
               description: str = None, icon: str = None) -> db.Category:
        """Create category"""
        category = db.Category(
            name=name,
            slug=slug,
            parent_id=parent_id,
            description=description,
            icon=icon
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category
    
    def get_all(self) -> List[db.Category]:
        """List category"""
        return self.db.query(db.Category).filter(
            db.Category.visible == True
        ).order_by(db.Category.order_display).all()
    
    def get_by_id(self, category_id: int) -> Optional[db.Category]:
        """Get category by ID"""
        return self.db.query(db.Category).filter(db.Category.id == category_id).first()
    
    def get_by_slug(self, slug: str) -> Optional[db.Category]:
        """Get category by slug"""
        return self.db.query(db.Category).filter(db.Category.slug == slug).first()

    def get_descendant_ids(self, parent_id: int) -> list[int]:
        """List id category child (all level) of parent_id."""
        categories = self.db.query(db.Category.id, db.Category.parent_id).filter(
            db.Category.visible == True
        ).all()

        children = []
        stack = [parent_id]
        while stack:
            current = stack.pop()
            for cat_id, cat_parent in categories:
                if cat_parent == current:
                    children.append(cat_id)
                    stack.append(cat_id)

        return children


class UserModel:
    """Model class management User"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_by_username(self, username: str) -> Optional[db.User]:
        """Get user follow username"""
        return self.db.query(db.User).filter(db.User.username == username).first()
    
    def get_by_email(self, email: str) -> Optional[db.User]:
        """Get user follow email"""
        return self.db.query(db.User).filter(db.User.email == email).first()
    
    def get_by_id(self, user_id: int) -> Optional[db.User]:
        """Get user follow ID"""
        return self.db.query(db.User).filter(db.User.id == user_id).first()
    
    def create(self, username: str, email: str, password: str, 
               full_name: str = None, phone: str = None, 
               role: db.UserRole = db.UserRole.USER) -> db.User:
        """
        Create new user
        
        Args:
            username: user name
            email: Email
            password: Password hashed
            full_name: Get full name
            phone: Phone
            role: Role (default is USER)
            
        Returns:
            User object
        """
        
        user = db.User(
            username=username,
            email=email,
            password_hash=utils.hash_password(password),
            full_name=full_name,
            phone=phone,
            role=role
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def authenticate(self, username: str, password: str) -> Optional[db.User]:
        """
        Valid user with username and password
        
        Args:
            username: username or password
            password: password
            
        Returns:
            User object if true, None if wrong
        """
        
        # Try username first
        user = self.get_by_username(username)
        
        # If not found, try email
        if not user:
            user = self.get_by_email(username)
        
        # Check account locked before check password
        if user and not user.is_active:
            return None  # account locked, deny sign-in
        
        if user and user.is_active and utils.verify_password(user.password_hash, password):
            return user
        
        return None
    
    def is_locked_user(self, username: str) -> bool:
        """
        check account locked
        
        Args:
            username: user name or email
            
        Returns:
            True nếu if locked, else False
        """
        # Try username first
        user = self.get_by_username(username)
        
        # If not found, try email
        if not user:
            user = self.get_by_email(username)
        
        if user and not user.is_active:
            return True
        
        return False


class InternationalNewsModel:
    """Model class management NewsInternational (news international by English)"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_by_id(self, news_id: int, include_deleted: bool = False) -> Optional[db.NewsInternational]:
        """
        Get article by ID
        
        Args:
            news_id: ID article
            include_deleted: if True, include article deleted (for admin)
        """
        query = self.db.query(db.NewsInternational).filter(db.NewsInternational.id == news_id)
        if not include_deleted:
            query = query.filter(db.NewsInternational.is_deleted == False)
        return query.first()

    def get_by_slug(self, slug: str) -> Optional[db.NewsInternational]:
        """Get article by slug (just only article don't delete)"""
        return (
            self.db.query(db.NewsInternational)
            .filter(
                db.NewsInternational.slug == slug,
                db.NewsInternational.is_deleted == False
            )
            .first()
        )

    def get_all(
        self,
        limit: int | None = None,
        offset: int = 0,
        status: db.NewsStatus | None = None,
        include_deleted: bool = False,
    ) -> list[db.NewsInternational]:
        """
        Lấy danh sách bài viết quốc tế
        
        Args:
            limit: Số lượng bài viết
            offset: Vị trí bắt đầu
            status: Lọc theo trạng thái
            include_deleted: Nếu True, lấy cả bài đã xóa (cho admin)
        """
        query = self.db.query(db.NewsInternational)

        if not include_deleted:
            query = query.filter(db.NewsInternational.is_deleted == False)

        if status:
            query = query.filter(db.NewsInternational.status == status)

        query = query.order_by(db.NewsInternational.created_at.desc())

        if limit:
            query = query.limit(limit).offset(offset)

        return query.all()

    def get_published(
        self, limit: int | None = None, offset: int = 0
    ) -> list[db.NewsInternational]:
        """Lấy danh sách bài viết quốc tế đã xuất bản (chỉ lấy bài chưa bị xóa)"""
        return self.get_all(
            limit=limit,
            offset=offset,
            status=db.NewsStatus.PUBLISHED,
        )

    def get_featured(self, limit: int = 10) -> list[db.NewsInternational]:
        """Lấy bài viết quốc tế nổi bật (chỉ lấy bài chưa bị xóa)"""
        return (
            self.db.query(db.NewsInternational)
            .filter(
                db.NewsInternational.is_featured.is_(True),
                db.NewsInternational.status == db.NewsStatus.PUBLISHED,
                db.NewsInternational.is_deleted == False,
            )
            .order_by(db.NewsInternational.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_hot(self, limit: int = 10) -> list[db.NewsInternational]:
        """Lấy tin quốc tế nóng nhất (chỉ lấy bài chưa bị xóa)"""
        return (
            self.db.query(db.NewsInternational)
            .filter(
                db.NewsInternational.is_hot.is_(True),
                db.NewsInternational.status == db.NewsStatus.PUBLISHED,
                db.NewsInternational.is_deleted == False,
            )
            .order_by(db.NewsInternational.view_count.desc())
            .limit(limit)
            .all()
        )

    def get_by_category(
        self, category_id: int, limit: int | None = None, offset: int = 0
    ) -> list[db.NewsInternational]:
        """Lấy bài viết quốc tế theo danh mục (chỉ lấy bài chưa bị xóa)"""
        query = (
            self.db.query(db.NewsInternational)
            .filter(
                db.NewsInternational.category_id == category_id,
                db.NewsInternational.status == db.NewsStatus.PUBLISHED,
                db.NewsInternational.is_deleted == False,
            )
            .order_by(db.NewsInternational.created_at.desc())
        )

        if limit:
            query = query.limit(limit).offset(offset)

        return query.all()

    def update(self, news_id: int, **kwargs) -> Optional[db.NewsInternational]:
        """
        Cập nhật bài viết quốc tế
        
        Args:
            news_id: ID bài viết
            **kwargs: Các trường cần cập nhật
            
        Returns:
            Updated NewsInternational object hoặc None
        """
        news = self.get_by_id(news_id)
        if not news:
            return None
        
        for key, value in kwargs.items():
            if hasattr(news, key):
                setattr(news, key, value)
        
        news.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(news)
        return news

    def approve(self, news_id: int, approved_by: int) -> Optional[db.NewsInternational]:
        """Duyệt bài viết quốc tế"""
        return self.update(
            news_id, 
            status=db.NewsStatus.PUBLISHED,
            approved_by=approved_by,
            published_at=datetime.utcnow()
        )
    
    def reject(self, news_id: int, approved_by: int, reason: str = None) -> Optional[db.NewsInternational]:
        """
        Từ chối bài viết quốc tế
        
        Args:
            news_id: ID bài viết
            approved_by: ID người từ chối
            reason: Lý do từ chối (nếu có)
        """
        result = self.update(
            news_id,
            status=db.NewsStatus.REJECTED,
            approved_by=approved_by
        )
        
        # Lưu lý do từ chối vào bảng news_international_rejections
        if result and reason:
            rejection = db.NewsInternationalRejection(
                news_international_id=news_id,
                rejected_by=approved_by,
                reason=reason
            )
            self.db.add(rejection)
            self.db.commit()
        
        return result


class InternationalCategoryModel:
    """Model class quản lý CategoryInternational (danh mục tin quốc tế)"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all(self) -> list[db.CategoryInternational]:
        """Lấy tất cả danh mục quốc tế đang hiển thị"""
        return (
            self.db.query(db.CategoryInternational)
            .filter(db.CategoryInternational.visible.is_(True))
            .order_by(db.CategoryInternational.order_display)
            .all()
        )

    def get_by_id(self, category_id: int) -> Optional[db.CategoryInternational]:
        """Lấy danh mục quốc tế theo ID"""
        return (
            self.db.query(db.CategoryInternational)
            .filter(db.CategoryInternational.id == category_id)
            .first()
        )

    def get_by_slug(self, slug: str) -> Optional[db.CategoryInternational]:
        """Lấy danh mục quốc tế theo slug"""
        return (
            self.db.query(db.CategoryInternational)
            .filter(db.CategoryInternational.slug == slug)
            .first()
        )