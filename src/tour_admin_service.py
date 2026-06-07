
from werkzeug.debug import console
import os
import re
import json
import shutil
from flask import jsonify

from database import (
    UserRole, 
    get_session, 
    Tour, 
    TourStatus
)
from command.component import DBTransactionInvoker
from command.tour import CreateTourCommand, UpdateTourCommand, SoftDeleteTourCommand, ApproveTourCommand, RejectTourCommand
from command.user import ToggleUserStatusCommand

class TourAdminService:
    
    @staticmethod
    def process_images_and_content(content: str, thumbnail: str, tour_id: int):
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
        image_urls = list(set(re.findall(img_pattern, content)))
        
        # chuyển từ temp sang tour
        temp_folder = os.path.join('src', 'static', 'uploads', 'tour', 'vn', 'temp')
        tour_folder = os.path.join('src', 'static', 'uploads', 'tour', 'vn', f'tour_{tour_id}')

        if os.path.exists(temp_folder):
            os.makedirs(tour_folder, exist_ok=True)
            for filename in os.listdir(temp_folder):
                src_path = os.path.join(temp_folder, filename)
                dst_path = os.path.join(tour_folder, filename)
                if os.path.isfile(src_path):
                    shutil.move(src_path, dst_path)

        updated_images = []
        if image_urls:
            updated_images = [img.replace('temp', f'tour_{tour_id}') if 'temp' in img else img for img in image_urls]
            for old_url, new_url in zip(image_urls, updated_images):
                content = content.replace(old_url, new_url)

        # chuyển thumbnail từ temp sang tour
        if thumbnail and 'temp' in thumbnail:
            thumbnail = thumbnail.replace('temp', f'tour_{tour_id}')

        return content, thumbnail, json.dumps(updated_images) if updated_images else None

    @staticmethod
    def create_tour(data: dict) -> tuple[bool, str, dict]:
        session = get_session()
        invoker = DBTransactionInvoker()
        
        # Mapping đúng cấu trúc bảng Tour
        tour_data = {
            'title': data.get('title'),
            'slug': data.get('slug'), 
            'content': data.get('content'),
            'summary': data.get('summary'),
            'thumbnail': data.get('thumbnail'),
            'author_id': data.get('user_id'),    # SỬA: Map sang author_id
            'location_id': data.get('location_id'), # SỬA: Map sang location_id thay vì category
            'duration_days': data.get('duration_days', 1),
            'price_per_adult': data.get('price_per_adult', 0.0),
            'price_per_child': data.get('price_per_child', 0.0),
            'category_name': data.get('category_name'),
            'status': data.get('status', TourStatus.DRAFT),
            'is_hot': data.get('is_hot', False),
            'is_featured': data.get('is_featured', False)
        }

        command = CreateTourCommand(tour_data)
        try:
            invoker.execute_transaction(session, [command])
            tour_id = command.tour_record.tour_id

            new_content, new_thumb, images_json = TourAdminService.process_images_and_content(
                tour_data['content'], tour_data['thumbnail'], tour_id
            )
            
            update_cmd = UpdateTourCommand(tour_id, {
                'content': new_content, 'thumbnail': new_thumb, 'images': images_json
            })
            invoker.execute_transaction(session, [update_cmd])
            
            return True, "Thành công", {"id": tour_id, "slug": tour_data['slug']}
        except Exception as e:
            print(e)
            return False, str(e), None
        finally:
            session.close()

    @staticmethod
    def update_tour(tour_id: int, data: dict) -> tuple[bool, str]:
        session = get_session()
        invoker = DBTransactionInvoker()
        
        new_content, new_thumb, images_json = TourAdminService.process_images_and_content(
            data.get('content', ''), data.get('thumbnail', ''), tour_id
        )
        
        update_data = {
            'title': data.get('title'),
            'slug': data.get('slug'),
            'content': new_content,
            'summary': data.get('summary'),
            'thumbnail': new_thumb,
            'images': images_json,
            'location_id': data.get('location_id'), # Sửa thành location_id
            'duration_days': data.get('duration_days', 1),
            'price_per_adult': data.get('price_per_adult'),
            'price_per_child': data.get('price_per_child'),
            'status': data.get('status'),
            'is_hot': data.get('is_hot'),
            'is_featured': data.get('is_featured'),
            'category_name': data.get('category_name'),
        }
        
        command = UpdateTourCommand(tour_id, update_data)
        try:
            invoker.execute_transaction(session, [command])
            return True, "Cập nhật thành công"
        except Exception as e:
            print(e)
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def delete_tour(tour_id: int) -> tuple[bool, str]:
        session = get_session()
        invoker = DBTransactionInvoker()
        command = SoftDeleteTourCommand(tour_id)
        try:
            invoker.execute_transaction(session, [command])
            return True, "Xóa tour thành công"
        except Exception as e:
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def api_approved_atour(tour_id: int, user_id: int) -> tuple[bool, str]:
        session = get_session()
        invoker = DBTransactionInvoker()
        command = ApproveTourCommand(tour_id, user_id)
        try:
            invoker.execute_transaction(session, [command])
            return True, "Duyệt tour thành công"
        except Exception as e:
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def api_rejected_atour(tour_id: int, user_id: int, reason: str) -> tuple[bool, str]:
        session = get_session()
        invoker = DBTransactionInvoker()
        command = RejectTourCommand(tour_id, user_id, reason)
        try:
            invoker.execute_transaction(session, [command])
            return True, "Từ chối tour thành công"
        except Exception as e:
            return False, str(e)
        finally:
            session.close()

    @staticmethod
    def user_toggle_status(user_id: int):

        # Sử dụng Command Pattern
        session_db = get_session()
        invoker = DBTransactionInvoker()
        command = ToggleUserStatusCommand(user_id)
        
        try:
            invoker.execute_transaction(session_db, [command])
            return {'success': True, 'message': 'Thay đổi trạng thái user thành công'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            session_db.close()
