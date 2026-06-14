from abc import ABC, abstractmethod
from database import Tour

from typing import List
from database import (
    Tour, 
    TourStatus
)

#######
# Composite Pattern sẽ đóng vai trò tính toán giá (total_price) cho giỏ hàng/gói dịch vụ trước khi lưu xuống bảng Bookings. 
# Nó xử lý sự khác biệt giữa Hotels (tính theo đêm) và Tour (tính theo người)
#######

class AbstractTourNode(ABC):

    """Component: Interface chung cho việc hiển thị cấu trúc Tour"""
    @abstractmethod
    def get_tour_count(self) -> int:
        pass

    @abstractmethod
    def show_tours(self, indent: str = "") -> str:
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass
