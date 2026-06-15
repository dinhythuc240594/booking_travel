from database import get_session, Bookings, BookingStatus, BookingType, Tour
from command.component import DBTransactionInvoker
from command.tour import CreateBookingCommand, ProcessPaymentCommand
from composite.booking import BookingPackage
from composite.hotel import HotelsBookingItem
from composite.tour import TourBookingItem


class BookingService:
    
    @staticmethod
    def create_combo_booking(data: dict):
        """Tạo booking kết hợp (Hotels + Tour) sử dụng Composite và Command Pattern"""
        session = get_session()
        try:
            # 1. Fetch dữ liệu để tính toán
            # hotel = session.query(Hotels).get(data.get('hotel_id'))
            tour = session.query(Tour).get(data.get('tour_id'))
            
            # if not hotel and not tour:
            if not tour:
                return False

            # 2. Sử dụng Composite Pattern để tạo gói và tính giá
            combo = BookingPackage(package_name=f"Combo Du lịch của User {data.get('user_id')}")
            
            # if hotel:
            #     combo.add_item(HotelsBookingItem(hotel, nights))
            if tour:
                combo.add_item(TourBookingItem(tour, data.get('persons')))
            
            print(combo.show_details()) # In ra chi tiết combo

            # 3. Sử dụng Command Pattern để thực thi giao dịch an toàn
            invoker = DBTransactionInvoker()
            commands = []

            # # Tạo danh sách các lệnh Bookings và Payment tương ứng
            # if hotel:
            #     hotel_cmd = CreateBookingCommand(
            #         user_id=user_id, 
            #         booking_type=BookingType.hotel, 
            #         reference_id=hotel.hotel_id, 
            #         total_price=float(hotel.price_per_night) * nights
            #     )
            #     commands.append(hotel_cmd)
            #     commands.append(ProcessPaymentCommand(hotel_cmd, hotel_cmd.total_price, payment_method))

            if tour:
                tour_cmd = CreateBookingCommand({
                    "user_id": data.get('user_id'), 
                    "booking_type": data.get('booking_type'), 
                    "reference_id": data.get('tour_id'), 
                    "total_price": data.get('total_price'),
                    "check_in_date": data.get('check_in_date'),
                    "check_out_date": data.get('check_out_date'),
                    "persons": data.get('persons'),
                    "adults": data.get('adults'),
                    "children": data.get('children'),
                    "payment_method": data.get('payment_method'),
                    "nights": data.get('nights'),
                    "hotel_id": data.get('hotel_id'),
                    "booking_status": data.get('booking_status')
                })
                commands.append(tour_cmd)
                commands.append(ProcessPaymentCommand(tour_cmd, tour_cmd.total_price, data.get('payment_method')))

            # Thực thi toàn bộ chuỗi transaction
            invoker.execute_transaction(session, commands)
            return True

        except Exception as e:
            print(e)
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
    def update_booking_status(booking_id: int, new_status: BookingStatus):
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
            print(f"Error in update_booking_status: {str(e)}")
            return False
        finally:
            session.close()

    @staticmethod
    def cancel_booking(booking_id: int):
        """Hủy Bookings (Soft logic) thay vì xóa khỏi CSDL"""
        return BookingService.update_booking_status(booking_id, BookingStatus.CANCELLED)

    @staticmethod
    def get_latest_booking_by_id(user_id: int):
        """
        Tìm kiếm booking (cả tour và hotel) theo booking_id.
        Nếu tour_id không tồn tại, trả về None để hiển thị thông báo lỗi thích hợp.
        """
        session = get_session()
        try:
            booking = session.query(Bookings).filter(Bookings.user_id == user_id).order_by(Bookings.booking_id.desc()).first()
            if booking and booking.booking_type == BookingType.TOUR and not session.query(Tour).filter(Tour.tour_id == booking.reference_id).first():
                return None
            return booking
        finally:
            session.close()

    @staticmethod
    def get_bookings_by_user_id(user_id: int):
        """Đọc thông tin Bookings qua User ID"""
        session = get_session()
        try:
            return session.query(Bookings).filter(Bookings.user_id == user_id).all()
        finally:
            session.close()

    @staticmethod
    def get_booking_status():
        """Lấy số lượng booking theo trạng thái"""
        session = get_session()
        try:
            return session.query(Bookings.booking_status).group_by(Bookings.booking_status).all()
        finally:
            session.close()

    @staticmethod
    def get_booking_total_price():
        """Lấy tổng doanh thu từ booking"""
        session = get_session()
        try:
            return session.query(Bookings.total_price).sum()
        finally:
            session.close()