from werkzeug.security import generate_password_hash, check_password_hash
import re

import database as db

DOMESTIC = [
    { "name": "Sa Pa, Lào Cai", "searchKey": "Sa Pa" },
    { "name": "Vịnh Hạ Long, Quảng Ninh", "searchKey": "Hạ Long" },
    { "name": "Đảo Phú Quốc, Kiên Giang", "searchKey": "Phú Quốc" },
    { "name": "Hội An, Quảng Nam", "searchKey": "Hội An" },
    { "name": "Đồng Văn, Hà Giang", "searchKey": "Hà Giang" },
    { "name": "Đà Lạt, Lâm Đồng", "searchKey": "Đà Lạt" },
    { "name": "Nha Trang, Khánh Hòa", "searchKey": "Nha Trang" },
]

CATEGORY_NAME = [
    { "id": "all", "name": "Tất cả" },
    { "id": "beach", "name": "Biển đảo" },
    { "id": "mountain", "name": "Núi rừng" },
    { "id": "resort", "name": "Nghỉ dưỡng" },
    { "id": "culture", "name": "Văn hóa" },
    # { "id": "international", "name": "Quốc tế" },
]

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
def validate_password(password: str) -> tuple:

    if not password:
        return False, "Mật khẩu không được để trống"
    
    if len(password) < 6:
        return False, "Mật khẩu phải có ít nhất 6 ký tự"
    
    if len(password) > 50:
        return False, "Mật khẩu không được vượt quá 50 ký tự"
    
    return True, ""

# valid format phone number
def validate_phone(phone: str) -> tuple:

    if not phone:
        return False, "Số điện thoại không được để trống"
    
    # remove space and  -
    phone_clean = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # format phone number:
    # 09xxxxxxxx, 08xxxxxxxx, 07xxxxxxxx, 05xxxxxxxx, 03xxxxxxxx
    # +849xxxxxxxx, +848xxxxxxxx, etc.
    pattern = r'^(\+84|0)(3[2-9]|5[6|8|9]|7[0|6-9]|8[1-6|8|9]|9[0-9])[0-9]{7}$'
    
    if not re.match(pattern, phone_clean):
        msg = "Số điện thoại không đúng định dạng (ví dụ: 0912345678 hoặc +84912345678)"
        return False, msg
    
    return True, ""

def generate_slug(title: str, status: str = None) -> str:
    """Tạo slug từ tiêu đề và trạng thái"""
    
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