from flask import Blueprint, render_template, request, jsonify, abort, redirect, url_for, flash, session, current_app
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import or_
from typing import Optional
from functools import wraps
from utils import validate_email, validate_password
from email_utils import send_email
import pytz
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from database import (
    ArticleStatus,
    ArticleTag,
    get_session,
    Articles,
    ArticleStatusEnum,
    UserRole,
    SavedArticles,
    ViewedArticles,
    NewsletterSubscription,
    PasswordResetToken,
    Setting,
    User,
    ArticleRejection,
    ArticleCategory,
    ArticleComment,
    Tag,
)
from models import (
    ArticleModel,
    UserModel,
    ArticleCategoryModel,
)


class AdminController:
    """Controller class quản lý các route của admin"""
    
    def __init__(self):
        """Khởi tạo controller"""
        self.db_session = get_session()
        self.articles_model = ArticleModel(self.db_session)
        self.user_model = UserModel(self.db_session)
        self.article_category_model = ArticleCategoryModel(self.db_session)
    
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
        total_articles = len(self.articles_model.get_all())
        published_articles = len(self.articles_model.get_all(status=ArticleStatusEnum.PUBLISHED))
        pending_articles = len(self.articles_model.get_all(status=ArticleStatusEnum.PENDING))
        draft_articles = len(self.articles_model.get_all(status=ArticleStatusEnum.DRAFT))
        
        # Article chờ duyệt
        pending_list = self.articles_model.get_all(status=ArticleStatusEnum.PENDING, limit=10)
        
        # Article mới nhất
        latest_articles = self.articles_model.get_all(limit=10)
        
        user = self.user_model.get_by_id(session['user_id'])

        return render_template('admin/admin.html',
                             total_articles=total_articles,
                             published_articles=published_articles,
                             pending_articles=pending_articles,
                             draft_articles=draft_articles,
                             pending_list=pending_list,
                             latest_articles=latest_articles,
                             user=user)
    
    def editor_dashboard(self):
        """
        Dashboard editor - Quản lý bài viết của biên tập viên
        Route: GET /admin/editor-dashboard
        """
        user_id = session.get('user_id')
        
        # Lấy article của editor (chỉ dùng để thống kê nhanh)
        all_articles = self.articles_model.get_all()
        my_articles = [a for a in all_articles if a.created_by == user_id]
        
        draft_articles = [a for a in my_articles if a.status == ArticleStatusEnum.DRAFT]
        pending_articles = [a for a in my_articles if a.status == ArticleStatusEnum.PENDING]
        published_articles = [a for a in my_articles if a.status == ArticleStatusEnum.PUBLISHED]
        categories = self.article_category_model.get_all()
        
        user = self.user_model.get_by_id(user_id)

        return render_template('editor/editor.html',
                             draft_articles=draft_articles,
                             pending_articles=pending_articles,
                             published_articles=published_articles,
                             categories=categories,
                             stat_total=len(my_articles),
                             stat_draft=len(draft_articles),
                             stat_pending=len(pending_articles),
                             stat_published=len(published_articles),
                             user=user)
    
    def article_list(self):
        """
        Danh sách article
        Route: GET /admin/articles
        """
        status_filter = request.args.get('status', None)
        page = request.args.get('page', 1, type=int)
        per_page = 20
        offset = (page - 1) * per_page
        
        status = None
        if status_filter:
            try:
                status = ArticleStatusEnum(status_filter)
            except ValueError:
                status = None
        
        articles_list = self.articles_model.get_all(
            limit=per_page,
            offset=offset,
            status=status
        )
        
        categories = self.article_category_model.get_all()
        
        return render_template('admin/articles_list.html',
                             articles_list=articles_list,
                             categories=categories,
                             current_status=status_filter,
                             page=page)
    
    def articles_create(self):
        """
        Tạo article mới
        Route: GET /admin/articles/create
        Route: POST /admin/articles/create
        """
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            category_id = request.form.get('category_id', type=int)
            summary = request.form.get('summary')
            thumbnail = request.form.get('thumbnail')
            status = request.form.get('status', ArticleStatusEnum.DRAFT.value)
            
            user_id = session.get('user_id')
            
            try:
                article_status = ArticleStatusEnum(status)
            except ValueError:
                article_status = ArticleStatusEnum.DRAFT
            
            article = self.articles_model.create(
                title=title,
                content=content,
                category_id=category_id,
                created_by=user_id,
                summary=summary,
                thumbnail=thumbnail,
                status=article_status
            )
            
            flash('Tạo article thành công', 'success')
            return redirect(url_for('admin.articles_edit', article_id=article.id))
        
        categories = self.article_category_model.get_all()
        return render_template('admin/articles_create.html', categories=categories)
    
    def articles_edit(self, article_id: int):
        """
        Chỉnh sửa article
        Route: GET /admin/articles/<article_id>/edit
        Route: POST /admin/articles/<article_id>/edit
        """
        article = self.articles_model.get_by_id(article_id)
        if not article:
            flash('Không tìm thấy article', 'error')
            return redirect(url_for('admin.articles_list'))
        
        # Kiểm tra quyền
        user_id = session.get('user_id')
        user = self.user_model.get_by_id(user_id)
        
        if user.role != UserRole.ADMIN and article.created_by != user_id:
            flash('Bạn không có quyền chỉnh sửa article này', 'error')
            return redirect(url_for('admin.articles_list'))
        
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            category_id = request.form.get('category_id', type=int)
            summary = request.form.get('summary')
            thumbnail = request.form.get('thumbnail')
            status = request.form.get('status')
            
            try:
                article_status = ArticleStatusEnum(status) if status else article.status
            except ValueError:
                article_status = article.status
            
            self.articles_model.update(
                article_id,
                title=title,
                content=content,
                category_id=category_id,
                summary=summary,
                thumbnail=thumbnail,
                status=article_status
            )
            
            flash('Cập nhật article thành công', 'success')
            return redirect(url_for('admin.articles_edit', article_id=article_id))
        
        categories = self.article_category_model.get_all()
        return render_template('admin/articles_edit.html',
                             article=article,
                             categories=categories)
    
    def articles_approve(self, article_id: int):
        """
        Duyệt article
        Route: POST /admin/articles/<article_id>/approve
        """
        user_id = session.get('user_id')
        article = self.articles_model.approve(article_id, user_id)
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            if article:
                return jsonify({'success': True, 'message': 'Đã duyệt article'})
            else:
                return jsonify({'success': False, 'error': 'Không tìm thấy article'}), 404
        
        if article:
            flash('Đã duyệt article', 'success')
        else:
            flash('Không tìm thấy article', 'error')
        
        return redirect(request.referrer or url_for('admin.dashboard'))
    
    def articles_reject(self, article_id: int):
        """
        Từ chối article và gửi email cho tác giả
        Route: POST /admin/articles/<article_id>/reject
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
        
        # Lấy thông tin article trước khi reject
        article = self.articles_model.get_by_id(article_id, include_deleted=False)
        if not article:
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'error': 'Không tìm thấy article'}), 404
            flash('Không tìm thấy article', 'error')
            return redirect(request.referrer or url_for('admin.dashboard'))
        
        # Thực hiện reject với lý do
        rejected_article = self.articles_model.reject(article_id, user_id, reason=reason)
        
        if not rejected_article:
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'error': 'Không thể từ chối article'}), 500
            flash('Không thể từ chối article', 'error')
            return redirect(request.referrer or url_for('admin.dashboard'))
        
        # Lấy thông tin tác giả
        creator = self.user_model.get_by_id(article.created_by)
        if creator and creator.email:
            try:
                # Tạo link article
                article_url = url_for('client.articles_detail', slug=article.slug, _external=True)
                
                email_subject = f"Article của bạn đã bị từ chối: {article.title}"
                
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
                        
                        <p>Chúng tôi rất tiếc phải thông báo rằng article của bạn đã bị từ chối:</p>
                        
                        <h3 style="color: #0066cc;">{article.title}</h3>
                        
                        <div class="reason-box">
                            <strong>Lý do từ chối:</strong>
                            <p style="margin-top: 10px; white-space: pre-wrap;">{reason}</p>
                        </div>
                        
                        <p>Bạn có thể xem lại article của mình tại link sau:</p>
                        <div style="text-align: center;">
                            <a href="{article_url}" class="article-link">Xem article</a>
                        </div>
                        
                        <p>Vui lòng xem xét lại article và chỉnh sửa theo góp ý trên trước khi gửi lại để duyệt.</p>
                        
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
    
    def articles_delete(self, article_id: int):
        """
        Xóa mềm article (soft delete) - set is_deleted = True
        Route: POST /admin/articles/<article_id>/delete
        """
        success = self.articles_model.delete(article_id)
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            if success:
                return jsonify({'success': True, 'message': 'Đã xóa article'})
            else:
                return jsonify({'success': False, 'error': 'Không tìm thấy article'}), 404
        
        if success:
            flash('Đã xóa article', 'success')
        else:
            flash('Không tìm thấy article', 'error')
        
        return redirect(url_for('admin.articles_list'))
    
    def api_articles_list(self):
        """
        API lấy danh sách article (JSON)
        Route: GET /admin/api/articles
        """
        status_filter = request.args.get('status', None)
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        status = None
        if status_filter:
            try:
                status = ArticleStatus(status_filter)
            except ValueError:
                pass
        
        articles_list = self.articles_model.get_all(limit=limit, offset=offset, status=status)
        
        return jsonify({
            'success': True,
            'data': [self._article_to_dict(article) for article in articles_list]
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
                status = ArticleStatus(status_str)
            except ValueError:
                status = None

        offset = (page - 1) * per_page

        items, total = self.articles_model.get_by_creator(
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
                "data": [self._article_to_dict(article) for article in items],
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
        
        items = self.db_session.query(Articles).filter(
            Articles.created_by == user_id,
            Articles.is_deleted == False,  # Chỉ lấy bài chưa bị xóa
            or_(
                Articles.status == ArticleStatusEnum.PUBLISHED,
                Articles.status == ArticleStatusEnum.REJECTED
            )
        ).order_by(
            desc(Articles.published_at),
            desc(Articles.updated_at)
        ).limit(limit).all()

        notifications = []
        for article in items:
            notification = {
                'id': article.id,
                'title': article.title,
                'status': article.status.value,
                'category_name': article.category.name if getattr(article, "category", None) else None,
                'published_at': article.published_at.isoformat() if article.published_at else None,
                'updated_at': article.updated_at.isoformat() if article.updated_at else None,
                'approved_by': article.approver.username if getattr(article, "approver", None) else None,
            }
            notifications.append(notification)

        return jsonify({
            "success": True,
            "data": notifications,
            "count": len(notifications)
        })
    
    def _article_to_dict(self, article) -> dict:
        """Chuyển đổi Article object thành dictionary dùng chung cho admin & client"""
        return {
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'status': article.status.value if getattr(article, "status", None) else None,
            # Thông tin danh mục
            'category': {
                'id': article.category.id if getattr(article, "category", None) else None,
                'name': article.category.name if getattr(article, "category", None) else None,
                'slug': article.category.slug if getattr(article, "category", None) else None,
            },
            # Các field phẳng phục vụ cho UI editor & client
            'category_name': article.category.name if getattr(article, "category", None) else None,
            'summary': getattr(article, "summary", None),
            'thumbnail': getattr(article, "thumbnail", None),
            'visible': getattr(article, "visible", True),
            'created_by': article.creator.username if getattr(article, "creator", None) else None,
            'approved_by': article.approver.username if getattr(article, "approver", None) else None,
            'view_count': getattr(article, "view_count", 0),
            'created_at': article.created_at.isoformat() if getattr(article, "created_at", None) else None,
            'published_at': article.published_at.isoformat() if getattr(article, "published_at", None) else None,
        }
    
    def api_statistics(self):
        """API lấy thống kê dashboard"""
        
        # Đếm số lượng bài viết theo trạng thái
        pending_count = self.db_session.query(Articles).filter(
            Articles.status == ArticleStatus.PENDING
        ).count() or 0
        
        approved_count = self.db_session.query(Articles).filter(
            Articles.status == ArticleStatus.PUBLISHED
        ).count() or 0
        
        rejected_count = self.db_session.query(Articles).filter(
            Articles.status == ArticleStatus.REJECTED
        ).count() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'pending': pending_count,
                'approved': approved_count,
                'rejected': rejected_count,
            }
        })
    
    def api_statistics_editor(self):
        """API lấy thống kê dashboard của editor"""
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
        
        total = self.db_session.query(Articles).filter(
            Articles.created_by == user_id
        ).count() or 0
        
        pending_count = self.db_session.query(Articles).filter(
            Articles.created_by == user_id, Articles.status == ArticleStatus.PENDING
        ).count() or 0
        
        approved_count = self.db_session.query(Articles).filter(
            Articles.created_by == user_id, Articles.status == ArticleStatus.PUBLISHED
        ).count() or 0
        
        published_count = self.db_session.query(Articles).filter(
            Articles.created_by == user_id, Articles.status == ArticleStatus.PUBLISHED
        ).count() or 0
        
        rejected_count = self.db_session.query(Articles).filter(
            Articles.created_by == user_id, Articles.status == ArticleStatus.REJECTED
        ).count() or 0
        
        draft_count = self.db_session.query(Articles).filter(
            Articles.created_by == user_id, Articles.status == ArticleStatus.DRAFT
        ).count() or 0

        article_approved = self.db_session.query(Articles).filter(
            Articles.created_by == user_id, Articles.status == ArticleStatus.PUBLISHED
        ).order_by(Articles.published_at.desc()).first()

        article_update = self.db_session.query(Articles).filter(
            Articles.created_by == user_id, Articles.status == ArticleStatus.DRAFT, Articles.updated_at > Articles.created_at
        ).order_by(Articles.created_at.desc()).first()

        article_newest = self.db_session.query(Articles).filter(
            Articles.created_by == user_id
        ).order_by(Articles.created_at.desc()).first()

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
        articles = self.articles_model.get_all(status=ArticleStatus.PENDING, limit=100)
        
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
        articles = self.articles_model.get_all(status=ArticleStatus.PUBLISHED, limit=100)
        
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
        news_articles = self.articles_model.get_all(status=ArticleStatus.REJECTED, limit=100)
        
        # Lấy thông tin từ chối từ database
        article_ids = [a.id for a in news_articles]
        
        # Query rejection reasons
        news_rejections = {}
        if article_ids:
            rejections = self.db_session.query(ArticleRejection).filter(
                ArticleRejection.article_id.in_(article_ids)
            ).order_by(ArticleRejection.created_at.desc()).all()
            # Lấy rejection mới nhất cho mỗi bài viết
            for rej in rejections:
                if rej.article_id not in news_rejections:
                    news_rejections[rej.article_id] = {
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
        
        data.sort(key=lambda x: x.get('rejected_at', x.get('date', '')), reverse=True)
        
        return jsonify({
            'success': True,
            'data': data
        })
    
    def api_rejected_article(self, article_id: int):
        # Query rejection reasons
        if article_id:
            article = self.articles_model.get_by_id(article_id)
            if article:
                rejection = self.db_session.query(ArticleRejection).filter(
                    ArticleRejection.article_id == article_id
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
    
    def api_chart_data(self):
        """API lấy dữ liệu cho biểu đồ"""
        from datetime import datetime, timedelta
        
        # Lấy dữ liệu 7 ngày gần nhất
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)

        # Đếm bài viết mới theo ngày
        new_articles = self.db_session.query(Articles).filter(
            Articles.created_at >= start_date
        ).group_by(Articles.created_at).count()
        
        # Đếm bài được duyệt theo ngày
        approved_articles = self.db_session.query(Articles).filter(
            Articles.published_at >= start_date,
            Articles.status == ArticleStatus.PUBLISHED
        ).group_by(Articles.published_at).count()
        
        new_dict = {str(item.date): item.count for item in new_articles}
        approved_dict = {str(item.date): item.count for item in approved_articles}
        
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
        articles = self.articles_model.get_hot(limit=10)
        
        return jsonify({
            'success': True,
            'data': [{
                'title': article.title,
                'views': article.view_count
            } for article in articles]
        })
    
    def api_article_detail(self, article_id: int):
        """API lấy chi tiết bài viết theo ID"""
        article = self.articles_model.get_by_id(article_id)
        
        if not article:
            return jsonify({
                'success': False,
                'message': 'Bài viết không tồn tại'
            }), 404
        
        # Lấy tags từ ArticleTag relationship
        article_tags = self.db_session.query(ArticleTag).filter(ArticleTag.article_id == article.id).all()
        tag_ids = [at.tag_id for at in article_tags]
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
    
    def api_categories(self):
        """API lấy danh sách danh mục"""
        categories = self.article_category_model.get_all()
        
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

            # Xóa liên kết ArticleTag trước khi xóa tag
            self.db_session.query(ArticleTag).where(ArticleTag.tag_id == tag_id).delete()
            self.db_session.delete(tag)
            self.db_session.commit()

            return jsonify({'success': True})
        except SQLAlchemyError as e:
            self.db_session.rollback()
            current_app.logger.exception('Lỗi xóa hashtag: %s', e)
            return jsonify({'success': False, 'error': 'Không thể xóa hashtag'}), 500

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
        status = data.get('status', ArticleStatus.DRAFT.value)
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
        
        # Kiểm tra ArticleCategory tồn tại
        category = self.db_session.query(ArticleCategory).filter(ArticleCategory.category_id == category_id).first()
        if not category:
            return jsonify({'success': False, 'error': 'Danh mục không tồn tại'}), 400
        
        try:
            article_status = ArticleStatus(status)
        except ValueError:
            article_status = ArticleStatus.DRAFT
        
        # Tạo slug từ tiêu đề và trạng thái
        print(title)
        print(status)
        base_slug = self._generate_slug(title, status)
        slug = base_slug
        
        # Kiểm tra slug trùng và thêm số nếu cần
        counter = 1
        while self.db_session.query(Articles).filter(Articles.slug == slug).first():
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
            article = Articles(
                title=title,
                slug=slug,
                content=content,
                summary=summary,
                thumbnail=thumbnail,
                images=images_json,
                category_id=category_id,
                created_by=user_id,
                status=article_status,
                is_hot=bool(is_hot),
                is_featured=bool(is_featured),
                published_at=datetime.utcnow() if article_status == ArticleStatus.PUBLISHED else None
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
                self.db_session.query(ArticleTag).filter(ArticleTag.news_id == article.id).delete()
                
                tag_names = self._parse_tags(tags)
                invalid_tags = []
                
                for tag_name in tag_names:
                    # CHỈ tìm tag có sẵn, KHÔNG tự tạo mới
                    tag = self.db_session.query(Tag).filter(Tag.name == tag_name).first()
                    if not tag:
                        invalid_tags.append(tag_name)
                        continue
                    
                    # Tạo ArticleTag mới
                    news_tag = ArticleTag(news_id=article.id, tag_id=tag.id)
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
        article = self.db_session.query(Articles).filter(Articles.id == article_id).first()
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
        category = self.db_session.query(ArticleCategory).filter(ArticleCategory.category_id == category_id).first()
        if not category:
            return jsonify({'success': False, 'error': 'Danh mục không tồn tại'}), 400
        
        try:
            article_status = ArticleStatus(status)
        except ValueError:
            article_status = article.status
        
        # Tạo slug từ tiêu đề và trạng thái
        base_slug = self._generate_slug(title, status)
        slug = base_slug
        
        # Kiểm tra slug trùng và thêm số nếu cần (nhưng không trùng với chính nó)
        counter = 1
        while self.db_session.query(Articles).filter(Articles.slug == slug, Articles.id != article_id).first():
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
            article.status = article_status
            article.is_hot = bool(is_hot)
            article.is_featured = bool(is_featured)
            article.published_at = datetime.utcnow() if article_status == ArticleStatus.PUBLISHED else article.published_at
            
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
                self.db_session.query(ArticleTag).filter(ArticleTag.news_id == article.id).delete()
                
                tag_names = self._parse_tags(tags)
                invalid_tags = []
                
                for tag_name in tag_names:
                    # CHỈ tìm tag có sẵn, KHÔNG tự tạo mới
                    tag = self.db_session.query(Tag).filter(Tag.name == tag_name).first()
                    if not tag:
                        invalid_tags.append(tag_name)
                        continue
                    
                    # Tạo ArticleTag mới
                    article_tag = ArticleTag(news_id=article.id, tag_id=tag.id)
                    self.db_session.add(article_tag)
                
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

    def api_menu_items(self):
        """API lấy danh sách categories (menu items)"""
        categories = self.db_session.query(ArticleCategory).order_by(
            ArticleCategory.order_display, ArticleCategory.parent_id
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
        
        parent = self.db_session.query(ArticleCategory).filter(ArticleCategory.id == parent_id).first()
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
        existing = self.db_session.query(ArticleCategory).filter(ArticleCategory.slug == slug).first()
        if existing:
            return jsonify({'success': False, 'error': 'Slug đã tồn tại'}), 400
        
        # Tính toán level
        level = self._calculate_level(parent_id)
        
        # Kiểm tra level không được vượt quá 4
        if level > 4:
            return jsonify({'success': False, 'error': 'Không thể tạo menu quá 4 cấp. Menu hiện tại đã đạt cấp tối đa.'}), 400
        
        category = ArticleCategory(
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
        category = self.db_session.query(ArticleCategory).filter(ArticleCategory.id == menu_id).first()
        if not category:
            return jsonify({'success': False, 'error': 'Không tìm thấy danh mục'}), 404
        
        data = request.json if request.is_json else request.form
        
        if 'name' in data:
            category.name = data['name']
        if 'slug' in data:
            # Kiểm tra slug trùng (trừ chính nó)
            existing = self.db_session.query(ArticleCategory).filter(
                ArticleCategory.slug == data['slug'],
                ArticleCategory.id != menu_id
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
                    parent_candidate = self.db_session.query(ArticleCategory).filter(ArticleCategory.id == parent_candidate_id).first()
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
        category = self.db_session.query(ArticleCategory).filter(ArticleCategory.id == menu_id).first()
        if not category:
            return jsonify({'success': False, 'error': 'Không tìm thấy danh mục'}), 404
        
        # Kiểm tra xem có tin tức nào đang sử dụng category này không
        news_count = self.db_session.query(Articles).filter(Articles.category_id == menu_id).count()
        if news_count > 0:
            return jsonify({
                'success': False,
                'error': f'Không thể xóa danh mục vì có {news_count} tin tức đang sử dụng'
            }), 400
        
        # Xóa các category con trước (cascade)
        children = self.db_session.query(ArticleCategory).filter(ArticleCategory.parent_id == menu_id).all()
        for child in children:
            # Kiểm tra tin tức của child category
            child_news_count = self.db_session.query(Articles).filter(Articles.category_id == child.id).count()
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
        count = self.db_session.query(ArticleCategory).count()
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
            category = ArticleCategory(
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
                category = ArticleCategory(
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
                
                category = self.db_session.query(ArticleCategory).filter(ArticleCategory.id == category_id).first()
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
        saved_news = self.db_session.query(SavedArticles).filter(
            SavedArticles.user_id == user.id
        ).order_by(SavedArticles.created_at.desc()).limit(20).all()
        
        # Lấy tin đã xem (cả site VN và EN)
        viewed_news = self.db_session.query(ViewedArticles).filter(
            ViewedArticles.user_id == user.id
        ).order_by(ViewedArticles.viewed_at.desc()).limit(20).all()

        comments = []

        # Tính số bình luận cho mỗi bài viết (cả news_id và news_international_id)
        comment_counts = {}
        if comments:
            news_ids = list(set([comment.news_id for comment in comments if comment.news_id]))
            
            from sqlalchemy import func
            
            # Đếm comments cho news_id
            if news_ids:
                counts_vn = self.db_session.query(ArticleComment).filter(
                    ArticleComment.news_id.in_(news_ids),
                    ArticleComment.is_active == True
                ).group_by(ArticleComment.news_id).count() or 0
                
                for news_id, count in counts_vn:
                    comment_counts[news_id] = count

        # Tính tổng số bình luận của cá nhân
        total_comments = self.db_session.query(ArticleComment).filter(
            ArticleComment.user_id == user.id,
            ArticleComment.is_active == True
        ).count()

        categories = self.article_category_model.get_all()
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
