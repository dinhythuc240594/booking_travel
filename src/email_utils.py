"""
Email utilities - cấu hình và gửi email bằng smtplib
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
from database import get_session, Setting
from flask import url_for, current_app


def generate_token(length=32):
    """
    Generate a random token
    
    Args:
        length: Length of token
        
    Returns:
        Random token string
    """
    return secrets.token_urlsafe(length)


def get_smtp_config():
    """
    Lấy cấu hình SMTP từ database settings hoặc fallback về hardcoded values
    
    Returns:
        Dictionary chứa cấu hình SMTP
    """
    try:
        # Thử lấy từ database settings
        db_session = get_session()
        try:
            smtp_settings = db_session.query(Setting).filter(
                Setting.category == 'smtp'
            ).all()
            
            if smtp_settings:
                settings_dict = {s.key: s.value for s in smtp_settings}
                
                # Nếu có đủ settings từ database, sử dụng chúng
                if settings_dict.get('smtp_server') and settings_dict.get('smtp_username') and settings_dict.get('smtp_password'):
                    return {
                        'server': settings_dict.get('smtp_server', 'smtp.gmail.com'),
                        'port': int(settings_dict.get('smtp_port', '587')),
                        'use_tls': settings_dict.get('smtp_use_tls', 'true').lower() == 'true',
                        'use_ssl': not (settings_dict.get('smtp_use_tls', 'true').lower() == 'true'),
                        'username': settings_dict.get('smtp_username', ''),
                        'password': settings_dict.get('smtp_password', ''),
                        'sender': settings_dict.get('smtp_from_email') or settings_dict.get('smtp_username', ''),
                        'prefix': '[BookingTravel] '
                    }
        except Exception as e:
            print(f"Error reading SMTP settings from database: {str(e)}")
        finally:
            db_session.close()
    except Exception as e:
        print(f"Error getting SMTP config: {str(e)}")
    
    # Fallback về hardcoded values
    return {
        'server': 'smtp.gmail.com',
        'port': 587,
        'use_tls': True,
        'use_ssl': False,
        'username': '',
        'password': '',
        'sender': '',
        'prefix': '[BookingTravel] '
    }


def send_email(to_email, subject, body_html, body_text=None):
    """
    Gửi email sử dụng SMTP
    
    Args:
        to_email: Email người nhận
        subject: Tiêu đề email
        body_html: Nội dung HTML
        body_text: Nội dung text (optional)
        
    Returns:
        True nếu gửi thành công, False nếu có lỗi
    """
    try:
        config = get_smtp_config()
        
        # Kiểm tra cấu hình
        if not config['username'] or not config['password']:
            print("Warning: SMTP credentials not configured. Email not sent.")
            return False
        
        # Tạo message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = config['prefix'] + subject
        msg['From'] = config['sender']
        msg['To'] = to_email
        
        # Thêm nội dung
        if body_text:
            part1 = MIMEText(body_text, 'plain', 'utf-8')
            msg.attach(part1)
        
        part2 = MIMEText(body_html, 'html', 'utf-8')
        msg.attach(part2)
        
        # Kết nối và gửi email
        if config['use_ssl']:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(config['server'], config['port'], context=context)
        else:
            server = smtplib.SMTP(config['server'], config['port'])
            if config['use_tls']:
                server.starttls()
        
        server.login(config['username'], config['password'])
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def send_newsletter_subscription_email(email, unsubscribe_token):
    """
    Gửi email xác nhận đăng ký newsletter
    
    Args:
        email: Email người đăng ký
        unsubscribe_token: Token để hủy đăng ký
        
    Returns:
        True nếu gửi thành công
    """
    try:
        unsubscribe_url = url_for('client.newsletter_unsubscribe', token=unsubscribe_token, _external=True)
    
        subject = "Xác nhận đăng ký nhận bản tin"
        body_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">Cảm ơn bạn đã đăng ký nhận bản tin!</h2>
                    <p>Bạn đã đăng ký nhận bản tin thành công. Chúng tôi sẽ gửi cho bạn những tin tức và cập nhật mới nhất.</p>
                    <p>Nếu bạn không đăng ký nhận bản tin này, vui lòng bỏ qua email này.</p>
                    <p>Để hủy đăng ký, vui lòng nhấp vào liên kết bên dưới:</p>
                    <p style="margin: 20px 0;">
                        <a href="{unsubscribe_url}" style="background-color: #e74c3c; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Hủy đăng ký</a>
                    </p>
                    <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
                        Đây là email tự động. Vui lòng không trả lời email này.
                    </p>
                </div>
            </body>
            </html>
        """
        body_text = f"""Cảm ơn bạn đã đăng ký nhận bản tin!

            Bạn đã đăng ký nhận bản tin thành công. Chúng tôi sẽ gửi cho bạn những tin tức và cập nhật mới nhất.

            Nếu bạn không đăng ký nhận bản tin này, vui lòng bỏ qua email này.

            Để hủy đăng ký, truy cập: {unsubscribe_url}
        """
        
        return send_email(email, subject, body_html, body_text)
        
    except Exception as e:
        print(f"Error sending newsletter subscription email: {str(e)}")
        return False


