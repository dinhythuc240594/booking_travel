USE BookingTravel;

-- =========================================================
-- 1. BẢNG USERS
-- (Sử dụng chính xác mã băm scrypt bạn đã cung cấp)
-- =========================================================
INSERT INTO users (username, email, password_hash, full_name, phone_number, role, is_active) VALUES
('admin_user', 'admin@bookingtravel.com', 'scrypt:32768:8:1$Y7ICFlFUHB1IEHA6$00e461ceb562bd73eeb3134d1b17e2875ca57fbe0357801a6ab92251c15ee233b5994fa738875c6b3dc9cafc3bca55754fbd38e371cd7fdfa8b2dfa0b96e7de9', 'Trần Quản Trị', '0901234567', 'admin', TRUE),
('staff_01', 'staff01@bookingtravel.com', 'scrypt:32768:8:1$Y7ICFlFUHB1IEHA6$00e461ceb562bd73eeb3134d1b17e2875ca57fbe0357801a6ab92251c15ee233b5994fa738875c6b3dc9cafc3bca55754fbd38e371cd7fdfa8b2dfa0b96e7de9', 'Nguyễn Nhân Viên', '0912345678', 'staff', TRUE),
('customer_01', 'customer01@gmail.com', 'scrypt:32768:8:1$Y7ICFlFUHB1IEHA6$00e461ceb562bd73eeb3134d1b17e2875ca57fbe0357801a6ab92251c15ee233b5994fa738875c6b3dc9cafc3bca55754fbd38e371cd7fdfa8b2dfa0b96e7de9', 'Lê Khách Hàng', '0923456789', 'customer', TRUE),
('customer_02', 'customer02@gmail.com', 'scrypt:32768:8:1$Y7ICFlFUHB1IEHA6$00e461ceb562bd73eeb3134d1b17e2875ca57fbe0357801a6ab92251c15ee233b5994fa738875c6b3dc9cafc3bca55754fbd38e371cd7fdfa8b2dfa0b96e7de9', 'Phạm Du Khách', '0934567890', 'customer', TRUE);

-- =========================================================
-- 2. BẢNG LOCATIONS
-- =========================================================
INSERT INTO locations (city, country, name, search_key, description, slug, is_published, is_popular, image_url, status) VALUES
('Đà Nẵng', 'Việt Nam', 'Thành phố Đà Nẵng', 'da nang, danang', 'Thành phố biển đáng sống nhất Việt Nam.', 'da-nang', TRUE, TRUE, 'danang_thumbnail.jpg', 'published'),
('Đà Lạt', 'Việt Nam', 'Thành phố Đà Lạt', 'da lat, dalat, lam dong', 'Thành phố ngàn hoa với khí hậu ôn hòa.', 'da-lat', TRUE, TRUE, 'dalat_thumbnail.jpg', 'published'),
('Phú Quốc', 'Việt Nam', 'Đảo Ngọc Phú Quốc', 'phu quoc, kien giang, dao ngoc', 'Hòn đảo lớn nhất Việt Nam với những bãi biển tuyệt đẹp.', 'phu-quoc', TRUE, FALSE, 'phuquoc_thumbnail.jpg', 'published');

-- =========================================================
-- 3. BẢNG HOTELS
-- =========================================================
INSERT INTO hotels (location_id, name, star_rating, price_per_night, address) VALUES
(1, 'InterContinental Danang Sun Peninsula Resort', 5, 8000000.00, 'Bán đảo Sơn Trà, Đà Nẵng'),
(1, 'Mường Thanh Luxury Đà Nẵng', 4, 1500000.00, '270 Võ Nguyên Giáp, Đà Nẵng'),
(2, 'Hôtel Colline Đà Lạt', 4, 1200000.00, '10 Phan Bội Châu, Phường 1, Đà Lạt');

