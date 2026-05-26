from flask import Blueprint, render_template, request, jsonify, abort, redirect, url_for, flash, session, current_app
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import or_
from typing import Optional
from functools import wraps
import pytz
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from database import (
    get_session,
    TourStatus,
    UserRole,
    SavedTours,
    ViewedTours,
    NewsletterSubscription,
    PasswordResetToken,
    Setting,
    User,
    ToursRejection,
)
from models import (
    ToursModel,
    UserModel,
)


class AdminController:
    """Controller class quản lý các route của admin"""
    
    def __init__(self):
        """Khởi tạo controller"""
        self.db_session = get_session()
        self.tours_model = ToursModel(self.db_session)
        self.user_model = UserModel(self.db_session)
    
    def login(self):
        """
        Trang đăng nhập admin
        Route: GET /admin/login
        Route: POST /admin/login
        """
        # Nếu đã đăng nhập, redirect đến dashboard tương ứng
        if 'user_id' in session and 'role' in session:
            if session['role'] == UserRole.ADMIN.value:
                return redirect(url_for('admin.dashboard'))
            elif session['role'] == UserRole.STAFF.value:
                return redirect(url_for('admin.editor_dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            remember = request.form.get('remember') == 'on'
            
            # Kiểm tra tài khoản bị khóa trước khi xác thực
            if self.user_model.is_locked_user(username):
                flash('Tài khoản đã bị khóa. Vui lòng liên hệ quản trị viên', 'error')
                return render_template('admin/login.html')
            
            user = self.user_model.authenticate(username, password)
            
            if user and user.is_active and user.role in [UserRole.ADMIN, UserRole.STAFF]:
                # Lưu session đăng nhập
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role.value
                
                # Nếu chọn "Ghi nhớ đăng nhập", set session permanent
                if remember:
                    session.permanent = True
                else:
                    session.permanent = False
                
                flash('Đăng nhập thành công', 'success')
                
                # Kiểm tra role và redirect đến đúng dashboard
                if user.role == UserRole.ADMIN:
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('admin.editor_dashboard'))
            else:
                flash('Tên đăng nhập hoặc mật khẩu không đúng', 'error')
        print(f"=== DEBUG login ===")
        return render_template('admin/login.html')
    
    def logout(self):
        """Đăng xuất - Xóa session đăng nhập"""
        # Xóa toàn bộ session
        session.clear()
        flash('Đã đăng xuất', 'success')
        return redirect(url_for('admin.login'))
    
    def dashboard(self):
        """
        Dashboard admin - Thống kê và quản lý
        Route: GET /admin/dashboard
        """
        # Thống kê
        total_tours = len(self.tours_model.get_all())
        published_tours = len(self.tours_model.get_all(status=TourStatus.PUBLISHED))
        pending_tours = len(self.tours_model.get_all(status=TourStatus.PENDING))
        draft_tours = len(self.tours_model.get_all(status=TourStatus.DRAFT))
        
        # Tour chờ duyệt
        pending_list = self.tours_model.get_all(status=TourStatus.PENDING, limit=10)
        
        # Tour mới nhất
        latest_tours = self.tours_model.get_all(limit=10)
        
        user = self.user_model.get_by_id(session['user_id'])

        return render_template('admin/admin.html',
                             total_tours=total_tours,
                             published_tours=published_tours,
                             pending_tours=pending_tours,
                             draft_tours=draft_tours,
                             pending_list=pending_list,
                             latest_tours=latest_tours,
                             user=user)
    
    def editor_dashboard(self):
        """
        Dashboard editor - Quản lý bài viết của biên tập viên
        Route: GET /admin/editor-dashboard
        """
        user_id = session.get('user_id')
        
        # Lấy tour của editor (chỉ dùng để thống kê nhanh)
        all_tours = self.tours_model.get_all()
        my_tours = [t for t in all_tours if t.created_by == user_id]
        
        draft_tours = [t for t in my_tours if t.status == TourStatus.DRAFT]
        pending_tours = [t for t in my_tours if t.status == TourStatus.PENDING]
        published_tours = [t for t in my_tours if t.status == TourStatus.PUBLISHED]
        categories = self.category_model.get_all()
        
        user = self.user_model.get_by_id(user_id)

        return render_template('editor/editor.html',
                             draft_tours=draft_tours,
                             pending_tours=pending_tours,
                             published_tours=published_tours,
                             categories=categories,
                             stat_total=len(my_tours),
                             stat_draft=len(draft_tours),
                             stat_pending=len(pending_tours),
                             stat_published=len(published_tours),
                             user=user)
    
    def tours_list(self):
        """
        Danh sách tour
        Route: GET /admin/tours
        """
        status_filter = request.args.get('status', None)
        page = request.args.get('page', 1, type=int)
        per_page = 20
        offset = (page - 1) * per_page
        
        status = None
        if status_filter:
            try:
                status = TourStatus(status_filter)
            except ValueError:
                status = None
        
        tours_list = self.tours_model.get_all(
            limit=per_page,
            offset=offset,
            status=status
        )
        
        categories = self.category_model.get_all()
        
        return render_template('admin/tours_list.html',
                             tours_list=tours_list,
                             categories=categories,
                             current_status=status_filter,
                             page=page)
    
    def tours_create(self):
        """
        Tạo tour mới
        Route: GET /admin/tours/create
        Route: POST /admin/tours/create
        """
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            category_id = request.form.get('category_id', type=int)
            summary = request.form.get('summary')
            thumbnail = request.form.get('thumbnail')
            status = request.form.get('status', TourStatus.DRAFT.value)
            
            user_id = session.get('user_id')
            
            try:
                tour_status = TourStatus(status)
            except ValueError:
                tour_status = TourStatus.DRAFT
            
            tour = self.tours_model.create(
                title=title,
                content=content,
                category_id=category_id,
                created_by=user_id,
                summary=summary,
                thumbnail=thumbnail,
                status=tour_status
            )
            
            flash('Tạo tour thành công', 'success')
            return redirect(url_for('admin.tours_edit', tour_id=tour.id))
        
        categories = self.category_model.get_all()
        return render_template('admin/tours_create.html', categories=categories)
    
    def tours_edit(self, tour_id: int):
        """
        Chỉnh sửa tour
        Route: GET /admin/tours/<tour_id>/edit
        Route: POST /admin/tours/<tour_id>/edit
        """
        tour = self.tours_model.get_by_id(tour_id)
        if not tour:
            flash('Không tìm thấy tour', 'error')
            return redirect(url_for('admin.tours_list'))
        
        # Kiểm tra quyền
        user_id = session.get('user_id')
        user = self.user_model.get_by_id(user_id)
        
        if user.role != UserRole.ADMIN and tour.created_by != user_id:
            flash('Bạn không có quyền chỉnh sửa tour này', 'error')
            return redirect(url_for('admin.tours_list'))
        
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            category_id = request.form.get('category_id', type=int)
            summary = request.form.get('summary')
            thumbnail = request.form.get('thumbnail')
            status = request.form.get('status')
            
            try:
                tour_status = TourStatus(status) if status else tour.status
            except ValueError:
                tour_status = tour.status
            
            self.tours_model.update(
                tour_id,
                title=title,
                content=content,
                category_id=category_id,
                summary=summary,
                thumbnail=thumbnail,
                status=tour_status
            )
            
            flash('Cập nhật tour thành công', 'success')
            return redirect(url_for('admin.tours_edit', tour_id=tour_id))
        
        categories = self.category_model.get_all()
        return render_template('admin/tours_edit.html',
                             tour=tour,
                             categories=categories)
    
    def news_approve(self, news_id: int):
        """
        Duyệt bài viết
        Route: POST /admin/news/<news_id>/approve
        """
        user_id = session.get('user_id')
        news = self.news_model.approve(news_id, user_id)
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            if news:
                return jsonify({'success': True, 'message': 'Đã duyệt bài viết'})
            else:
                return jsonify({'success': False, 'error': 'Không tìm thấy bài viết'}), 404
        
        if news:
            flash('Đã duyệt bài viết', 'success')
        else:
            flash('Không tìm thấy bài viết', 'error')
        
        return redirect(request.referrer or url_for('admin.dashboard'))
    
    def news_reject(self, news_id: int):
        """
        Từ chối bài viết và gửi email cho tác giả
        Route: POST /admin/news/<news_id>/reject
        """
        user_id = session.get('user_id')
        
        # Lấy lý do từ chối từ request body
        if request.is_json:
            reason = request.json.get('reason', '').strip()
        else:
            reason = request.form.get('reason', '').strip()
        
        if not reason:
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'error': 'Vui lòng nhập lý do từ chối'}), 400
            flash('Vui lòng nhập lý do từ chối', 'error')
            return redirect(request.referrer or url_for('admin.dashboard'))
        
        # Lấy thông tin bài viết trước khi reject
        news = self.news_model.get_by_id(news_id, include_deleted=False)
        if not news:
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'error': 'Không tìm thấy bài viết'}), 404
            flash('Không tìm thấy bài viết', 'error')
            return redirect(request.referrer or url_for('admin.dashboard'))
        
        # Thực hiện reject với lý do
        rejected_news = self.news_model.reject(news_id, user_id, reason=reason)
        
        if not rejected_news:
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'error': 'Không thể từ chối bài viết'}), 500
            flash('Không thể từ chối bài viết', 'error')
            return redirect(request.referrer or url_for('admin.dashboard'))
        
        # Lấy thông tin tác giả
        creator = self.user_model.get_by_id(news.created_by)
        if creator and creator.email:
            try:
                # Tạo link bài viết
                article_url = url_for('client.news_detail', slug=news.slug, _external=True)
                
                # Tạo nội dung email
                from email_utils import send_email
                
                email_subject = f"Bài viết của bạn đã bị từ chối: {news.title}"
                
                email_body_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                            max-width: 600px;
                            margin: 0 auto;
                            padding: 20px;
                        }}
                        .header {{
                            background-color: #dc3545;
                            color: white;
                            padding: 20px;
                            text-align: center;
                            border-radius: 5px 5px 0 0;
                        }}
                        .content {{
                            background-color: #f8f9fa;
                            padding: 20px;
                            border: 1px solid #dee2e6;
                        }}
                        .reason-box {{
                            background-color: white;
                            border-left: 4px solid #dc3545;
                            padding: 15px;
                            margin: 20px 0;
                        }}
                        .article-link {{
                            display: inline-block;
                            background-color: #0066cc;
                            color: white;
                            padding: 12px 24px;
                            text-decoration: none;
                            border-radius: 5px;
                            margin: 20px 0;
                        }}
                        .footer {{
                            text-align: center;
                            color: #6c757d;
                            font-size: 12px;
                            margin-top: 20px;
                            padding-top: 20px;
                            border-top: 1px solid #dee2e6;
                        }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h2>Thông báo từ chối bài viết</h2>
                    </div>
                    <div class="content">
                        <p>Xin chào <strong>{creator.full_name or creator.username}</strong>,</p>
                        
                        <p>Chúng tôi rất tiếc phải thông báo rằng bài viết của bạn đã bị từ chối:</p>
                        
                        <h3 style="color: #0066cc;">{news.title}</h3>
                        
                        <div class="reason-box">
                            <strong>Lý do từ chối:</strong>
                            <p style="margin-top: 10px; white-space: pre-wrap;">{reason}</p>
                        </div>
                        
                        <p>Bạn có thể xem lại bài viết của mình tại link sau:</p>
                        <div style="text-align: center;">
                            <a href="{article_url}" class="article-link">Xem bài viết</a>
                        </div>
                        
                        <p>Vui lòng xem xét lại bài viết và chỉnh sửa theo góp ý trên trước khi gửi lại để duyệt.</p>
                        
                        <p>Trân trọng,<br>
                        <strong>Ban biên tập VnNews</strong></p>
                    </div>
                    <div class="footer">
                        <p>Đây là email tự động. Vui lòng không trả lời email này.</p>
                        <p>© 2024 VnNews. All rights reserved.</p>
                    </div>
                </body>
                </html>
                """
                
                # Gửi email
                email_sent = send_email(
                    to_email=creator.email,
                    subject=email_subject,
                    body_html=email_body_html
                )
                
                if not email_sent:
                    print(f"Warning: Không thể gửi email từ chối đến {creator.email}")
                
            except Exception as e:
                print(f"Error sending rejection email: {str(e)}")
                # Vẫn tiếp tục dù email không gửi được
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': True, 
                'message': 'Đã từ chối bài viết và gửi email cho tác giả',
                'reason': reason
            })
        
        flash('Đã từ chối bài viết và gửi email cho tác giả', 'success')
        return redirect(request.referrer or url_for('admin.dashboard'))
    
    def news_delete(self, news_id: int):
        """
        Xóa mềm bài viết (soft delete) - set is_deleted = True
        Route: POST /admin/news/<news_id>/delete
        """
        success = self.news_model.delete(news_id)
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            if success:
                return jsonify({'success': True, 'message': 'Đã xóa bài viết'})
            else:
                return jsonify({'success': False, 'error': 'Không tìm thấy bài viết'}), 404
        
        if success:
            flash('Đã xóa bài viết', 'success')
        else:
            flash('Không tìm thấy bài viết', 'error')
        
        return redirect(url_for('admin.news_list'))
    
    def international_news_approve(self, news_id: int):
        """
        Duyệt bài viết quốc tế
        Route: POST /admin/international/<news_id>/approve
        """
        user_id = session.get('user_id')
        news = self.int_news_model.approve(news_id, user_id)
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            if news:
                return jsonify({'success': True, 'message': 'Đã duyệt bài viết quốc tế'})
            else:
                return jsonify({'success': False, 'error': 'Không tìm thấy bài viết'}), 404
        
        if news:
            flash('Đã duyệt bài viết quốc tế', 'success')
        else:
            flash('Không tìm thấy bài viết', 'error')
        
        return redirect(request.referrer or url_for('admin.dashboard'))
    
    def international_news_reject(self, news_id: int):
        """
        Từ chối bài viết quốc tế và gửi email cho tác giả
        Route: POST /admin/international/<news_id>/reject
        """
        user_id = session.get('user_id')
        
        # Lấy lý do từ chối từ request body
        if request.is_json:
            reason = request.json.get('reason', '').strip()
        else:
            reason = request.form.get('reason', '').strip()
        
        if not reason:
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'error': 'Vui lòng nhập lý do từ chối'}), 400
            flash('Vui lòng nhập lý do từ chối', 'error')
            return redirect(request.referrer or url_for('admin.dashboard'))
        
        # Lấy thông tin bài viết trước khi reject
        news = self.int_news_model.get_by_id(news_id, include_deleted=False)
        if not news:
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'error': 'Không tìm thấy bài viết'}), 404
            flash('Không tìm thấy bài viết', 'error')
            return redirect(request.referrer or url_for('admin.dashboard'))
        
        # Thực hiện reject với lý do
        rejected_news = self.int_news_model.reject(news_id, user_id, reason=reason)
        
        if not rejected_news:
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'error': 'Không thể từ chối bài viết'}), 500
            flash('Không thể từ chối bài viết', 'error')
            return redirect(request.referrer or url_for('admin.dashboard'))
        
        # Lấy thông tin tác giả và gửi email (tương tự như news_reject)
        creator = self.user_model.get_by_id(news.created_by)
        if creator and creator.email:
            try:
                # Tạo link bài viết
                article_url = url_for('client.news_detail_en', slug=news.slug, _external=True)
                
                # Tạo nội dung email
                from email_utils import send_email
                
                email_subject = f"Your article has been rejected: {news.title}"
                
                email_body_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                            max-width: 600px;
                            margin: 0 auto;
                            padding: 20px;
                        }}
                        .header {{
                            background-color: #dc3545;
                            color: white;
                            padding: 20px;
                            text-align: center;
                            border-radius: 5px 5px 0 0;
                        }}
                        .content {{
                            background-color: #f8f9fa;
                            padding: 20px;
                            border: 1px solid #dee2e6;
                        }}
                        .reason-box {{
                            background-color: white;
                            border-left: 4px solid #dc3545;
                            padding: 15px;
                            margin: 20px 0;
                        }}
                        .article-link {{
                            display: inline-block;
                            background-color: #0066cc;
                            color: white;
                            padding: 12px 24px;
                            text-decoration: none;
                            border-radius: 5px;
                            margin: 20px 0;
                        }}
                        .footer {{
                            text-align: center;
                            color: #6c757d;
                            font-size: 12px;
                            margin-top: 20px;
                            padding-top: 20px;
                            border-top: 1px solid #dee2e6;
                        }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h2>Article Rejection Notice</h2>
                    </div>
                    <div class="content">
                        <p>Hello <strong>{creator.full_name or creator.username}</strong>,</p>
                        
                        <p>We regret to inform you that your article has been rejected:</p>
                        
                        <h3 style="color: #0066cc;">{news.title}</h3>
                        
                        <div class="reason-box">
                            <strong>Rejection reason:</strong>
                            <p style="margin-top: 10px; white-space: pre-wrap;">{reason}</p>
                        </div>
                        
                        <p>You can review your article at the following link:</p>
                        <div style="text-align: center;">
                            <a href="{article_url}" class="article-link">View Article</a>
                        </div>
                        
                        <p>Please review your article and make the necessary changes based on the feedback above before resubmitting for approval.</p>
                        
                        <p>Best regards,<br>
                        <strong>VnNews Editorial Team</strong></p>
                    </div>
                    <div class="footer">
                        <p>This is an automated email. Please do not reply to this email.</p>
                        <p>© 2024 VnNews. All rights reserved.</p>
                    </div>
                </body>
                </html>
                """
                
                # Gửi email
                email_sent = send_email(
                    to_email=creator.email,
                    subject=email_subject,
                    body_html=email_body_html
                )
                
                if not email_sent:
                    print(f"Warning: Không thể gửi email từ chối đến {creator.email}")
                
            except Exception as e:
                print(f"Error sending rejection email: {str(e)}")
                # Vẫn tiếp tục dù email không gửi được
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({
                'success': True, 
                'message': 'Đã từ chối bài viết quốc tế và gửi email cho tác giả',
                'reason': reason
            })
        
        flash('Đã từ chối bài viết quốc tế và gửi email cho tác giả', 'success')
        return redirect(request.referrer or url_for('admin.dashboard'))
    
    def international_news_delete(self, news_id: int):
        """
        Xóa mềm bài viết quốc tế (soft delete) - set is_deleted = True
        Route: POST /admin/international/<news_id>/delete
        """
        from database import NewsInternational
        article = self.db_session.query(NewsInternational).filter(NewsInternational.id == news_id).first()
        
        if not article:
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'error': 'Không tìm thấy bài viết'}), 404
            flash('Không tìm thấy bài viết', 'error')
            return redirect(request.referrer or url_for('admin.dashboard'))
        
        # Soft delete - set is_deleted = True
        article.is_deleted = True
        article.updated_at = datetime.utcnow()
        self.db_session.commit()
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': True, 'message': 'Đã xóa bài viết quốc tế'})
        
        flash('Đã xóa bài viết quốc tế', 'success')
        return redirect(request.referrer or url_for('admin.dashboard'))
    
    def international_news_submit(self, news_id: int):
        """
        Gửi bài viết quốc tế nháp để duyệt (chuyển từ DRAFT sang PENDING)
        Route: POST /admin/international/<news_id>/submit
        """
        from database import NewsInternational, NewsStatus
        article = self.db_session.query(NewsInternational).filter(NewsInternational.id == news_id).first()
        
        if not article:
            return jsonify({'success': False, 'error': 'Không tìm thấy bài viết'}), 404
        
        if article.status != NewsStatus.DRAFT:
            return jsonify({'success': False, 'error': 'Chỉ có thể gửi bài viết nháp để duyệt'}), 400
        
        article.status = NewsStatus.PENDING
        article.updated_at = datetime.utcnow()
        self.db_session.commit()
        
        return jsonify({'success': True, 'message': 'Đã gửi bài viết để duyệt'})
    
    def api_edit_international_article(self, article_id: int):
        """API chỉnh sửa bài viết quốc tế theo ID"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
        
        from database import NewsInternational, CategoryInternational, NewsStatus
        article = self.db_session.query(NewsInternational).filter(NewsInternational.id == article_id).first()
        if not article:
            return jsonify({'success': False, 'error': 'Bài viết không tồn tại'}), 400
        
        data = request.json if request.is_json else request.form
        
        # Lấy dữ liệu từ form
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        category_id = data.get('category_id') or data.get('category')
        summary = data.get('summary') or data.get('description', '').strip()
        thumbnail = data.get('thumbnail', '').strip()
        status = data.get('status', article.status.value)
        
        # Validation
        if not title:
            return jsonify({'success': False, 'error': 'Vui lòng nhập tiêu đề bài viết'}), 400
        
        if not content:
            return jsonify({'success': False, 'error': 'Vui lòng nhập nội dung bài viết'}), 400
        
        if not category_id:
            return jsonify({'success': False, 'error': 'Vui lòng chọn danh mục'}), 400
        
        try:
            category_id = int(category_id)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Danh mục không hợp lệ'}), 400
        
        # Kiểm tra category tồn tại
        category = self.db_session.query(CategoryInternational).filter(CategoryInternational.id == category_id).first()
        if not category:
            return jsonify({'success': False, 'error': 'Danh mục không tồn tại'}), 400
        
        try:
            news_status = NewsStatus(status)
        except ValueError:
            news_status = article.status
        
        # Tạo slug từ tiêu đề
        base_slug = self._generate_slug(title)
        slug = base_slug
        
        # Kiểm tra slug trùng và thêm số nếu cần (nhưng không trùng với chính nó)
        counter = 1
        while self.db_session.query(NewsInternational).filter(NewsInternational.slug == slug, NewsInternational.id != article_id).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Extract images từ HTML content
        import re
        image_urls = []
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
        matches = re.findall(img_pattern, content)
        for img_url in matches:
            if img_url and img_url not in image_urls:
                image_urls.append(img_url)
        
        # Lưu images dưới dạng JSON
        images_json = None
        if image_urls:
            import json
            images_json = json.dumps(image_urls)
        
        try:
            # Cập nhật bài viết
            article.title = title
            article.slug = slug
            article.content = content
            article.summary = summary
            article.thumbnail = thumbnail
            article.images = images_json
            article.category_id = category_id
            article.status = news_status
            article.published_at = datetime.utcnow() if news_status == NewsStatus.PUBLISHED else article.published_at
            article.updated_at = datetime.utcnow()
            
            self.db_session.commit()
            self.db_session.refresh(article)
            
            return jsonify({
                'success': True,
                'message': 'Đã cập nhật bài viết quốc tế',
                'data': {
                    'id': article.id,
                    'title': article.title,
                    'status': article.status.value
                }
            })
        except Exception as e:
            self.db_session.rollback()
            return jsonify({'success': False, 'error': f'Lỗi khi cập nhật bài viết: {str(e)}'}), 500
    
    def api_news_list(self):
        """
        API lấy danh sách bài viết (JSON)
        Route: GET /admin/api/news
        """
        status_filter = request.args.get('status', None)
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        status = None
        if status_filter:
            try:
                status = NewsStatus(status_filter)
            except ValueError:
                pass
        
        news_list = self.news_model.get_all(limit=limit, offset=offset, status=status)
        
        return jsonify({
            'success': True,
            'data': [self._news_to_dict(news) for news in news_list]
        })

    def api_my_articles(self):
        """
        API lấy danh sách bài viết của editor hiện tại (JSON)
        Route: GET /admin/api/my-articles
        Query params:
            status: draft|pending|published|rejected|all (mặc định: all)
            page: trang hiện tại (mặc định: 1)
            per_page: số bài mỗi trang (mặc định: 10)
            search: từ khóa tìm kiếm
        """
        if "user_id" not in session:
            return jsonify({"success": False, "error": "Chưa đăng nhập"}), 401

        user_id = session["user_id"]

        status_str = request.args.get("status", "all")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        search = request.args.get("search", None)

        # Chuẩn hóa tham số
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 10

        status = None
        if status_str and status_str != "all":
            try:
                status = NewsStatus(status_str)
            except ValueError:
                status = None

        offset = (page - 1) * per_page

        items, total = self.news_model.get_by_creator(
            creator_id=user_id,
            limit=per_page,
            offset=offset,
            status=status,
            search=search,
        )

        total_pages = (total + per_page - 1) // per_page if total > 0 else 1

        return jsonify(
            {
                "success": True,
                "data": [self._news_to_dict(news) for news in items],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "pages": total_pages,
                },
            }
        )
    
    def api_current_user(self):
        """
        API lấy thông tin user hiện tại từ session (JSON)
        Route: GET /admin/api/current-user
        """
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Chưa đăng nhập'
            }), 401
        
        user = self.user_model.get_by_id(session['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'error': 'Không tìm thấy user'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'id': user.id,
                'username': user.username,
                'name': user.full_name or user.username,
                'role': user.role.value,
                'email': user.email
            }
        })
    
    def api_editor_notifications(self):
        """
        API lấy các bài viết được duyệt/từ chối gần đây của editor hiện tại (JSON)
        Route: GET /admin/api/editor-notifications
        Query params:
            limit: số lượng bài viết tối đa (mặc định: 20)
        """
        if "user_id" not in session:
            return jsonify({"success": False, "error": "Chưa đăng nhập"}), 401

        user_id = session["user_id"]
        limit = request.args.get("limit", 20, type=int)
        
        if limit < 1 or limit > 100:
            limit = 20

        # Lấy các bài viết được duyệt hoặc từ chối gần đây của editor này
        # Sắp xếp theo published_at (nếu có) hoặc updated_at (khi bị từ chối)
        from sqlalchemy import or_, desc
        
        items = self.db_session.query(News).filter(
            News.created_by == user_id,
            News.is_deleted == False,  # Chỉ lấy bài chưa bị xóa
            or_(
                News.status == NewsStatus.PUBLISHED,
                News.status == NewsStatus.REJECTED
            )
        ).order_by(
            desc(News.published_at),
            desc(News.updated_at)
        ).limit(limit).all()

        notifications = []
        for news in items:
            notification = {
                'id': news.id,
                'title': news.title,
                'status': news.status.value,
                'category_name': news.category.name if getattr(news, "category", None) else None,
                'published_at': news.published_at.isoformat() if news.published_at else None,
                'updated_at': news.updated_at.isoformat() if news.updated_at else None,
                'approved_by': news.approver.username if getattr(news, "approver", None) else None,
            }
            notifications.append(notification)

        return jsonify({
            "success": True,
            "data": notifications,
            "count": len(notifications)
        })
    
    def _news_to_dict(self, news) -> dict:
        """Chuyển đổi News object thành dictionary dùng chung cho admin & client"""
        return {
            'id': news.id,
            'title': news.title,
            'slug': news.slug,
            'status': news.status.value if getattr(news, "status", None) else None,
            # Thông tin danh mục
            'category': {
                'id': news.category.id if getattr(news, "category", None) else None,
                'name': news.category.name if getattr(news, "category", None) else None,
                'slug': news.category.slug if getattr(news, "category", None) else None,
            },
            # Các field phẳng phục vụ cho UI editor & client
            'category_name': news.category.name if getattr(news, "category", None) else None,
            'summary': getattr(news, "summary", None),
            'thumbnail': getattr(news, "thumbnail", None),
            'visible': getattr(news, "visible", True),
            'created_by': news.creator.username if getattr(news, "creator", None) else None,
            'approved_by': news.approver.username if getattr(news, "approver", None) else None,
            'view_count': getattr(news, "view_count", 0),
            'created_at': news.created_at.isoformat() if getattr(news, "created_at", None) else None,
            'published_at': news.published_at.isoformat() if getattr(news, "published_at", None) else None,
        }
    
    def api_statistics(self):
        """API lấy thống kê dashboard"""
        from sqlalchemy import func
        
        # Đếm số lượng bài viết theo trạng thái
        pending_count = self.db_session.query(func.count(News.id)).filter(
            News.status == NewsStatus.PENDING
        ).scalar() or 0
        
        approved_count = self.db_session.query(func.count(News.id)).filter(
            News.status == NewsStatus.PUBLISHED
        ).scalar() or 0
        
        rejected_count = self.db_session.query(func.count(News.id)).filter(
            News.status == NewsStatus.REJECTED
        ).scalar() or 0
        
        api_pending_count = self.db_session.query(func.count(NewsInternational.id)).filter(NewsInternational.is_api == True, NewsInternational.status == NewsStatus.PENDING).scalar() or 0
        api_approved_count = self.db_session.query(func.count(NewsInternational.id)).filter(NewsInternational.is_api == True, NewsInternational.status == NewsStatus.PUBLISHED).scalar() or 0
        api_rejected_count = self.db_session.query(func.count(NewsInternational.id)).filter(NewsInternational.is_api == True, NewsInternational.status == NewsStatus.REJECTED).scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'pending': pending_count,
                'approved': approved_count,
                'rejected': rejected_count,
                'api_pending': api_pending_count,
                'api_approved': api_approved_count,
                'api_rejected': api_rejected_count
            }
        })
    
    def api_statistics_editor(self):
        """API lấy thống kê dashboard của editor"""
        from sqlalchemy import func
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
        
        total = self.db_session.query(func.count(News.id)).filter(
            News.created_by == user_id
        ).scalar() or 0
        
        pending_count = self.db_session.query(func.count(News.id)).filter(
            News.created_by == user_id, News.status == NewsStatus.PENDING
        ).scalar() or 0
        
        approved_count = self.db_session.query(func.count(News.id)).filter(
            News.created_by == user_id, News.status == NewsStatus.PUBLISHED
        ).scalar() or 0
        
        published_count = self.db_session.query(func.count(News.id)).filter(
            News.created_by == user_id, News.status == NewsStatus.PUBLISHED
        ).scalar() or 0
        
        rejected_count = self.db_session.query(func.count(News.id)).filter(
            News.created_by == user_id, News.status == NewsStatus.REJECTED
        ).scalar() or 0
        
        draft_count = self.db_session.query(func.count(News.id)).filter(
            News.created_by == user_id, News.status == NewsStatus.DRAFT
        ).scalar() or 0

        article_approved = self.db_session.query(News).filter(
            News.created_by == user_id, News.status == NewsStatus.PUBLISHED
        ).order_by(News.published_at.desc()).first()

        article_update = self.db_session.query(News).filter(
            News.created_by == user_id, News.status == NewsStatus.DRAFT, News.updated_at > News.created_at
        ).order_by(News.created_at.desc()).first()

        article_newest = self.db_session.query(News).filter(
            News.created_by == user_id
        ).order_by(News.created_at.desc()).first()

        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'pending': pending_count,
                'published': published_count,
                'rejected': rejected_count,
                'approved': approved_count,
                'draft': draft_count,
                'article_approved': article_approved.title if article_approved else '',
                'article_update': article_update.title if article_update else '',
                'article_newest': article_newest.title if article_newest else ''
            }
        })

    def api_pending_articles(self):
        """API lấy danh sách bài viết chờ duyệt"""
        articles = self.news_model.get_all(status=NewsStatus.PENDING, limit=100)
        
        return jsonify({
            'success': True,
            'data': [{
                'id': article.id,
                'title': article.title,
                'author': article.creator.username if article.creator else 'N/A',
                'category': article.category.name if article.category else 'N/A',
                'date': article.created_at.strftime('%d/%m/%Y %H:%M') if article.created_at else '',
                'status': article.status.value
            } for article in articles]
        })
    
    def api_approved_articles(self):
        """API lấy danh sách bài viết đã duyệt"""
        articles = self.news_model.get_all(status=NewsStatus.PUBLISHED, limit=100)
        
        return jsonify({
            'success': True,
            'data': [{
                'id': article.id,
                'title': article.title,
                'author': article.creator.username if article.creator else 'N/A',
                'category': article.category.name if article.category else 'N/A',
                'date': article.published_at.strftime('%d/%m/%Y %H:%M') if article.published_at else '',
                'views': article.view_count
            } for article in articles]
        })
    
    def api_rejected_articles(self):
        """API lấy danh sách bài viết bị từ chối (bao gồm cả news và news_international)"""
        # Lấy bài viết trong nước bị từ chối
        news_articles = self.news_model.get_all(status=NewsStatus.REJECTED, limit=100)
        
        # Lấy bài viết quốc tế bị từ chối
        int_articles = self.int_news_model.get_all(status=NewsStatus.REJECTED, limit=100)
        
        # Lấy thông tin từ chối từ database
        news_ids = [a.id for a in news_articles]
        int_news_ids = [a.id for a in int_articles]
        
        # Query rejection reasons
        news_rejections = {}
        if news_ids:
            rejections = self.db_session.query(NewsRejection).filter(
                NewsRejection.news_id.in_(news_ids)
            ).order_by(NewsRejection.created_at.desc()).all()
            # Lấy rejection mới nhất cho mỗi bài viết
            for rej in rejections:
                if rej.news_id not in news_rejections:
                    news_rejections[rej.news_id] = {
                        'reason': rej.reason,
                        'rejected_by': rej.rejector.username if rej.rejector else 'N/A',
                        'rejected_at': rej.created_at.strftime('%d/%m/%Y %H:%M') if rej.created_at else ''
                    }
        
        int_rejections = {}
        if int_news_ids:
            rejections = self.db_session.query(NewsInternationalRejection).filter(
                NewsInternationalRejection.news_international_id.in_(int_news_ids)
            ).order_by(NewsInternationalRejection.created_at.desc()).all()
            # Lấy rejection mới nhất cho mỗi bài viết
            for rej in rejections:
                if rej.news_international_id not in int_rejections:
                    int_rejections[rej.news_international_id] = {
                        'reason': rej.reason,
                        'rejected_by': rej.rejector.username if rej.rejector else 'N/A',
                        'rejected_at': rej.created_at.strftime('%d/%m/%Y %H:%M') if rej.created_at else ''
                    }
        
        # Tạo danh sách kết quả
        data = []
        
        # Thêm bài viết trong nước
        for article in news_articles:
            rejection_info = news_rejections.get(article.id, {})
            data.append({
                'id': article.id,
                'title': article.title,
                'author': article.creator.username if article.creator else 'N/A',
                'category': article.category.name if article.category else 'N/A',
                'date': article.created_at.strftime('%d/%m/%Y %H:%M') if article.created_at else '',
                'type': 'news',
                'rejection_reason': rejection_info.get('reason', ''),
                'rejected_by': rejection_info.get('rejected_by', ''),
                'rejected_at': rejection_info.get('rejected_at', '')
            })
        
        # Thêm bài viết quốc tế
        for article in int_articles:
            rejection_info = int_rejections.get(article.id, {})
            data.append({
                'id': article.id,
                'title': article.title,
                'author': article.creator.username if article.creator else 'N/A',
                'category': article.category.name if article.category else 'N/A',
                'date': article.created_at.strftime('%d/%m/%Y %H:%M') if article.created_at else '',
                'type': 'international',
                'rejection_reason': rejection_info.get('reason', ''),
                'rejected_by': rejection_info.get('rejected_by', ''),
                'rejected_at': rejection_info.get('rejected_at', '')
            })
        
        # Sắp xếp theo ngày từ chối hoặc ngày tạo
        data.sort(key=lambda x: x.get('rejected_at', x.get('date', '')), reverse=True)
        
        return jsonify({
            'success': True,
            'data': data
        })
    
    def api_rejected_article(self, article_id: int):
        # Query rejection reasons
        if article_id:
            article = self.news_model.get_by_id(article_id)
            if article:
                rejection = self.db_session.query(NewsRejection).filter(
                    NewsRejection.news_id == article_id
                ).first()
                if rejection:
                    return jsonify({
                        'success': True,
                        'id': article.id,
                        'title': article.title,
                        'author': article.creator.username if article.creator else 'N/A',
                        'category': article.category.name if article.category else 'N/A',
                        'date': article.created_at.strftime('%d/%m/%Y %H:%M') if article.created_at else '',
                        'type': 'news',
                        'rejection_reason': rejection.reason,
                        'rejected_by': rejection.rejector.username if rejection.rejector else 'N/A',
                        'rejected_at': rejection.created_at.strftime('%d/%m/%Y %H:%M') if rejection.created_at else ''
                    })
                else:
                    return jsonify({'success': False, 'error': 'Không tìm thấy lý do từ chối'}), 404
            else:
                return jsonify({'success': False, 'error': 'Bài viết không tồn tại'}), 404

    def api_api_articles(self):
        """API lấy danh sách bài viết từ API bên ngoài (chỉ hiển thị, không lưu)"""
        # Lấy dữ liệu từ session hoặc cache (tạm thời lưu trong session)
        # Hoặc fetch lại từ API nếu cần
        api_articles = session.get('api_articles_cache', [])
        
        return jsonify({
            'success': True,
            'data': api_articles
        })
    
    def api_international_articles(self):
        """API lấy danh sách bài viết quốc tế (đã duyệt) từ bảng NewsInternational"""
        articles = (
            self.db_session.query(NewsInternational)
            .join(CategoryInternational)
            .filter(
                NewsInternational.status == NewsStatus.PUBLISHED,
                NewsInternational.is_deleted == False  # Chỉ lấy bài chưa bị xóa
            )
            .order_by(NewsInternational.published_at.desc())
            .limit(100)
            .all()
        )

        return jsonify({
            'success': True,
            'data': [{
                'id': article.id,
                'title': article.title,
                'category': article.category.name if article.category else 'N/A',
                'author': article.author if article.is_api and article.author else (article.creator.username if article.creator else 'N/A'),
                'approver': article.approver.username if article.approver else 'N/A',
                'is_api': article.is_api,
                'status': 'Approved',
                'views': article.view_count,
                'published': article.published_at.strftime('%d/%m/%Y %H:%M') if article.published_at else ''
            } for article in articles]
        })
    
    def api_international_pending(self):
        """API lấy danh sách bài viết quốc tế chờ duyệt từ bảng NewsInternational"""
        articles = (
            self.db_session.query(NewsInternational)
            .join(CategoryInternational)
            .filter(
                NewsInternational.status == NewsStatus.PENDING,
                NewsInternational.is_deleted == False  # Chỉ lấy bài chưa bị xóa
            )
            .order_by(NewsInternational.created_at.desc())
            .limit(100)
            .all()
        )

        return jsonify({
            'success': True,
            'data': [{
                'id': article.id,
                'title': article.title,
                'category': article.category.name if article.category else 'N/A',
                'author': article.author if article.is_api and article.author else (article.creator.username if article.creator else 'N/A'),
                'approver': article.approver.username if article.approver else None,
                'is_api': article.is_api,
                'submitted': article.created_at.strftime('%d/%m/%Y %H:%M') if article.created_at else ''
            } for article in articles]
        })
    
    def api_international_drafts(self):
        """API lấy danh sách bài viết quốc tế nháp từ bảng NewsInternational"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
        
        search = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = (
            self.db_session.query(NewsInternational)
            .join(CategoryInternational)
            .filter(
                NewsInternational.status == NewsStatus.DRAFT,
                NewsInternational.created_by == user_id,  # Chỉ lấy bài của editor hiện tại
                NewsInternational.is_deleted == False  # Chỉ lấy bài chưa bị xóa
            )
        )
        
        # Tìm kiếm theo title nếu có
        if search:
            query = query.filter(NewsInternational.title.ilike(f'%{search}%'))
        
        total = query.count()
        articles = query.order_by(NewsInternational.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

        return jsonify({
            'success': True,
            'data': [{
                'id': article.id,
                'title': article.title,
                'category': article.category.name if article.category else 'N/A',
                'category_id': article.category_id,
                'author': article.author if article.is_api and article.author else (article.creator.username if article.creator else 'N/A'),
                'is_api': article.is_api,
                'created_at': article.created_at.strftime('%d/%m/%Y %H:%M') if article.created_at else '',
                'status': article.status.value
            } for article in articles],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
    
    def api_my_international_articles(self):
        """API lấy danh sách bài viết quốc tế của editor hiện tại"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', None)
        search = request.args.get('search', '').strip()
        
        query = (
            self.db_session.query(NewsInternational)
            .join(CategoryInternational)
            .filter(
                NewsInternational.created_by == user_id,
                NewsInternational.is_deleted == False  # Chỉ lấy bài chưa bị xóa
            )
        )
        
        # Lọc theo status nếu có
        if status and status != 'all':
            try:
                status_enum = NewsStatus(status)
                query = query.filter(NewsInternational.status == status_enum)
            except ValueError:
                pass
        
        # Tìm kiếm theo title nếu có
        if search:
            query = query.filter(NewsInternational.title.ilike(f'%{search}%'))
        
        total = query.count()
        articles = query.order_by(NewsInternational.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': article.id,
                'title': article.title,
                'category': article.category.name if article.category else 'N/A',
                'category_id': article.category_id,
                'status': article.status.value,
                'created_at': article.created_at.strftime('%d/%m/%Y %H:%M') if article.created_at else '',
                'published_at': article.published_at.strftime('%d/%m/%Y %H:%M') if article.published_at else '',
                'view_count': article.view_count or 0
            } for article in articles],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
    
    def api_international_pending_editor(self):
        """API lấy danh sách bài viết quốc tế chờ duyệt của editor"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
        
        search = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = (
            self.db_session.query(NewsInternational)
            .join(CategoryInternational)
            .filter(
                NewsInternational.status == NewsStatus.PENDING,
                NewsInternational.created_by == user_id,  # Chỉ lấy bài của editor hiện tại
                NewsInternational.is_deleted == False  # Chỉ lấy bài chưa bị xóa
            )
        )
        
        if search:
            query = query.filter(NewsInternational.title.ilike(f'%{search}%'))
        
        total = query.count()
        articles = query.order_by(NewsInternational.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': article.id,
                'title': article.title,
                'category': article.category.name if article.category else 'N/A',
                'category_id': article.category_id,
                'status': article.status.value,
                'created_at': article.created_at.strftime('%d/%m/%Y %H:%M') if article.created_at else '',
                'submitted': article.created_at.strftime('%d/%m/%Y %H:%M') if article.created_at else ''
            } for article in articles],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
    
    def api_international_published_editor(self):
        """API lấy danh sách bài viết quốc tế đã xuất bản của editor"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
        
        search = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = (
            self.db_session.query(NewsInternational)
            .join(CategoryInternational)
            .filter(
                NewsInternational.status == NewsStatus.PUBLISHED,
                NewsInternational.created_by == user_id,  # Chỉ lấy bài của editor hiện tại
                NewsInternational.is_deleted == False  # Chỉ lấy bài chưa bị xóa
            )
        )
        
        if search:
            query = query.filter(NewsInternational.title.ilike(f'%{search}%'))
        
        total = query.count()
        articles = query.order_by(NewsInternational.published_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': article.id,
                'title': article.title,
                'category': article.category.name if article.category else 'N/A',
                'category_id': article.category_id,
                'published_at': article.published_at.strftime('%d/%m/%Y %H:%M') if article.published_at else '',
                'view_count': article.view_count or 0
            } for article in articles],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
    
    def api_fetch_api_news(self):
        """API lấy bài viết mới từ RSS Feed hoặc API bên ngoài"""
        import feedparser
        import requests
        from datetime import datetime, timedelta
        import re
        
        try:
            # Lấy thông tin từ request
            data = request.json if request.is_json else {}
            source_type = data.get('source_type', 'rss')  # 'rss' hoặc 'api'
            rss_url = data.get('rss_url', 'https://vnexpress.net/rss/tin-moi-nhat.rss')
            
            # Lấy API token từ settings hoặc từ request (nếu user muốn override)
            api_token = data.get('api_key')
            if not api_token:
                # Lấy từ settings nếu không có trong request
                token_setting = self.db_session.query(Setting).filter(
                    Setting.key == 'api_token'
                ).first()
                api_token = token_setting.value if token_setting else None
            
            urls = data.get('urls', [])  # Danh sách URLs để fetch
            region = data.get('region', 'domestic')  # 'domestic' hoặc 'international'
            category_id = data.get('category_id', '')  # ID danh mục
            limit = data.get('limit', 20)
            
            articles = []
            
            # Nếu là RSS feed
            if source_type == 'rss' and rss_url:
                try:
                    feed = feedparser.parse(rss_url)
                    
                    if feed.bozo and feed.bozo_exception:
                        return jsonify({
                            'success': False,
                            'error': f'Lỗi parse RSS: {feed.bozo_exception}'
                        }), 400
                    
                    for entry in feed.entries[:limit]:
                        # Extract image từ description hoặc enclosure
                        image_url = ''
                        if 'enclosures' in entry and entry.enclosures:
                            image_url = entry.enclosures[0].get('url', '')
                        elif 'media_content' in entry and entry.media_content:
                            image_url = entry.media_content[0].get('url', '')
                        else:
                            # Try to extract image from description HTML
                            desc = entry.get('description', '')
                            img_match = re.search(r'<img[^>]+src="([^"]+)"', desc)
                            if img_match:
                                image_url = img_match.group(1)
                        
                        # Clean description HTML tags
                        description = entry.get('description', '')
                        description = re.sub(r'<[^>]+>', '', description)
                        description = description.replace('&nbsp;', ' ').strip()
                        
                        articles.append({
                            'title': entry.get('title', 'No title'),
                            'description': description[:500] if description else 'No description',
                            'url': entry.get('link', ''),
                            'urlToImage': image_url,
                            'source': {'name': feed.feed.get('title', 'RSS Feed')},
                            'author': entry.get('author', 'Unknown'),
                            'publishedAt': entry.get('published', datetime.utcnow().isoformat()),
                            'content': description
                        })
                    
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'error': f'Lỗi fetch RSS: {str(e)}'
                    }), 500
            
            # Nếu là API với token
            elif source_type == 'api' and api_token:
                try:
                    # Kiểm tra mode
                    mode = data.get('mode', 'urls')
                    headers = {
                        'Authorization': f'Bearer {api_token}',
                        'Content-Type': 'application/json'
                    }
                    
                    if mode == 'category':
                        # Mode: Theo khu vực & danh mục - Gọi 2 endpoints tuần tự
                        if not category_id:
                            return jsonify({
                                'success': False,
                                'error': 'Vui lòng chọn danh mục'
                            }), 400
                        
                        # Bước 1: Gọi endpoint để lấy danh sách URLs
                        rss_endpoint = f'https://news-api.techreview.pro/rss/{category_id}/urls'
                        rss_params = {'limit': limit}
                        if region == 'international':
                            rss_params['source'] = 'en'
                        
                        rss_response = requests.get(rss_endpoint, headers=headers, params=rss_params, timeout=30)
                        
                        if rss_response.status_code != 200:
                            return jsonify({
                                'success': False,
                                'error': f'Lỗi lấy danh sách URLs: {rss_response.status_code}'
                            }), rss_response.status_code
                        
                        rss_data = rss_response.json()
                        if not rss_data.get('success') or not rss_data.get('data', {}).get('urls'):
                            return jsonify({
                                'success': False,
                                'error': 'Không tìm thấy URLs từ danh mục này'
                            }), 400
                        
                        # Lấy danh sách URLs từ response
                        urls = rss_data['data']['urls']
                        
                        # Bước 2: Gọi endpoint articles với URLs vừa lấy được
                        api_endpoint = 'https://news-api.techreview.pro/articles'
                        payload = {'urls': urls}
                        
                    elif mode == 'urls':
                        # Mode: Theo danh sách URL
                        if not urls:
                            return jsonify({
                                'success': False,
                                'error': 'Vui lòng cung cấp danh sách URLs'
                            }), 400
                        
                        api_endpoint = 'https://news-api.techreview.pro/articles'
                        payload = {'urls': urls}
                        
                    else:
                        return jsonify({
                            'success': False,
                            'error': 'Mode không hợp lệ'
                        }), 400
                    
                    response = requests.post(api_endpoint, json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        api_data = response.json()
                        
                        # Kiểm tra response format
                        if api_data.get('success') and api_data.get('data', {}).get('articles'):
                            api_articles = api_data['data']['articles']
                            
                            # Format articles theo cấu trúc mới
                            for api_article in api_articles[:limit]:
                                # Parse description array - bao gồm cả text và image theo đúng thứ tự
                                description_items = api_article.get('description', [])
                                description_html_parts = []
                                description_texts = []
                                
                                for item in description_items:
                                    if isinstance(item, dict):
                                        if item.get('type') == 'text':
                                            text_content = item.get('text', '').strip()
                                            if text_content:
                                                description_texts.append(text_content)
                                                description_html_parts.append(f'<p>{text_content}</p>')
                                        elif item.get('type') == 'image':
                                            img_src = item.get('src', '')
                                            img_alt = item.get('alt', '')
                                            if img_src:
                                                description_html_parts.append(f'<img src="{img_src}" alt="{img_alt}" />')
                                
                                # Join text cho summary/description ngắn
                                description_text = ' '.join(description_texts)
                                # Join HTML cho content đầy đủ với cả hình ảnh
                                description_html = '\n'.join(description_html_parts)
                                
                                # Lấy main image hoặc first image
                                main_image = api_article.get('mainImage', '')
                                if not main_image and api_article.get('images'):
                                    first_img = api_article['images'][0]
                                    # Handle new image structure {src, alt}
                                    main_image = first_img.get('src', '') if isinstance(first_img, dict) else first_img
                                
                                # Parse images array - extract src từ objects
                                images_data = api_article.get('images', [])
                                image_urls = []
                                for img in images_data:
                                    if isinstance(img, dict):
                                        img_src = img.get('src', '')
                                        if img_src:
                                            image_urls.append(img_src)
                                    elif isinstance(img, str):
                                        image_urls.append(img)
                                
                                articles.append({
                                    'title': api_article.get('title', 'No title'),
                                    'description': api_article.get('summary', description_text[:500]),
                                    'url': api_article.get('link', ''),
                                    'urlToImage': main_image,
                                    'source': {'name': 'Custom API'},
                                    'author': api_article.get('author', 'Unknown'),
                                    'publishedAt': api_article.get('pubDate', datetime.utcnow().isoformat()),
                                    'content': description_html,  # Sử dụng HTML với cả text và images
                                    'images': image_urls
                                })
                        else:
                            return jsonify({
                                'success': False,
                                'error': f"API trả về lỗi: {api_data.get('message', 'Unknown error')}"
                            }), 400
                            
                    elif response.status_code == 401:
                        return jsonify({
                            'success': False,
                            'error': 'API token không hợp lệ hoặc đã hết hạn'
                        }), 401
                    else:
                        return jsonify({
                            'success': False,
                            'error': f'Lỗi API: {response.status_code} - {response.text}'
                        }), response.status_code
                        
                except requests.exceptions.RequestException as e:
                    return jsonify({
                        'success': False,
                        'error': f'Lỗi kết nối API: {str(e)}'
                    }), 500
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'error': f'Lỗi khi fetch từ API: {str(e)}'
                    }), 500
            
            # Nếu không có articles
            elif not articles:
                return jsonify({
                    'success': False,
                    'error': 'Không có bài viết nào được tìm thấy'
                }), 400
            
            # Format dữ liệu để trả về
            formatted_articles = []
            for idx, article in enumerate(articles):
                source_name = article.get('source', {}).get('name', 'Unknown') if isinstance(article.get('source'), dict) else str(article.get('source', 'Unknown'))
                published_at = article.get('publishedAt', datetime.utcnow().isoformat())
                
                # Lấy content, nếu là RSS thì fetch full content từ URL
                content = article.get('content', article.get('description', ''))
                article_url = article.get('url', '')
                
                # Nếu là RSS và có URL, fetch full content
                if source_type == 'rss' and article_url:
                    full_content = self._fetch_article_content(article_url)
                    if full_content:
                        content = full_content
                
                # Nếu là API, content đã có đầy đủ rồi
                formatted_articles.append({
                    'id': f'api_{idx}_{datetime.utcnow().timestamp()}',  # Temporary ID
                    'title': article.get('title', 'No title'),
                    'summary': article.get('description', ''),
                    'content': content,
                    'thumbnail': article.get('urlToImage', ''),
                    'source': source_name,
                    'source_url': article_url,
                    'author': article.get('author', 'Unknown'),
                    'published_at': published_at,
                    'images': article.get('images', [])  # Thêm images array cho API articles
                })
            
            # Lưu vào session để sử dụng sau (tạm thời)
            session['api_articles_cache'] = formatted_articles
            
            return jsonify({
                'success': True,
                'message': f'Đã lấy {len(formatted_articles)} bài viết',
                'count': len(formatted_articles),
                'data': formatted_articles
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def api_save_api_article(self):
        """API lưu bài viết từ API vào bảng news hoặc news_international tùy theo region"""
        # Tạo session mới để tránh lỗi "transaction closed"
        db_session = get_session()
        
        try:
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
            
            data = request.json if request.is_json else request.form
            
            # Lấy dữ liệu bài viết từ request
            article_data = data.get('article')
            if not article_data:
                return jsonify({'success': False, 'error': 'Thiếu dữ liệu bài viết'}), 400
            
            # Lấy thông tin từ request
            category_id = data.get('category_id')
            if category_id:
                category_id = int(category_id)
            
            status = data.get('status', NewsStatus.DRAFT.value)
            region = data.get('region', 'domestic')  # domestic hoặc international
            is_hot = data.get('is_hot', False)
            is_featured = data.get('is_featured', False)
            
            # Convert to boolean nếu là string
            if isinstance(is_hot, str):
                is_hot = is_hot.lower() in ('true', '1', 'yes', 'on')
            if isinstance(is_featured, str):
                is_featured = is_featured.lower() in ('true', '1', 'yes', 'on')
            
            if not category_id:
                return jsonify({'success': False, 'error': 'Vui lòng chọn danh mục'}), 400
            
            try:
                news_status = NewsStatus(status)
            except ValueError:
                news_status = NewsStatus.DRAFT
            
            # Kiểm tra category tồn tại theo region
            if region == 'international':
                category = db_session.query(CategoryInternational).filter(CategoryInternational.id == category_id).first()
                if not category:
                    return jsonify({'success': False, 'error': 'Danh mục quốc tế không tồn tại'}), 400
            else:
                category = db_session.query(Category).filter(Category.id == category_id).first()
                if not category:
                    return jsonify({'success': False, 'error': 'Danh mục không tồn tại'}), 400
            
            # Parse published_at nếu có
            published_at = None
            if article_data.get('published_at'):
                try:
                    from dateutil import parser
                    published_at = parser.parse(article_data['published_at'])
                except:
                    published_at = datetime.utcnow()
            
            # Tạo slug từ title
            title = article_data.get('title', 'Untitled')
            base_slug = self._generate_slug(title)
            
            # Kiểm tra xem bài viết với slug này đã tồn tại chưa (theo region)
            if region == 'international':
                existing_news = db_session.query(NewsInternational).filter(NewsInternational.slug == base_slug).first()
                if existing_news:
                    return jsonify({
                        'success': False,
                        'error': 'Bài viết quốc tế đã được lưu trước đó'
                    }), 400
                
                # Tạo bài viết quốc tế mới
                news = NewsInternational(
                    title=title,
                    slug=base_slug,
                    summary=article_data.get('summary', ''),
                    content=article_data.get('content', article_data.get('summary', '')),
                    thumbnail=article_data.get('thumbnail'),
                    category_id=category_id,
                    created_by=user_id,
                    approved_by=user_id if news_status == NewsStatus.PUBLISHED else None,
                    status=news_status,
                    is_api=True,  # Đánh dấu bài từ API
                    is_hot=bool(is_hot),
                    is_featured=bool(is_featured),
                    published_at=published_at if news_status == NewsStatus.PUBLISHED else None,
                    author=article_data.get('author'),  # Lưu tác giả gốc từ API
                )
            else:
                existing_news = db_session.query(News).filter(News.slug == base_slug).first()
                if existing_news:
                    return jsonify({
                        'success': False,
                        'error': 'Bài viết đã được lưu trước đó'
                    }), 400
                
                # Tạo bài viết trong nước mới
                news = News(
                    title=title,
                    slug=base_slug,
                    summary=article_data.get('summary', ''),
                    content=article_data.get('content', article_data.get('summary', '')),
                    thumbnail=article_data.get('thumbnail'),
                    category_id=category_id,
                    created_by=user_id,
                    approved_by=user_id if news_status == NewsStatus.PUBLISHED else None,
                    status=news_status,
                    is_api=True,  # Đánh dấu bài từ API
                    is_hot=bool(is_hot),
                    is_featured=bool(is_featured),
                    published_at=published_at if news_status == NewsStatus.PUBLISHED else None,
                    author=article_data.get('author'),
                )
            
            db_session.add(news)
            db_session.commit()
            
            news_id = news.id
            
            # Xóa bài viết vừa lưu khỏi cache session
            api_articles_cache = session.get('api_articles_cache', [])
            article_id = article_data.get('id')
            if article_id:
                # Lọc bỏ bài viết vừa lưu
                api_articles_cache = [a for a in api_articles_cache if a.get('id') != article_id]
                session['api_articles_cache'] = api_articles_cache
            
            message = f'Đã lưu bài viết {"quốc tế" if region == "international" else ""} với trạng thái {news_status.value}'
            
            return jsonify({
                'success': True,
                'message': message,
                'news_id': news_id,
                'article_id': article_id,
                'region': region
            })
            
        except IntegrityError as e:
            db_session.rollback()
            # Lỗi trùng lặp dữ liệu (duplicate key)
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'duplicate key' in error_msg.lower() or 'unique constraint' in error_msg.lower():
                return jsonify({
                    'success': False,
                    'error': 'Bài viết đã được lưu trước đó'
                }), 400
            else:
                return jsonify({
                    'success': False,
                    'error': 'Lỗi khi lưu bài viết'
                }), 500
        except Exception as e:
            db_session.rollback()
            return jsonify({
                'success': False,
                'error': 'Không thể lưu bài viết'
            }), 500
        finally:
            db_session.close()
    
    def api_chart_data(self):
        """API lấy dữ liệu cho biểu đồ"""
        from sqlalchemy import func, extract
        from datetime import datetime, timedelta
        
        # Lấy dữ liệu 7 ngày gần nhất
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        # Đếm bài viết mới theo ngày
        new_articles = self.db_session.query(
            func.date(News.created_at).label('date'),
            func.count(News.id).label('count')
        ).filter(
            News.created_at >= start_date
        ).group_by(func.date(News.created_at)).all()
        
        # Đếm bài được duyệt theo ngày
        approved_articles = self.db_session.query(
            func.date(News.published_at).label('date'),
            func.count(News.id).label('count')
        ).filter(
            News.published_at >= start_date,
            News.status == NewsStatus.PUBLISHED
        ).group_by(func.date(News.published_at)).all()
        
        # Tạo dictionary cho dễ truy cập
        new_dict = {str(item.date): item.count for item in new_articles}
        approved_dict = {str(item.date): item.count for item in approved_articles}
        
        # Tạo labels và data cho 7 ngày
        labels = []
        new_data = []
        approved_data = []
        
        for i in range(7):
            date = (start_date + timedelta(days=i)).date()
            date_str = str(date)
            labels.append(date.strftime('%d/%m'))
            new_data.append(new_dict.get(date_str, 0))
            approved_data.append(approved_dict.get(date_str, 0))
        
        return jsonify({
            'success': True,
            'data': {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Bài viết mới',
                        'data': new_data
                    },
                    {
                        'label': 'Bài được duyệt',
                        'data': approved_data
                    }
                ]
            }
        })
    
    def api_hot_articles(self):
        """API lấy danh sách bài viết hot nhất"""
        articles = self.news_model.get_hot(limit=10)
        
        return jsonify({
            'success': True,
            'data': [{
                'title': article.title,
                'views': article.view_count
            } for article in articles]
        })
    
    def api_article_detail(self, article_id: int):
        """API lấy chi tiết bài viết theo ID"""
        article = self.news_model.get_by_id(article_id)
        
        if not article:
            return jsonify({
                'success': False,
                'message': 'Bài viết không tồn tại'
            }), 404
        
        # Lấy tags từ NewsTag relationship
        news_tags = self.db_session.query(NewsTag).filter(NewsTag.news_id == article.id).all()
        tag_ids = [nt.tag_id for nt in news_tags]
        tags = self.db_session.query(Tag).filter(Tag.id.in_(tag_ids)).all() if tag_ids else []
        tags_list = [f"#{tag.name}" for tag in tags]
        tags_string = ' '.join(tags_list) if tags_list else ''
        
        # Xác định author: nếu là bài từ API thì dùng author field, không thì dùng creator
        author_name = article.author if (hasattr(article, 'is_api') and article.is_api and hasattr(article, 'author') and article.author) else (article.creator.username if article.creator else 'N/A')
        author_full_name = article.author if (hasattr(article, 'is_api') and article.is_api and hasattr(article, 'author') and article.author) else (article.creator.full_name if article.creator and article.creator.full_name else article.creator.username if article.creator else 'N/A')
        
        return jsonify({
            'success': True,
            'data': {
                'id': article.id,
                'title': article.title,
                'slug': article.slug,
                'summary': article.summary or '',
                'content': article.content or '',
                'thumbnail': article.thumbnail or '',
                'category': article.category.name if article.category else 'N/A',
                'category_id': article.category_id,
                'author': author_name,
                'author_full_name': author_full_name,
                'approver': article.approver.username if article.approver else None,
                'approver_full_name': article.approver.full_name if article.approver and article.approver.full_name else (article.approver.username if article.approver else None),
                'is_api': article.is_api if hasattr(article, 'is_api') else False,
                'status': article.status.value,
                'created_at': article.created_at.strftime('%d/%m/%Y %H:%M') if article.created_at else '',
                'published_at': article.published_at.strftime('%d/%m/%Y %H:%M') if article.published_at else '',
                'updated_at': article.updated_at.strftime('%d/%m/%Y %H:%M') if article.updated_at else '',
                'view_count': article.view_count,
                'is_featured': article.is_featured if hasattr(article, 'is_featured') else False,
                'is_hot': article.is_hot if hasattr(article, 'is_hot') else False,
                'is_deleted': article.is_deleted if hasattr(article, 'is_deleted') else False,
                'tags': tags_string
            }
        })
    
    def api_international_article_detail(self, article_id: int):
        """API lấy chi tiết bài viết quốc tế theo ID"""
        from database import NewsInternational
        article = self.db_session.query(NewsInternational).filter(NewsInternational.id == article_id).first()
        
        if not article:
            return jsonify({
                'success': False,
                'message': 'Bài viết không tồn tại'
            }), 404
        
        # Xác định author: nếu là bài từ API thì dùng author field, không thì dùng creator
        author_name = article.author if (article.is_api and article.author) else (article.creator.username if article.creator else 'N/A')
        author_full_name = article.author if (article.is_api and article.author) else (article.creator.full_name if article.creator and article.creator.full_name else article.creator.username if article.creator else 'N/A')
        
        return jsonify({
            'success': True,
            'data': {
                'id': article.id,
                'title': article.title,
                'slug': article.slug,
                'summary': article.summary or '',
                'content': article.content or '',
                'thumbnail': article.thumbnail or '',
                'category': article.category.name if article.category else 'N/A',
                'category_id': article.category_id,
                'author': author_name,
                'author_full_name': author_full_name,
                'approver': article.approver.username if article.approver else None,
                'approver_full_name': article.approver.full_name if article.approver and article.approver.full_name else (article.approver.username if article.approver else None),
                'is_api': article.is_api,
                'status': article.status.value,
                'created_at': article.created_at.strftime('%d/%m/%Y %H:%M') if article.created_at else '',
                'published_at': article.published_at.strftime('%d/%m/%Y %H:%M') if article.published_at else '',
                'updated_at': article.updated_at.strftime('%d/%m/%Y %H:%M') if article.updated_at else '',
                'view_count': article.view_count,
                'is_featured': article.is_featured,
                'is_hot': article.is_hot
            }
        })
    
    def api_categories(self):
        """API lấy danh sách danh mục"""
        categories = self.category_model.get_all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': cat.id,
                'name': cat.name,
                'slug': cat.slug
            } for cat in categories]
        })
    
    def api_tags(self):
        """API lấy danh sách tags để autocomplete"""
        search = request.args.get('search', '').strip()
        
        query = self.db_session.query(Tag).order_by(Tag.name)
        
        if search:
            # Tìm tags có tên chứa search term (không phân biệt hoa thường)
            query = query.filter(Tag.name.ilike(f'%{search}%'))
        
        tags = query.limit(20).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': tag.id,
                'name': tag.name,
                'slug': tag.slug
            } for tag in tags]
        })

    def api_create_tag(self):
        """API tạo hashtag mới"""
        data = request.get_json(silent=True) or {}
        name = (data.get('name') or '').strip()
        slug = (data.get('slug') or '').strip() or None

        if not name:
            return jsonify({'success': False, 'error': 'Tên hashtag không được để trống'}), 400

        # Chuẩn hóa: bỏ dấu # nếu có
        if name.startswith('#'):
            name = name[1:]

        # Nếu không truyền slug, tự sinh từ name
        if not slug:
            slug = self._generate_slug(name)

        try:
            # Kiểm tra trùng slug
            existing = self.db_session.query(Tag).filter(Tag.slug == slug).first()
            if existing:
                return jsonify({'success': False, 'error': 'Hashtag đã tồn tại'}), 400

            tag = Tag(name=name, slug=slug)
            self.db_session.add(tag)
            self.db_session.commit()

            return jsonify({
                'success': True,
                'data': {
                    'id': tag.id,
                    'name': tag.name,
                    'slug': tag.slug
                }
            })
        except SQLAlchemyError as e:
            self.db_session.rollback()
            current_app.logger.exception('Lỗi tạo hashtag: %s', e)
            return jsonify({'success': False, 'error': 'Không thể tạo hashtag'}), 500

    def api_update_tag(self, tag_id: int):
        """API cập nhật hashtag"""
        data = request.get_json(silent=True) or {}
        name = (data.get('name') or '').strip()
        slug = (data.get('slug') or '').strip() or None

        if not name:
            return jsonify({'success': False, 'error': 'Tên hashtag không được để trống'}), 400

        if name.startswith('#'):
            name = name[1:]

        if not slug:
            slug = self._generate_slug(name)

        try:
            tag = self.db_session.query(Tag).filter(Tag.id == tag_id).first()
            if not tag:
                return jsonify({'success': False, 'error': 'Không tìm thấy hashtag'}), 404

            # Kiểm tra slug trùng với tag khác
            existing = self.db_session.query(Tag).filter(Tag.slug == slug, Tag.id != tag_id).first()
            if existing:
                return jsonify({'success': False, 'error': 'Slug đã được dùng bởi hashtag khác'}), 400

            tag.name = name
            tag.slug = slug
            self.db_session.commit()

            return jsonify({
                'success': True,
                'data': {
                    'id': tag.id,
                    'name': tag.name,
                    'slug': tag.slug
                }
            })
        except SQLAlchemyError as e:
            self.db_session.rollback()
            current_app.logger.exception('Lỗi cập nhật hashtag: %s', e)
            return jsonify({'success': False, 'error': 'Không thể cập nhật hashtag'}), 500

    def api_delete_tag(self, tag_id: int):
        """API xóa hashtag"""
        try:
            tag = self.db_session.query(Tag).filter(Tag.id == tag_id).first()
            if not tag:
                return jsonify({'success': False, 'error': 'Không tìm thấy hashtag'}), 404

            # Xóa liên kết NewsTag trước khi xóa tag
            self.db_session.query(NewsTag).where(NewsTag.tag_id == tag_id).delete()
            self.db_session.delete(tag)
            self.db_session.commit()

            return jsonify({'success': True})
        except SQLAlchemyError as e:
            self.db_session.rollback()
            current_app.logger.exception('Lỗi xóa hashtag: %s', e)
            return jsonify({'success': False, 'error': 'Không thể xóa hashtag'}), 500

    def api_international_categories(self):
        """API lấy danh sách danh mục tin quốc tế (categories_international)"""
        categories = self.int_category_model.get_all()

        return jsonify({
            'success': True,
            'data': [{
                'id': cat.id,
                'name': cat.name,
                'slug': cat.slug,
            } for cat in categories]
        })
    
    def _parse_tags(self, tags_string: str) -> list:
        """Parse tags từ string có thể chứa hashtag format (#tag_name), comma-separated hoặc cách nhau bằng khoảng trắng"""
        import re
        tag_names = []

        if not tags_string:
            return []
        
        # Tách theo dấu phẩy, dấu chấm phẩy HOẶC khoảng trắng
        parts = re.split(r'[,\s;]+', tags_string)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Nếu có dấu # ở đầu, loại bỏ nó
            if part.startswith('#'):
                part = part[1:]
            
            # Loại bỏ các ký tự đặc biệt không hợp lệ
            part = re.sub(r'[^\w\s-]', '', part)
            part = part.strip()
            
            if part:
                tag_names.append(part)
        
        # Loại bỏ trùng lặp và trả về
        return list(dict.fromkeys(tag_names))
    
    def _generate_slug(self, title: str, status: str = None) -> str:
        """Tạo slug từ tiêu đề và trạng thái"""
        import re
        
        # Mapping tiếng Việt sang không dấu
        vietnamese_map = {
            'à': 'a', 'á': 'a', 'ạ': 'a', 'ả': 'a', 'ã': 'a', 'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ậ': 'a', 'ẩ': 'a', 'ẫ': 'a',
            'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ặ': 'a', 'ẳ': 'a', 'ẵ': 'a',
            'è': 'e', 'é': 'e', 'ẹ': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ê': 'e', 'ề': 'e', 'ế': 'e', 'ệ': 'e', 'ể': 'e', 'ễ': 'e',
            'ì': 'i', 'í': 'i', 'ị': 'i', 'ỉ': 'i', 'ĩ': 'i',
            'ò': 'o', 'ó': 'o', 'ọ': 'o', 'ỏ': 'o', 'õ': 'o', 'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ộ': 'o', 'ổ': 'o', 'ỗ': 'o',
            'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ợ': 'o', 'ở': 'o', 'ỡ': 'o',
            'ù': 'u', 'ú': 'u', 'ụ': 'u', 'ủ': 'u', 'ũ': 'u', 'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ự': 'u', 'ử': 'u', 'ữ': 'u',
            'ỳ': 'y', 'ý': 'y', 'ỵ': 'y', 'ỷ': 'y', 'ỹ': 'y',
            'đ': 'd',
            'À': 'a', 'Á': 'a', 'Ạ': 'a', 'Ả': 'a', 'Ã': 'a', 'Â': 'a', 'Ầ': 'a', 'Ấ': 'a', 'Ậ': 'a', 'Ẩ': 'a', 'Ẫ': 'a',
            'Ă': 'a', 'Ằ': 'a', 'Ắ': 'a', 'Ặ': 'a', 'Ẳ': 'a', 'Ẵ': 'a',
            'È': 'e', 'É': 'e', 'Ẹ': 'e', 'Ẻ': 'e', 'Ẽ': 'e', 'Ê': 'e', 'Ề': 'e', 'Ế': 'e', 'Ệ': 'e', 'Ể': 'e', 'Ễ': 'e',
            'Ì': 'i', 'Í': 'i', 'Ị': 'i', 'Ỉ': 'i', 'Ĩ': 'i',
            'Ò': 'o', 'Ó': 'o', 'Ọ': 'o', 'Ỏ': 'o', 'Õ': 'o', 'Ô': 'o', 'Ồ': 'o', 'Ố': 'o', 'Ộ': 'o', 'Ổ': 'o', 'Ỗ': 'o',
            'Ơ': 'o', 'Ờ': 'o', 'Ớ': 'o', 'Ợ': 'o', 'Ở': 'o', 'Ỡ': 'o',
            'Ù': 'u', 'Ú': 'u', 'Ụ': 'u', 'Ủ': 'u', 'Ũ': 'u', 'Ư': 'u', 'Ừ': 'u', 'Ứ': 'u', 'Ự': 'u', 'Ử': 'u', 'Ữ': 'u',
            'Ỳ': 'y', 'Ý': 'y', 'Ỵ': 'y', 'Ỷ': 'y', 'Ỹ': 'y',
            'Đ': 'd'
        }
        
        slug = title.lower()
        
        # Chuyển đổi tiếng Việt có dấu sang không dấu
        for viet_char, eng_char in vietnamese_map.items():
            slug = slug.replace(viet_char, eng_char)
        
        # Loại bỏ ký tự đặc biệt, chỉ giữ chữ, số, khoảng trắng và dấu gạch ngang
        slug = re.sub(r'[^\w\s-]', '', slug)
        # Thay nhiều khoảng trắng hoặc dấu gạch ngang bằng một dấu gạch ngang
        slug = re.sub(r'[-\s]+', '-', slug)
        # Loại bỏ dấu gạch ngang ở đầu và cuối
        slug = slug.strip('-')
        
        # Thêm prefix trạng thái nếu cần (tùy chọn)
        if status and status != 'published':
            slug = f"{slug}-{status}"
        
        return slug
    
    def api_create_international_article(self):
        """API tạo bài viết quốc tế mới từ editor form"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
        
        from database import NewsInternational, CategoryInternational
        
        data = request.json if request.is_json else request.form
        
        # Lấy dữ liệu từ form
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        category_id = data.get('category_id') or data.get('category')
        summary = data.get('summary') or data.get('description', '').strip()
        thumbnail = data.get('thumbnail', '').strip()
        author = data.get('author', '').strip()
        status = data.get('status', NewsStatus.DRAFT.value)
        
        # Validation
        if not title:
            return jsonify({'success': False, 'error': 'Vui lòng nhập tiêu đề bài viết'}), 400
        
        if not content:
            return jsonify({'success': False, 'error': 'Vui lòng nhập nội dung bài viết'}), 400
        
        if not category_id:
            return jsonify({'success': False, 'error': 'Vui lòng chọn danh mục'}), 400
        
        try:
            category_id = int(category_id)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Danh mục không hợp lệ'}), 400
        
        # Kiểm tra category tồn tại
        category = self.db_session.query(CategoryInternational).filter(CategoryInternational.id == category_id).first()
        if not category:
            return jsonify({'success': False, 'error': 'Danh mục không tồn tại'}), 400
        
        try:
            news_status = NewsStatus(status)
        except ValueError:
            news_status = NewsStatus.DRAFT
        
        # Tạo slug từ tiêu đề
        base_slug = self._generate_slug(title)
        slug = base_slug
        
        # Kiểm tra slug trùng và thêm số nếu cần
        counter = 1
        while self.db_session.query(NewsInternational).filter(NewsInternational.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Extract images từ HTML content
        import re
        image_urls = []
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
        matches = re.findall(img_pattern, content)
        for img_url in matches:
            if img_url and img_url not in image_urls:
                image_urls.append(img_url)
        
        # Lưu images dưới dạng JSON
        images_json = None
        if image_urls:
            import json
            images_json = json.dumps(image_urls)
        
        try:
            # Tạo bài viết quốc tế mới
            news = NewsInternational(
                title=title,
                slug=slug,
                summary=summary,
                content=content,
                thumbnail=thumbnail,
                images=images_json,
                category_id=category_id,
                created_by=user_id,
                approved_by=user_id if news_status == NewsStatus.PUBLISHED else None,
                status=news_status,
                author=author if author else None,
                published_at=datetime.utcnow() if news_status == NewsStatus.PUBLISHED else None
            )
            
            self.db_session.add(news)
            self.db_session.commit()
            self.db_session.refresh(news)
            
            return jsonify({
                'success': True,
                'message': 'Đã tạo bài viết quốc tế',
                'data': {
                    'id': news.id,
                    'title': news.title,
                    'status': news.status.value
                }
            })
        except IntegrityError as e:
            self.db_session.rollback()
            return jsonify({'success': False, 'error': 'Bài viết đã tồn tại'}), 400
        except Exception as e:
            self.db_session.rollback()
            current_app.logger.exception('Lỗi tạo bài viết quốc tế: %s', e)
            return jsonify({'success': False, 'error': f'Không thể tạo bài viết: {str(e)}'}), 500
    
    def api_create_article(self):
        """API tạo bài viết mới từ editor form"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
        
        data = request.json if request.is_json else request.form
        
        # Lấy dữ liệu từ form
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        category_id = data.get('category_id') or data.get('category')
        summary = data.get('summary') or data.get('description', '').strip()
        thumbnail = data.get('thumbnail', '').strip()
        tags = data.get('tags', '').strip()
        status = data.get('status', NewsStatus.DRAFT.value)
        is_hot = data.get('is_hot', False)
        is_featured = data.get('is_featured', False)
        
        # Convert to boolean nếu là string
        if isinstance(is_hot, str):
            is_hot = is_hot.lower() in ('true', '1', 'yes', 'on')
        if isinstance(is_featured, str):
            is_featured = is_featured.lower() in ('true', '1', 'yes', 'on')
        
        # Validation
        if not title:
            return jsonify({'success': False, 'error': 'Vui lòng nhập tiêu đề bài viết'}), 400
        
        if not content:
            return jsonify({'success': False, 'error': 'Vui lòng nhập nội dung bài viết'}), 400
        
        if not category_id:
            return jsonify({'success': False, 'error': 'Vui lòng chọn danh mục'}), 400
        
        try:
            category_id = int(category_id)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Danh mục không hợp lệ'}), 400
        
        # Kiểm tra category tồn tại
        category = self.db_session.query(Category).filter(Category.id == category_id).first()
        if not category:
            return jsonify({'success': False, 'error': 'Danh mục không tồn tại'}), 400
        
        try:
            news_status = NewsStatus(status)
        except ValueError:
            news_status = NewsStatus.DRAFT
        
        # Tạo slug từ tiêu đề và trạng thái
        print(title)
        print(status)
        base_slug = self._generate_slug(title, status)
        slug = base_slug
        
        # Kiểm tra slug trùng và thêm số nếu cần
        counter = 1
        while self.db_session.query(News).filter(News.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Extract images từ HTML content
        import re
        image_urls = []
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
        matches = re.findall(img_pattern, content)
        for img_url in matches:
            if img_url and img_url not in image_urls:
                image_urls.append(img_url)
        
        # Lưu images dưới dạng JSON
        images_json = None
        if image_urls:
            import json
            images_json = json.dumps(image_urls)
        
        try:
            # Tạo bài viết mới
            article = News(
                title=title,
                slug=slug,
                content=content,
                summary=summary,
                thumbnail=thumbnail,
                images=images_json,
                category_id=category_id,
                created_by=user_id,
                status=news_status,
                is_hot=bool(is_hot),
                is_featured=bool(is_featured),
                published_at=datetime.utcnow() if news_status == NewsStatus.PUBLISHED else None
            )
            
            self.db_session.add(article)
            self.db_session.commit()
            self.db_session.refresh(article)
            
            # Di chuyển ảnh từ temp folder sang folder của bài viết nếu có
            if article.id:
                temp_folder = os.path.join('src', 'static', 'uploads', 'news', 'vn', 'temp')
                news_folder = os.path.join('src', 'static', 'uploads', 'news', 'vn', f'news_{article.id}')
                
                if os.path.exists(temp_folder):
                    os.makedirs(news_folder, exist_ok=True)
                    # Di chuyển các file từ temp sang news folder
                    import shutil
                    for filename in os.listdir(temp_folder):
                        src_path = os.path.join(temp_folder, filename)
                        dst_path = os.path.join(news_folder, filename)
                        if os.path.isfile(src_path):
                            shutil.move(src_path, dst_path)
                            # Cập nhật URL trong thumbnail và content nếu cần
                            if thumbnail and 'temp' in thumbnail:
                                thumbnail = thumbnail.replace('temp', f'news_{article.id}')
                                article.thumbnail = thumbnail
                            if images_json:
                                import json
                                images = json.loads(images_json)
                                updated_images = [img.replace('temp', f'news_{article.id}') if 'temp' in img else img for img in images]
                                article.images = json.dumps(updated_images)
                                # Cập nhật content với URL mới
                                for old_url, new_url in zip(images, updated_images):
                                    if old_url != new_url:
                                        content = content.replace(old_url, new_url)
                                        article.content = content
                    self.db_session.commit()
            
            # Xử lý tags nếu có - CHỈ chấp nhận tags có sẵn trong bảng tags
            if tags:
                # Xóa các tags cũ của bài viết (nếu có)
                self.db_session.query(NewsTag).filter(NewsTag.news_id == article.id).delete()
                
                tag_names = self._parse_tags(tags)
                invalid_tags = []
                
                for tag_name in tag_names:
                    # CHỈ tìm tag có sẵn, KHÔNG tự tạo mới
                    tag = self.db_session.query(Tag).filter(Tag.name == tag_name).first()
                    if not tag:
                        invalid_tags.append(tag_name)
                        continue
                    
                    # Tạo NewsTag mới
                    news_tag = NewsTag(news_id=article.id, tag_id=tag.id)
                    self.db_session.add(news_tag)
                
                # Nếu có tags không hợp lệ, trả về lỗi
                if invalid_tags:
                    self.db_session.rollback()
                    return jsonify({
                        'success': False, 
                        'error': f'Các tags sau không tồn tại trong hệ thống: {", ".join(invalid_tags)}. Vui lòng chỉ sử dụng tags có sẵn.'
                    }), 400
            
            self.db_session.commit()
        except IntegrityError as e:
            self.db_session.rollback()
            # Trả về thông điệp lỗi gốc từ DB (ví dụ: Key (slug)=... already exists.)
            message = getattr(e, "orig", None)
            message = str(message) if message else str(e)
            return jsonify({'success': False, 'error': message}), 400
        except SQLAlchemyError as e:
            self.db_session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

        return jsonify({
            'success': True,
            'message': 'Tạo bài viết thành công',
            'data': {
                'id': article.id,
                'slug': article.slug,
                'title': article.title
            }
        })

    def api_edit_article(self, article_id: int):
        """API chỉnh sửa bài viết theo ID"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
        
        data = request.json if request.is_json else request.form
        article = self.db_session.query(News).filter(News.id == article_id).first()
        if not article:
            return jsonify({'success': False, 'error': 'Bài viết không tồn tại'}), 400
        
        # Lấy dữ liệu từ form
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        category_id = data.get('category_id') or data.get('category')
        summary = data.get('summary') or data.get('description', '').strip()
        thumbnail = data.get('thumbnail', '').strip()
        tags = data.get('tags', '').strip()
        status = data.get('status', article.status.value)
        is_hot = data.get('is_hot', article.is_hot if hasattr(article, 'is_hot') else False)
        is_featured = data.get('is_featured', article.is_featured if hasattr(article, 'is_featured') else False)
        
        # Convert to boolean nếu là string
        if isinstance(is_hot, str):
            is_hot = is_hot.lower() in ('true', '1', 'yes', 'on')
        if isinstance(is_featured, str):
            is_featured = is_featured.lower() in ('true', '1', 'yes', 'on')
        
        # Validation
        if not title:
            return jsonify({'success': False, 'error': 'Vui lòng nhập tiêu đề bài viết'}), 400
        
        if not content:
            return jsonify({'success': False, 'error': 'Vui lòng nhập nội dung bài viết'}), 400
        
        if not category_id:
            return jsonify({'success': False, 'error': 'Vui lòng chọn danh mục'}), 400
        
        try:
            category_id = int(category_id)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Danh mục không hợp lệ'}), 400
        
        # Kiểm tra category tồn tại
        category = self.db_session.query(Category).filter(Category.id == category_id).first()
        if not category:
            return jsonify({'success': False, 'error': 'Danh mục không tồn tại'}), 400
        
        try:
            news_status = NewsStatus(status)
        except ValueError:
            news_status = article.status
        
        # Tạo slug từ tiêu đề và trạng thái
        base_slug = self._generate_slug(title, status)
        slug = base_slug
        
        # Kiểm tra slug trùng và thêm số nếu cần (nhưng không trùng với chính nó)
        counter = 1
        while self.db_session.query(News).filter(News.slug == slug, News.id != article_id).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Extract images từ HTML content
        import re
        image_urls = []
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
        matches = re.findall(img_pattern, content)
        for img_url in matches:
            if img_url and img_url not in image_urls:
                image_urls.append(img_url)
        
        # Lưu images dưới dạng JSON
        images_json = None
        if image_urls:
            import json
            images_json = json.dumps(image_urls)
        
        try:
            # Cập nhật bài viết
            article.title = title
            article.slug = slug
            article.content = content
            article.summary = summary
            article.thumbnail = thumbnail
            article.images = images_json
            article.category_id = category_id
            article.status = news_status
            article.is_hot = bool(is_hot)
            article.is_featured = bool(is_featured)
            article.published_at = datetime.utcnow() if news_status == NewsStatus.PUBLISHED else article.published_at
            
            self.db_session.commit()
            self.db_session.refresh(article)
            
            # Di chuyển ảnh từ temp folder sang folder của bài viết nếu có
            if article.id:
                temp_folder = os.path.join('src', 'static', 'uploads', 'news', 'vn', 'temp')
                news_folder = os.path.join('src', 'static', 'uploads', 'news', 'vn', f'news_{article.id}')
                
                if os.path.exists(temp_folder):
                    os.makedirs(news_folder, exist_ok=True)
                    # Di chuyển các file từ temp sang news folder
                    import shutil
                    for filename in os.listdir(temp_folder):
                        src_path = os.path.join(temp_folder, filename)
                        dst_path = os.path.join(news_folder, filename)
                        if os.path.isfile(src_path):
                            shutil.move(src_path, dst_path)
                            # Cập nhật URL trong thumbnail và content nếu cần
                            if thumbnail and 'temp' in thumbnail:
                                thumbnail = thumbnail.replace('temp', f'news_{article.id}')
                                article.thumbnail = thumbnail
                            if images_json:
                                import json
                                images = json.loads(images_json)
                                updated_images = [img.replace('temp', f'news_{article.id}') if 'temp' in img else img for img in images]
                                article.images = json.dumps(updated_images)
                                # Cập nhật content với URL mới
                                for old_url, new_url in zip(images, updated_images):
                                    if old_url != new_url:
                                        content = content.replace(old_url, new_url)
                                        article.content = content
                    self.db_session.commit()
            
            # Xử lý tags nếu có - CHỈ chấp nhận tags có sẵn trong bảng tags
            if tags:
                # Xóa các tags cũ của bài viết
                self.db_session.query(NewsTag).filter(NewsTag.news_id == article.id).delete()
                
                tag_names = self._parse_tags(tags)
                invalid_tags = []
                
                for tag_name in tag_names:
                    # CHỈ tìm tag có sẵn, KHÔNG tự tạo mới
                    tag = self.db_session.query(Tag).filter(Tag.name == tag_name).first()
                    if not tag:
                        invalid_tags.append(tag_name)
                        continue
                    
                    # Tạo NewsTag mới
                    news_tag = NewsTag(news_id=article.id, tag_id=tag.id)
                    self.db_session.add(news_tag)
                
                # Nếu có tags không hợp lệ, trả về lỗi
                if invalid_tags:
                    self.db_session.rollback()
                    return jsonify({
                        'success': False, 
                        'error': f'Các tags sau không tồn tại trong hệ thống: {", ".join(invalid_tags)}. Vui lòng chỉ sử dụng tags có sẵn.'
                    }), 400
            
            self.db_session.commit()
        except IntegrityError as e:
            self.db_session.rollback()
            message = getattr(e, "orig", None)
            message = str(message) if message else str(e)
            return jsonify({'success': False, 'error': message}), 400
        except SQLAlchemyError as e:
            self.db_session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
        
        return jsonify({
            'success': True,
            'message': 'Cập nhật bài viết thành công',
            'data': {
                'id': article.id,
                'slug': article.slug,
                'title': article.title
            }
        })
    
    def api_upload_image(self):
        """API upload ảnh cho bài viết"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
        
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'Không có file được chọn'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Không có file được chọn'}), 400
        
        # Kiểm tra file hợp lệ
        if not self._allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File không hợp lệ. Chỉ chấp nhận: png, jpg, jpeg, gif, webp'}), 400
        
        # Lấy news_id từ request (nếu có) để lưu vào thư mục tương ứng
        news_id = request.form.get('news_id')
        
        # Tạo thư mục lưu ảnh
        if news_id:
            upload_folder = os.path.join('src', 'static', 'uploads', 'news', 'vn', f'news_{news_id}')
        else:
            # Nếu chưa có news_id, lưu vào thư mục temp
            upload_folder = os.path.join('src', 'static', 'uploads', 'news', 'vn', 'temp')
        
        os.makedirs(upload_folder, exist_ok=True)
        
        # Tạo tên file an toàn
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(upload_folder, filename)
        
        # Lưu file
        file.save(filepath)
        
        # Tạo URL trả về (relative to static folder)
        image_url = f"static/uploads/news/vn/{'news_' + str(news_id) if news_id else 'temp'}/{filename}"
        
        return jsonify({
            'success': True,
            'message': 'Upload ảnh thành công',
            'url': f'/{image_url}',
            'image_url': image_url
        })

    # def _generate_slug(self, title: str) -> str:
    #     """Tạo slug từ tiêu đề - chuyển tiếng Việt có dấu thành không dấu"""
    #     import re
    #     import unicodedata
        
    #     # Chuyển thành chữ thường
    #     slug = title.lower()
        
    #     # Bảng chuyển đổi tiếng Việt có dấu sang không dấu
    #     vietnamese_map = {
    #         'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
    #         'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
    #         'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
    #         'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
    #         'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
    #         'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
    #         'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
    #         'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
    #         'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
    #         'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
    #         'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
    #         'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    #         'đ': 'd',
    #     }
        
    #     # Thay thế các ký tự tiếng Việt
    #     for viet, latin in vietnamese_map.items():
    #         slug = slug.replace(viet, latin)
        
    #     # Xóa các ký tự không phải chữ cái, số, khoảng trắng, dấu gạch ngang
    #     slug = re.sub(r'[^\w\s-]', '', slug)
        
    #     # Thay thế nhiều khoảng trắng hoặc dấu gạch ngang liên tiếp bằng một dấu gạch ngang
    #     slug = re.sub(r'[-\s]+', '-', slug)
        
    #     return slug.strip('-')
    
    def api_menu_items(self):
        """API lấy danh sách categories (menu items)"""
        categories = self.db_session.query(Category).order_by(
            Category.order_display, Category.parent_id
        ).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': item.id,
                'name': item.name,
                'slug': item.slug,
                'icon': item.icon,
                'order': item.order_display,
                'parent_id': item.parent_id,
                'level': item.level if hasattr(item, 'level') else 1,
                'visible': item.visible
            } for item in categories]
        })
    
    def _calculate_level(self, parent_id):
        """Tính toán level dựa trên parent_id"""
        if not parent_id:
            return 1
        
        parent = self.db_session.query(Category).filter(Category.id == parent_id).first()
        if not parent:
            return 1
        
        return parent.level + 1
    
    def api_create_menu_item(self):
        """API tạo category mới (menu item)"""
        data = request.json if request.is_json else request.form
        
        name = data.get('name')
        slug = data.get('slug')
        icon = data.get('icon')
        order = data.get('order', 0)
        parent_id = data.get('parent_id')
        visible = data.get('visible', True)
        description = data.get('description')
        
        if not name:
            return jsonify({'success': False, 'error': 'Tên danh mục không được để trống'}), 400
        
        if not slug:
            # Tự động tạo slug
            slug = self._generate_slug(name)
        
        # Kiểm tra slug trùng
        existing = self.db_session.query(Category).filter(Category.slug == slug).first()
        if existing:
            return jsonify({'success': False, 'error': 'Slug đã tồn tại'}), 400
        
        # Tính toán level
        level = self._calculate_level(parent_id)
        
        # Kiểm tra level không được vượt quá 4
        if level > 4:
            return jsonify({'success': False, 'error': 'Không thể tạo menu quá 4 cấp. Menu hiện tại đã đạt cấp tối đa.'}), 400
        
        category = Category(
            name=name,
            slug=slug,
            icon=icon if icon else None,
            order_display=order,
            parent_id=int(parent_id) if parent_id else None,
            level=level,
            visible=visible,
            description=description if description else None
        )
        
        self.db_session.add(category)
        self.db_session.commit()
        self.db_session.refresh(category)
        
        return jsonify({
            'success': True,
            'message': 'Đã tạo danh mục mới',
            'data': {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'level': category.level
            }
        })
    
    def api_update_menu_item(self, menu_id: int):
        """API cập nhật category (menu item)"""
        category = self.db_session.query(Category).filter(Category.id == menu_id).first()
        if not category:
            return jsonify({'success': False, 'error': 'Không tìm thấy danh mục'}), 404
        
        data = request.json if request.is_json else request.form
        
        if 'name' in data:
            category.name = data['name']
        if 'slug' in data:
            # Kiểm tra slug trùng (trừ chính nó)
            existing = self.db_session.query(Category).filter(
                Category.slug == data['slug'],
                Category.id != menu_id
            ).first()
            if existing:
                return jsonify({'success': False, 'error': 'Slug đã tồn tại'}), 400
            category.slug = data['slug']
        if 'icon' in data:
            category.icon = data['icon'] if data['icon'] else None
        if 'order' in data:
            category.order_display = int(data['order'])
        if 'parent_id' in data:
            parent_id = data['parent_id']
            # Kiểm tra không được set parent là chính nó
            if parent_id == menu_id:
                return jsonify({'success': False, 'error': 'Không thể set parent là chính nó'}), 400
            
            # Kiểm tra không được set parent là con cháu của chính nó (tránh vòng lặp)
            if parent_id:
                # Kiểm tra xem parent_id có phải là con cháu của menu_id không
                def is_descendant(parent_candidate_id, ancestor_id):
                    if parent_candidate_id == ancestor_id:
                        return True
                    parent_candidate = self.db_session.query(Category).filter(Category.id == parent_candidate_id).first()
                    if not parent_candidate or not parent_candidate.parent_id:
                        return False
                    return is_descendant(parent_candidate.parent_id, ancestor_id)
                
                if is_descendant(int(parent_id), menu_id):
                    return jsonify({'success': False, 'error': 'Không thể set parent là con cháu của chính nó'}), 400
            
            category.parent_id = int(parent_id) if parent_id else None
            
            # Tính toán lại level khi parent_id thay đổi
            new_level = self._calculate_level(category.parent_id)
            if new_level > 4:
                return jsonify({'success': False, 'error': 'Không thể tạo menu quá 4 cấp. Menu hiện tại đã đạt cấp tối đa.'}), 400
            category.level = new_level
        if 'visible' in data:
            category.visible = bool(data['visible'])
        if 'description' in data:
            category.description = data['description'] if data['description'] else None
        
        category.updated_at = datetime.utcnow()
        self.db_session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Đã cập nhật danh mục',
            'data': {
                'id': category.id,
                'name': category.name,
                'level': category.level
            }
        })
    
    def api_delete_menu_item(self, menu_id: int):
        """API xóa category (menu item)"""
        category = self.db_session.query(Category).filter(Category.id == menu_id).first()
        if not category:
            return jsonify({'success': False, 'error': 'Không tìm thấy danh mục'}), 404
        
        # Kiểm tra xem có tin tức nào đang sử dụng category này không
        news_count = self.db_session.query(News).filter(News.category_id == menu_id).count()
        if news_count > 0:
            return jsonify({
                'success': False,
                'error': f'Không thể xóa danh mục vì có {news_count} tin tức đang sử dụng'
            }), 400
        
        # Xóa các category con trước (cascade)
        children = self.db_session.query(Category).filter(Category.parent_id == menu_id).all()
        for child in children:
            # Kiểm tra tin tức của child category
            child_news_count = self.db_session.query(News).filter(News.category_id == child.id).count()
            if child_news_count == 0:
                self.db_session.delete(child)
        
        self.db_session.delete(category)
        self.db_session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Đã xóa danh mục'
        })
    
    def api_init_default_menu_items(self):
        """API khởi tạo categories mặc định (menu items)"""
        # Kiểm tra xem đã có categories chưa
        count = self.db_session.query(Category).count()
        if count > 0:
            return jsonify({
                'success': False,
                'error': 'Đã có categories trong database'
            }), 400
        
        # Sử dụng DEFAULT_CATEGORIES từ database.py
        from database import DEFAULT_CATEGORIES
        
        # Tạo categories (tạo parent trước)
        created_items = {}  # Map slug -> real_id
        
        # Tạo parent categories trước
        parent_categories = [c for c in DEFAULT_CATEGORIES if c['parent_id'] is None]
        parent_categories.sort(key=lambda x: x['order_display'])
        
        for cat_data in parent_categories:
            category = Category(
                name=cat_data['name'],
                slug=cat_data['slug'],
                icon=cat_data['icon'],
                order_display=cat_data['order_display'],
                parent_id=None,
                visible=True
            )
            self.db_session.add(category)
            self.db_session.flush()  # Để lấy ID
            created_items[cat_data['slug']] = category.id
        
        # Tạo child categories (nếu có trong DEFAULT_CATEGORIES)
        child_categories = [c for c in DEFAULT_CATEGORIES if c['parent_id'] is not None]
        child_categories.sort(key=lambda x: (x['parent_id'], x['order_display']))
        
        for cat_data in child_categories:
            # Tìm parent_id từ slug của parent
            parent_slug = None
            for parent_cat in DEFAULT_CATEGORIES:
                if parent_cat.get('id') == cat_data['parent_id']:
                    parent_slug = parent_cat['slug']
                    break
            
            if parent_slug and parent_slug in created_items:
                parent_id = created_items[parent_slug]
                category = Category(
                    name=cat_data['name'],
                    slug=cat_data['slug'],
                    icon=cat_data['icon'],
                    order_display=cat_data['order_display'],
                    parent_id=parent_id,
                    visible=True
                )
                self.db_session.add(category)
                self.db_session.flush()
                created_items[cat_data['slug']] = category.id
        
        self.db_session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Đã khởi tạo {len(DEFAULT_CATEGORIES)} categories mặc định',
            'count': len(DEFAULT_CATEGORIES)
        })
    
    def api_update_menu_order(self):
        """API cập nhật thứ tự categories (drag & drop)"""
        data = request.json if request.is_json else {}
        items = data.get('items', [])
        
        if not items:
            return jsonify({'success': False, 'error': 'Thiếu dữ liệu'}), 400
        
        try:
            for item_data in items:
                category_id = item_data.get('id')
                new_order = item_data.get('order', 0)
                parent_id = item_data.get('parent_id')
                
                category = self.db_session.query(Category).filter(Category.id == category_id).first()
                if category:
                    category.order_display = new_order
                    if parent_id is not None:
                        # Kiểm tra không được set parent là chính nó
                        if parent_id == category_id:
                            continue
                        category.parent_id = int(parent_id) if parent_id else None
                    else:
                        category.parent_id = None
                    category.updated_at = datetime.utcnow()
            
            self.db_session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Đã cập nhật thứ tự danh mục'
            })
        except Exception as e:
            self.db_session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def api_international_menu_items(self):
        """API lấy danh sách international categories (menu items)"""
        categories = self.db_session.query(CategoryInternational).order_by(
            CategoryInternational.order_display, CategoryInternational.parent_id
        ).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': item.id,
                'name': item.name,
                'slug': item.slug,
                'icon': item.icon,
                'order': item.order_display,
                'parent_id': item.parent_id,
                'level': item.level if hasattr(item, 'level') else 1,
                'visible': item.visible
            } for item in categories]
        })
    
    def api_create_international_menu_item(self):
        """API tạo international category mới (menu item)"""
        data = request.json if request.is_json else request.form
        
        name = data.get('name')
        slug = data.get('slug')
        icon = data.get('icon')
        order = data.get('order', 0)
        parent_id = data.get('parent_id')
        visible = data.get('visible', True)
        description = data.get('description')
        
        if not name:
            return jsonify({'success': False, 'error': 'Tên danh mục không được để trống'}), 400
        
        if not slug:
            # Tự động tạo slug
            slug = self._generate_slug(name)
        
        # Kiểm tra slug trùng
        existing = self.db_session.query(CategoryInternational).filter(CategoryInternational.slug == slug).first()
        if existing:
            return jsonify({'success': False, 'error': 'Slug đã tồn tại'}), 400
        
        # Tính toán level
        level = self._calculate_international_level(parent_id)
        
        # Kiểm tra level không được vượt quá 4
        if level > 4:
            return jsonify({'success': False, 'error': 'Không thể tạo menu quá 4 cấp. Menu hiện tại đã đạt cấp tối đa.'}), 400
        
        category = CategoryInternational(
            name=name,
            slug=slug,
            icon=icon if icon else None,
            order_display=order,
            parent_id=int(parent_id) if parent_id else None,
            level=level,
            visible=visible,
            description=description if description else None
        )
        
        self.db_session.add(category)
        self.db_session.commit()
        self.db_session.refresh(category)
        
        return jsonify({
            'success': True,
            'message': 'Đã tạo danh mục mới',
            'data': {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'level': category.level
            }
        })
    
    def api_update_international_menu_item(self, menu_id: int):
        """API cập nhật international category (menu item)"""
        category = self.db_session.query(CategoryInternational).filter(CategoryInternational.id == menu_id).first()
        if not category:
            return jsonify({'success': False, 'error': 'Không tìm thấy danh mục'}), 404
        
        data = request.json if request.is_json else request.form
        
        if 'name' in data:
            category.name = data['name']
        if 'slug' in data:
            # Kiểm tra slug trùng (trừ chính nó)
            existing = self.db_session.query(CategoryInternational).filter(
                CategoryInternational.slug == data['slug'],
                CategoryInternational.id != menu_id
            ).first()
            if existing:
                return jsonify({'success': False, 'error': 'Slug đã tồn tại'}), 400
            category.slug = data['slug']
        if 'icon' in data:
            category.icon = data['icon'] if data['icon'] else None
        if 'order' in data:
            category.order_display = int(data['order'])
        if 'parent_id' in data:
            parent_id = data['parent_id']
            # Kiểm tra không được set parent là chính nó
            if parent_id == menu_id:
                return jsonify({'success': False, 'error': 'Không thể set parent là chính nó'}), 400
            
            # Kiểm tra không được set parent là con cháu của chính nó (tránh vòng lặp)
            if parent_id:
                # Kiểm tra xem parent_id có phải là con cháu của menu_id không
                def is_descendant(parent_candidate_id, ancestor_id):
                    if parent_candidate_id == ancestor_id:
                        return True
                    parent_candidate = self.db_session.query(CategoryInternational).filter(CategoryInternational.id == parent_candidate_id).first()
                    if not parent_candidate or not parent_candidate.parent_id:
                        return False
                    return is_descendant(parent_candidate.parent_id, ancestor_id)
                
                if is_descendant(int(parent_id), menu_id):
                    return jsonify({'success': False, 'error': 'Không thể set parent là con cháu của chính nó'}), 400
            
            category.parent_id = int(parent_id) if parent_id else None
            
            # Tính toán lại level khi parent_id thay đổi
            new_level = self._calculate_international_level(category.parent_id)
            if new_level > 4:
                return jsonify({'success': False, 'error': 'Không thể tạo menu quá 4 cấp. Menu hiện tại đã đạt cấp tối đa.'}), 400
            category.level = new_level
        if 'visible' in data:
            category.visible = bool(data['visible'])
        if 'description' in data:
            category.description = data['description'] if data['description'] else None
        
        category.updated_at = datetime.utcnow()
        self.db_session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Đã cập nhật danh mục',
            'data': {
                'id': category.id,
                'name': category.name,
                'level': category.level
            }
        })
    
    def api_delete_international_menu_item(self, menu_id: int):
        """API xóa international category (menu item)"""
        category = self.db_session.query(CategoryInternational).filter(CategoryInternational.id == menu_id).first()
        if not category:
            return jsonify({'success': False, 'error': 'Không tìm thấy danh mục'}), 404
        
        # Kiểm tra xem có tin tức nào đang sử dụng category này không
        news_count = self.db_session.query(NewsInternational).filter(NewsInternational.category_id == menu_id).count()
        if news_count > 0:
            return jsonify({
                'success': False,
                'error': f'Không thể xóa danh mục vì có {news_count} tin tức đang sử dụng'
            }), 400
        
        # Xóa các category con trước (cascade)
        children = self.db_session.query(CategoryInternational).filter(CategoryInternational.parent_id == menu_id).all()
        for child in children:
            # Kiểm tra tin tức của child category
            child_news_count = self.db_session.query(NewsInternational).filter(NewsInternational.category_id == child.id).count()
            if child_news_count == 0:
                self.db_session.delete(child)
        
        self.db_session.delete(category)
        self.db_session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Đã xóa danh mục'
        })
    
    def _calculate_international_level(self, parent_id):
        """Tính toán level dựa trên parent_id cho international categories"""
        if not parent_id:
            return 1
        
        parent = self.db_session.query(CategoryInternational).filter(CategoryInternational.id == parent_id).first()
        if not parent:
            return 1
        
        return parent.level + 1
    
    def api_init_default_international_menu_items(self):
        """API khởi tạo international categories mặc định (menu items)"""
        # Kiểm tra xem đã có categories chưa
        count = self.db_session.query(CategoryInternational).count()
        if count > 0:
            return jsonify({
                'success': False,
                'error': 'Đã có categories trong database'
            }), 400
        
        # Sử dụng DEFAULT_CATEGORIES_EN từ database.py
        from database import DEFAULT_CATEGORIES_EN
        
        # Tạo categories (tạo parent trước)
        created_items = {}  # Map slug -> real_id
        
        # Tạo parent categories trước
        parent_categories = [c for c in DEFAULT_CATEGORIES_EN if c['parent_id'] is None]
        parent_categories.sort(key=lambda x: x['order_display'])
        
        for cat_data in parent_categories:
            category = CategoryInternational(
                name=cat_data['name'],
                slug=cat_data['slug'],
                icon=cat_data['icon'],
                order_display=cat_data['order_display'],
                parent_id=None,
                level=1,
                visible=True
            )
            self.db_session.add(category)
            self.db_session.flush()  # Để lấy ID
            created_items[cat_data['slug']] = category.id
        
        # Tạo child categories (nếu có trong DEFAULT_CATEGORIES_EN)
        child_categories = [c for c in DEFAULT_CATEGORIES_EN if c['parent_id'] is not None]
        child_categories.sort(key=lambda x: (x['parent_id'], x['order_display']))
        
        for cat_data in child_categories:
            # Tìm parent_id từ slug của parent
            parent_slug = None
            for parent_cat in DEFAULT_CATEGORIES_EN:
                if parent_cat.get('id') == cat_data['parent_id']:
                    parent_slug = parent_cat['slug']
                    break
            
            if parent_slug and parent_slug in created_items:
                parent_id = created_items[parent_slug]
                parent_category = self.db_session.query(CategoryInternational).filter(CategoryInternational.id == parent_id).first()
                level = parent_category.level + 1 if parent_category else 2
                
                category = CategoryInternational(
                    name=cat_data['name'],
                    slug=cat_data['slug'],
                    icon=cat_data['icon'],
                    order_display=cat_data['order_display'],
                    parent_id=parent_id,
                    level=level,
                    visible=True
                )
                self.db_session.add(category)
                self.db_session.flush()
                created_items[cat_data['slug']] = category.id
        
        self.db_session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Đã khởi tạo {len(DEFAULT_CATEGORIES_EN)} categories mặc định',
            'count': len(DEFAULT_CATEGORIES_EN)
        })
    
    def api_update_international_menu_order(self):
        """API cập nhật thứ tự international categories (drag & drop)"""
        data = request.json if request.is_json else {}
        items = data.get('items', [])
        
        if not items:
            return jsonify({'success': False, 'error': 'Thiếu dữ liệu'}), 400
        
        try:
            for item_data in items:
                category_id = item_data.get('id')
                new_order = item_data.get('order', 0)
                parent_id = item_data.get('parent_id')
                
                category = self.db_session.query(CategoryInternational).filter(CategoryInternational.id == category_id).first()
                if category:
                    category.order_display = new_order
                    if parent_id is not None:
                        # Kiểm tra không được set parent là chính nó
                        if parent_id == category_id:
                            continue
                        category.parent_id = int(parent_id) if parent_id else None
                        # Tính toán lại level
                        category.level = self._calculate_international_level(category.parent_id)
                    else:
                        category.parent_id = None
                        category.level = 1
                    category.updated_at = datetime.utcnow()
            
            self.db_session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Đã cập nhật thứ tự danh mục'
            })
        except Exception as e:
            self.db_session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    def _allowed_file(self, filename):
        """Kiểm tra file có được phép upload không"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})

    def profile(self):
        """
        Trang thông tin cá nhân của user
        Route: GET /profile
        """
        print(f"=== DEBUG profile ===")
        print(f"Session: {session}")
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để xem thông tin cá nhân', 'error')
            return redirect(url_for('admin.login'))
        
        user = self.user_model.get_by_id(session['user_id'])
        if not user:
            flash('Không tìm thấy thông tin người dùng', 'error')
            session.clear()
            return redirect(url_for('admin.login'))
        
        # Lấy tin đã lưu (cả site VN và EN)
        saved_news = self.db_session.query(SavedNews).filter(
            SavedNews.user_id == user.id
        ).order_by(SavedNews.created_at.desc()).limit(20).all()
        
        # Lấy tin đã xem (cả site VN và EN)
        viewed_news = self.db_session.query(ViewedNews).filter(
            ViewedNews.user_id == user.id
        ).order_by(ViewedNews.viewed_at.desc()).limit(20).all()
        
        # Lấy tất cả bình luận của user (cả site VN và EN), sau đó lọc không trùng news_id/news_international_id
        all_comments = self.db_session.query(Comment).filter(
            Comment.user_id == user.id
        ).order_by(Comment.created_at.desc()).all()

        comments = []
        seen_news_ids = set()
        seen_news_international_ids = set()
        for comment in all_comments:
            # Mỗi bài viết chỉ lấy 1 bình luận – ưu tiên bình luận mới nhất
            if comment.news_id and comment.news_id not in seen_news_ids:
                comments.append(comment)
                seen_news_ids.add(comment.news_id)
            elif comment.news_international_id and comment.news_international_id not in seen_news_international_ids:
                comments.append(comment)
                seen_news_international_ids.add(comment.news_international_id)
            if len(comments) >= 20:
                break
        
        # Tính số bình luận cho mỗi bài viết (cả news_id và news_international_id)
        comment_counts = {}
        if comments:
            news_ids = list(set([comment.news_id for comment in comments if comment.news_id]))
            news_international_ids = list(set([comment.news_international_id for comment in comments if comment.news_international_id]))
            
            from sqlalchemy import func
            
            # Đếm comments cho news_id
            if news_ids:
                counts_vn = self.db_session.query(
                    Comment.news_id,
                    func.count(Comment.id).label('count')
                ).filter(
                    Comment.news_id.in_(news_ids),
                    Comment.is_active == True
                ).group_by(Comment.news_id).all()
                
                for news_id, count in counts_vn:
                    comment_counts[news_id] = count
            
            # Đếm comments cho news_international_id
            if news_international_ids:
                counts_en = self.db_session.query(
                    Comment.news_international_id,
                    func.count(Comment.id).label('count')
                ).filter(
                    Comment.news_international_id.in_(news_international_ids),
                    Comment.is_active == True
                ).group_by(Comment.news_international_id).all()
                
                for news_international_id, count in counts_en:
                    comment_counts[news_international_id] = count
        
        # Tính tổng số bình luận của cá nhân
        total_comments = self.db_session.query(Comment).filter(
            Comment.user_id == user.id,
            Comment.is_active == True
        ).count()

        categories = self.category_model.get_all()
        return render_template('admin/profile.html', 
                             user=user, 
                             categories=categories,
                             saved_news=saved_news,
                             viewed_news=viewed_news,
                             comments=comments,
                             comment_counts=comment_counts,
                             total_comments=total_comments,
                             )
    
    # User Management Methods
    def api_users_list(self):
        """API lấy danh sách users"""
        try:
            search = request.args.get('search', '').strip()
            role_filter = request.args.get('role', '')
            status_filter = request.args.get('status', '')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            query = self.db_session.query(User)
            
            # Filter by search
            if search:
                query = query.filter(
                    or_(
                        User.username.ilike(f'%{search}%'),
                        User.email.ilike(f'%{search}%'),
                        User.full_name.ilike(f'%{search}%')
                    )
                )
            
            # Filter by role
            if role_filter:
                query = query.filter(User.role == role_filter)
            
            # Filter by status
            if status_filter == 'active':
                query = query.filter(User.is_active == True)
            elif status_filter == 'inactive':
                query = query.filter(User.is_active == False)
            
            # Count total
            total = query.count()
            
            # Pagination
            offset = (page - 1) * per_page
            users = query.order_by(User.created_at.desc()).limit(per_page).offset(offset).all()
            
            users_data = []
            for user in users:
                users_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'phone': user.phone,
                    'role': user.role.value if user.role else 'user',
                    'is_active': user.is_active,
                    'created_at': user.created_at.strftime('%d/%m/%Y %H:%M') if user.created_at else '',
                    'avatar': user.avatar
                })
            
            return jsonify({
                'success': True,
                'users': users_data,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def api_create_user(self):
        """API tạo user mới"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        current_user = self.user_model.get_by_id(session['user_id'])
        if not current_user or current_user.role != UserRole.ADMIN:
            return jsonify({'success': False, 'error': 'Permission denied'}), 403
        
        try:
            data = request.json if request.is_json else request.form
            username = data.get('username', '').strip()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            full_name = data.get('full_name', '').strip()
            phone = data.get('phone', '').strip()
            role_str = data.get('role', 'user')
            
            from auth_utils import validate_email, validate_password
            
            # Validation
            if not username:
                return jsonify({'success': False, 'error': 'Tên đăng nhập không được để trống'}), 400
            
            if self.user_model.get_by_username(username):
                return jsonify({'success': False, 'error': 'Tên đăng nhập đã tồn tại'}), 400
            
            if not validate_email(email):
                return jsonify({'success': False, 'error': 'Email không đúng định dạng'}), 400
            
            if self.user_model.get_by_email(email):
                return jsonify({'success': False, 'error': 'Email đã được sử dụng'}), 400
            
            password_valid, password_error = validate_password(password)
            if not password_valid:
                return jsonify({'success': False, 'error': password_error}), 400
            
            # Convert role string to enum
            role_map = {'admin': UserRole.ADMIN, 'staff': UserRole.STAFF, 'user': UserRole.CUSTOMER}
            role = role_map.get(role_str.lower(), UserRole.CUSTOMER)
            
            # Create user
            user = self.user_model.create(
                username=username,
                email=email,
                password=password,
                full_name=full_name if full_name else None,
                phone=phone if phone else None,
                role=role
            )
            
            return jsonify({
                'success': True,
                'message': 'Tạo tài khoản thành công',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role.value
                }
            })
        except Exception as e:
            self.db_session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def api_update_user(self, user_id: int):
        """API cập nhật user hoặc lấy thông tin user"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        current_user = self.user_model.get_by_id(session['user_id'])
        if not current_user or current_user.role != UserRole.ADMIN:
            return jsonify({'success': False, 'error': 'Permission denied'}), 403
        
        try:
            user = self.user_model.get_by_id(user_id)
            if not user:
                return jsonify({'success': False, 'error': 'Không tìm thấy người dùng'}), 404
            
            # GET request - return user info
            if request.method == 'GET':
                return jsonify({
                    'success': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'full_name': user.full_name,
                        'phone': user.phone,
                        'role': user.role.value if user.role else 'user',
                        'is_active': user.is_active
                    }
                })
            
            # PUT request - update user
            data = request.json if request.is_json else request.form
            full_name = data.get('full_name', '').strip()
            email = data.get('email', '').strip().lower()
            phone = data.get('phone', '').strip()
            role_str = data.get('role', '')
            
            # Update fields
            if full_name is not None:
                user.full_name = full_name if full_name else None
            if email and email != user.email:
                from auth_utils import validate_email
                if not validate_email(email):
                    return jsonify({'success': False, 'error': 'Email không đúng định dạng'}), 400
                if self.user_model.get_by_email(email):
                    return jsonify({'success': False, 'error': 'Email đã được sử dụng'}), 400
                user.email = email
            if phone is not None:
                user.phone = phone if phone else None
            if role_str:
                role_map = {'admin': UserRole.ADMIN, 'staff': UserRole.STAFF, 'user': UserRole.CUSTOMER}
                if role_str.lower() in role_map:
                    user.role = role_map[role_str.lower()]
            
            user.updated_at = datetime.utcnow()
            self.db_session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Cập nhật thông tin thành công'
            })
        except Exception as e:
            self.db_session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def api_toggle_user_status(self, user_id: int):
        """API khóa/mở khóa user"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        current_user = self.user_model.get_by_id(session['user_id'])
        if not current_user or current_user.role != UserRole.ADMIN:
            return jsonify({'success': False, 'error': 'Permission denied'}), 403
        
        try:
            user = self.user_model.get_by_id(user_id)
            if not user:
                return jsonify({'success': False, 'error': 'Không tìm thấy người dùng'}), 404
            
            # Không cho phép khóa chính mình
            if user.id == current_user.id:
                return jsonify({'success': False, 'error': 'Không thể khóa tài khoản của chính bạn'}), 400
            
            # Toggle status
            user.is_active = not user.is_active
            user.updated_at = datetime.utcnow()
            self.db_session.commit()
            
            status_text = 'mở khóa' if user.is_active else 'khóa'
            return jsonify({
                'success': True,
                'message': f'Đã {status_text} tài khoản thành công',
                'is_active': user.is_active
            })
        except Exception as e:
            self.db_session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Settings Management Methods
    def api_get_settings(self):
        """API lấy settings"""
        try:
            category = request.args.get('category', '')
            query = self.db_session.query(Setting)
            
            if category:
                query = query.filter(Setting.category == category)
            
            settings = query.all()
            settings_data = {s.key: {'value': s.value, 'description': s.description, 'category': s.category} for s in settings}
            
            return jsonify({
                'success': True,
                'settings': settings_data
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def api_update_settings(self):
        """API cập nhật settings"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        current_user = self.user_model.get_by_id(session['user_id'])
        if not current_user or current_user.role != UserRole.ADMIN:
            return jsonify({'success': False, 'error': 'Permission denied'}), 403
        
        try:
            data = request.json if request.is_json else request.form
            
            for key, value in data.items():
                setting = self.db_session.query(Setting).filter(Setting.key == key).first()
                if setting:
                    setting.value = value if value else None
                    setting.updated_at = datetime.utcnow()
                else:
                    # Tạo setting mới nếu chưa tồn tại
                    category = 'general'
                    if 'api' in key.lower() or 'token' in key.lower():
                        category = 'api'
                    elif 'mail' in key.lower() or 'smtp' in key.lower():
                        category = 'smtp'
                    
                    setting = Setting(
                        key=key,
                        value=value if value else None,
                        category=category
                    )
                    self.db_session.add(setting)
            
            self.db_session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Cập nhật cài đặt thành công'
            })
        except Exception as e:
            self.db_session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def api_test_email(self):
        """API test gửi email"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        current_user = self.user_model.get_by_id(session['user_id'])
        if not current_user or current_user.role != UserRole.ADMIN:
            return jsonify({'success': False, 'error': 'Permission denied'}), 403
        
        try:
            data = request.json if request.is_json else request.form
            test_email = data.get('email', '').strip()
            
            if not test_email:
                return jsonify({'success': False, 'error': 'Email không được để trống'}), 400
            
            from auth_utils import validate_email
            if not validate_email(test_email):
                return jsonify({'success': False, 'error': 'Email không đúng định dạng'}), 400
            
            # Lấy SMTP settings từ database
            smtp_settings = {}
            settings = self.db_session.query(Setting).filter(
                Setting.category == 'smtp'
            ).all()
            
            for s in settings:
                smtp_settings[s.key] = s.value
            
            # Kiểm tra settings có đủ không
            required_fields = ['smtp_server', 'smtp_port', 'smtp_username', 'smtp_password']
            missing_fields = [f for f in required_fields if not smtp_settings.get(f)]
            
            if missing_fields:
                return jsonify({
                    'success': False,
                    'error': f'Thiếu cài đặt: {", ".join(missing_fields)}'
                }), 400
            
            # Gửi email test
            from email_utils import send_email
            
            subject = "Test Email - VnNews"
            body_html = """
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">Email Test thành công!</h2>
                    <p>Đây là email test từ hệ thống VnNews.</p>
                    <p>Nếu bạn nhận được email này, có nghĩa là cài đặt SMTP của bạn đã hoạt động đúng.</p>
                    <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
                        Đây là email tự động. Vui lòng không trả lời email này.
                    </p>
                </div>
            </body>
            </html>
            """
            body_text = """Email Test thành công!

Đây là email test từ hệ thống VnNews.

Nếu bạn nhận được email này, có nghĩa là cài đặt SMTP của bạn đã hoạt động đúng.
"""
            
            # Tạm thời cập nhật email_utils với settings từ database
            # (Trong thực tế, nên refactor email_utils để đọc từ database)
            success = send_email(test_email, subject, body_html, body_text)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Email test đã được gửi thành công! Vui lòng kiểm tra hộp thư của bạn.'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Không thể gửi email. Vui lòng kiểm tra lại cài đặt SMTP.'
                }), 500
                
        except Exception as e:
            print(f"Error in api_test_email: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