def send_password_reset_email(user_email, reset_token):
    """
    Gửi email reset mật khẩu
    
    Args:
        user_email: Email người dùng
        reset_token: Token để reset mật khẩu
        
    Returns:
        True nếu gửi thành công
    """
    try:
        # Tạo URL reset mật khẩu
        reset_url = url_for('client.reset_password', token=reset_token, _external=True)
        
        subject = "Yêu cầu đặt lại mật khẩu"
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Yêu cầu đặt lại mật khẩu</h2>
                <p>Bạn đã yêu cầu đặt lại mật khẩu. Vui lòng nhấp vào liên kết bên dưới để đặt lại mật khẩu:</p>
                <p style="margin: 20px 0;">
                    <a href="{reset_url}" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Đặt lại mật khẩu</a>
                </p>
                <p>Liên kết này sẽ hết hạn sau 1 giờ.</p>
                <p>Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này. Mật khẩu của bạn sẽ không thay đổi.</p>
                <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
                    Đây là email tự động. Vui lòng không trả lời email này.
                </p>
            </div>
        </body>
        </html>
        """
        body_text = f"""Yêu cầu đặt lại mật khẩu

            Bạn đã yêu cầu đặt lại mật khẩu. Vui lòng nhấp vào liên kết bên dưới để đặt lại mật khẩu:

            {reset_url}

            Liên kết này sẽ hết hạn sau 1 giờ.

            Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này. Mật khẩu của bạn sẽ không thay đổi.
        """
        
        return send_email(user_email, subject, body_html, body_text)
        
    except Exception as e:
        print(f"Error sending password reset email: {str(e)}")
        return False


def send_booking_approved_email(to_email, user_name, booking_id, tour_title, check_in_date, total_price):
    """
    Gửi email thông báo đơn đặt tour đã được duyệt
    """
    try:
        subject = f"Đơn đặt tour #{booking_id} đã được duyệt thành công"
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f9f9f9; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border: 1px solid #eef2f3;">
                <div style="text-align: center; border-bottom: 2px solid #00acc1; padding-bottom: 20px; margin-bottom: 20px;">
                    <h2 style="color: #00acc1; margin: 0;">Xác Nhận Duyệt Đơn Đặt Tour</h2>
                    <p style="color: #7f8c8d; margin: 5px 0 0 0;">Mã đơn: #{booking_id}</p>
                </div>
                <p>Xin chào <strong>{user_name}</strong>,</p>
                <p>Chúc mừng bạn! Yêu cầu đặt tour của bạn đã được duyệt thành công. Dưới đây là thông tin chi tiết:</p>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background-color: #f8f9fa;">
                        <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold; width: 35%;">Tên Tour:</td>
                        <td style="padding: 10px; border: 1px solid #dee2e6;">{tour_title}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold;">Ngày khởi hành:</td>
                        <td style="padding: 10px; border: 1px solid #dee2e6;">{check_in_date}</td>
                    </tr>
                    <tr style="background-color: #f8f9fa;">
                        <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold;">Tổng tiền:</td>
                        <td style="padding: 10px; border: 1px solid #dee2e6; color: #e74c3c; font-weight: bold;">{total_price} VNĐ</td>
                    </tr>
                </table>
                <p>Nhân viên của chúng tôi sẽ liên hệ trực tiếp với bạn qua số điện thoại để hỗ trợ chuẩn bị trước ngày khởi hành.</p>
                <p>Chúc quý khách có một chuyến đi vui vẻ và ý nghĩa!</p>
                <div style="border-top: 1px solid #eeeeee; padding-top: 20px; margin-top: 30px; text-align: center; color: #95a5a6; font-size: 12px;">
                    <p>Đây là email tự động từ hệ thống VnTravel. Vui lòng không trả lời trực tiếp email này.</p>
                </div>
            </div>
        </body>
        </html>
        """
        body_text = f"""Xin chào {user_name},
        Yêu cầu đặt tour #{booking_id} của bạn đã được duyệt thành công.
        Tên Tour: {tour_title}
        Ngày khởi hành: {check_in_date}
        Tổng tiền: {total_price} VNĐ
        Chúc quý khách có một chuyến đi vui vẻ!
        """
        return send_email(to_email, subject, body_html, body_text)
    except Exception as e:
        print(f"Error sending booking approved email: {str(e)}")
        return False


