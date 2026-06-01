
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from datetime import datetime
from typing import List, Optional
import database as db
from booking_service import BookingService
from user_service import UserService
import utils
from related_service import RelatedService


class ArticleModel:
    """Model class managers Article follow OOP"""
    
    def __init__(self, db_session: Session):
        """
        Initialization ArticlesModel
        
        Args:
            db_session: SQLAlchemy session
        """
        self.db = db_session
    
    def create(self, title: str, content: str, category_id: int, 
               created_by: int, summary: str = None, thumbnail: str = None,
               slug: str = None, status: db.ArticleStatus = db.ArticleStatus.DRAFT) -> db.Article:
        """
        Create article

        Args:
            title: Title article
            content: Content article
            category_id: ID category
            created_by: ID creator
            summary: Summary article
            thumbnail: URL avatar
            slug: URL slug (auto generate if None)
            status: Status article (default is DRAFT)
            
        Returns:
            News object
        """
        if slug is None:
            slug = self._generate_slug(title)
        
        article = db.Article(
            title=title,
            slug=slug,
            content=content,
            summary=summary,
            thumbnail=thumbnail,
            category_id=category_id,
            created_by=created_by,
            status=status
        )
        
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article
    
    def get_by_id(self, article_id: int, include_deleted: bool = False) -> Optional[db.Article]:
        """
        Get article follow ID

        Args:
            article_id: ID article
            include_deleted: if True, include article deleted (for admin)
        """
        query = self.db.query(db.Article).filter(db.Article.id == article_id)
        if not include_deleted:
            query = query.filter(db.Article.is_deleted == False)
        return query.first()
    
    def get_by_slug(self, slug: str) -> Optional[db.Article]:
        """Get article follow slug (instead get article deleted)"""
        return self.db.query(db.Article).filter(
            db.Article.slug == slug,
            db.Article.is_deleted == False
        ).first()
    
    def get_all(self, limit: int = None, offset: int = 0, 
                status: db.ArticleStatus = None, include_deleted: bool = False) -> List[db.Article]:
        """
        List article follow filter, support pagging
        
        Args:
            limit: amount article
            offset: position start
            status: filter status
            include_deleted: If True, get article deleted (for admin)
            
        Returns:
            List of Article objects
        """
        query = self.db.query(db.Article)
        
        if not include_deleted:
            query = query.filter(db.Article.is_deleted == False)
        
        if status:
            query = query.filter(db.Article.status == status)
        
        query = query.order_by(desc(db.Article.created_at))
        
        if limit:
            query = query.limit(limit).offset(offset)
        
        return query.all()

    def get_by_creator(
        self,
        creator_id: int,
        limit: int | None = None,
        offset: int = 0,
        status: db.ArticleStatus | None = None,
        search: str | None = None,
        include_deleted: bool = False,
    ) -> tuple[list[db.Article], int]:
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
        query = self.db.query(db.Article).filter(db.Article.created_by == creator_id)

        if not include_deleted:
            query = query.filter(db.Article.is_deleted == False)

        if status:
            query = query.filter(db.Article.status == status)

        if search:
            like_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    db.Article.title.ilike(like_pattern),
                    db.Article.summary.ilike(like_pattern),
                )
            )

        total = query.count()

        query = query.order_by(desc(db.Article.created_at))

        if limit:
            query = query.limit(limit).offset(offset)

        items = query.all()
        return items, total

    def get_published(self, limit: int = None, offset: int = 0) -> List[db.Article]:
        """List article published (just only article don't deleted)"""
        return self.get_all(
            limit=limit, 
            offset=offset, 
            status=db.ArticleStatus.PUBLISHED
        )
    
    def search(self, keyword: str, limit: int = 20) -> List[db.Article]:
        """List article by keyword (just only article don't deleted)"""
        return self.db.query(db.Article).filter(
            or_(
                db.Article.title.ilike(f'%{keyword}%'),
                db.Article.content.ilike(f'%{keyword}%'),
                db.Article.summary.ilike(f'%{keyword}%')
            ),
            db.Article.status == db.ArticleStatus.PUBLISHED,
            db.Article.is_deleted == False
        ).order_by(desc(db.Article.created_at)).limit(limit).all()

    def update(self, article_id: int, **kwargs) -> Optional[db.Article]:
        """
        Update article

        Args:
            article_id: Article ID
            **kwargs: Fields need update
            
        Returns:
            Updated Article object or None
        """
        article = self.get_by_id(article_id)
        if not article:
            return None
        
        for key, value in kwargs.items():
            if hasattr(article, key):
                setattr(article, key, value)
        
        article.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(article)
        return article

    def approve(self, article_id: int, approved_by: int) -> Optional[db.Article]:
        """Article approved"""
        return self.update(
            article_id,
            status=db.ArticleStatus.PUBLISHED,
            approved_by=approved_by,
            published_at=datetime.utcnow()
        )
    
    def reject(self, article_id: int, approved_by: int, reason: str = None) -> Optional[db.Article]:
        """
        Article reject
        
        Args:
            article_id: Article ID
            approved_by: ID user rejected
            reason: Content reject
        """
        result = self.update(
            article_id,
            status=db.ArticleStatus.REJECTED,
            approved_by=approved_by
        )
        
        # Save content reject of article_rejections
        if result and reason:
            rejection = db.ArticleRejection(
                article_id=article_id,
                rejected_by=approved_by,
                reason=reason
            )
            self.db.add(rejection)
            self.db.commit()
        
        return result

    def delete(self, article_id: int) -> bool:
        """
        delete article (soft delete) - set is_deleted = True
        """
        article = self.get_by_id(article_id)
        if not article:
            return False
        
        article.is_deleted = True
        article.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def increment_view(self, article_id: int) -> None:
        """increase views"""
        article = self.get_by_id(article_id)
        if article:
            article.view_count += 1
            self.db.commit()
    
    def _generate_slug(self, title: str) -> str:
        """create slug from title"""
        import re
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')


