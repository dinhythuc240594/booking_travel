
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
import database as db
import datetime
import utils
import json
from service.tour_admin_service import TourAdminService
from service.tour_client_service import TourClientService


class TourModel:
    """Model class managers Tours follow OOP"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create(self, title: str, content: str, location_id: int, 
               author_id: int, duration_days: int = 1, 
               price_per_adult: float = 0.0, 
               price_per_child: float = 0.0,
               summary: str = None, thumbnail: str = None, images: str = None,
               slug: str = None, status: db.TourStatus = db.TourStatus.DRAFT) -> db.Tour:
        
        if slug is None:
            slug = self._generate_slug(title)
        
        tour = TourAdminService.create_tour({
            "title": title, 
            "content": content, 
            "location_id": location_id, 
            "author_id": author_id, 
            "duration_days": duration_days, 
            "price_per_adult": price_per_adult, 
            "price_per_child": price_per_child, 
            "summary": summary, 
            "thumbnail": thumbnail, 
            "images": images, 
            "slug": slug, 
            "status": status
        })

        return tour
    
    def get_by_id(self, tour_id: int, include_deleted: bool = False) -> db.Tour:
        query = self.db.query(db.Tour).filter(db.Tour.tour_id == tour_id)
        if not include_deleted:
            query = query.filter(db.Tour.is_deleted == False)
        return query.first()
    
    def get_by_slug(self, slug: str) -> db.Tour:
        return TourAdminService.get_tour_by_slug({"slug": slug})
    
    def get_by_category_name(self, category_name: str) -> db.Tour:
        return TourClientService.get_by_category_name(category_name)

    def get_all(self, limit: int = None, offset: int = 0, 
                status: db.TourStatus = None, include_deleted: bool = False) -> list[db.Tour]:
        query = self.db.query(db.Tour)
        if not include_deleted:
            query = query.filter(db.Tour.is_deleted == False)
        if status:
            query = query.filter(db.Tour.status == status)
        query = query.order_by(desc(db.Tour.created_at))
        if limit:
            query = query.limit(limit).offset(offset)
        return query.all()

    def get_by_author(self, author_id: int, limit: int = None, offset: int = 0,
                       status: db.TourStatus = None, search: str = None, 
                       include_deleted: bool = False) -> tuple[list[db.Tour], int]:
        query = self.db.query(db.Tour).filter(db.Tour.author_id == author_id) # Sửa từ created_by
        if not include_deleted:
            query = query.filter(db.Tour.is_deleted == False)
        if status:
            query = query.filter(db.Tour.status == status)
        if search:
            like_pattern = f"%{search}%"
            query = query.filter(or_(db.Tour.title.ilike(like_pattern), db.Tour.summary.ilike(like_pattern)))

        total = query.count()
        query = query.order_by(desc(db.Tour.created_at))
        if limit:
            query = query.limit(limit).offset(offset)
        return query.all(), total

    def update(self, tour_id: int, **kwargs) -> db.Tour:
        tour = self.get_by_id(tour_id)
        if not tour:
            return None
        for key, value in kwargs.items():
            if hasattr(tour, key):
                setattr(tour, key, value)
        tour.updated_at = datetime.datetime.utcnow()
        self.db.commit()
        self.db.refresh(tour)
        return tour

    def approve(self, tour_id: int, reviewer_id: int) -> db.Tour:
        return self.update(tour_id, status=db.TourStatus.PUBLISHED, 
                           reviewer_id=reviewer_id, published_at=datetime.datetime.utcnow())
    
    def reject(self, tour_id: int, reviewer_id: int, reason: str = None) -> db.Tour:
        result = self.update(tour_id, status=db.TourStatus.REJECTED, reviewer_id=reviewer_id)
        if result and reason:
            rejection = db.TourRejection(tour_id=tour_id, rejected_by=reviewer_id, reason=reason)
            self.db.add(rejection)
            self.db.commit()
        return result
    
    def delete(self, tour_id: int) -> bool:
        tour = self.get_by_id(tour_id)
        if not tour: return False
        tour.is_deleted = True
        tour.updated_at = datetime.datetime.utcnow()
        self.db.commit()
        return True
    
    def search(self, keyword: str, limit: int = None, offset: int = 0) -> list[db.Tour]:
        like_pattern = f"%{keyword}%"
        query = self.db.query(db.Tour).join(db.Location, isouter=True).filter(
            db.Tour.status == db.TourStatus.PUBLISHED,
            db.Tour.is_deleted == False,
            or_(
                db.Tour.title.ilike(like_pattern),
                db.Tour.summary.ilike(like_pattern),
                db.Location.name.ilike(like_pattern),
                db.Location.city.ilike(like_pattern)
            )
        ).order_by(desc(db.Tour.created_at))
        if limit:
            query = query.limit(limit).offset(offset)
        return query.all()

    def get_public_tours(self, limit: int = None, offset: int = 0) -> list[db.Tour]:
        query = self.db.query(db.Tour).filter(
            db.Tour.status == db.TourStatus.PUBLISHED,
            db.Tour.is_deleted == False
        ).order_by(desc(db.Tour.created_at))
        if limit:
            query = query.limit(limit).offset(offset)
        return query.all()

    def _tour_to_dict(self, tour: db.Tour, adult: int = 1, children: int = 0) -> dict:
        
        # Parse images JSON string nếu có
        images_list = []
        if tour.images:
            try:
                images_list = json.loads(tour.images)
            except:
                pass

        # Parse inputs to int safely
        try:
            adult = int(adult)
        except:
            adult = 1
        try:
            children = int(children)
        except:
            children = 0

        price_adult = float(tour.price_per_adult) if tour.price_per_adult else 0.0
        price_child = float(tour.price_per_child) if tour.price_per_child else 0.0
        disc_price = float(tour.discount_price) if getattr(tour, 'discount_price', None) is not None else None
        
        effective_adult_price = disc_price if disc_price is not None else price_adult
        total_price = (effective_adult_price * adult) + (price_child * children)

        return {
            "tour_id": tour.tour_id,
            "location_id": tour.location_id,
            "title": tour.title,
            "slug": tour.slug,
            "summary": tour.summary,
            "content": tour.content,
            "duration_days": tour.duration_days,
            "price_per_adult": price_adult,
            "price_per_child": price_child,
            "discount_price": disc_price,
            "total_price": total_price,
            "thumbnail": tour.thumbnail,
            "images": images_list, # Trả về list thay vì chuỗi JSON string
            "is_hot": tour.is_hot,
            "is_featured": tour.is_featured,
            "view_count": tour.view_count,
            "status": tour.status.value if tour.status else None, # Lấy giá trị của Enum
            # Convert DateTime -> String
            "published_at": tour.published_at.strftime('%Y-%m-%d %H:%M:%S') if tour.published_at else None,
            "created_at": tour.created_at.strftime('%Y-%m-%d %H:%M:%S') if tour.created_at else None,
            
            # Nếu muốn lấy thêm thông tin từ bảng liên kết (Relationship)
            "author_name": tour.author.username if tour.author else None,
            "location_name": tour.location.city if getattr(tour, 'location', None) else None,
            "country": tour.location.country if getattr(tour, 'location', None) else "Việt Nam"
        }


    def _generate_slug(self, title: str) -> str:
        import re
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')

    def get_tours_tree(self, author_id=None) -> dict:
        """Lấy cây thư mục cấu trúc các Tour theo Composite Pattern"""
        return TourClientService.get_tours_tree(author_id).to_dict()