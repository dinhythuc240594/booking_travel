from abc import ABC, abstractmethod
from typing import List

from database import Hotel, Tours

#######
# Composite Pattern sẽ đóng vai trò tính toán giá (total_price) cho giỏ hàng/gói dịch vụ trước khi lưu xuống bảng Booking. 
# Nó xử lý sự khác biệt giữa Hotel (tính theo đêm) và Tours (tính theo người)
#######

class AbstractBookingItem(ABC):
    """Component: Interface chung cho mọi item chuẩn bị được book"""
    @abstractmethod
    def get_total_price(self) -> float:
        pass

    @abstractmethod
    def show_details(self, indent: str = "") -> str:
        pass

class HotelBookingItem(AbstractBookingItem):
    """Leaf 1: Xử lý giá của Hotel (Giá * Số đêm)"""
    def __init__(self, hotel, nights: int):
        self.hotel = hotel  # instance của class Hotel
        self.nights = nights

    def get_total_price(self) -> float:
        return float(self.hotel.price_per_night) * self.nights

    def show_details(self, indent: str = "") -> str:
        return f"{indent}- 🏨 Khách sạn: {self.hotel.name} ({self.nights} đêm) - ${self.get_total_price()}"

class TourBookingItem(AbstractBookingItem):
    """Leaf 2: Xử lý giá của Tour (Giá * Số người)"""
    def __init__(self, tour, persons: int):
        self.tour = tour    # instance của class Tours
        self.persons = persons

    def get_total_price(self) -> float:
        return float(self.tour.price_per_person) * self.persons

    def show_details(self, indent: str = "") -> str:
        return f"{indent}- 🚌 Tour: {self.tour.name} ({self.persons} người) - ${self.get_total_price()}"

class BookingPackage(AbstractBookingItem):
    """Composite: Gói combo chứa nhiều Hotel và Tour"""
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