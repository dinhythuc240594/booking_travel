from abc import ABC, abstractmethod
from typing import List

from database import (
    Setting,
    Hotels, 
    Tour, 
    Location,
    TourStatus
)

#######
# Composite Pattern sẽ đóng vai trò tính toán giá (total_price) cho giỏ hàng/gói dịch vụ trước khi lưu xuống bảng Bookings. 
# Nó xử lý sự khác biệt giữa Hotels (tính theo đêm) và Tour (tính theo người)
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
    def __init__(self, hotels: Hotels, nights: int):
        self.hotels = hotels
        self.nights = nights

    def get_total_price(self) -> float:
        return float(self.hotels.price_per_night) * self.nights

    def show_details(self, indent: str = "") -> str:
        return f"{indent}- 🏨 Khách sạn: {self.hotels.name} ({self.nights} đêm) - ${self.get_total_price()}"


class TourBookingItem(AbstractBookingItem):

    """Leaf 2: Xử lý giá của Tour (Giá * Số người)"""
    def __init__(self, tour: Tour, persons: int):
        self.tour = tour
        self.persons = persons

    def get_total_price(self) -> float:
        return float(self.tour.price_per_person) * self.persons

    def show_details(self, indent: str = "") -> str:
        return f"{indent}- 🚌 Tour: {self.tour.name} ({self.persons} người) - ${self.get_total_price()}"


class BookingPackage(AbstractBookingItem):

    """Composite: Gói combo chứa nhiều Hotels và Tour. Tính tổng giá trị và hiển thị chi tiết."""
    def __init__(self, package_name: str):
        self.package_name = package_name
        self.items: List[AbstractBookingItem] = []

    def add_item(self, item: AbstractBookingItem):
        self.items.append(item)
        
    def remove_item(self, item: AbstractBookingItem):
        self.items.remove(item)

    def get_total_price(self) -> float:
        return sum(item.get_total_price() for item in self.items)

    def show_details(self, indent: str = "") -> str:
        details = f"{indent}📦 GÓI COMBO: {self.package_name} | Tổng giá trị: ${self.get_total_price()}\n"
        for item in self.items:
            details += item.show_details(indent + "  ") + "\n"
        return details.rstrip()


class AbstractTourNode(ABC):

    """Component: Interface chung cho việc hiển thị cấu trúc Tour"""
    @abstractmethod
    def get_tour_count(self) -> int:
        pass

    @abstractmethod
    def show_tours(self, indent: str = "") -> str:
        pass


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
            
        return f"{indent}- {status_icon} [ID: {self.tour.tour_id}] {self.tour.name} | Trạng thái: {self.tour.status.value}"


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


class AbstractSettingNode(ABC):

    """Component: Interface chung cho Cài đặt"""
    @abstractmethod
    def to_dict(self) -> dict:
        pass


class SettingLeaf(AbstractSettingNode):

    """Leaf: Một cấu hình đơn lẻ (VD: smtp_port)"""
    def __init__(self, setting: Setting):
        self.setting = setting

    def to_dict(self) -> dict:
        return {
            self.setting.key: {
                'value': self.setting.value,
                'description': self.setting.description,
                'category': self.setting.category
            }
        }


class SettingCategoryComposite(AbstractSettingNode):

    """Composite: Một nhóm cấu hình (VD: Thư mục API Settings, SMTP Settings)"""
    def __init__(self, category_name: str):
        self.category_name = category_name
        self.children: List[AbstractSettingNode] = []

    def add(self, component: AbstractSettingNode):
        self.children.append(component)

    def to_dict(self) -> dict:
        """Gom toàn bộ dữ liệu của các cấu hình con (trả về JSON cho Frontend)"""
        category_data = {}
        for child in self.children:
            category_data.update(child.to_dict())
        return {self.category_name: category_data}