from database import get_session, Bookings, SavedTours, ViewedTours
from sqlalchemy.orm import joinedload

class RelatedService:

    @staticmethod
    def get_user_booking_history(user_id: int):
        """Lấy toàn bộ lịch sử Bookings của một người dùng kèm theo chi tiết thanh toán"""
        session = get_session()
        try:
            # Dùng joinedload để tránh lỗi N+1 query khi lấy payments
            bookings = session.query(Bookings)\
                .options(joinedload(Bookings.payments))\
                .filter(Bookings.user_id == user_id)\
                .order_by(Bookings.created_at.desc()).all()
            return bookings
        finally:    
            session.close()

    @staticmethod
    def save_tour_for_later(user_id: int, tour_id: int):
        """Chức năng 'Yêu thích/Lưu lại' Tour"""
        session = get_session()
        try:
            # Kiểm tra xem đã lưu chưa
            existing = session.query(SavedTours).filter_by(user_id=user_id, tour_id=tour_id).first()
            if not existing:
                saved_tour = SavedTours(user_id=user_id, tour_id=tour_id)
                session.add(saved_tour)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()

    @staticmethod
    def record_viewed_tour(user_id: int, tour_id: int):
        """Ghi nhận lịch sử xem Tour của người dùng (Để làm recommendation sau này)"""
        session = get_session()
        try:
            view = ViewedTours(user_id=user_id, tour_id=tour_id)
            session.add(view)
            session.commit()
        except Exception as e:
            session.rollback()
        finally:
            session.close()