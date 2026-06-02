from abc import ABC, abstractmethod
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
