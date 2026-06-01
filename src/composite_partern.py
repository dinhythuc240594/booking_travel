from abc import ABC, abstractmethod
from typing import List

from database import (
    Hotels, 
    Tour, 
    Location, 
    Tour)

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
    def __init__(self, hotels, nights: int):
        self.hotels = hotels  # instance của class Hotels
        self.nights = nights

    def get_total_price(self) -> float:
        return float(self.hotels.price_per_night) * self.nights

    def show_details(self, indent: str = "") -> str:
        return f"{indent}- 🏨 Khách sạn: {self.hotels.name} ({self.nights} đêm) - ${self.get_total_price()}"


class TourBookingItem(AbstractBookingItem):
    """Leaf 2: Xử lý giá của Tour (Giá * Số người)"""
    def __init__(self, tour, persons: int):
        self.tour = tour    # instance của class Tour
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

    def get_total_price(self) -> float:
        return sum(item.get_total_price() for item in self.items)

    def show_details(self, indent: str = "") -> str:
        details = f"{indent}📦 GÓI COMBO: {self.package_name} | Tổng giá trị: ${self.get_total_price()}\n"
        for item in self.items:
            details += item.show_details(indent + "  ") + "\n"
        return details.rstrip()


class AbstractLocationNode(ABC):
    """Component: Interface chung cho việc nhóm Tour theo Địa điểm"""
    
    @abstractmethod
    def get_tour_count(self) -> int:
        """Đếm số lượng Tour"""
        pass

    @abstractmethod
    def show_tours(self, indent: str = "") -> str:
        """Hiển thị cấu trúc cây"""
        pass


class TourLeafNode(AbstractLocationNode):
    """Leaf: Đại diện cho 1 Tour đơn lẻ."""
    def __init__(self, tour: Tour):
        self.tour = tour

    def get_tour_count(self) -> int:
        return 1

    def show_tours(self, indent: str = "") -> str:
        return f"{indent}- 🚌 Tour: {self.tour.name} ({self.tour.duration_days} ngày) - Giá: ${self.tour.price_per_person}"


class LocationCompositeNode(AbstractLocationNode):
    """Composite: Đại diện cho 1 Khu vực/Địa điểm. Chứa các Tour thuộc khu vực này."""
    def __init__(self, location: Location):
        self.location = location
        self.children: List[AbstractLocationNode] = []

    def add_child(self, component: AbstractLocationNode):
        self.children.append(component)
        
    def remove_child(self, component: AbstractLocationNode):
        self.children.remove(component)

    def get_tour_count(self) -> int:
        """Tính tổng số Tour trong địa điểm này"""
        return sum(child.get_tour_count() for child in self.children)

    def show_tours(self, indent: str = "") -> str:
        """In ra danh sách Địa điểm và các Tour trực thuộc"""
        details = f"{indent}📍 ĐỊA ĐIỂM: {self.location.city}, {self.location.country} | Tổng số Tour: {self.get_tour_count()}\n"
        for child in self.children:
            details += child.show_tours(indent + "   ") + "\n"
        return details.rstrip()