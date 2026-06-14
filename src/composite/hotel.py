
from composite.abstract_booking import AbstractBookingItem
from database import Hotels


class HotelsBookingItem(AbstractBookingItem):

    """Leaf 1: Xử lý giá của Hotels (Giá * Số đêm)"""
    def __init__(self, hotels: Hotels, nights: int):
        self.hotels = hotels
        self.nights = nights

    def get_total_price(self) -> float:
        return float(self.hotels.price_per_night) * self.nights

    def show_details(self, indent: str = "") -> str:
        return f"{indent}- 🏨 Khách sạn: {self.hotels.name} ({self.nights} đêm) - ${self.get_total_price()}"

    def to_dict(self) -> dict:
        return {
            "type": "hotel",
            "hotel_id": self.hotels.hotel_id,
            "name": self.hotels.name,
            "nights": self.nights,
            "price_per_night": float(self.hotels.price_per_night),
            "total_price": self.get_total_price()
        }
