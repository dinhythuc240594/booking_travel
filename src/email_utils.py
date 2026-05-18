"""
Email utilities - cấu hình và gửi email bằng smtplib
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import secrets
import os
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
        from database import get_session, Setting
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
                        'prefix': '[VnNews] '
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
        'prefix': '[VnNews] '
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


def send_newsletter_subscription_email(email, unsubscribe_token, site='vn'):
    """
    Gửi email xác nhận đăng ký newsletter
    
    Args:
        email: Email người đăng ký
        unsubscribe_token: Token để hủy đăng ký
        site: 'vn' hoặc 'en'
        
    Returns:
        True nếu gửi thành công
    """
    try:
        # Tạo URL hủy đăng ký
        if site == 'en':
            unsubscribe_url = url_for('client.newsletter_unsubscribe', token=unsubscribe_token, _external=True)
        else:
            unsubscribe_url = url_for('client.newsletter_unsubscribe', token=unsubscribe_token, _external=True)
        
        if site == 'en':
            subject = "Newsletter Subscription Confirmation"
            body_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">Thank you for subscribing to our newsletter!</h2>
                    <p>You have successfully subscribed to our newsletter. We will send you the latest news and updates.</p>
                    <p>If you did not subscribe to this newsletter, please ignore this email.</p>
                    <p>To unsubscribe, click the link below:</p>
                    <p style="margin: 20px 0;">
                        <a href="{unsubscribe_url}" style="background-color: #e74c3c; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Unsubscribe</a>
                    </p>
                    <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
                        This is an automated email. Please do not reply.
                    </p>
                </div>
            </body>
            </html>
            """
            body_text = f"""Thank you for subscribing to our newsletter!

You have successfully subscribed to our newsletter. We will send you the latest news and updates.

If you did not subscribe to this newsletter, please ignore this email.

To unsubscribe, visit: {unsubscribe_url}
"""
        else:
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


def send_password_reset_email(user_email, reset_token, site='vn'):
    """
    Gửi email reset mật khẩu
    
    Args:
        user_email: Email người dùng
        reset_token: Token để reset mật khẩu
        site: 'vn' hoặc 'en'
        
    Returns:
        True nếu gửi thành công
    """
    try:
        # Tạo URL reset mật khẩu
        reset_url = url_for('client.reset_password', token=reset_token, _external=True)
        
        if site == 'en':
            subject = "Password Reset Request"
            body_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">Password Reset Request</h2>
                    <p>You have requested to reset your password. Click the link below to reset your password:</p>
                    <p style="margin: 20px 0;">
                        <a href="{reset_url}" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a>
                    </p>
                    <p>This link will expire in 1 hour.</p>
                    <p>If you did not request a password reset, please ignore this email. Your password will remain unchanged.</p>
                    <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
                        This is an automated email. Please do not reply.
                    </p>
                </div>
            </body>
            </html>
            """
            body_text = f"""Password Reset Request

You have requested to reset your password. Click the link below to reset your password:

{reset_url}

This link will expire in 1 hour.

If you did not request a password reset, please ignore this email. Your password will remain unchanged.
"""
        else:
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