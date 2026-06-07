

import os
import shutil
from database import (
    get_session, 
    Bookings, 
    Savedtour, 
    Viewedtour,
    Location
    )
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
            existing = session.query(Savedtour).filter_by(user_id=user_id, tour_id=tour_id).first()
            if not existing:
                saved_tour = Savedtour(user_id=user_id, tour_id=tour_id)
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
            view = Viewedtour(user_id=user_id, tour_id=tour_id)
            session.add(view)
            session.commit()
        except Exception as e:
            session.rollback()
        finally:
            session.close()

    @staticmethod
    def create_location_bulk(locations: list) -> bool:
        """Tạo nhiều location cùng lúc"""
        session = get_session()
        try:
            for location in locations:

                # Mapping đúng cấu trúc bảng location
                location_data = {
                    'name': location.get('name'),
                    'search_key': location.get('search_key'),
                    'city': location.get('city'),
                    'country': location.get('country'),
                    'description': location.get('description'),
                    'slug': location.get('slug'),
                    'image_url': location.get('image_url'),
                }

                location = Location(**location_data)
                session.add(location)
                session.commit()
                session.refresh(location)

                if location.location_id:
                    temp_folder = os.path.join('src', 'static', 'uploads', 'locations', 'vn', 'temp')
                    location_folder = os.path.join('src', 'static', 'uploads', 'locations', 'vn', f'location_{location.location_id}')
                    
                    if os.path.exists(temp_folder):
                        os.makedirs(location_folder, exist_ok=True)
                        # Di chuyển các file từ temp sang location folder
                        for filename in os.listdir(temp_folder):
                            src_path = os.path.join(temp_folder, filename)
                            dst_path = os.path.join(location_folder, filename)
                            if os.path.isfile(src_path):
                                shutil.move(src_path, dst_path)
                                if location.image_url and 'temp' in location.image_url:
                                    image_url = location.image_url.replace('temp', f'location_{location.location_id}')
                                    location.image_url = image_url
                        session.commit()

            return True
        except Exception as e:
            print(e)
            session.rollback()
            return False
        finally:
            session.close()

    @staticmethod
    def get_location_by_id(location_id):
        """Lấy thông tin người dùng theo ID"""
        session = get_session()
        try:
            return session.query(Location).filter(Location.location_id == location_id).first()
        finally:
            session.close()