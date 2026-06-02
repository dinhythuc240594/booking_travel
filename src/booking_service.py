from database import get_session, Bookings, BookingTypeEnum, BookingStatusEnum, PaymentMethodEnum, Hotels, Tour
from command.component import DBTransactionInvoker
from command.tour import CreateBookingCommand, ProcessPaymentCommand
from composite.booking import HotelsBookingItem, TourBookingItem, BookingPackage

class BookingService:
    
    @staticmethod
    def create_combo_booking(user_id: int, hotel_id: int, nights: int, tour_id: int, persons: int, payment_method: PaymentMethodEnum):
        """Tạo booking kết hợp (Hotels + Tour) sử dụng Composite và Command Pattern"""
        session = get_session()
        try:
            # 1. Fetch dữ liệu để tính toán
            hotel = session.query(Hotels).get(hotel_id)
            tour = session.query(Tour).get(tour_id)
            
            if not hotel and not tour:
                return False

            # 2. Sử dụng Composite Pattern để tạo gói và tính giá
            combo = BookingPackage(package_name=f"Combo Du lịch của User {user_id}")
            
            if hotel:
                combo.add_item(HotelsBookingItem(hotel, nights))
            if tour:
                combo.add_item(TourBookingItem(tour, persons))
            
            print(combo.show_details()) # In ra chi tiết combo

            # 3. Sử dụng Command Pattern để thực thi giao dịch an toàn
            invoker = DBTransactionInvoker()
            commands = []

            # Tạo danh sách các lệnh Bookings và Payment tương ứng
            if hotel:
                hotel_cmd = CreateBookingCommand(
                    user_id=user_id, 
                    booking_type=BookingTypeEnum.hotel, 
                    reference_id=hotel.hotel_id, 
                    total_price=float(hotel.price_per_night) * nights
                )
                commands.append(hotel_cmd)
                commands.append(ProcessPaymentCommand(hotel_cmd, hotel_cmd.total_price, payment_method))

            if tour:
                tour_cmd = CreateBookingCommand(
                    user_id=user_id, 
                    booking_type=BookingTypeEnum.tour, 
                    reference_id=tour.tour_id, 
                    total_price=float(tour.price_per_person) * persons
                )
                commands.append(tour_cmd)
                commands.append(ProcessPaymentCommand(tour_cmd, tour_cmd.total_price, payment_method))

            # Thực thi toàn bộ chuỗi transaction
            invoker.execute_transaction(session, commands)
            return True

        except Exception as e:
            return False
        finally:
            session.close()

    @staticmethod
    def get_booking_by_id(booking_id: int):
        """Đọc thông tin sau khi đã tạo booking để xác nhận (sử dụng cho mục đích test)"""
        session = get_session()
        try:
            return session.query(Bookings).filter(Bookings.booking_id == booking_id).first()
        finally:
            session.close()

    @staticmethod
    def update_booking_status(booking_id: int, new_status: BookingStatusEnum):
        """Cập nhật trạng thái Bookings thủ công (VD: từ pending sang completed)"""
        session = get_session()
        try:
            booking = session.query(Bookings).filter(Bookings.booking_id == booking_id).first()
            if booking:
                booking.booking_status = new_status
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()

    @staticmethod
    def cancel_booking(booking_id: int):
        """Hủy Bookings (Soft logic) thay vì xóa khỏi CSDL"""
        return BookingService.update_booking_status(booking_id, BookingStatusEnum.cancelled)