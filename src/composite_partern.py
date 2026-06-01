from abc import ABC, abstractmethod
from typing import List

from database import (
    Hotels, 
    Tours, 
    ArticleCategory, 
    Articles)

#######
# Composite Pattern sẽ đóng vai trò tính toán giá (total_price) cho giỏ hàng/gói dịch vụ trước khi lưu xuống bảng Bookings. 
# Nó xử lý sự khác biệt giữa Hotels (tính theo đêm) và Tours (tính theo người)
#######


class AbstractBookingItem(ABC):
    """Component: Interface chung cho mọi item chuẩn bị được book"""
    @abstractmethod
    def get_total_price(self) -> float:
        pass

    @abstractmethod
    def show_details(self, indent: str = "") -> str:
        pass


class HotelsBookingItem(AbstractBookingItem):
    """Leaf 1: Xử lý giá của Hotels (Giá * Số đêm)"""
    def __init__(self, hotels, nights: int):
        self.hotels = hotels  # instance của class Hotels
        self.nights = nights

    def get_total_price(self) -> float:
        return float(self.hotels.price_per_night) * self.nights

    def show_details(self, indent: str = "") -> str:
        return f"{indent}- 🏨 Khách sạn: {self.hotels.name} ({self.nights} đêm) - ${self.get_total_price()}"


class TourBookingItem(AbstractBookingItem):
    """Leaf 2: Xử lý giá của Tours (Giá * Số người)"""
    def __init__(self, tours, persons: int):
        self.tours = tours    # instance của class Tours
        self.persons = persons

    def get_total_price(self) -> float:
        return float(self.tours.price_per_person) * self.persons

    def show_details(self, indent: str = "") -> str:
        return f"{indent}- 🚌 Tour: {self.tours.name} ({self.persons} người) - ${self.get_total_price()}"


class BookingPackage(AbstractBookingItem):
    """Composite: Gói combo chứa nhiều Hotels và Tours. Tính tổng giá trị và hiển thị chi tiết."""
    def __init__(self, package_name: str):
        self.package_name = package_name
        self.items: List[AbstractBookingItem] = []

    def add_item(self, item: AbstractBookingItem):
        self.items.append(item)

    def get_total_price(self) -> float:
        return sum(item.get_total_price() for item in self.items)

    def show_details(self, indent: str = "") -> str:
        details = f"{indent}📦 GÓI COMBO: {self.package_name} | Tổng giá trị: ${self.get_total_price()}\n"
        for item in self.items:
            details += item.show_details(indent + "  ") + "\n"
        return details.rstrip()


class AbstractContentNode(ABC):
    """Component: Interface chung cho Danh mục và Bài viết"""
    
    @abstractmethod
    def get_article_count(self) -> int:
        """Đếm số lượng bài viết"""
        pass

    @abstractmethod
    def show_structure(self, indent: str = "") -> str:
        """Hiển thị cấu trúc dạng cây"""
        pass


class ArticleLeaf(AbstractContentNode):
    """Leaf: Đại diện cho 1 Bài viết độc lập. Không chứa con."""
    def __init__(self, article: Articles):
        self.article = article

    def get_article_count(self) -> int:
        return 1 # Một bài viết đếm là 1

    def show_structure(self, indent: str = "") -> str:
        status_icon = "🟢" if self.article.status.value == "approved" else "🟡"
        return f"{indent}- {status_icon} Bài viết: {self.article.title} (Lượt xem: {self.article.view_count})"


class CategoryComposite(AbstractContentNode):
    """Composite: Đại diện cho 1 Danh mục. Có thể chứa bài viết hoặc danh mục con."""
    def __init__(self, category: ArticleCategory):
        self.category = category
        self.children: List[AbstractContentNode] = []

    def add_child(self, component: AbstractContentNode):
        """Thêm một bài viết hoặc danh mục con vào danh mục này"""
        self.children.append(component)
        
    def remove_child(self, component: AbstractContentNode):
        self.children.remove(component)

    def get_article_count(self) -> int:
        """Đệ quy đếm tổng số bài viết trong danh mục này và TẤT CẢ danh mục con"""
        return sum(child.get_article_count() for child in self.children)

    def show_structure(self, indent: str = "") -> str:
        """Đệ quy in ra cấu trúc cây của danh mục"""
        details = f"{indent}📂 DANH MỤC: {self.category.name} | Tổng bài viết: {self.get_article_count()}\n"
        for child in self.children:
            details += child.show_structure(indent + "   ") + "\n"
        return details.rstrip()