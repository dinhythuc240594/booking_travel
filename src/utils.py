from werkzeug.security import generate_password_hash, check_password_hash
import re

# hash password before save into db
def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)

# valid format email
def validate_email(email: str) -> bool:

    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# valid format password
def validate_password(site: str, password: str) -> tuple:

    if not password:
        return False, "Mật khẩu không được để trống" if site == 'vn' else 'Password do not empty'
    
    if len(password) < 6:
        return False, "Mật khẩu phải có ít nhất 6 ký tự" if site == 'vn' else 'The password must have at least 6 characters.'
    
    if len(password) > 50:
        return False, "Mật khẩu không được vượt quá 50 ký tự" if site == 'vn' else 'Passwords must not exceed 50 characters.'
    
    return True, ""

# valid format phone number
def validate_phone(site, phone: str) -> tuple:

    if not phone:
        return False, "Số điện thoại không được để trống" if site == 'vn' else "The phone number do not empty"
    
    # remove space and  -
    phone_clean = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # format phone number:
    # 09xxxxxxxx, 08xxxxxxxx, 07xxxxxxxx, 05xxxxxxxx, 03xxxxxxxx
    # +849xxxxxxxx, +848xxxxxxxx, etc.
    pattern = r'^(\+84|0)(3[2-9]|5[6|8|9]|7[0|6-9]|8[1-6|8|9]|9[0-9])[0-9]{7}$'
    
    if not re.match(pattern, phone_clean):
        msg = "Số điện thoại không đúng định dạng (ví dụ: 0912345678 hoặc +84912345678)" if site == 'vn' else "The phone number is not in the correct format (e.g., 0912345678 or +84912345678)"
        return False, msg
    
    return True, ""

def _news_to_dict(news):
    """Convert News object to dictionary"""
    return {
        'id': news.id,
        'title': news.title,
        'slug': news.slug,
        'summary': news.summary,
        'thumbnail': news.thumbnail,
        'category': {
            'id': news.category.id,
            'name': news.category.name,
            'slug': news.category.slug
        },
        'view_count': news.view_count,
        'is_featured': news.is_featured,
        'is_hot': news.is_hot,
        'published_at': news.published_at.isoformat() if news.published_at else None,
        'created_at': news.created_at.isoformat()
    }

def _category_to_dict(category) -> dict:
    """Convert Category object to dictionary"""
    return {
        'id': category.id,
        'name': category.name,
        'slug': category.slug,
        'icon': category.icon,
        'parent_id': category.parent_id
    }