from random import random
from database import Location
from flask import Blueprint, render_template, request, jsonify, abort, redirect, url_for, flash, session, current_app
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import or_, desc
import re
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from utils import validate_email, validate_password, generate_slug, verify_password, hash_password, CATEGORY_NAME, CATEGORY_NAME_DICT
from email_utils import send_email
from template_html import EMAIL_BODY_HTML, EMAIL_SUBJECT_TEST, EMAIL_BODY_HTML_TEST, EMAIL_BODY_TEXT_TEST
from database import (
    Tour,
    TourRejection,
    TourStatus,
    get_session,
    UserRole,
    Setting,
    User,
    Bookings,
    BookingStatus,
    BookingType,
)
from models.tour_models import TourModel
from models.user_models import AdminModel
from models.booking_models import BookingModel
from models.related_models import LocationModel, SettingModel


class AdminController:
    """Controller class quản lý các route của admin"""
    
    def __init__(self):
        """Khởi tạo controller"""
        self.db_session = get_session()
        self.tour_model = TourModel(self.db_session)
        self.admin_model = AdminModel(self.db_session)
        self.booking_model = BookingModel(self.db_session)
        self.setting_model = SettingModel(self.db_session)
        self.location_model = LocationModel(self.db_session)
    
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

            data = request.json if request.is_json else request.form
            username = data.get('username')
            password = data.get('password')
            remember = data.get('remember') == 'on'
            
            # Kiểm tra tài khoản bị khóa trước khi xác thực
            if self.admin_model.is_locked_user(username):
                flash('Tài khoản đã bị khóa. Vui lòng liên hệ quản trị viên', 'error')
                return render_template('admin/login.html')
            
            user = self.admin_model.authenticate(username, password)
            
            if user and user.is_active and user.role in [UserRole.ADMIN, UserRole.STAFF]:
                # Lưu session đăng nhập
                session['user_id'] = user.user_id
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
        
        if 'user_id' not in session:
            return redirect(url_for('admin.login'))

        user = self.admin_model.get_by_id(session['user_id'])

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
        my_tours = [t for t in all_tours if t.author_id == user_id]
        
        draft_tours = [t for t in my_tours if t.status == TourStatus.DRAFT]
        pending_tours = [t for t in my_tours if t.status == TourStatus.PENDING]
        published_tours = [t for t in my_tours if t.status == TourStatus.PUBLISHED]
        
        user = self.admin_model.get_by_id(user_id)

        location_list = self.location_model.get_all()

        return render_template('editor/editor.html',
                             draft_tours=draft_tours,
                             pending_tours=pending_tours,
                             published_tours=published_tours,
                             stat_total=len(my_tours),
                             stat_draft=len(draft_tours),
                             stat_pending=len(pending_tours),
                             stat_published=len(published_tours),
                             categories=CATEGORY_NAME,
                             locations=location_list,
                             user=user)
    
    def tour_list(self):
        """
        Danh sách tour
        Route: GET /admin/tour
        """
        status_filter = request.args.get('status', 'ALL')
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

            data = request.json if request.is_json else request.form
            title = data.get('title')
            content = data.get('content')
            summary = data.get('summary')
            thumbnail = data.get('thumbnail')
            status = data.get('status', TourStatus.DRAFT.value)
            
            user_id = session.get('user_id')
            
            try:
                tour_status = TourStatus(status)
            except ValueError:
                tour_status = TourStatus.DRAFT
            
            tour = self.tour_model.create(
                title=title,
                content=content,
                author_id=user_id,
                summary=summary,
                thumbnail=thumbnail,
                status=tour_status
            )
            
            flash('Tạo tour thành công', 'success')
            return redirect(url_for('admin.tours_edit', tour_id=tour.tour_id))
    
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
        user = self.admin_model.get_by_id(user_id)
        
        if user.role != UserRole.ADMIN and tour.author_id != user_id:
            flash('Bạn không có quyền chỉnh sửa tour này', 'error')
            return redirect(url_for('admin.tours_list'))
            
        # Kiểm tra trạng thái bài viết theo quyền
        if user.role == UserRole.STAFF:
            if tour.status not in [TourStatus.DRAFT, TourStatus.REJECTED]:
                flash('Bài viết đang trong trạng thái chờ duyệt hoặc đã xuất bản, bạn không thể chỉnh sửa', 'error')
                return redirect(url_for('admin.editor_dashboard'))
        elif user.role == UserRole.ADMIN:
            if tour.status not in [TourStatus.PENDING, TourStatus.APPROVED, TourStatus.PUBLISHED]:
                flash('Bài viết đang do nhân viên soạn thảo hoặc chỉnh sửa, admin không thể chỉnh sửa', 'error')
                return redirect(url_for('admin.tours_list'))
        
        if request.method == 'POST':

            data = request.json if request.is_json else request.form
            title = data.get('title')
            content = data.get('content')
            summary = data.get('summary')
            thumbnail = data.get('thumbnail')
            status = data.get('status')
            
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
        data = request.json if request.is_json else request.form
        reason = data.get('reason', '').strip()
        
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
        author = self.admin_model.get_by_id(tour.author_id)
        if author and author.email:
            try:
                # Tạo link tour
                tour_url = url_for('client.tours_detail', slug=tour.slug, _external=True)
                
                email_subject = f"Tour của bạn đã bị từ chối: {tour.title}"
                
                email_body_html = EMAIL_BODY_HTML.format(author.full_name or author.username, tour.title, reason, tour_url)
                
                # Gửi email
                email_sent = send_email(
                    to_email=author.email,
                    subject=email_subject,
                    body_html=email_body_html
                )
                
                if not email_sent:
                    print(f"Warning: Không thể gửi email từ chối đến {author.email}")
                
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

        items, total = self.tour_model.get_by_author(
            author_id=user_id,
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
        
        user = self.admin_model.get_by_id(session['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'error': 'Không tìm thấy user'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': user.user_id,
                'username': user.username,
                'name': user.full_name or user.username,
                'role': user.role.value,
                'email': user.email,
                'avatar': user.avatar,
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
            Tour.author_id == user_id,
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
                'tour_id': tour.tour_id,
                'title': tour.title,
                'status': tour.status.value,
                'published_at': tour.published_at.isoformat() if tour.published_at else None,
                'updated_at': tour.updated_at.isoformat() if tour.updated_at else None,
                'reviewer_id': tour.reviewer_id if getattr(tour, "reviewer_id", None) else None,
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
            'tour_id': tour.tour_id,
            'title': tour.title,
            'slug': tour.slug,
            'status': tour.status.value if getattr(tour, "status", None) else None,
            'summary': getattr(tour, "summary", None),
            'thumbnail': getattr(tour, "thumbnail", None),
            'visible': getattr(tour, "visible", True),
            'author_id': tour.author_id if getattr(tour, "author_id", None) else None,
            'reviewer_id': tour.reviewer_id if getattr(tour, "reviewer_id", None) else None,
            'view_count': getattr(tour, "view_count", 0),
            'created_at': tour.created_at.isoformat() if getattr(tour, "created_at", None) else None,
            'published_at': tour.published_at.isoformat() if getattr(tour, "published_at", None) else None,
            'category_name': CATEGORY_NAME_DICT.get(getattr(tour, "category_name", None), 'N/A')
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
        
        res = self.admin_model.statistics_editor(user_id)
        data = res['data']

        return jsonify({
            'success': True,
            'data': {
                'total': data['total'],
                'pending': data['pending_count'],
                'published': data['published_count'],
                'rejected': data['rejected_count'],
                'approved': data['approved_count'],
                'draft': data['draft_count'],
                'tour_approved': data['tour_approved'].title if data['tour_approved'] else '',
                'tour_update': data['tour_update'].title if data['tour_update'] else '',
                'tour_newest': data['tour_newest'].title if data['tour_newest'] else ''
            }
        })

    def api_pending_tour(self):
        """API lấy danh sách bài viết chờ duyệt"""
        tour = self.tour_model.get_all(status=TourStatus.PENDING, limit=100)

        return jsonify({
            'success': True,
            'data': [{
                'tour_id': tour.tour_id,
                'title': tour.title,
                'author': tour.author.username if tour.author else 'N/A',
                'date': tour.created_at.strftime('%d/%m/%Y %H:%M') if tour.created_at else '',
                'category_name': CATEGORY_NAME_DICT[tour.category_name] if tour.category_name else 'N/A',
                'status': tour.status.value
            } for tour in tour]
        })
    
    def api_approved_tour(self):
        """API lấy danh sách bài viết đã duyệt"""
        tour = self.tour_model.get_all(status=TourStatus.PUBLISHED, limit=100)
        
        return jsonify({
            'success': True,
            'data': [{
                'tour_id': tour.tour_id,
                'title': tour.title,
                'category_name': CATEGORY_NAME_DICT[tour.category_name] if tour.category_name else 'N/A',
                'author': tour.author.username if tour.author else 'N/A',
                'date': tour.published_at.strftime('%d/%m/%Y %H:%M') if tour.published_at else '',
                'views': tour.view_count
            } for tour in tour]
        })
    
    def api_rejected_tour(self):

        # Lấy tour bị từ chối
        news_tour = self.tour_model.get_all(status=TourStatus.REJECTED, limit=100)
        
        # Lấy thông tin từ chối từ database
        tour_ids = [t.tour_id for t in news_tour]
        
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
            rejection_info = news_rejections.get(tour.tour_id, {})
            data.append({
                'tour_id': tour.tour_id,
                'title': tour.title,
                'author': tour.author.username if tour.author else 'N/A',
                'date': tour.created_at.strftime('%d/%m/%Y %H:%M') if tour.created_at else '',
                'type': 'tour',
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
        
        # Xác định author: nếu là bài từ API thì dùng author field, không thì dùng author.username hoặc author.full_name nếu có
        author_name = tour.author if (hasattr(tour, 'is_api') and tour.is_api and hasattr(tour, 'author') and tour.author) else (tour.author.username if tour.author else 'N/A')
        author_full_name = tour.author if (hasattr(tour, 'is_api') and tour.is_api and hasattr(tour, 'author') and tour.author) else (tour.author.full_name if tour.author and tour.author.full_name else tour.author.username if tour.author else 'N/A')
        
        return jsonify({
            'success': True,
            'data': {
                'tour_id': tour.tour_id,
                'title': tour.title,
                'slug': tour.slug,
                'summary': tour.summary or '',
                'content': tour.content or '',
                'thumbnail': tour.thumbnail or '',
                'author': author_name,
                'author_full_name': author_full_name,
                'reviewer': tour.reviewer.username if tour.reviewer else None,
                'reviewer_full_name': tour.reviewer.full_name if tour.reviewer and tour.reviewer.full_name else (tour.reviewer.username if tour.reviewer else None),
                'is_api': tour.is_api if hasattr(tour, 'is_api') else False,
                'status': tour.status.value,
                'created_at': tour.created_at.strftime('%d/%m/%Y %H:%M') if tour.created_at else '',
                'published_at': tour.published_at.strftime('%d/%m/%Y %H:%M') if tour.published_at else '',
                'updated_at': tour.updated_at.strftime('%d/%m/%Y %H:%M') if tour.updated_at else '',
                'view_count': tour.view_count,
                'is_featured': tour.is_featured if hasattr(tour, 'is_featured') else False,
                'is_hot': tour.is_hot if hasattr(tour, 'is_hot') else False,
                'is_deleted': tour.is_deleted if hasattr(tour, 'is_deleted') else False,
                'category_name': tour.category_name,
                'location_id': tour.location_id,
                'price_per_adult': tour.price_per_adult,
                'price_per_child': tour.price_per_child,
            }
        })

    def api_create_tour(self):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
            
        data = request.json if request.is_json else request.form
        
        # Validation cơ bản
        if not data.get('title'):
            return jsonify({'success': False, 'error': 'Thiếu tiêu đề'}), 400

        if not data.get('content'):
            return jsonify({'success': False, 'error': 'Thiếu nội dung'}), 400

        data_dict = dict(data)
        data_dict['user_id'] = user_id
        
        try:
            status = TourStatus(data.get('status', TourStatus.DRAFT.value))
        except ValueError:
            status = TourStatus.DRAFT
            
        data_dict['status'] = status
        data_dict['slug'] = generate_slug(data.get('title'), status.value) + str(random())[:8]
        data_dict['price_per_adult'] = float(data.get('price_per_adult', '0.0'))
        data_dict['price_per_child'] = float(data.get('price_per_child', '0.0'))

        result = self.admin_model.create_tour(data_dict)
        tour_obj = self.tour_model.get_by_id(result['tour_id'])
        data = self._tour_to_dict(tour_obj) if tour_obj else None
        return jsonify({'success': result.get('success'), 'message': result.get('message'), 'data': data})

    def api_edit_tour(self, tour_id: int):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
            
        user = self.admin_model.get_by_id(user_id)
        if not user or user.role not in [UserRole.ADMIN, UserRole.STAFF]:
            return jsonify({'success': False, 'error': 'Không có quyền thực hiện hành động này'}), 403

        tour = self.tour_model.get_by_id(tour_id, include_deleted=True)
        if not tour:
            return jsonify({'success': False, 'error': 'Không tìm thấy bài viết'}), 404

        # Kiểm tra quyền tác giả đối với staff
        if user.role == UserRole.STAFF and tour.author_id != user_id:
            return jsonify({'success': False, 'error': 'Bạn không có quyền chỉnh sửa bài viết này'}), 403

        # Kiểm tra trạng thái bài viết theo quyền
        if user.role == UserRole.STAFF:
            if tour.status not in [TourStatus.DRAFT, TourStatus.REJECTED]:
                return jsonify({'success': False, 'error': 'Bài viết đang trong trạng thái chờ duyệt hoặc đã xuất bản, bạn không thể chỉnh sửa'}), 403
        elif user.role == UserRole.ADMIN:
            if tour.status not in [TourStatus.PENDING, TourStatus.APPROVED, TourStatus.PUBLISHED]:
                return jsonify({'success': False, 'error': 'Bài viết đang do nhân viên soạn thảo hoặc chỉnh sửa, admin không thể chỉnh sửa'}), 403

        data = dict(request.json if request.is_json else request.form)

        for field in ['is_hot', 'is_featured']:
            if field in data and isinstance(data[field], str):
                data[field] = data[field].lower() in ('true', '1', 'yes', 'on')

        result = self.admin_model.edit_tour(tour_id, data)
        tour_obj = self.tour_model.get_by_id(tour_id, include_deleted=True)
        data = self._tour_to_dict(tour_obj) if tour_obj else None
        return jsonify({'success': result.get('success'), 'message': result.get('message'), 'data': data})

    def api_delete_tour(self, tour_id: int):
        
        result = self.admin_model.delete_tour(tour_id)
        tour_obj = self.tour_model.get_by_id(tour_id, include_deleted=True)
        data = self._tour_to_dict(tour_obj) if tour_obj else None
        return jsonify({'success': result.get('success'), 'message': result.get('message'), 'data': data})

    def api_approve_atour(self, tour_id: int):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401

        data = self.admin_model.approve_tour(tour_id, user_id)
        tour_obj = self.tour_model.get_by_id(tour_id, include_deleted=True)
        data['data'] = self._tour_to_dict(tour_obj) if tour_obj else None
        return jsonify({'success': data.get('success'), 'message': data.get('message'), 'data': data.get('data')})

    def api_reject_atour(self, tour_id: int):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
            
        data = request.form or request.json
        reason = data.get('reason', '')
        data = self.admin_model.reject_tour(tour_id, user_id, reason)
        tour_obj = self.tour_model.get_by_id(tour_id, include_deleted=True)
        data['data'] = self._tour_to_dict(tour_obj) if tour_obj else None
        return jsonify({'success': data.get('success'), 'message': data.get('message'), 'data': data.get('data')})

    def api_get_category(self):
        categories = CATEGORY_NAME
        return jsonify({'success': True, 'data': categories})

    def api_get_user(self, user_id: int):
        user = self.admin_model.get_by_id(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'Người dùng không tồn tại'}), 404
        return jsonify({
            'success': True,
            'data': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role.value,
                'phone_number': user.phone_number,
                'is_active': user.is_active,
                'created_at': user.created_at.strftime('%d/%m/%Y %H:%M') if user.created_at else '',
            }
        })

    def api_toggle_user_status(self, user_id: int):
        success, message = self.admin_model.user_toggle_status(user_id)
        return jsonify({'success': success, 'message': message})

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
        data = request.json if request.is_json else request.form
        type_data = data.get('type_data')

        # Nếu chưa có tour_id, lưu vào thư mục temp
        upload_folder = os.path.join('src', 'static', 'uploads', type_data, 'vn', 'temp')
        
        os.makedirs(upload_folder, exist_ok=True)
        
        # Tạo tên file an toàn
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(upload_folder, filename)
        
        # Lưu file
        file.save(filepath)
        
        # Tạo URL trả về (relative to static folder)
        image_url = f"static/uploads/{type_data}/vn/{'temp'}/{filename}"
        
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


    def profile_user(self):
        """
        Trang thông tin cá nhân của user
        Route: GET POST /profile
        """
        if 'user_id' not in session:
            return jsonify({'status': False, 'message': 'Chưa đăng nhập'}), 401
        
        user = self.admin_model.get_by_id(session['user_id'])
        if not user:
            return jsonify({'status': False, 'message': 'Không tìm thấy thông tin người dùng'}), 404

        if request.method == 'POST':
            data = request.json if request.is_json else request.form
            action = data.get('action')
            if action == 'update_avatar':
                if 'avatar' not in request.files:
                    return jsonify({'status': False, 'message': 'Không có file được chọn'}), 400
                
                file = request.files['avatar']
                if file.filename == '':
                    return jsonify({'status': False, 'message': 'Không có file được chọn'}), 400
                
                if file and self._allowed_file(file.filename):
                    filename = secure_filename(f"avatar_{user.user_id}_{file.filename}")
                    # Tạo đường dẫn upload folder
                    upload_folder = os.path.join('src', 'static', 'uploads', 'avatars')
                    os.makedirs(upload_folder, exist_ok=True)
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    
                    # Xóa avatar cũ nếu có
                    if user.avatar:
                        old_path = user.avatar.lstrip('/')
                        old_path = os.path.join('src', old_path) if not old_path.startswith('src') else old_path
                        if os.path.exists(old_path):
                            try:
                                os.remove(old_path)
                            except:
                                pass
                    
                    # Lưu đường dẫn avatar (relative to static folder)
                    avatar_url = f"static/uploads/avatars/{filename}"
                    user.avatar = avatar_url
                    self.db_session.commit()
                    
                    # Cập nhật session
                    session['avatar'] = avatar_url
                    
                    return jsonify({'status': True, 'message': 'Cập nhật avatar thành công', 'avatar_url': f'/{avatar_url}'})
                else:
                    return jsonify({'status': False, 'message': 'File không hợp lệ. Chỉ chấp nhận: png, jpg, jpeg, gif, webp'}), 400
            
            elif action == 'update_info':
                data = request.json if request.is_json else request.form
                full_name = data.get('full_name', '').strip()
                email = data.get('email', '').strip()
                phone_number = data.get('phone_number', '').strip()
                gender = data.get('gender', '').strip()
                date_of_birth = data.get('date_of_birth', '').strip()
                address = data.get('address', '').strip()
                
                if email and email != user.email:
                    existing_user = self.admin_model.get_by_email(email)
                    if existing_user and existing_user.user_id != user.user_id:
                        return jsonify({'status': False, 'message': 'Email này đã được sử dụng'}), 400

                self.admin_model.update(user.user_id, {
                    'full_name': full_name,
                    'email': email,
                    'phone_number': phone_number,
                    'gender': gender,
                    'date_of_birth': date_of_birth,
                    'address': address
                })
                
                user = self.admin_model.get_by_id(session['user_id'])
                session['full_name'] = user.full_name or user.username
                
                return jsonify({
                    'status': True, 
                    'message': 'Cập nhật thông tin thành công', 
                    'user': {
                        'full_name': user.full_name, 
                        'email': user.email, 
                        'phone_number': user.phone_number, 
                        'gender': user.gender, 
                        'date_of_birth': user.date_of_birth, 
                        'address': user.address
                    }
                })
            
            elif action == 'change_password':
                data = request.json if request.is_json else request.form
                current_password = data.get('current_password')
                new_password = data.get('new_password')
                confirm_password = data.get('confirm_password')
                
                if not verify_password(user.password_hash, current_password):
                    return jsonify({'status': False, 'message': 'Mật khẩu hiện tại không đúng'})
                
                if new_password != confirm_password:
                    return jsonify({'status': False, 'message': 'Mật khẩu mới và xác nhận không khớp'})
                
                if len(new_password) < 6:
                    return jsonify({'status': False, 'message': 'Mật khẩu phải có ít nhất 6 ký tự'})
                
                user.password_hash = hash_password(new_password)
                self.db_session.commit()
                
                return jsonify({'status': True, 'message': 'Đổi mật khẩu thành công'})
            
        return jsonify({'status': False, 'message': 'Hành động không hợp lệ'})

    #### profile admin or editor ####
    def profile(self):
        """
        Trang thông tin cá nhân của user
        Route: GET POST /profile
        """
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để xem thông tin cá nhân', 'error')
            return redirect(url_for('admin.login'))
        
        user = self.admin_model.get_by_id(session['user_id'])
        print(user.avatar)
        if not user:
            flash('Không tìm thấy thông tin người dùng', 'error')
            session.clear()
            return redirect(url_for('admin.login'))

        if request.method == 'POST':
            data = request.json if request.is_json else request.form
            action = data.get('action')
            if action == 'update_avatar':
                if 'avatar' not in request.files:
                    return jsonify({'success': False, 'message': 'Không có file được chọn'}), 400
                
                file = request.files['avatar']
                if file.filename == '':
                    return jsonify({'success': False, 'message': 'Không có file được chọn'}), 400
                
                if file and self._allowed_file(file.filename):
                    filename = secure_filename(f"avatar_{user.user_id}_{file.filename}")
                    # Tạo đường dẫn upload folder
                    upload_folder = os.path.join('src', 'static', 'uploads', 'avatars')
                    os.makedirs(upload_folder, exist_ok=True)
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    
                    # Xóa avatar cũ nếu có
                    if user.avatar:
                        old_path = user.avatar.lstrip('/')
                        old_path = os.path.join('src', old_path) if not old_path.startswith('src') else old_path
                        if os.path.exists(old_path):
                            try:
                                os.remove(old_path)
                            except:
                                pass
                    
                    # Lưu đường dẫn avatar (relative to static folder)
                    avatar_url = f"static/uploads/avatars/{filename}"
                    # user.avatar = avatar_url
                    # self.db_session.commit()
                    self.admin_model.update(user.user_id, {'avatar': avatar_url})
                    
                    # Cập nhật session
                    session['avatar'] = avatar_url
                    
                    return jsonify({'success': True, 'message': 'Cập nhật avatar thành công', 'avatar_url': f'/{avatar_url}'})
                else:
                    return jsonify({'success': False, 'message': 'File không hợp lệ. Chỉ chấp nhận: png, jpg, jpeg, gif, webp'}), 400
            
            elif action == 'update_info':
                data = request.json if request.is_json else request.form
                full_name = data.get('full_name', '').strip()
                email = data.get('email', '').strip()
                phone = data.get('phone', '').strip()
                
                if email and email != user.email:
                    existing_user = self.admin_model.get_by_email(email)
                    if existing_user and existing_user.user_id != user.user_id:
                        flash('Email này đã được sử dụng', 'error')
                        return redirect(url_for('admin.profile'))
                
                self.admin_model.update(user.user_id, {
                    'full_name': full_name if full_name else None,
                    'email': email,
                    'phone_number': phone if phone else None
                })
                
                session['full_name'] = user.full_name or user.username
                
                flash('Cập nhật thông tin thành công', 'success')
                return redirect(url_for('admin.profile'))
            
            elif action == 'change_password':
                data = request.json if request.is_json else request.form
                current_password = data.get('current_password')
                new_password = data.get('new_password')
                confirm_password = data.get('confirm_password')
                
                if not verify_password(user.password_hash, current_password):
                    flash('Mật khẩu hiện tại không đúng', 'error')
                    return redirect(url_for('admin.profile'))
                
                if new_password != confirm_password:
                    flash('Mật khẩu mới và xác nhận không khớp', 'error')
                    return redirect(url_for('admin.profile'))
                
                if len(new_password) < 6:
                    flash('Mật khẩu phải có ít nhất 6 ký tự', 'error')
                    return redirect(url_for('admin.profile'))
                
                user.password_hash = hash_password(new_password)
                self.db_session.commit()
                
                flash('Đổi mật khẩu thành công', 'success')
                return redirect(url_for('admin.profile'))
            
            flash('Hành động không hợp lệ', 'error')
            return redirect(url_for('admin.profile'))

        return render_template('admin/profile.html', 
                             user=user
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
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'phone_number': user.phone_number,
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
        
        current_user = self.admin_model.get_by_id(session['user_id'])
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
            
            if self.admin_model.get_by_username(username):
                return jsonify({'success': False, 'error': 'Tên đăng nhập đã tồn tại'}), 400
            
            if not validate_email(email):
                return jsonify({'success': False, 'error': 'Email không đúng định dạng'}), 400
            
            if self.admin_model.get_by_email(email):
                return jsonify({'success': False, 'error': 'Email đã được sử dụng'}), 400
            
            password_valid, password_error = validate_password(password)
            if not password_valid:
                return jsonify({'success': False, 'error': password_error}), 400
            
            # Convert role string to enum
            role_map = {'admin': UserRole.ADMIN, 'staff': UserRole.STAFF, 'user': UserRole.CUSTOMER}
            role = role_map.get(role_str.lower(), UserRole.CUSTOMER)
            
            # Create user
            user = self.admin_model.create(
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
                'data': {
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role.value
                }
            })
        except Exception as e:
            self.db_session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def api_update_user(self, user_id):
        """API cập nhật user hoặc lấy thông tin user"""

        current_user_id = session['user_id']
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Bạn không có quyền truy cập'}), 401

        try:
            user = self.admin_model.get_by_id(user_id)
            if not user:
                return jsonify({'success': False, 'error': 'Không tìm thấy người dùng'}), 404
            
            # GET request - return user info
            if request.method == 'GET':
                return jsonify({
                    'success': True,
                    'data': {
                        'user_id': user.user_id,
                        'username': user.username,
                        'email': user.email,
                        'full_name': user.full_name,
                        'phone_number': user.phone_number,
                        'role': user.role.value if user.role else 'user',
                        'is_active': user.is_active
                    }
                })
            
            # POST request - update user
            data = request.json if request.is_json else request.form
            full_name = data.get('full_name', '').strip()
            # email = data.get('email', '').strip().lower()
            phone = data.get('phone', '').strip()
            role_str = data.get('role', '')

            success = self.admin_model.update(user_id, {
                'full_name': full_name,
                # 'email': email,
                'phone_number': phone,
                'role': role_str,
                'updated_at': datetime.utcnow()
            })
            
            return jsonify({
                'success': success,
                'message': 'Cập nhật thông tin thành công' if success else 'Cập nhật thông tin thất bại'
            })
        except Exception as e:
            self.db_session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    def api_create_location(self):
        """API tạo danh sách địa điểm"""
        try:
            if 'user_id' not in session:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            current_user = self.admin_model.get_by_id(session['user_id'])
            if not current_user or current_user.role != UserRole.ADMIN:
                return jsonify({'success': False, 'error': 'Permission denied'}), 403
            
            data = request.json if request.is_json else request.form
            name = data.get('name', '').strip()
            search_key = data.get('search_key', '').strip()
            city = data.get('city', '').strip()
            country = data.get('country', '').strip()
            description = data.get('description', '').strip()
            image_url = data.get('image_url', '').strip()
            slug = data.get('slug', '')
            
            success = self.location_model.create_location_bulk(
                [{   
                'name':name,
                'search_key':search_key,
                'city':city,
                'country':country,
                'description':description,
                'image_url':image_url,
                'slug':slug
                }]
            )

            return jsonify({
                'success': success,
                'message': "Tạo danh sách địa điểm thành công" if success else "Tạo danh sách địa điểm thất bại",
            })
        except Exception as e:
            self.db_session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    def api_update_location(self, location_id):
        """API cập nhật danh sách địa điểm"""
        try:
            if 'user_id' not in session:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            current_user = self.admin_model.get_by_id(session['user_id'])
            if not current_user or current_user.role != UserRole.ADMIN:
                return jsonify({'success': False, 'error': 'Permission denied'}), 403
            
            data = request.json if request.is_json else request.form
            name = data.get('name', '').strip()
            search_key = data.get('search_key', '').strip()
            city = data.get('city', '').strip()
            country = data.get('country', '').strip()
            description = data.get('description', '').strip()
            image_url = data.get('image_url', '').strip()
            # location_id = data.get('location_id', '')
            location = self.location_model.get_by_id(location_id)
            if not location:
                return jsonify({'success': False, 'error': 'Không tìm thấy địa điểm'}), 404
            success = self.location_model.update_location(
                {
                    'location_id':location_id,
                    'name':name,
                    'search_key':search_key,
                    'city':city,
                    'country':country,
                    'description':description,
                    'image_url':image_url
                }
            )
            
            return jsonify({
                'success': success,
                'message': "Cập nhật danh sách địa điểm thành công" if success else "Cập nhật danh sách địa điểm thất bại",
            })
        except Exception as e:
            self.db_session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    def api_delete_location(self, location_id):
        try:
            if 'user_id' not in session:
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            current_user = self.admin_model.get_by_id(session['user_id'])
            if not current_user or current_user.role != UserRole.ADMIN:
                return jsonify({'success': False, 'error': 'Permission denied'}), 403
            
            data = request.json if request.is_json else request.form
            # location_id = data.get('location_id')
            location = self.location_model.get_by_id(location_id)
            if not location:
                return jsonify({'success': False, 'error': 'Không tìm thấy địa điểm'}), 404
            success = self.location_model.delete_location(location_id)
            
            return jsonify({
                'success': success,
                'message': "Xóa danh sách địa điểm thành công" if success else "Xóa danh sách địa điểm thất bại",
            })
        except Exception as e:
            self.db_session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    def api_location(self):
        """API lấy danh sách địa điểm"""
        try:
            query = self.db_session.query(Location)
            locations = query.all()
            locations_data = []
            for location in locations:
                locations_data.append({
                    'location_id': location.location_id,
                    'name': location.name,
                    'search_key': location.search_key,
                    'city': location.city,
                    'country': location.country,
                    'description': location.description,
                    'image_url': location.image_url
                })

            print(locations_data)

            return jsonify({
                'success': True,
                'locations': locations_data
            })
        except Exception as e:
            self.db_session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    def api_get_location(self, location_id):
        try:
            location = self.location_model.get_by_id(location_id)
            if not location:
                return jsonify({'success': False, 'error': 'Không tìm thấy địa điểm'}), 404
            return jsonify({
                'success': True,
                'location': {
                    'location_id': location.location_id,
                    'name': location.name,
                    'search_key': location.search_key,
                    'city': location.city,
                    'country': location.country,
                    'description': location.description,
                    'image_url': location.image_url,
                    'slug': location.slug
                }
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
        data = request.json if request.is_json else request.form
        success = self.setting_model.update_settings(data)
        
        if success:
            return jsonify({'success': True, 'message': 'Cập nhật cài đặt thành công'})
        return jsonify({'success': False, 'error': 'Có lỗi khi cập nhật'}), 500
    
    def api_test_email(self):
        """API test gửi email"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        current_user = self.admin_model.get_by_id(session['user_id'])
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
            
            # Tạm thời cập nhật email_utils với settings từ database
            # (Trong thực tế, nên refactor email_utils để đọc từ database)
            success = send_email(test_email, EMAIL_SUBJECT_TEST, EMAIL_BODY_HTML_TEST, EMAIL_BODY_TEXT_TEST)
            
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

    def api_bookings_list(self):
        """API lấy danh sách bookings cho admin"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
        
        # Verify role admin
        if session.get('role') != UserRole.ADMIN.value:
            return jsonify({'success': False, 'error': 'Không có quyền truy cập'}), 403
            
        try:
            status_str = request.args.get('status', 'all')
            search = request.args.get('search', '').strip()
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:
                per_page = 10
                
            offset = (page - 1) * per_page
            
            # Khởi tạo query kết nối với bảng User
            query = self.db_session.query(Bookings).join(User, Bookings.user_id == User.user_id)
            
            # Tìm kiếm (tên khách hàng, email, sđt, hoặc tiêu đề tour)
            if search:
                # Join với Tour để search tiêu đề tour nếu booking_type là TOUR
                query = query.outerjoin(Tour, (Bookings.reference_id == Tour.tour_id) & (Bookings.booking_type == BookingType.TOUR))
                query = query.filter(
                    or_(
                        User.full_name.ilike(f"%{search}%"),
                        User.email.ilike(f"%{search}%"),
                        User.username.ilike(f"%{search}%"),
                        User.phone_number.ilike(f"%{search}%"),
                        Tour.title.ilike(f"%{search}%")
                    )
                )
                
            # Lọc theo trạng thái
            if status_str and status_str != 'all':
                try:
                    status_enum = BookingStatus(status_str)
                    query = query.filter(Bookings.booking_status == status_enum)
                except ValueError:
                    pass
                    
            # Sắp xếp mới nhất
            query = query.order_by(Bookings.created_at.desc())
            
            # Count và lấy dữ liệu
            total = query.count()
            bookings_list = query.limit(per_page).offset(offset).all()
            
            data = []
            for b in bookings_list:
                tour_title = None
                tour_image = None
                tour_slug = None
                if b.booking_type == BookingType.TOUR:
                    tour = self.db_session.query(Tour).get(b.reference_id)
                    if tour:
                        tour_title = tour.title
                        tour_image = tour.thumbnail
                        tour_slug = tour.slug
                        
                data.append({
                    'id': b.booking_id,
                    'user_id': b.user_id,
                    'userName': b.user.full_name or b.user.username,
                    'userEmail': b.user.email,
                    'userPhone': b.user.phone_number or '',
                    'booking_type': b.booking_type.value if b.booking_type else None,
                    'reference_id': b.reference_id,
                    'tourId': b.reference_id if b.booking_type == BookingType.TOUR else None,
                    'tourTitle': tour_title or 'N/A',
                    'tourImage': tour_image,
                    'tourSlug': tour_slug,
                    'departureDate': b.check_in_date.strftime('%Y-%m-%d') if b.check_in_date else None,
                    'check_in_date': b.check_in_date.strftime('%Y-%m-%d') if b.check_in_date else None,
                    'check_out_date': b.check_out_date.strftime('%Y-%m-%d') if b.check_out_date else None,
                    'totalPrice': float(b.total_price) if b.total_price else 0.0,
                    'status': b.booking_status.value if b.booking_status else None,
                    'booking_status': b.booking_status.value if b.booking_status else None,
                    'createdAt': b.created_at.strftime('%Y-%m-%d %H:%M:%S') if b.created_at else None,
                })
                
            total_pages = (total + per_page - 1) // per_page if total > 0 else 1
            
            return jsonify({
                'success': True,
                'data': data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': total_pages
                }
            })
        except Exception as e:
            print(f"Error in api_bookings_list: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    def api_update_booking_status(self, booking_id):
        """API cập nhật trạng thái booking cho admin"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
            
        if session.get('role') != UserRole.ADMIN.value:
            return jsonify({'success': False, 'error': 'Không có quyền truy cập'}), 403
            
        try:
            data = request.json if request.is_json else request.form
            status_str = data.get('status')
            if not status_str:
                return jsonify({'success': False, 'error': 'Thiếu trạng thái mới'}), 400
                
            try:
                new_status = BookingStatus(status_str)
            except ValueError:
                return jsonify({'success': False, 'error': 'Trạng thái không hợp lệ'}), 400
                
            booking = self.db_session.query(Bookings).filter(Bookings.booking_id == booking_id).first()
            if not booking:
                return jsonify({'success': False, 'error': 'Không tìm thấy booking'}), 404
                
            booking.booking_status = new_status
            self.db_session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Cập nhật trạng thái booking #{booking_id} thành {status_str} thành công'
            })
        except Exception as e:
            self.db_session.rollback()
            print(f"Error in api_update_booking_status: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    def api_bookings_statistics(self):
        """API lấy thống kê đặt tour cho dashboard admin"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
            
        if session.get('role') != UserRole.ADMIN.value:
            return jsonify({'success': False, 'error': 'Không có quyền truy cập'}), 403
            
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            # Gọi booking_model lấy thống kê qua Command Pattern
            cmd_result = self.booking_model.get_bookings_statistics(start_date)
            
            # Chuẩn bị dữ liệu trả về theo format của frontend
            stats = {
                'total_bookings': cmd_result['total_bookings'],
                'total_revenue': cmd_result['total_revenue'],
                'pending_count': cmd_result['pending_count'],
                'confirmed_count': cmd_result['confirmed_count'],
                'completed_count': cmd_result['completed_count'],
                'cancelled_count': cmd_result['cancelled_count'],
            }
            
            # Xử lý dữ liệu biểu đồ xu hướng 7 ngày
            daily_dict = cmd_result['daily_dict']
            labels = []
            booking_counts_data = []
            revenue_data = []
            
            for i in range(7):
                date = (start_date + timedelta(days=i)).date()
                date_str = str(date)
                labels.append(date.strftime('%d/%m'))
                day_data = daily_dict.get(date_str, {'count': 0, 'revenue': 0.0})
                booking_counts_data.append(day_data['count'])
                revenue_data.append(day_data['revenue'])
                
            stats['chart_data'] = {
                'labels': labels,
                'bookings': booking_counts_data,
                'revenue': revenue_data
            }
            
            # Xử lý 5 Bookings gần nhất
            stats['recent_bookings'] = []
            for b in cmd_result['recent_bookings']:
                tour_title = None
                if b.booking_type == BookingType.TOUR:
                    tour = self.db_session.query(Tour).get(b.reference_id)
                    if tour:
                        tour_title = tour.title
                        
                stats['recent_bookings'].append({
                    'id': b.booking_id,
                    'userName': b.user.full_name or b.user.username,
                    'tourTitle': tour_title or 'N/A',
                    'totalPrice': float(b.total_price) if b.total_price else 0.0,
                    'status': b.booking_status.value if b.booking_status else None,
                    'createdAt': b.created_at.strftime('%Y-%m-%d %H:%M:%S') if b.created_at else None,
                })
                
            return jsonify({
                'success': True,
                'data': stats
            })
        except Exception as e:
            print(f"Error in api_bookings_statistics: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    def api_tours_tree(self):
        """API lấy cây thư mục cấu trúc các Tour theo Composite Pattern cho Admin hoặc Staff"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
            
        role = session.get('role')
        if role not in [UserRole.ADMIN.value, UserRole.STAFF.value]:
            return jsonify({'success': False, 'error': 'Không có quyền truy cập'}), 403
            
        user_id = session.get('user_id')
        author_id = user_id if role == UserRole.STAFF.value else None
            
        try:
            tree_dict = self.tour_model.get_tours_tree(author_id)
            return jsonify({
                'success': True,
                'tree': tree_dict
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
