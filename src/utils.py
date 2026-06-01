from werkzeug.security import generate_password_hash, check_password_hash
import re

import database as db
from composite_partern import CategoryComposite, ArticleLeaf

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

def build_category_tree(session, category_record) -> CategoryComposite:
    node = CategoryComposite(category_record)
    
    articles = session.query(db.Articles).filter_by(category_id=category_record.category_id).all()
    for article in articles:
        node.add_child(ArticleLeaf(article))
    
    sub_categories = session.query(db.ArticleCategory).filter_by(parent_id=category_record.category_id).all()
    for sub_cat in sub_categories:
        child_tree = build_category_tree(session, sub_cat)
        node.add_child(child_tree)
    
    return node