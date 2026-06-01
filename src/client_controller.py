
from flask import render_template, request, jsonify, abort, redirect, url_for, flash, session
import pytz
from datetime import datetime, timedelta
from utils import validate_email, validate_password, validate_phone, hash_password
from database import (
    get_session,
    TourStatus,
    UserRole,
    Viewedtour,
    Savedtour, 
    PasswordResetToken,
)

from models import (
    tourModel,
    UserModel,
)


class Controller():

    """Mangaer controller - manage related user, tour, ..."""
    
    # db_session = get_session()
    # tour_model = tourModel(db_session)
    # user_model = UserModel(db_session)

    def __init__(self):
        """initialize controller"""
        self.db_session = get_session()
        self.tour_model = tourModel(self.db_session)
        self.user_model = UserModel(self.db_session)

    def list_tour(self, limit=None, offset=None):
        """
        List latest tour
        Route: GET /
        """
        db_session = self.db_session
        try:
            latest_tour = self.tour_model.get_published(limit=limit, offset=offset)

            return latest_tour
        finally:
            db_session.close()

    def handle_login(self, site):

        username = request.form.get('username')
        password = request.form.get('password')

        if self.user_model.is_locked_user(username):
            if site == 'en':
                flash('Account has been locked. Please contact administrator', 'error')
                return redirect(url_for('client.en_user_login'))
            else:
                flash('Tài khoản đã bị khóa. Vui lòng liên hệ quản trị viên', 'error')
                return redirect(url_for('client.user_login'))
        
        user = self.user_model.authenticate(username, password)
        
        if user and user.is_active and user.role == UserRole.CUSTOMER:
            session['user_id'] = user.id
            session['username'] = user.username
            session['full_name'] = user.full_name or user.username
            session['role'] = user.role.value
            
            
            if site == 'en':
                flash('Login successful', 'success')
                return redirect(url_for('client.en_index'))
            else:
                flash('Đăng nhập thành công', 'success')
                return redirect(url_for('client.home'))
        else:
            if site == 'en':
                print('Username or password is incorrect')
                flash('Username or password is incorrect', 'error')
                return redirect(url_for('client.en_user_login'))
            else:
                print('Tên đăng nhập hoặc mật khẩu không đúng')
                flash('Tên đăng nhập hoặc mật khẩu không đúng', 'error')
                return redirect(url_for('client.user_login'))


    def checkLogin(self):
        """
        Check login for user
        """
        
        site = session.get('site')
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') == 'on' else False

        # check status locked of account before authentication
        if self.user_model.is_locked_user(username):
            if site == 'en':
                flash('Account has been locked. Please contact administrator', 'error')
                return redirect(url_for('client.en_user_login'))
            else:
                flash('Tài khoản đã bị khóa. Vui lòng liên hệ quản trị viên', 'error')
                return redirect(url_for('client.user_login'))
        
        user = self.user_model.authenticate(username, password)
        
        if user and user.is_active and user.role == UserRole.CUSTOMER:
            session['user_id'] = user.id
            session['username'] = user.username
            session['full_name'] = user.full_name or user.username
            session['role'] = user.role.value

            if remember:
                session.permanent = True
            else:
                session.permanent = False

            flash('Đăng nhập thành công', 'success')
            return redirect(url_for('client.home'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng', 'error')
            return redirect(url_for('client.user_login'))

    def register(self):
        """
        Page register user
        Route: POST /register
        """
        
        # Validation
        errors = []
        
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Validate username
        if not username:
            errors.append('Tên đăng nhập không được để trống')
        elif len(username) < 3:
            errors.append('Tên đăng nhập phải có ít nhất 3 ký tự')
        elif self.user_model.get_by_username(username):
            errors.append('Tên đăng nhập đã tồn tại')
        
        # Validate email
        if not validate_email(email):
            errors.append('Email không đúng định dạng')
        elif self.user_model.get_by_email(email):
            errors.append('Email đã được sử dụng')
        
        # Validate phone
        phone_valid, phone_error = validate_phone(phone)
        if not phone_valid:
            errors.append(phone_error)
        
        # Validate password
        password_valid, password_error = validate_password(password)
        if not password_valid:
            errors.append(password_error)
        elif password != confirm_password:
            errors.append('Mật khẩu xác nhận không khớp')
        
        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            try:
                # Clean phone number
                phone_clean = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                
                user = self.user_model.create(
                    username=username,
                    email=email,
                    password=hash_password(password),
                    full_name=full_name if full_name else None,
                    phone=phone_clean,
                    role=UserRole.CUSTOMER
                )
                
                if user:
                    return jsonify({"message": "User created", "user_id": user.user_id}), 201
            except Exception as e:
                return jsonify({"error": "Failed to create user", "message": str(e)}), 400

    def forgot_password(self):
        """
        Page forgot password - Request reset
        Route: POST /forgot-password
        """
        email = request.form.get('email', '').strip().lower()
        site = session.get('site')

        from utils import validate_email
        from email_utils import generate_token, send_password_reset_email
        
        # Validation
        if not email:
            flash('Email không được để trống' if site == 'vn' else 'Email is required', 'error')
        elif not validate_email(email):
            flash('Email không đúng định dạng' if site == 'vn' else 'Invalid email format', 'error')
        else:
            # Tìm user
            user = self.user_model.get_by_email(email)
            
            if user:
                # Tạo token reset
                reset_token = generate_token()
                expires_at = datetime.utcnow() + timedelta(hours=1)  # Token hết hạn sau 1 giờ
                
                # Vô hiệu hóa các token cũ của user này
                old_tokens = self.db_session.query(PasswordResetToken).filter(
                    PasswordResetToken.user_id == user.id,
                    PasswordResetToken.used == False
                ).all()
                for old_token in old_tokens:
                    old_token.used = True
                
                # Tạo token mới
                reset_token_obj = PasswordResetToken(
                    user_id=user.id,
                    token=reset_token,
                    expires_at=expires_at
                )
                self.db_session.add(reset_token_obj)
                self.db_session.commit()
                
                # Gửi email reset
                send_password_reset_email(user.email, reset_token, site)
            
            # Luôn hiển thị thông báo thành công (bảo mật)
            success_msg = 'Nếu email tồn tại trong hệ thống, chúng tôi đã gửi link đặt lại mật khẩu đến email của bạn.' if site == 'vn' else 'If the email exists in our system, we have sent a password reset link to your email.'
            flash(success_msg, 'success')
            return redirect(url_for('client.user_login', site=site))

    def tours_detail(self, tours_slug: str):
        """
        Page tour detail
        Route: GET /tour/<tours_slug>
        """
        db_session = self.db_session
        try:

            print(f"Slug received: {tours_slug}")
            
            tour_model = self.tour_model(db_session)
            
            tour = tour_model.get_by_slug(tours_slug)
            print(f"Tour found: {tour}")
            
            if not tour:
                print(f"Tour not found for slug: {tours_slug}")
                abort(404)
            
            print(f"Tour status: {tour.status}")
            if tour.status != TourStatus.PUBLISHED:
                print(f"Tour not published, status: {tour.status}")
                abort(404)

            is_saved = False
            user_id = None

            if 'user_id' in session:
                user_id = session['user_id']

                existing_viewed = db_session.query(Viewedtour).filter(
                    Viewedtour.user_id == user_id,
                    Viewedtour.tour_id == tour.id,
                    Viewedtour.site == 'vn'
                ).first()
                
                if not existing_viewed:
                    viewed_tour = Viewedtour(
                        user_id=user_id,
                        tour_id=tour.id,
                        site='vn'
                    )
                    db_session.add(viewed_tour)
                    db_session.commit()
                else:

                    existing_viewed.viewed_at = datetime.utcnow()
                    db_session.commit()

                saved_tour = db_session.query(Savedtour).filter(
                    Savedtour.user_id == user_id,
                    Savedtour.tour_id == tour.id,
                    Savedtour.site == 'vn'
                ).first()
                is_saved = saved_tour is not None

            time_format = '%d-%m-%Y %H:%M'
            time_zone = 'Asia/Ho_Chi_Minh'
            
            format_time = lambda x: x.astimezone(pytz.timezone(time_zone)).strftime(time_format)

            return render_template('client/tours_detail.html',
                                 tour=tour,
                                 is_saved=is_saved,
                                 user_id=user_id,
                                 format_time=format_time)
        except Exception as e:
            db_session.rollback()
            
            import traceback
            print(f"Error in tours_detail: {str(e)}")
            traceback.print_exc()
            
            abort(404)
        finally:
            db_session.close()
    
    def search_tours(self, keyword, page):
        """
        Search tour by keyword
        Route: GET /search?q=<keyword>
        """
        db_session = self.db_session
        try:

            tours_model = self.tours_model(db_session)

            if not keyword:
                return []
            
            per_page = 25
            offset = (page - 1) * per_page
            
            tours_list = tours_model.search(keyword, limit=per_page + offset)
            tours_list = tours_list[offset:offset + per_page]
            
            return tours_list
        finally:
            db_session.close()