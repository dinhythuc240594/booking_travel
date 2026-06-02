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