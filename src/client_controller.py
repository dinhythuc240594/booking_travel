
from models.user_models import CustomerModel
from hashlib import new
from database import Tour
from flask import render_template, request, jsonify, abort, redirect, url_for, flash, session
import pytz
import json
from datetime import datetime, timedelta
from utils import validate_email, validate_password, validate_phone, hash_password, DOMESTIC
from email_utils import generate_token, send_password_reset_email
from database import (
    get_session,
    TourStatus,
    UserRole,
    Viewedtour,
    Savedtour, 
    PasswordResetToken,
)

from models.tour_models import TourModel
from models.user_models import CustomerModel
from models.booking_models import BookingModel
from models.related_models import LocationModel

PER_PAGE = 25
CATEGORY_MAP = {
    'beach': ['beach', 'Biển', 'Biển đảo'],
    'mountain': ['mountain', 'Núi', 'Núi rừng', 'Khám phá', 'Mạo hiểm'],
    'resort': ['resort', 'Nghỉ dưỡng', 'Nghỉ dưỡng 5 sao'],
    'culture': ['culture', 'Văn hóa', 'Văn hóa - Lịch sử', 'Trải nghiệm'],
}


class Controller():

    """Mangaer controller - manage related user, tour, ..."""

    def __init__(self):
        """initialize controller"""
        self.db_session = get_session()
        self.booking_model = BookingModel(self.db_session)
        self.tour_model = TourModel(self.db_session)
        self.customer_model = CustomerModel(self.db_session)
        self.location_model = LocationModel(self.db_session)

    def list_tour(self, limit = 25, offset = 0):
        """
        Danh sách tour
        Route: GET /tour
        """
        try:
            category = request.args.get('category')
            if category and category != 'all':
                if category in CATEGORY_MAP:
                    from sqlalchemy import or_
                    query = self.db_session.query(Tour).filter(Tour.is_deleted == False, Tour.status == TourStatus.PUBLISHED)
                    filters = [Tour.category_name.ilike(f"%{name}%") for name in CATEGORY_MAP[category]]
                    query = query.filter(or_(*filters))
                    tours_list = query.all()
                else:
                    tours_list = self.tour_model.get_by_category_name(category)
                
                tours_json = [self.tour_model._tour_to_dict(tour) for tour in tours_list]
                return tours_json
            else:
                tours_list = self.tour_model.get_public_tours(limit, offset)
                tours_json = [self.tour_model._tour_to_dict(tour) for tour in tours_list]
                return tours_json
        finally:
            self.db_session.close()

    def handle_login(self):

        data = request.json if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')

        if self.customer_model.is_locked_user(username):
            flash('Tài khoản đã bị khóa. Vui lòng liên hệ quản trị viên', 'error')
            return redirect(url_for('client.user_login'))
        
        user = self.customer_model.authenticate(username, password)
        
        if user and user.is_active and user.role == UserRole.CUSTOMER:
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['full_name'] = user.full_name or user.username
            session['role'] = user.role.value

            flash('Đăng nhập thành công', 'success')
            return redirect(url_for('client.home'))
        else:
            print('Tên đăng nhập hoặc mật khẩu không đúng')
            flash('Tên đăng nhập hoặc mật khẩu không đúng', 'error')
            return redirect(url_for('client.user_login'))

    def check_login(self):
        """
        Check login for user
        """
        
        if not request.is_json:
            return jsonify({
                'status': False,
                'code': 400,
                'message': 'Yêu cầu không đúng định dạng',
                'user': {}
            })
        
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')
        remember = True if data.get('remember') == 'on' else False

        print(f"username: {email}\npassword: {password}")

        # check status locked of account before authentication
        if self.customer_model.is_locked_user(email):
            return jsonify({
                'status': False,
                'code': 400,
                'message': 'Tài khoản đã bị khóa. Vui lòng liên hệ quản trị viên',
                'user': {}
            })
        
        user = self.customer_model.authenticate(email, password)
        
        if user and user.is_active and user.role == UserRole.CUSTOMER:
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['full_name'] = user.full_name or user.username
            session['role'] = user.role.value

            if remember:
                session.permanent = True
            else:
                session.permanent = False

            user = {
                # "id": user.user_id,
                "email": user.email,
                "name": user.full_name,
                "role": user.role.value,
                "phoneNumber": user.phone_number,
                "address": user.address,
                "gender": user.gender,
                "dateOfBirth": user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else '',
                "createdAt": user.created_at.strftime('%d/%m/%Y %H:%M') if user.created_at else '',
                "updatedAt": user.updated_at.strftime('%d/%m/%Y %H:%M') if user.updated_at else '',
            }

            return jsonify({
                'status': True,
                'code': 200,
                'message': 'success',
                'user': user
            })
        else:
            return jsonify({
                'status': False,
                'code': 401,
                'message': 'failed',
                'user': {}
            })

    def register(self):
        """
        Page register user
        Route: POST /register
        """
        
        if not request.is_json:
            return jsonify({
                'status': 400,
                'message': 'Yêu cầu không đúng định dạng',
                'user': {}
            })

        data = request.get_json()

        # Validation
        errors = []
        
        username = data.get('email', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        full_name = data.get('full_name', '').strip()
        phone = data.get('phone', '').strip()
        
        print(f"username: {username}\nemail: {email}\npassword: {password}\nconfirm_password: {confirm_password}\nfull_name: {full_name}\nphone: {phone}")

        # Validate username
        if not username:
            errors.append('Tên đăng nhập không được để trống')
        elif len(username) < 3:
            errors.append('Tên đăng nhập phải có ít nhất 3 ký tự')
        elif self.customer_model.get_by_username(username):
            errors.append('Tên đăng nhập đã tồn tại')
        
        # Validate email
        if not validate_email(email):
            errors.append('Email không đúng định dạng')
        elif self.customer_model.get_by_email(email):
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
                return jsonify({
                    'status': 400,
                    'message': error,
                    'user': {}
                })
        else:
            try:
                # Clean phone number
                phone_clean = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                
                user = self.customer_model.create(
                    username=username,
                    email=email,
                    password=hash_password(password),
                    full_name=full_name if full_name else None,
                    phone=phone_clean,
                    role=UserRole.CUSTOMER
                )
                
                if user:
                    user = {
                        "id": user.user_id,
                        "email": user.email,
                        "name": user.full_name,
                        "role": user.role.value,
                        "phone": user.phone_number,
                        "createdAt": user.created_at.strftime('%d/%m/%Y %H:%M') if user.created_at else '',
                        "updatedAt": user.updated_at.strftime('%d/%m/%Y %H:%M') if user.updated_at else '',
                    }
                    return jsonify({
                        'status': 200,
                        'message': 'success',
                        'user': user
                    })
            except Exception as e:
                print(e)
                return jsonify({
                    'status': 400,
                    'message': 'failed',
                    'user': {}
                })

    def forgot_password(self):
        """
        Page forgot password - Request reset
        Route: POST /forgot-password
        """

        data = request.json if request.is_json else request.form
        email = data.get('email', '').strip().lower()
        
        # Validation
        if not email:
            flash('Email không được để trống')
        elif not validate_email(email):
            flash('Email không đúng định dạng')
        else:
            # Tìm user
            user = self.customer_model.get_by_email(email)
            
            if user:
                # Tạo token reset
                reset_token = generate_token()
                expires_at = datetime.utcnow() + timedelta(hours=1)  # Token hết hạn sau 1 giờ
                
                # Vô hiệu hóa các token cũ của user này
                old_tokens = self.db_session.query(PasswordResetToken).filter(
                    PasswordResetToken.user_id == user.user_id,
                    PasswordResetToken.used == False
                ).all()
                for old_token in old_tokens:
                    old_token.used = True
                
                # Tạo token mới
                reset_token_obj = PasswordResetToken(
                    user_id=user.user_id,
                    token=reset_token,
                    expires_at=expires_at
                )
                self.db_session.add(reset_token_obj)
                self.db_session.commit()
                
                # Gửi email reset
                send_password_reset_email(user.email, reset_token)
            
            # Luôn hiển thị thông báo thành công (bảo mật)
            success_msg = 'Nếu email tồn tại trong hệ thống, chúng tôi đã gửi link đặt lại mật khẩu đến email của bạn. Vui lòng kiểm tra hộp thư của bạn.'
            flash(success_msg, 'success')
            return redirect(url_for('client.user_login'))

    def tours_detail(self, tours_slug: str):
        """
        Page tour detail
        Route: GET /tour/<tours_slug>
        """
        try:

            print(f"Slug received: {tours_slug}")
            
            tour_model = self.tour_model
            
            tour = tour_model.get_by_slug(tours_slug)
            if not tour:
                print(f"Tour not found for slug: {tours_slug}")
                return None
            print(f"Tour status: {tour.status}")
            if tour.status != TourStatus.PUBLISHED:
                print(f"Tour not published, status: {tour.status}")
                return None

            is_saved = False
            user_id = None

            if 'user_id' in session:
                user_id = session['user_id']

                existing_viewed = self.db_session.query(Viewedtour).filter(
                    Viewedtour.user_id == user_id,
                    Viewedtour.tour_id == tour.tour_id,
                ).first()
                
                if not existing_viewed:
                    viewed_tour = Viewedtour(
                        user_id=user_id,
                        tour_id=tour.tour_id,
                    )
                    self.db_session.add(viewed_tour)
                    self.db_session.commit()
                else:

                    existing_viewed.viewed_at = datetime.utcnow()
                    self.db_session.commit()

                saved_tour = self.db_session.query(Savedtour).filter(
                    Savedtour.user_id == user_id,
                    Savedtour.tour_id == tour.tour_id,
                ).first()
                is_saved = saved_tour is not None

            return {
                "tour": tour_model._tour_to_dict(tour),
                "is_saved": is_saved,
                "user_id": user_id,
            }
        except Exception as e:
            self.db_session.rollback()
            
            import traceback
            print(f"Error in tours_detail: {str(e)}")
            traceback.print_exc()
            
            return None
        finally:
            self.db_session.close()
    
    def search_tours(self):
        """
        Search tour by keyword
        Route: GET /search?q=<keyword>
        """
        try:

            tours_model = self.tour_model

            search = request.args.get('search', None)
            date_from = request.args.get('date_from', None)
            date_to = request.args.get('date_to', None)
            guest = request.args.get('guest', None)
            
            # Safely parse adult and children as int to prevent type crash
            try:
                adult = int(request.args.get('adult', request.args.get('adults', 1)))
            except (ValueError, TypeError):
                adult = 1
                
            try:
                children = int(request.args.get('children', 0))
            except (ValueError, TypeError):
                children = 0
                
            status_filter = request.args.get('status', None)
            page = request.args.get('page', 1, type=int)
            per_page = 25
            offset = (page - 1) * per_page
            
            status = None
            if status_filter:
                try:
                    status = TourStatus(status_filter)
                except ValueError:
                    status = None
            
            if search:
                tour_list = self.tour_model.search(
                    keyword=search,
                    limit=per_page,
                    offset=offset
                )
            else:
                tour_list = self.tour_model.get_public_tours(
                    limit=per_page,
                    offset=offset
                )
            tours_json = [self.tour_model._tour_to_dict(tour, adult, children) for tour in tour_list]
            return tours_json

        finally:
            self.db_session.close()

    def bookings(self):
        try:
            booking_model = self.booking_model
            user_id = session.get('user_id')
            print(f"User ID: {user_id}")
            if not user_id:
                return jsonify([])
            booking_list = booking_model.get_by_user_id(user_id)
            json_bookings = [booking_model._booking_to_dict(booking) for booking in booking_list]
            return jsonify(json_bookings)
        except Exception as e:
            self.db_session.rollback()
            print(f"Error in bookings: {str(e)}")
            return jsonify([])

    def locations(self):
        """API lấy danh sách địa điểm"""
        try:
            location_type = request.args.get('type')
            is_popular_str = request.args.get('is_popular', "false").lower()
            is_popular = is_popular_str == "true"
            locations = self.location_model.get_location(is_popular=is_popular)
            locations = [self.location_model._location_to_dict(location) for location in locations]

            if not locations:
                locations = DOMESTIC

            # Filter by location type (domestic / international)
            if location_type:
                location_type = location_type.lower()
                if location_type == 'domestic':
                    locations = [loc for loc in locations if loc.get('country', '').lower() in ['vietnam', 'việt nam']]
                elif location_type == 'international':
                    locations = [loc for loc in locations if loc.get('country', '').lower() not in ['vietnam', 'việt nam']]

            if is_popular:
                locations.sort(key=lambda x : x["toursCount"], reverse=True)
                locations = locations[:6]

                for location in locations:
                    if location["toursCount"] > 10:
                        location["className"] = "md:col-span-1 md:row-span-2 h-[340px] md:h-[420px]"
                    else:
                        location["className"] = "md:col-span-1 md:row-span-1 h-[200px]"

            return locations
        except Exception as e:
            self.db_session.rollback()
            print(f"error: " + str(e))
            return []

    def create_booking(self):
        """
        Tạo booking mới cho Tour
        Route: POST /bookings
        """
        try:

            if not request.is_json:
                return jsonify({
                    'status': 400,
                    'message': 'Yêu cầu không đúng định dạng JSON'
                }), 400

            data = request.get_json()
            
            # Lấy user_id từ session hoặc request body
            user_id = session.get('user_id')
            print(f"user_id: {user_id}")
            if not user_id:
                return jsonify({
                    'status': 401,
                    'message': 'Yêu cầu đăng nhập để đặt tour'
                }), 401

            tour_id = data.get('tourId')
            departure_date_str = data.get('departureDate')
            adults = int(data.get('adults', 1))
            children = int(data.get('children', 0))
            total_price = float(data.get('totalPrice', 0))

            if not tour_id:
                return jsonify({
                    'status': 400,
                    'message': 'Thiếu mã tour'
                }), 400

            # Tìm tour
            tour = self.tour_model.get_by_id(tour_id)
            if not tour:
                return jsonify({
                    'status': 404,
                    'message': 'Không tìm thấy tour trong hệ thống'
                }), 404

            # Chuyển đổi ngày đi
            try:
                departure_date = datetime.strptime(departure_date_str, '%Y-%m-%d')
            except Exception:
                departure_date = datetime.now() + timedelta(days=7)

            # Tạo đối tượng Booking mới
            success = self.booking_model.create_combo_booking(
                user_id, 
                None,
                None,
                tour_id,
                adults,
                data.get('paymentMethod', 'credit_card'),
                departure_date,
                total_price,
                departure_date + timedelta(days=tour.duration_days)
            )

            if success:
                booking = self.booking_model.get_latest_by_user_id(user_id)
                return jsonify({
                    'status': 200,
                    'message': 'Đặt tour thành công',
                    'booking': self.booking_model._booking_to_dict(booking)
                }), 200
            else:
                return jsonify({
                    'status': 400,
                    'message': 'Đặt tour thất bại',
                    'booking': None
                }), 400

        except Exception as e:
            self.db_session.rollback()
            print(f"Error in create_booking: {str(e)}")
            return jsonify({
                'status': 500,
                'message': f'Lỗi hệ thống khi đặt tour: {str(e)}'
            }), 500
        finally:
            self.db_session.close()

    def cancel_booking_route(self, booking_id):
        """
        Hủy đặt chỗ của người dùng
        Route: POST /bookings/cancel/<booking_id>
        """
        try:
            success = self.booking_model.cancel_booking(booking_id)
            if success:
                return jsonify({
                    'status': 200,
                    'message': 'Hủy đặt chỗ thành công'
                }), 200
            else:
                return jsonify({
                    'status': 400,
                    'message': 'Không thể hủy đặt chỗ này'
                }), 400
        except Exception as e:
            return jsonify({
                'status': 500,
                'message': f'Lỗi hệ thống: {str(e)}'
            }), 500

    def get_tours_tree(self):
        """
        Lấy cấu trúc cây phân cấp tour sử dụng Composite Pattern.
        Route: GET /tours/tree
        """
        try:
            tree_dict = self.tour_model.get_tours_tree()
            return jsonify({
                'success': True,
                'tree': tree_dict
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

