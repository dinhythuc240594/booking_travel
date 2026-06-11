from composite.abstract_booking import AbstractBookingItem
from typing import List

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