def send_booking_completed_email(to_email, user_name, booking_id, tour_title, check_in_date, total_price, adults, children, payment_method):
    """
    Gửi email thông báo đơn đặt tour đã hoàn thành kèm hóa đơn điện tử
    """
    try:
        subject = f"Hóa đơn hoàn thành dịch vụ đặt tour #{booking_id}"
        
        pay_methods = {
            'credit_card': 'Thẻ tín dụng',
            'paypal': 'Paypal',
            'bank_transfer': 'Chuyển khoản ngân hàng',
            'cash': 'Tiền mặt'
        }
        pay_method_vn = pay_methods.get(payment_method, payment_method or 'Thẻ tín dụng')
        
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f9f9f9; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border: 1px solid #eef2f3;">
                <div style="text-align: center; border-bottom: 2px solid #2ecc71; padding-bottom: 20px; margin-bottom: 20px;">
                    <h2 style="color: #2ecc71; margin: 0;">HÓA ĐƠN ĐIỆN TỬ</h2>
                    <p style="color: #7f8c8d; margin: 5px 0 0 0;">Mã hóa đơn/đơn hàng: #{booking_id}</p>
                    <p style="color: #95a5a6; font-size: 12px; margin: 5px 0 0 0;">Trạng thái: Đã hoàn thành & Thanh toán</p>
                </div>
                
                <p>Kính gửi quý khách <strong>{user_name}</strong>,</p>
                <p>Cảm ơn quý khách đã tin tưởng và đồng hành cùng VnTravel. Chuyến đi của quý khách đã hoàn thành tốt đẹp. Dưới đây là hóa đơn chi tiết dịch vụ đã thực hiện:</p>
                
                <div style="background-color: #fcfcfc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <h4 style="margin-top: 0; color: #2c3e50; border-bottom: 1px solid #edf2f7; padding-bottom: 8px;">Chi tiết hóa đơn</h4>
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                        <tr>
                            <td style="padding: 6px 0; color: #718096;">Khách hàng:</td>
                            <td style="padding: 6px 0; text-align: right; font-weight: bold; color: #2d3748;">{user_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #718096;">Email:</td>
                            <td style="padding: 6px 0; text-align: right; color: #2d3748;">{to_email}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #718096;">Tên Tour:</td>
                            <td style="padding: 6px 0; text-align: right; font-weight: bold; color: #2d3748;">{tour_title}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #718096;">Khởi hành:</td>
                            <td style="padding: 6px 0; text-align: right; color: #2d3748;">{check_in_date}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #718096;">Số lượng:</td>
                            <td style="padding: 6px 0; text-align: right; color: #2d3748;">{adults} Người lớn {f", {children} Trẻ em" if children > 0 else ""}</td>
                        </tr>
                        <tr>
                            <td style="padding: 6px 0; color: #718096;">Phương thức thanh toán:</td>
                            <td style="padding: 6px 0; text-align: right; color: #2d3748;">{pay_method_vn}</td>
                        </tr>
                        <tr style="border-top: 1px solid #e2e8f0; font-size: 16px;">
                            <td style="padding: 12px 0 0 0; font-weight: bold; color: #2c3e50;">Tổng thanh toán:</td>
                            <td style="padding: 12px 0 0 0; text-align: right; font-weight: bold; color: #2ecc71;">{total_price} VNĐ</td>
                        </tr>
                    </table>
                </div>
                
                <p>Hóa đơn này được tạo tự động và xác nhận giao dịch thanh toán của quý khách là thành công.</p>
                <p>Rất hân hạnh được phục vụ quý khách trong những hành trình tiếp theo!</p>
                
                <div style="border-top: 1px solid #eeeeee; padding-top: 20px; margin-top: 30px; text-align: center; color: #95a5a6; font-size: 12px;">
                    <p>Đây là email tự động từ hệ thống VnTravel. Vui lòng không trả lời trực tiếp email này.</p>
                </div>
            </div>
        </body>
        </html>
        """
        body_text = f"""Kính gửi quý khách {user_name},
        Cảm ơn quý khách đã tin tưởng VnTravel. Chuyến đi của quý khách đã hoàn thành.
        
        HÓA ĐƠN CHI TIẾT
        Mã đơn đặt tour: #{booking_id}
        Tên Tour: {tour_title}
        Khởi hành: {check_in_date}
        Hành khách: {adults} Người lớn, {children} Trẻ em
        Phương thức thanh toán: {pay_method_vn}
        Tổng thanh toán: {total_price} VNĐ
        
        Trân trọng cảm ơn quý khách!
        """
        return send_email(to_email, subject, body_html, body_text)
    except Exception as e:
        print(f"Error sending booking completed email: {str(e)}")
        return False