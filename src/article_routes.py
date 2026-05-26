

from flask import Blueprint, render_template, request, jsonify, abort, make_response, session
from database import (
    get_session,
    ArticleCategory, 
    ArticleComment, 
    ArticleStatusEnum
)
from models import BookingModel
from command_partern import (
    DBTransactionInvoker, 
    CreateArticleCommand, 
    ChangeArticleStatusCommand, 
    SubscribeNewsletterCommand
)

import secrets

import base
import client_controller
import json
import utils


# Create Blueprint for client with url_prefix is empty to redirect route
# and template_folder for html files in folder client
article_bp = Blueprint('article', __name__, 
                     url_prefix='/api/articles',
                     template_folder='templates')


controller = client_controller.Controller


class BaseClientView(base.BaseView, controller):

    db_session = get_session()


class CreateArticleView(BaseClientView):

    def post(self):
        """API Tạo bài viết mới dưới dạng Bản nháp (Draft)"""
        data = request.json
        
        invoker = DBTransactionInvoker()
        
        try:
            # Tự động tạo slug nếu không truyền vào
            title = data.get('title')
            slug = data.get('slug', title.lower().replace(" ", "-")) if title else None
            
            command = CreateArticleCommand(
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
                "article_id": command.article_record.article_id
            }), 21
            
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        finally:
            self.db_session.close()


class ReviewArticleView(BaseClientView):

    def post(self, article_id):
        """API Duyệt hoặc Từ chối bài viết dành cho Admin/Editor"""
        data = request.json
        action = data.get('action') # 'approve' hoặc 'reject'
        reviewer_id = data.get('reviewer_id')
        
        db_session = self.db_session
        invoker = DBTransactionInvoker()
        
        if action == 'approve':
            status = ArticleStatusEnum.approved
        elif action == 'reject':
            status = ArticleStatusEnum.rejected
        else:
            return jsonify({"error": "Hành động duyệt không hợp lệ (Yêu cầu 'approve' hoặc 'reject')"}), 400
            
        try:
            command = ChangeArticleStatusCommand(
                article_id=article_id,
                new_status=status,
                reviewer_id=reviewer_id
            )
            invoker.execute_transaction(db_session, [command])
            return jsonify({"message": f"Đã chuyển trạng thái bài viết sang: {status.value}"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        finally:
            db_session.close()


class CommentArticleView(BaseClientView):
    def post(self, article_id):
        """API Thêm bình luận (hoặc phản hồi bình luận khác) vào bài viết"""
        data = request.json
        db_session = self.db_session
        try:
            comment = ArticleComment(
                article_id=article_id,
                user_id=int(data.get('user_id')),
                parent_id=data.get('parent_id'), # Khác NULL nếu là reply comment
                content=data.get('content')
            )
            db_session.add(comment)
            db_session.commit()
            return jsonify({"message": "Đã gửi bình luận thành công"}), 201
        except Exception as e:
            db_session.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            db_session.close()


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


class GetCategoryStructureView(BaseClientView):
    def post(self, category_id):
        """API Trả về tổng quan cấu trúc và số lượng bài viết của một danh mục (Gồm cả con)"""
        db_session = self.db_session
        try:
            category = db_session.query(ArticleCategory).get(category_id)
            if not category:
                return jsonify({"error": "Không tìm thấy danh mục này"}), 404
                
            # Gọi Composite Pattern để dựng cây
            category_tree = utils.build_category_tree(db_session, category)
            
            return jsonify({
                "category_name": category.name,
                "total_articles_including_subs": category_tree.get_article_count(),
                "visual_structure": category_tree.show_structure()
            }), 200
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


article_bp.add_url_rule('/create', 'create_article', CreateArticleView.as_view('create_article'))
article_bp.add_url_rule('/<int:article_id>/review', 'review_article', ReviewArticleView.as_view('review_article'))
article_bp.add_url_rule('/<int:article_id>/comment', 'comment_article', CommentArticleView.as_view('comment_article'))
article_bp.add_url_rule('/subscribe-newsletter', 'subscribe_newsletter', SubscribeNewsletterView.as_view('subscribe_newsletter'))
article_bp.add_url_rule('/category/<int:category_id>/structure', 'get_category_structure', GetCategoryStructureView.as_view('get_category_structure'))
article_bp.add_url_rule('/create-combo-booking', 'create_combo_booking', CreateComboBookingView.as_view('create_combo_booking'))
