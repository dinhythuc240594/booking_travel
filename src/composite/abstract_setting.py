from abc import ABC, abstractmethod


#######
# Composite Pattern sẽ đóng vai trò tính toán giá (total_price) cho giỏ hàng/gói dịch vụ trước khi lưu xuống bảng Bookings. 
# Nó xử lý sự khác biệt giữa Hotels (tính theo đêm) và Tour (tính theo người)
#######

class AbstractSettingNode(ABC):

    """Component: Interface chung cho Cài đặt"""
    @abstractmethod
    def to_dict(self) -> dict:
        pass

