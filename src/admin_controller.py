from flask import Blueprint, render_template, request, jsonify, abort, redirect, url_for, flash, session, current_app
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import or_, desc
from utils import validate_email, validate_password
from email_utils import send_email
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from database import (
    Tour,
    TourRejection,
    TourStatus,
    get_session,
    UserRole,
    NewsletterSubscription,
    PasswordResetToken,
    Setting,
    User,
    Tag,
)
from models import (
    TourModel,
    UserModel,
    BookingModel
)


class AdminController:
    """Controller class quản lý các route của admin"""
    
    def __init__(self):
        """Khởi tạo controller"""
        self.db_session = get_session()
        self.tour_model = TourModel(self.db_session)
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
        total_tour = len(self.tour_model.get_all())
        published_tour = len(self.tour_model.get_all(status=TourStatus.PUBLISHED))
        pending_tour = len(self.tour_model.get_all(status=TourStatus.PENDING))
        draft_tour = len(self.tour_model.get_all(status=TourStatus.DRAFT))
        
        # Tour chờ duyệt
        pending_list = self.tour_model.get_all(status=TourStatus.PENDING, limit=10)
        
        # Tour mới nhất
        latest_tours = self.tour_model.get_all(limit=10)
        
        user = self.user_model.get_by_id(session['user_id'])

        return render_template('admin/admin.html',
                             total_tours=total_tour,
                             published_tours=published_tour,
                             pending_tours=pending_tour,
                             draft_tours=draft_tour,
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
        all_tours = self.tour_model.get_all()
        my_tours = [t for t in all_tours if t.created_by == user_id]
        
        draft_tours = [t for t in my_tours if t.status == TourStatus.DRAFT]
        pending_tours = [t for t in my_tours if t.status == TourStatus.PENDING]
        published_tours = [t for t in my_tours if t.status == TourStatus.PUBLISHED]
        
        user = self.user_model.get_by_id(user_id)

        return render_template('editor/editor.html',
                             draft_tours=draft_tours,
                             pending_tours=pending_tours,
                             published_tours=published_tours,
                             stat_total=len(my_tours),
                             stat_draft=len(draft_tours),
                             stat_pending=len(pending_tours),
                             stat_published=len(published_tours),
                             user=user)
    
    def tour_list(self):
        """
        Danh sách tour
        Route: GET /admin/tour
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
        
        tour_list = self.tour_model.get_all(
            limit=per_page,
            offset=offset,
            status=status
        )
        
        return render_template('admin/tours_list.html',
                             tour_list=tour_list,
                             current_status=status_filter,
                             page=page)
    
    def tour_create(self):
        """
        Tạo tour mới
        Route: GET /admin/tour/create
        Route: POST /admin/tour/create
        """
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            summary = request.form.get('summary')
            thumbnail = request.form.get('thumbnail')
            status = request.form.get('status', TourStatus.DRAFT.value)
            
            user_id = session.get('user_id')
            
            try:
                tour_status = TourStatus(status)
            except ValueError:
                tour_status = TourStatus.DRAFT
            
            tour = self.tour_model.create(
                title=title,
                content=content,
                created_by=user_id,
                summary=summary,
                thumbnail=thumbnail,
                status=tour_status
            )
            
            flash('Tạo tour thành công', 'success')
            return redirect(url_for('admin.tours_edit', tour_id=tour.id))
    
    def tours_edit(self, tour_id: int):
        """
        Chỉnh sửa tour
        Route: GET /admin/tour/<tour_id>/edit
        Route: POST /admin/tour/<tour_id>/edit
        """
        tour = self.tour_model.get_by_id(tour_id)
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
            summary = request.form.get('summary')
            thumbnail = request.form.get('thumbnail')
            status = request.form.get('status')
            
            try:
                tour_status = TourStatus(status) if status else tour.status
            except ValueError:
                tour_status = tour.status
            
            self.tour_model.update(
                tour_id,
                title=title,
                content=content,
                summary=summary,
                thumbnail=thumbnail,
                status=tour_status
            )
            
            flash('Cập nhật tour thành công', 'success')
            return redirect(url_for('admin.tours_edit', tour_id=tour_id))
        
        return render_template('admin/tours_edit.html',
                             tour=tour)
    
    def tours_approve(self, tour_id: int):
        """
        Duyệt tour
        Route: POST /admin/tour/<tour_id>/approve
        """
        user_id = session.get('user_id')
        tour = self.tour_model.approve(tour_id, user_id)
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            if tour:
                return jsonify({'success': True, 'message': 'Đã duyệt tour'})
            else:
                return jsonify({'success': False, 'error': 'Không tìm thấy tour'}), 404
        
        if tour:
            flash('Đã duyệt tour', 'success')
        else:
            flash('Không tìm thấy tour', 'error')
        
        return redirect(request.referrer or url_for('admin.dashboard'))
    
    def tours_reject(self, tour_id: int):
        """
        Từ chối tour và gửi email cho tác giả
        Route: POST /admin/tour/<tour_id>/reject
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
        
        # Lấy thông tin tour trước khi reject
        tour = self.tour_model.get_by_id(tour_id, include_deleted=False)
        if not tour:
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'error': 'Không tìm thấy tour'}), 404
            flash('Không tìm thấy tour', 'error')
            return redirect(request.referrer or url_for('admin.dashboard'))
        
        # Thực hiện reject với lý do
        rejected_tour = self.tour_model.reject(tour_id, user_id, reason=reason)
        
        if not rejected_tour:
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'error': 'Không thể từ chối tour'}), 500
            flash('Không thể từ chối tour', 'error')
            return redirect(request.referrer or url_for('admin.dashboard'))
        
        # Lấy thông tin tác giả
        creator = self.user_model.get_by_id(tour.created_by)
        if creator and creator.email:
            try:
                # Tạo link tour
                tour_url = url_for('client.tours_detail', slug=tour.slug, _external=True)
                
                email_subject = f"Tour của bạn đã bị từ chối: {tour.title}"
                
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
                        .tour-link {{
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
                        
                        <p>Chúng tôi rất tiếc phải thông báo rằng tour của bạn đã bị từ chối:</p>
                        
                        <h3 style="color: #0066cc;">{tour.title}</h3>
                        
                        <div class="reason-box">
                            <strong>Lý do từ chối:</strong>
                            <p style="margin-top: 10px; white-space: pre-wrap;">{reason}</p>
                        </div>
                        
                        <p>Bạn có thể xem lại tour của mình tại link sau:</p>
                        <div style="text-align: center;">
                            <a href="{tour_url}" class="tour-link">Xem tour</a>
                        </div>
                        
                        <p>Vui lòng xem xét lại tour và chỉnh sửa theo góp ý trên trước khi gửi lại để duyệt.</p>
                        
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
    
    def tour_delete(self, tour_id: int):
        """
        Xóa mềm tour (soft delete) - set is_deleted = True
        Route: POST /admin/tour/<tour_id>/delete
        """
        success = self.tour_model.delete(tour_id)
        
        if request.is_json or request.headers.get('Content-Type') == 'application/json':
            if success:
                return jsonify({'success': True, 'message': 'Đã xóa tour'})
            else:
                return jsonify({'success': False, 'error': 'Không tìm thấy tour'}), 404
        
        if success:
            flash('Đã xóa tour', 'success')
        else:
            flash('Không tìm thấy tour', 'error')
        
        return redirect(url_for('admin.tour_list'))
    
    def api_tour_list(self):
        """
        API lấy danh sách tour (JSON)
        Route: GET /admin/api/tour
        """
        status_filter = request.args.get('status', None)
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        status = None
        if status_filter:
            try:
                status = TourStatus(status_filter)
            except ValueError:
                pass
        
        tour_list = self.tour_model.get_all(limit=limit, offset=offset, status=status)
        
        return jsonify({
            'success': True,
            'data': [self._tour_to_dict(tour) for tour in tour_list]
        })

    def api_my_tour(self):
        """
        API lấy danh sách tour của editor hiện tại (JSON)
        Route: GET /admin/api/my-tour
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
                status = TourStatus(status_str)
            except ValueError:
                status = None

        offset = (page - 1) * per_page

        items, total = self.tour_model.get_by_creator(
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
                "data": [self._tour_to_dict(tour) for tour in items],
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
        
        items = self.db_session.query(Tour).filter(
            Tour.created_by == user_id,
            Tour.is_deleted == False,  # Chỉ lấy bài chưa bị xóa
            or_(
                Tour.status == TourStatus.PUBLISHED,
                Tour.status == TourStatus.REJECTED
            )
        ).order_by(
            desc(Tour.published_at),
            desc(Tour.updated_at)
        ).limit(limit).all()

        notifications = []
        for tour in items:
            notification = {
                'id': tour.id,
                'title': tour.title,
                'status': tour.status.value,
                'published_at': tour.published_at.isoformat() if tour.published_at else None,
                'updated_at': tour.updated_at.isoformat() if tour.updated_at else None,
                'approved_by': tour.approver.username if getattr(tour, "approver", None) else None,
            }
            notifications.append(notification)

        return jsonify({
            "success": True,
            "data": notifications,
            "count": len(notifications)
        })
    
    def _tour_to_dict(self, tour) -> dict:
        """Chuyển đổi Tour object thành dictionary dùng chung cho admin & client"""
        return {
            'id': tour.id,
            'title': tour.title,
            'slug': tour.slug,
            'status': tour.status.value if getattr(tour, "status", None) else None,
            'category_name': tour.category.name if getattr(tour, "category", None) else None,
            'summary': getattr(tour, "summary", None),
            'thumbnail': getattr(tour, "thumbnail", None),
            'visible': getattr(tour, "visible", True),
            'created_by': tour.creator.username if getattr(tour, "creator", None) else None,
            'approved_by': tour.approver.username if getattr(tour, "approver", None) else None,
            'view_count': getattr(tour, "view_count", 0),
            'created_at': tour.created_at.isoformat() if getattr(tour, "created_at", None) else None,
            'published_at': tour.published_at.isoformat() if getattr(tour, "published_at", None) else None,
        }
    
    def api_statistics(self):
        """API lấy thống kê dashboard"""
        
        # Đếm số lượng bài viết theo trạng thái
        pending_count = self.db_session.query(Tour).filter(
            Tour.status == TourStatus.PENDING
        ).count() or 0
        
        approved_count = self.db_session.query(Tour).filter(
            Tour.status == TourStatus.PUBLISHED
        ).count() or 0
        
        rejected_count = self.db_session.query(Tour).filter(
            Tour.status == TourStatus.REJECTED
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
        
        total = self.db_session.query(Tour).filter(
            Tour.created_by == user_id
        ).count() or 0
        
        pending_count = self.db_session.query(Tour).filter(
            Tour.created_by == user_id, Tour.status == TourStatus.PENDING
        ).count() or 0
        
        approved_count = self.db_session.query(Tour).filter(
            Tour.created_by == user_id, Tour.status == TourStatus.PUBLISHED
        ).count() or 0
        
        published_count = self.db_session.query(Tour).filter(
            Tour.created_by == user_id, Tour.status == TourStatus.PUBLISHED
        ).count() or 0
        
        rejected_count = self.db_session.query(Tour).filter(
            Tour.created_by == user_id, Tour.status == TourStatus.REJECTED
        ).count() or 0
        
        draft_count = self.db_session.query(Tour).filter(
            Tour.created_by == user_id, Tour.status == TourStatus.DRAFT
        ).count() or 0

        tour_approved = self.db_session.query(Tour).filter(
            Tour.created_by == user_id, Tour.status == TourStatus.PUBLISHED
        ).order_by(Tour.published_at.desc()).first()

        tour_update = self.db_session.query(Tour).filter(
            Tour.created_by == user_id, Tour.status == TourStatus.DRAFT, Tour.updated_at > Tour.created_at
        ).order_by(Tour.created_at.desc()).first()

        tour_newest = self.db_session.query(Tour).filter(
            Tour.created_by == user_id
        ).order_by(Tour.created_at.desc()).first()

        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'pending': pending_count,
                'published': published_count,
                'rejected': rejected_count,
                'approved': approved_count,
                'draft': draft_count,
                'tour_approved': tour_approved.title if tour_approved else '',
                'tour_update': tour_update.title if tour_update else '',
                'tour_newest': tour_newest.title if tour_newest else ''
            }
        })

    def api_pending_tour(self):
        """API lấy danh sách bài viết chờ duyệt"""
        tour = self.tour_model.get_all(status=TourStatus.PENDING, limit=100)
        
        return jsonify({
            'success': True,
            'data': [{
                'id': tour.id,
                'title': tour.title,
                'author': tour.creator.username if tour.creator else 'N/A',
                'category': tour.category.name if tour.category else 'N/A',
                'date': tour.created_at.strftime('%d/%m/%Y %H:%M') if tour.created_at else '',
                'status': tour.status.value
            } for tour in tour]
        })
    
    def api_approved_tour(self):
        """API lấy danh sách bài viết đã duyệt"""
        tour = self.tour_model.get_all(status=TourStatus.PUBLISHED, limit=100)
        
        return jsonify({
            'success': True,
            'data': [{
                'id': tour.id,
                'title': tour.title,
                'author': tour.creator.username if tour.creator else 'N/A',
                'category': tour.category.name if tour.category else 'N/A',
                'date': tour.published_at.strftime('%d/%m/%Y %H:%M') if tour.published_at else '',
                'views': tour.view_count
            } for tour in tour]
        })
    
    def api_rejected_tour(self):
        """API lấy danh sách bài viết bị từ chối (bao gồm cả news và news_international)"""
        # Lấy bài viết trong nước bị từ chối
        news_tour = self.tour_model.get_all(status=TourStatus.REJECTED, limit=100)
        
        # Lấy thông tin từ chối từ database
        tour_ids = [t.id for t in news_tour]
        
        # Query rejection reasons
        news_rejections = {}
        if tour_ids:
            rejections = self.db_session.query(TourRejection).filter(
                TourRejection.tour_id.in_(tour_ids)
            ).order_by(TourRejection.created_at.desc()).all()
            # Lấy rejection mới nhất cho mỗi bài viết
            for rej in rejections:
                if rej.tour_id not in news_rejections:
                    news_rejections[rej.tour_id] = {
                        'reason': rej.reason,
                        'rejected_by': rej.rejector.username if rej.rejector else 'N/A',
                        'rejected_at': rej.created_at.strftime('%d/%m/%Y %H:%M') if rej.created_at else ''
                    }
        
        # Tạo danh sách kết quả
        data = []
        
        # Thêm bài viết trong nước
        for tour in news_tour:
            rejection_info = news_rejections.get(tour.id, {})
            data.append({
                'id': tour.id,
                'title': tour.title,
                'author': tour.creator.username if tour.creator else 'N/A',
                'category': tour.category.name if tour.category else 'N/A',
                'date': tour.created_at.strftime('%d/%m/%Y %H:%M') if tour.created_at else '',
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

    def api_api_tour(self):
        """API lấy danh sách bài viết từ API bên ngoài (chỉ hiển thị, không lưu)"""
        # Lấy dữ liệu từ session hoặc cache (tạm thời lưu trong session)
        # Hoặc fetch lại từ API nếu cần
        api_tour = session.get('api_tour_cache', [])
        
        return jsonify({
            'success': True,
            'data': api_tour
        })

    def api_chart_data(self):
        """API lấy dữ liệu cho biểu đồ"""
        
        # Lấy dữ liệu 7 ngày gần nhất
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)

        # Đếm bài viết mới theo ngày
        new_tour = self.db_session.query(Tour).filter(
            Tour.created_at >= start_date
        ).group_by(Tour.created_at).count()
        
        # Đếm bài được duyệt theo ngày
        approved_tour = self.db_session.query(Tour).filter(
            Tour.published_at >= start_date,
            Tour.status == TourStatus.PUBLISHED
        ).group_by(Tour.published_at).count()
        
        new_dict = {str(item.date): item.count for item in new_tour}
        approved_dict = {str(item.date): item.count for item in approved_tour}
        
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

    def api_tour_detail(self, tour_id: int):
        """API lấy chi tiết bài viết theo ID"""
        tour = self.tour_model.get_by_id(tour_id)
        
        if not tour:
            return jsonify({
                'success': False,
                'message': 'Bài viết không tồn tại'
            }), 404
        
        # Xác định author: nếu là bài từ API thì dùng author field, không thì dùng creator
        author_name = tour.author if (hasattr(tour, 'is_api') and tour.is_api and hasattr(tour, 'author') and tour.author) else (tour.creator.username if tour.creator else 'N/A')
        author_full_name = tour.author if (hasattr(tour, 'is_api') and tour.is_api and hasattr(tour, 'author') and tour.author) else (tour.creator.full_name if tour.creator and tour.creator.full_name else tour.creator.username if tour.creator else 'N/A')
        
        return jsonify({
            'success': True,
            'data': {
                'id': tour.id,
                'title': tour.title,
                'slug': tour.slug,
                'summary': tour.summary or '',
                'content': tour.content or '',
                'thumbnail': tour.thumbnail or '',
                'category': tour.category.name if tour.category else 'N/A',
                'category_id': tour.category_id,
                'author': author_name,
                'author_full_name': author_full_name,
                'approver': tour.approver.username if tour.approver else None,
                'approver_full_name': tour.approver.full_name if tour.approver and tour.approver.full_name else (tour.approver.username if tour.approver else None),
                'is_api': tour.is_api if hasattr(tour, 'is_api') else False,
                'status': tour.status.value,
                'created_at': tour.created_at.strftime('%d/%m/%Y %H:%M') if tour.created_at else '',
                'published_at': tour.published_at.strftime('%d/%m/%Y %H:%M') if tour.published_at else '',
                'updated_at': tour.updated_at.strftime('%d/%m/%Y %H:%M') if tour.updated_at else '',
                'view_count': tour.view_count,
                'is_featured': tour.is_featured if hasattr(tour, 'is_featured') else False,
                'is_hot': tour.is_hot if hasattr(tour, 'is_hot') else False,
                'is_deleted': tour.is_deleted if hasattr(tour, 'is_deleted') else False,
            }
        })

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

    def api_create_tour(self):
        """API tạo tour mới từ editor form"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
        
        data = request.json if request.is_json else request.form
        
        # Lấy dữ liệu từ form
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        summary = data.get('summary') or data.get('description', '').strip()
        thumbnail = data.get('thumbnail', '').strip()
        status = data.get('status', TourStatus.DRAFT.value)
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

        try:
            tour_status = TourStatus(status)
        except ValueError:
            tour_status = TourStatus.DRAFT
        
        base_slug = self._generate_slug(title, status)
        slug = base_slug
        
        counter = 1
        while self.db_session.query(Tour).filter(Tour.slug == slug).first():
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
            tour = Tour(
                title=title,
                slug=slug,
                content=content,
                summary=summary,
                thumbnail=thumbnail,
                images=images_json,
                created_by=user_id,
                status=tour_status,
                is_hot=bool(is_hot),
                is_featured=bool(is_featured),
                published_at=datetime.utcnow() if tour_status == TourStatus.PUBLISHED else None
            )
            
            self.db_session.add(tour)
            self.db_session.commit()
            self.db_session.refresh(tour)
            
            # Di chuyển ảnh từ temp folder sang folder của bài viết nếu có
            if tour.id:
                temp_folder = os.path.join('src', 'static', 'uploads', 'news', 'vn', 'temp')
                news_folder = os.path.join('src', 'static', 'uploads', 'news', 'vn', f'news_{tour.id}')
                
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
                                thumbnail = thumbnail.replace('temp', f'news_{tour.id}')
                                tour.thumbnail = thumbnail
                            if images_json:
                                import json
                                images = json.loads(images_json)
                                updated_images = [img.replace('temp', f'news_{tour.id}') if 'temp' in img else img for img in images]
                                tour.images = json.dumps(updated_images)
                                # Cập nhật content với URL mới
                                for old_url, new_url in zip(images, updated_images):
                                    if old_url != new_url:
                                        content = content.replace(old_url, new_url)
                                        tour.content = content
                    self.db_session.commit()
            
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
                'id': tour.id,
                'slug': tour.slug,
                'title': tour.title
            }
        })

    def api_edit_tour(self, tour_id: int):
        """API chỉnh sửa bài viết theo ID"""
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
        
        data = request.json if request.is_json else request.form
        tour = self.db_session.query(Tour).filter(Tour.id == tour_id).first()
        if not tour:
            return jsonify({'success': False, 'error': 'Bài viết không tồn tại'}), 400
        
        # Lấy dữ liệu từ form
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        category_id = data.get('category_id') or data.get('category')
        summary = data.get('summary') or data.get('description', '').strip()
        thumbnail = data.get('thumbnail', '').strip()
        status = data.get('status', tour.status.value)
        is_hot = data.get('is_hot', tour.is_hot if hasattr(tour, 'is_hot') else False)
        is_featured = data.get('is_featured', tour.is_featured if hasattr(tour, 'is_featured') else False)
        
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
        
        try:
            tour_status = TourStatus(status)
        except ValueError:
            tour_status = tour.status
        
        # Tạo slug từ tiêu đề và trạng thái
        base_slug = self._generate_slug(title, status)
        slug = base_slug
        
        # Kiểm tra slug trùng và thêm số nếu cần (nhưng không trùng với chính nó)
        counter = 1
        while self.db_session.query(Tour).filter(Tour.slug == slug, Tour.id != tour_id).first():
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
            tour.title = title
            tour.slug = slug
            tour.content = content
            tour.summary = summary
            tour.thumbnail = thumbnail
            tour.images = images_json
            tour.category_id = category_id
            tour.status = tour_status
            tour.is_hot = bool(is_hot)
            tour.is_featured = bool(is_featured)
            tour.published_at = datetime.utcnow() if tour_status == TourStatus.PUBLISHED else tour.published_at
            
            self.db_session.commit()
            self.db_session.refresh(tour)
            
            # Di chuyển ảnh từ temp folder sang folder của bài viết nếu có
            if tour.id:
                temp_folder = os.path.join('src', 'static', 'uploads', 'news', 'vn', 'temp')
                news_folder = os.path.join('src', 'static', 'uploads', 'news', 'vn', f'news_{tour.id}')
                
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
                                thumbnail = thumbnail.replace('temp', f'news_{tour.id}')
                                tour.thumbnail = thumbnail
                            if images_json:
                                import json
                                images = json.loads(images_json)
                                updated_images = [img.replace('temp', f'news_{tour.id}') if 'temp' in img else img for img in images]
                                tour.images = json.dumps(updated_images)
                                # Cập nhật content với URL mới
                                for old_url, new_url in zip(images, updated_images):
                                    if old_url != new_url:
                                        content = content.replace(old_url, new_url)
                                        tour.content = content
                    self.db_session.commit()

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
                'id': tour.id,
                'slug': tour.slug,
                'title': tour.title
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
        
        booking = self.db_session.query(BookingModel).filter(
            BookingModel.user_id == user.id
        ).order_by(BookingModel.created_at.desc()).limit(20).all()

        return render_template('admin/profile.html', 
                             user=user, 
                             booking=booking
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
