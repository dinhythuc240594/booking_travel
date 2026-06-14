
from composite.abstract_booking import AbstractBookingItem
from composite.abstract_tour import AbstractTourNode
from database import Tour, TourStatus
from typing import List


class TourBookingItem(AbstractBookingItem):

    """Leaf 2: Xử lý giá của Tour (Giá * Số người)"""
    def __init__(self, tour: Tour, persons: int):
        self.tour = tour
        self.persons = persons

    def get_total_price(self) -> float:
        return (float(self.tour.price_per_adult) * self.persons) + (float(self.tour.price_per_child) * self.persons)

    def show_details(self, indent: str = "") -> str:
        return f"{indent}- 🚌 Tour: {self.tour.title} ({self.persons} người) - ${self.get_total_price()}"

    def to_dict(self) -> dict:
        return {
            "type": "tour",
            "tour_id": self.tour.tour_id,
            "title": self.tour.title,
            "persons": self.persons,
            "price_per_adult": float(self.tour.price_per_adult),
            "price_per_child": float(self.tour.price_per_child),
            "total_price": self.get_total_price()
        }


class TourLeafNode(AbstractTourNode):

    """Leaf: Đại diện cho 1 Tour đơn lẻ."""
    def __init__(self, tour: Tour):
        self.tour = tour

    def get_tour_count(self) -> int:
        return 1

    def show_tours(self, indent: str = "") -> str:
        # Cấu hình icon theo trạng thái bài viết/tour
        if self.tour.status == TourStatus.PUBLISHED:
            status_icon = "🟢"
        elif self.tour.status == TourStatus.PENDING:
            status_icon = "🟡"
        else:
            status_icon = "🔴"
            
        return f"{indent}- {status_icon} [ID: {self.tour.tour_id}] {self.tour.title} | Trạng thái: {self.tour.status.value}"

    def to_dict(self) -> dict:
        return {
            "type": "leaf",
            "tour_id": self.tour.tour_id,
            "title": self.tour.title,
            "slug": self.tour.slug,
            "status": self.tour.status.value if self.tour.status else None,
            "category": self.tour.category_name,
            "price_per_adult": float(self.tour.price_per_adult),
            "price_per_child": float(self.tour.price_per_child),
            "duration_days": self.tour.duration_days,
            "thumbnail": self.tour.thumbnail
        }


class TourGroupComposite(AbstractTourNode):

    """Composite Đa Năng: Nhóm Tour theo Địa điểm, Trạng thái, hoặc Tác giả (Staff)"""
    def __init__(self, group_name: str, group_type: str = "Thư mục"):
        self.group_name = group_name
        self.group_type = group_type # Có thể là "Địa điểm", "Trạng thái", "Tác giả"
        self.children: List[AbstractTourNode] = []

    def add_child(self, component: AbstractTourNode):
        self.children.append(component)
        
    def remove_child(self, component: AbstractTourNode):
        self.children.remove(component)

    def get_tour_count(self) -> int:
        """Tính tổng số Tour trong nhóm này"""
        return sum(child.get_tour_count() for child in self.children)

    def show_tours(self, indent: str = "") -> str:
        """In ra danh sách Nhóm và các Tour trực thuộc"""
        details = f"{indent}📂 {self.group_type.upper()}: {self.group_name} | Tổng số Tour: {self.get_tour_count()}\n"
        for child in self.children:
            details += child.show_tours(indent + "   ") + "\n"
        return details.rstrip()

    def to_dict(self) -> dict:
        return {
            "type": "composite",
            "group_name": self.group_name,
            "group_type": self.group_type,
            "tour_count": self.get_tour_count(),
            "children": [child.to_dict() for child in self.children]
        }