from abc import ABC, abstractmethod
from typing import List

# ==========================================
# PHẦN 1: ÁP DỤNG COMPOSITE PATTERN
# ==========================================

class TravelComponent(ABC):
    """Lớp cơ sở (Component) cho tất cả các dịch vụ du lịch"""
    @abstractmethod
    def get_price(self) -> float:
        pass

    @abstractmethod
    def show_details(self, indent: str = "") -> str:
        pass

class Flight(TravelComponent):
    """Dịch vụ đơn lẻ (Leaf) - Chuyến bay"""
    def __init__(self, flight_code: str, price: float):
        self.flight_code = flight_code
        self.price = price

    def get_price(self) -> float:
        return self.price

    def show_details(self, indent: str = "") -> str:
        return f"{indent}- ✈️ Chuyến bay ({self.flight_code}) : ${self.price}"

class Hotel(TravelComponent):
    """Dịch vụ đơn lẻ (Leaf) - Khách sạn"""
    def __init__(self, hotel_name: str, price: float):
        self.hotel_name = hotel_name
        self.price = price

    def get_price(self) -> float:
        return self.price

    def show_details(self, indent: str = "") -> str:
        return f"{indent}- 🏨 Khách sạn ({self.hotel_name}) : ${self.price}"

class TravelPackage(TravelComponent):
    """Gói dịch vụ (Composite) - Chứa nhiều dịch vụ khác"""
    def __init__(self, package_name: str):
        self.package_name = package_name
        self.children: List[TravelComponent] = []

    def add_component(self, component: TravelComponent):
        self.children.append(component)

    def remove_component(self, component: TravelComponent):
        self.children.remove(component)

    def get_price(self) -> float:
        # Tính tổng giá của tất cả các dịch vụ con bên trong
        return sum(child.get_price() for child in self.children)

    def show_details(self, indent: str = "") -> str:
        details = f"{indent}📦 GÓI DU LỊCH: {self.package_name} | Tổng giá: ${self.get_price()}\n"
        for child in self.children:
            details += child.show_details(indent + "  ") + "\n"
        return details.rstrip()

# ==========================================
# PHẦN 2: THIẾT KẾ ROLE CLIENT VÀ ADMIN/STAFF
# ==========================================

class User(ABC):
    def __init__(self, username: str):
        self.username = username

class AdminStaff(User):
    """Admin/Staff có quyền tạo và lắp ráp các gói dịch vụ"""
    def create_package(self, name: str) -> TravelPackage:
        print(f"[Admin/Staff: {self.username}] Đang khởi tạo gói mới: '{name}'")
        return TravelPackage(name)

    def add_service(self, package: TravelPackage, service: TravelComponent):
        package.add_component(service)
        print(f"[Admin/Staff: {self.username}] Đã thêm dịch vụ vào gói '{package.package_name}'")

class Client(User):
    """Client có quyền xem chi tiết và đặt dịch vụ (đơn lẻ hoặc trọn gói)"""
    def view_services(self, service: TravelComponent):
        print(f"\n--- [Client: {self.username}] ĐANG XEM THÔNG TIN DỊCH VỤ ---")
        print(service.show_details())
        print("-------------------------------------------------------")

    def book_service(self, service: TravelComponent):
        print(f"\n✅ [Client: {self.username}] Đã đặt thành công! Tổng thanh toán: ${service.get_price()}")

# ==========================================
# 1. RECEIVERS: Các dịch vụ cốt lõi xử lý logic
# ==========================================

class FlightService:
    def book_ticket(self, flight_id: str, passenger: str) -> bool:
        print(f"[FlightService] ✈️ Đã đặt vé chuyến bay '{flight_id}' cho khách hàng '{passenger}'.")
        return True

    def cancel_ticket(self, flight_id: str, passenger: str) -> bool:
        print(f"[FlightService] ❌ Đã hủy vé chuyến bay '{flight_id}' của khách hàng '{passenger}'.")
        return True

class HotelService:
    def reserve_room(self, hotel_id: str, guest: str) -> bool:
        print(f"[HotelService] 🏨 Đã đặt phòng tại khách sạn '{hotel_id}' cho khách hàng '{guest}'.")
        return True

    def cancel_room(self, hotel_id: str, guest: str) -> bool:
        print(f"[HotelService] ❌ Đã hủy phòng tại khách sạn '{hotel_id}' của khách hàng '{guest}'.")
        return True

# ==========================================
# 2. COMMAND INTERFACE
# ==========================================

class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass

# ==========================================
# 3. CONCRETE COMMANDS: Lệnh cụ thể
# ==========================================

class BookFlightCommand(Command):
    def __init__(self, flight_service: FlightService, flight_id: str, passenger: str):
        self.flight_service = flight_service
        self.flight_id = flight_id
        self.passenger = passenger

    def execute(self) -> None:
        self.flight_service.book_ticket(self.flight_id, self.passenger)

    def undo(self) -> None:
        self.flight_service.cancel_ticket(self.flight_id, self.passenger)

class BookHotelCommand(Command):
    def __init__(self, hotel_service: HotelService, hotel_id: str, guest: str):
        self.hotel_service = hotel_service
        self.hotel_id = hotel_id
        self.guest = guest

    def execute(self) -> None:
        self.hotel_service.reserve_room(self.hotel_id, self.guest)

    def undo(self) -> None:
        self.hotel_service.cancel_room(self.hotel_id, self.guest)

# ==========================================
# 4. INVOKER: Quản lý và thực thi lệnh
# ==========================================

class BookingManager:
    """Invoker lưu trữ và thực thi các lệnh, hỗ trợ rollback toàn bộ nếu cần"""
    def __init__(self):
        self._history: List[Command] = []

    def execute_command(self, command: Command) -> None:
        command.execute()
        self._history.append(command)

    def undo_last(self) -> None:
        if self._history:
            command = self._history.pop()
            command.undo()
        else:
            print("[BookingManager] ⚠️ Không có giao dịch nào để hoàn tác.")

    def rollback_all(self) -> None:
        print("\n[BookingManager] 🔄 PHÁT HIỆN LỖI! Đang tiến hành rollback toàn bộ giao dịch...")
        while self._history:
            command = self._history.pop()
            command.undo()
        print("[BookingManager] ✅ Rollback hoàn tất.")
        