class ArticleCategoryModel:
    """Model class quản lý Category"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create(self, name: str, slug: str, parent_id: int = None, 
               description: str = None, icon: str = None) -> db.ArticleCategory:
        """Tạo danh mục mới"""
        category = db.ArticleCategory(
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
    
    def get_all(self) -> List[db.ArticleCategory]:
        """Lấy tất cả danh mục"""
        return self.db.query(db.ArticleCategory).filter(
            db.ArticleCategory.visible == True
        ).order_by(db.ArticleCategory.order_display).all()
    
    def get_by_id(self, category_id: int) -> Optional[db.ArticleCategory]:
        """Lấy danh mục theo ID"""
        return self.db.query(db.ArticleCategory).filter(db.ArticleCategory.id == category_id).first()
    
    def get_by_slug(self, slug: str) -> Optional[db.ArticleCategory]:
        """Lấy danh mục theo slug"""
        return self.db.query(db.ArticleCategory).filter(db.ArticleCategory.slug == slug).first()

    def get_descendant_ids(self, parent_id: int) -> list[int]:
        """Lấy danh sách id danh mục con (mọi cấp) của parent_id."""
        categories = self.db.query(db.ArticleCategory.id, db.ArticleCategory.parent_id).filter(
            db.ArticleCategory.visible == True
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
        return UserService.get_user_by_id(user_id)
    
    def create(self, username: str, email: str, password: str, 
               full_name: str = None, phone: str = None, 
               role: db.UserRole = db.UserRole.CUSTOMER) -> db.User:
        """
        Create new user
        
        Args:
            username: user name
            email: Email
            password: Password hashed
            full_name: Get full name
            phone: Phone
            role: Role (default is CUSTOMER)
            
        Returns:
            User object
        """

        user = UserService.create_user(
                username=username,
                email=email,
                password_hash=password,
                full_name=full_name if full_name else None,
                phone_number=phone,
                role=role
            )

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


class BookingModel:
    """Model class management Bookings"""
    
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_combo_booking(self, user_id: int, hotel_id: int, nights: int, tour_id: int, persons: int, payment_method_str: str) -> bool:
        """
        Create booking follow combo API. 
        Note: BookingService trả về boolean (True/False) cho giao dịch này.
        """
        # Convert string to Enum payment method
        payment_method = db.PaymentMethodEnum.from_string(payment_method_str)
        if not payment_method:
            payment_method = db.PaymentMethodEnum.credit_card # Default fallback

        success = BookingService.create_combo_booking(
            user_id=user_id, 
            hotel_id=hotel_id, 
            nights=nights,
            tour_id=tour_id, 
            persons=persons, 
            payment_method=payment_method
        )
        return success

    def get_by_id(self, booking_id: int) -> Optional[db.Bookings]:
        """Đọc thông tin Bookings qua ID"""
        return BookingService.get_booking_by_id(booking_id)

    def update_status(self, booking_id: int, new_status: db.BookingStatusEnum) -> bool:
        """Cập nhật trạng thái Bookings (VD: từ pending sang completed)"""
        return BookingService.update_booking_status(booking_id, new_status)

    def cancel_booking(self, booking_id: int) -> bool:
        """Hủy Bookings (Soft logic)"""
        return BookingService.cancel_booking(booking_id)


class TourModel:
    """Model class management Tour"""
    
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_tour(self, user_id: int, hotel_id: int, nights: int, tour_id: int, persons: int, payment_method_str: str) -> bool:
        """
        Create booking follow combo API. 
        Note: BookingService trả về boolean (True/False) cho giao dịch này.
        """
        # Convert string to Enum payment method
        payment_method = db.PaymentMethodEnum.from_string(payment_method_str)
        if not payment_method:
            payment_method = db.PaymentMethodEnum.credit_card # Default fallback

        success = BookingService.create_combo_booking(
            user_id=user_id, 
            hotel_id=hotel_id, 
            nights=nights,
            tour_id=tour_id, 
            persons=persons, 
            payment_method=payment_method
        )
        return success

    def get_by_id(self, booking_id: int) -> Optional[db.Bookings]:
        """Đọc thông tin Bookings qua ID"""
        return BookingService.get_booking_by_id(booking_id)

    def update_status(self, booking_id: int, new_status: db.BookingStatusEnum) -> bool:
        """Cập nhật trạng thái Bookings (VD: từ pending sang completed)"""
        return BookingService.update_booking_status(booking_id, new_status)

    def cancel_booking(self, booking_id: int) -> bool:
        """Hủy Bookings (Soft logic)"""
        return BookingService.cancel_booking(booking_id)


class RelatedActivityModel:
    """Model class management Related user activities (History, Saved, Viewed)"""
    
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_booking_history(self, user_id: int) -> List[db.Bookings]:
        """
        Lấy toàn bộ lịch sử Bookings của một người dùng kèm theo chi tiết thanh toán
        """
        return RelatedService.get_user_booking_history(user_id)

    def save_tour(self, user_id: int, tour_id: int) -> bool:
        """
        Chức năng 'Yêu thích/Lưu lại' Tour
        """
        return RelatedService.save_tour_for_later(user_id, tour_id)

    def record_tour_view(self, user_id: int, tour_id: int) -> None:
        """
        Ghi nhận lịch sử xem Tour của người dùng
        """
        # RelatedService.record_viewed_tour không trả về giá trị, chỉ thực thi commit
        RelatedService.record_viewed_tour(user_id, tour_id)


