
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
import database as db
import model


class Controller():

    """Quản lý các route của client"""
    
    def __init__(self):
        """Khởi tạo controller"""
        self.db_session = db.get_session()
        self.news_model = model.NewsModel(self.db_session)
        self.category_model = model.CategoryModel(self.db_session)
        self.user_model = model.UserModel(self.db_session)
        
        self.int_news_model = model.InternationalNewsModel(self.db_session)
        self.int_category_model = model.InternationalCategoryModel(self.db_session)

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
        
        if user and user.is_active and user.role == db.UserRole.USER:
            session['user_id'] = user.id
            session['username'] = user.username
            session['full_name'] = user.full_name or user.username
            session['role'] = user.role.value
            
            # Nếu chọn "Ghi nhớ đăng nhập", set session permanent
            if remember:
                session.permanent = True
            else:
                session.permanent = False

            flash('Đăng nhập thành công', 'success')
            return redirect(url_for('client.index'))
        else:
            print('Tên đăng nhập hoặc mật khẩu không đúng')
            flash('Tên đăng nhập hoặc mật khẩu không đúng', 'error')
            return redirect(url_for('client.user_login'))


    def register(self):
        """
        Trang đăng ký cho user
        Route: POST /register
        """

        from utils import validate_email, validate_password, validate_phone
        
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
                    password=password,
                    full_name=full_name if full_name else None,
                    phone=phone_clean,
                    role=db.UserRole.USER
                )
                
                flash('Đăng ký thành công! Vui lòng đăng nhập', 'success')
                return redirect(url_for('client.user_login'))
            except Exception as e:
                flash('Có lỗi xảy ra khi đăng ký. Vui lòng thử lại', 'error')

    def forgot_password(self):
        """
        Trang quên mật khẩu - Yêu cầu reset
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
                old_tokens = self.db_session.query(db.PasswordResetToken).filter(
                    db.PasswordResetToken.user_id == user.id,
                    db.PasswordResetToken.used == False
                ).all()
                for old_token in old_tokens:
                    old_token.used = True
                
                # Tạo token mới
                reset_token_obj = db.PasswordResetToken(
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

    def init_menu_item(self):
        
        count = self.db_session.query(db.Category).count()
        if count > 0:
            return {
                'success': False,
                'error': 'Đã có categories trong database'
            }
        
        created_items = {}
        parent_categories = [c for c in db.DEFAULT_CATEGORIES if c['parent_id'] is None]
        parent_categories.sort(key=lambda x: x['order_display'])

        for cat_data in parent_categories:
            category = db.Category(
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

        child_categories = [c for c in db.DEFAULT_CATEGORIES if c['parent_id'] is not None]
        child_categories.sort(key=lambda x: (x['parent_id'], x['order_display']))

        for cat_data in child_categories:
            parent_slug = None
            for parent_cat in db.DEFAULT_CATEGORIES:
                if parent_cat.get('id') == cat_data['parent_id']:
                    parent_slug = parent_cat['slug']
                    break

            if parent_slug and parent_slug in created_items:
                parent_id = created_items[parent_slug]
                parent_id = created_items[parent_slug]
                category = db.Category(
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

        return {
            'success': True,
            'message': f'Đã khởi tạo {len(db.DEFAULT_CATEGORIES)} categories mặc định',
            'count': len(db.DEFAULT_CATEGORIES)
        }