-- =========================================================
-- 4. BẢNG TOUR
-- =========================================================
INSERT INTO tour (location_id, title, author_id, reviewer_id, summary, content, duration_days, thumbnail, category_name, price_per_adult, price_per_child, discount_price, images, is_published, is_hot, is_featured, slug, view_count, status) VALUES
(1, 'Khám Phá Bán Đảo Sơn Trà - Lặn Ngắm San Hô', 2, 1, 'Trải nghiệm lặn ngắm san hô tuyệt đẹp tại Sơn Trà.', 'Nội dung chi tiết lịch trình Sơn Trà...', 1, 'sontra_thumb.jpg', 'Khám phá', 600000.00, 300000.00, 500000.00, '["sontra_1.jpg", "sontra_2.jpg"]', TRUE, TRUE, TRUE, 'kham-pha-son-tra', 150, 'published'),
(2, 'Tour Săn Mây Đồi Chè Cầu Đất', 2, 1, 'Đón bình minh rực rỡ tại đồi chè Cầu Đất.', 'Nội dung chi tiết tour săn mây...', 1, 'sanmay_thumb.jpg', 'Trải nghiệm', 400000.00, 250000.00, 350000.00, '["sanmay_1.jpg", "sanmay_2.jpg"]', TRUE, FALSE, TRUE, 'san-may-cau-dat', 85, 'published'),
(3, 'Tour Câu Mực Đêm Phú Quốc', 2, NULL, 'Trải nghiệm câu mực đêm cùng ngư dân.', 'Nội dung tour câu mực...', 1, 'caumuc_thumb.jpg', 'Mạo hiểm', 500000.00, 200000.00, NULL, '["caumuc_1.jpg"]', FALSE, FALSE, FALSE, 'cau-muc-dem-phu-quoc', 10, 'pending');

-- =========================================================
-- 5. BẢNG BOOKINGS
-- =========================================================
INSERT INTO bookings (user_id, booking_type, reference_id, check_in_date, check_out_date, total_price, booking_status) VALUES
(3, 'hotel', 2, '2026-07-15 14:00:00', '2026-07-17 12:00:00', 3000000.00, 'confirmed'), -- Đặt Mường Thanh (2 đêm)
(4, 'tour', 1, '2026-08-10 07:00:00', '2026-08-10 17:00:00', 1200000.00, 'pending');   -- Đặt 2 vé người lớn tour Sơn Trà

-- =========================================================
-- 6. BẢNG PAYMENTS
-- =========================================================
INSERT INTO payments (booking_id, amount, payment_method, payment_status) VALUES
(1, 3000000.00, 'credit_card', 'successful'),
(2, 1200000.00, 'bank_transfer', 'pending');

-- =========================================================
-- 7. BẢNG PASSWORD_RESET_TOKENS
-- =========================================================
INSERT INTO password_reset_tokens (user_id, token, expires_at, used) VALUES
(3, 'random_token_string_123', '2026-06-08 10:00:00', FALSE);

-- =========================================================
-- 8. BẢNG NEWSLETTER_SUBSCRIPTIONS
-- =========================================================
INSERT INTO newsletter_subscriptions (email, is_active, unsubscribe_token, user_id) VALUES
('customer01@gmail.com', TRUE, 'unsub_cust01', 3),
('anonymous_guest@example.com', TRUE, 'unsub_guest01', NULL);

-- =========================================================
-- 9. BẢNG TAGS
-- =========================================================
INSERT INTO tags (name, slug) VALUES
('Biển', 'bien'),
('Nghỉ dưỡng', 'nghi-duong'),
('Săn mây', 'san-may');

-- =========================================================
-- 10. BẢNG SETTINGS
-- =========================================================
INSERT INTO settings (`key`, value, description, category) VALUES
('site_name', 'Booking Travel Vietnam', 'Tên website hiển thị trên header', 'General'),
('contact_email', 'support@bookingtravel.com', 'Email liên hệ hỗ trợ', 'Contact'),
('maintenance_mode', 'false', 'Bật/tắt chế độ bảo trì', 'System');

-- =========================================================
-- 11. BẢNG TOUR_REJECTIONS
-- =========================================================
-- Giả sử tour thứ 3 bị từ chối một lần trước khi chuyển sang pending
INSERT INTO tour_rejections (tour_id, rejected_by, reason) VALUES
(3, 1, 'Vui lòng bổ sung thêm hình ảnh chất lượng cao cho tour câu mực đêm.');

-- =========================================================
-- 12. BẢNG TOUR_COMMENTS
-- =========================================================
INSERT INTO tour_comments (tour_id, user_id, parent_id, content, is_active) VALUES
(1, 3, NULL, 'Tour rất tuyệt vời, ngắm được nhiều san hô!', TRUE),
(1, 2, 1, 'Cảm ơn bạn đã trải nghiệm dịch vụ của chúng tôi!', TRUE);

-- =========================================================
-- 13. BẢNG SAVED_TOUR
-- =========================================================
INSERT INTO saved_tour (user_id, tour_id) VALUES
(3, 2),
(4, 1);

-- =========================================================
-- 14. BẢNG VIEWED_TOUR
-- =========================================================
INSERT INTO viewed_tour (user_id, tour_id) VALUES
(3, 1),
(3, 2),
(4, 1),
(4, 2);