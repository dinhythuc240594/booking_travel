

from flask import Blueprint, render_template, request, jsonify, abort, make_response, session
from database import (
    get_session,
    TourStatus
)
from models import BookingModel
from command_partern import (
    CreateTourCommand,
    DBTransactionInvoker, 
    # TourComment, 
    ChangetourtatusCommand, 
    SubscribeNewsletterCommand
)

import secrets

import base
import client_controller


# Create Blueprint for client with url_prefix is empty to redirect route
# and template_folder for html files in folder client
tour_bp = Blueprint('tour', __name__, 
                     url_prefix='/api/tour',
                     template_folder='templates')


controller = client_controller.Controller


class BaseClientView(base.BaseView, controller):

    db_session = get_session()


class CreateTourView(BaseClientView):

    def post(self):
        """API Tạo bài viết mới dưới dạng Bản nháp (Draft)"""
        data = request.json
        
        invoker = DBTransactionInvoker()
        
        try:
            # Tự động tạo slug nếu không truyền vào
            title = data.get('title')
            slug = data.get('slug', title.lower().replace(" ", "-")) if title else None
            
            command = CreateTourCommand(
                author_id=int(data.get('author_id')),
                category_id=data.get('category_id'),
                title=title,
                slug=slug,
                content=data.get('content')
            )
            
            # Thực thi qua Invoker để kiểm soát Transaction an toàn
            invoker.execute_transaction(self.db_session, [command])
            return jsonify({
                "message": "Tạo bài viết nháp thành công!", 
                "tour_id": command.tour_record.tour_id
            }), 21
            
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        finally:
            self.db_session.close()


class ReviewTourView(BaseClientView):

    def post(self, tour_id):
        """API Duyệt hoặc Từ chối bài viết dành cho Admin/Editor"""
        data = request.json
        action = data.get('action') # 'approve' hoặc 'reject'
        reviewer_id = data.get('reviewer_id')
        
        db_session = self.db_session
        invoker = DBTransactionInvoker()
        
        if action == 'approve':
            status = TourStatus.approved
        elif action == 'reject':
            status = TourStatus.rejected
        else:
            return jsonify({"error": "Hành động duyệt không hợp lệ (Yêu cầu 'approve' hoặc 'reject')"}), 400
            
        try:
            command = ChangetourtatusCommand(
                tour_id=tour_id,
                new_status=status,
                reviewer_id=reviewer_id
            )
            invoker.execute_transaction(db_session, [command])
            return jsonify({"message": f"Đã chuyển trạng thái bài viết sang: {status.value}"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        finally:
            db_session.close()


# class CommentTourView(BaseClientView):
#     def post(self, tour_id):
#         """API Thêm bình luận (hoặc phản hồi bình luận khác) vào tour"""
#         data = request.json
#         db_session = self.db_session
#         try:
#             comment = TourComment(
#                 tour_id=tour_id,
#                 user_id=int(data.get('user_id')),
#                 parent_id=data.get('parent_id'), # Khác NULL nếu là reply comment
#                 content=data.get('content')
#             )
#             db_session.add(comment)
#             db_session.commit()
#             return jsonify({"message": "Đã gửi bình luận thành công"}), 201
#         except Exception as e:
#             db_session.rollback()
#             return jsonify({"error": str(e)}), 400
#         finally:
#             db_session.close()


class SubscribeNewsletterView(BaseClientView):
    def post(self):
        """API Đăng ký nhận bản tin khuyến mãi/tin tức"""
        data = request.json
        email = data.get('email')
        user_id = data.get('user_id') # Có thể không đăng nhập vẫn ký nhận tin
        
        if not email:
            return jsonify({"error": "Vui lòng cung cấp Email"}), 400
            
        db_session = self.db_session
        invoker = DBTransactionInvoker()
        unsubscribe_token = secrets.token_urlsafe(32) # Tạo mã hủy đăng ký ngẫu nhiên
        
        try:
            command = SubscribeNewsletterCommand(
                email=email,
                unsubscribe_token=unsubscribe_token,
                user_id=user_id
            )
            invoker.execute_transaction(db_session, [command])
            return jsonify({"message": "Đăng ký nhận tin tức thành công!"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        finally:
            db_session.close()


class CreateComboBookingView(BaseClientView):
    def post(self):
        db_session = self.db_session
        booking_model = BookingModel(db_session)
        
        data = request.json if request.is_json else request.form
        success = booking_model.create_combo_booking(
            user_id=int(data.get('user_id', 1)),
            hotel_id=int(data.get('hotel_id')) if data.get('hotel_id') else None,
            nights=int(data.get('nights', 0)),
            tour_id=int(data.get('tour_id')) if data.get('tour_id') else None,
            persons=int(data.get('persons', 0)),
            payment_method_str=data.get('payment_method', 'credit_card')
        )
        
        db_session.close()
        if success:
            return jsonify({"message": "Đặt Combo du lịch thành công!"}), 201
        return jsonify({"error": "Đặt combo thất bại"}), 400


tour_bp.add_url_rule('/create', 'create_tour', CreateTourView.as_view('create_tour'))
tour_bp.add_url_rule('/<int:tour_id>/review', 'review_tour', ReviewTourView.as_view('review_tour'))
# tour_bp.add_url_rule('/<int:tour_id>/comment', 'comment_tour', CommentTourView.as_view('comment_tour'))
tour_bp.add_url_rule('/subscribe-newsletter', 'subscribe_newsletter', SubscribeNewsletterView.as_view('subscribe_newsletter'))
tour_bp.add_url_rule('/create-combo-booking', 'create_combo_booking', CreateComboBookingView.as_view('create_combo_booking'))
