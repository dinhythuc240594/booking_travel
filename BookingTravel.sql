-- Tạo và sử dụng cơ sở dữ liệu
CREATE DATABASE IF NOT EXISTS BookingTravel;
USE BookingTravel;

-- =========================================================
-- 1. BẢNG USERS
-- =========================================================
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NULL,
    phone_number VARCHAR(20) NULL,
    avatar VARCHAR(255) NULL,
    date_of_birth DATE NULL,
    gender VARCHAR(10) NULL,
    address VARCHAR(500) NULL,
    role ENUM('customer', 'admin', 'staff') DEFAULT 'customer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================================================
-- 2. BẢNG LOCATIONS
-- =========================================================
CREATE TABLE IF NOT EXISTS locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    search_key VARCHAR(100) NOT NULL,
    description TEXT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    is_published BOOLEAN DEFAULT TRUE,
    is_popular BOOLEAN DEFAULT FALSE,
    image_url TEXT NULL,
    status ENUM('draft', 'pending', 'approved', 'rejected', 'published') DEFAULT 'draft',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================================================
-- 3. BẢNG HOTELS
-- =========================================================
CREATE TABLE IF NOT EXISTS hotels (
    hotel_id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NULL,
    name VARCHAR(150) NOT NULL,
    star_rating INT NULL CHECK (star_rating >= 1 AND star_rating <= 5),
    price_per_night DECIMAL(10, 2) NOT NULL,
    address VARCHAR(255) NULL,
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE SET NULL
);

-- =========================================================
-- 4. BẢNG TOUR
-- =========================================================
CREATE TABLE IF NOT EXISTS tour (
    tour_id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NULL,
    title VARCHAR(255) NOT NULL,
    author_id INT NOT NULL,
    reviewer_id INT NULL,
    summary TEXT NULL,
    content TEXT NOT NULL,
    duration_days INT NOT NULL DEFAULT 1,
    thumbnail VARCHAR(255) NULL,
    category_name VARCHAR(255) NULL,
    price_per_adult DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
    price_per_child DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
    discount_price DECIMAL(10, 2) NULL,
    images TEXT NULL, -- Lưu trữ mảng JSON ảnh
    is_published BOOLEAN DEFAULT FALSE,
    is_hot BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    slug VARCHAR(255) NOT NULL UNIQUE,
    view_count INT DEFAULT 0,
    status ENUM('draft', 'pending', 'approved', 'rejected', 'published') DEFAULT 'draft',
    is_deleted BOOLEAN DEFAULT FALSE,
    published_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE SET NULL,
    FOREIGN KEY (author_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- =========================================================
-- 5. BẢNG BOOKINGS
-- =========================================================
CREATE TABLE IF NOT EXISTS bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    booking_type ENUM('hotel', 'tour') NOT NULL,
    reference_id INT NOT NULL, 
    check_in_date DATETIME NULL,
    check_out_date DATETIME NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    booking_status ENUM('pending', 'confirmed', 'cancelled', 'completed') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- =========================================================
-- 6. BẢNG PAYMENTS
-- =========================================================
CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('credit_card', 'paypal', 'bank_transfer', 'cash') NOT NULL,
    payment_status ENUM('pending', 'successful', 'failed', 'refunded') DEFAULT 'pending',
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE
);

-- =========================================================
-- 7. BẢNG PASSWORD_RESET_TOKENS
-- =========================================================
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- =========================================================
-- 8. BẢNG NEWSLETTER_SUBSCRIPTIONS
-- =========================================================
CREATE TABLE IF NOT EXISTS newsletter_subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    unsubscribe_token VARCHAR(255) NOT NULL UNIQUE,
    subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    unsubscribed_at DATETIME NULL,
    user_id INT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- =========================================================
-- 9. BẢNG TAGS
-- =========================================================
CREATE TABLE IF NOT EXISTS tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    slug VARCHAR(50) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================================================
-- 10. BẢNG SETTINGS
-- =========================================================
CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(100) NOT NULL UNIQUE,
    value TEXT NULL,
    description TEXT NULL,
    category VARCHAR(50) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================================================
-- 11. BẢNG TOUR_REJECTIONS
-- =========================================================
CREATE TABLE IF NOT EXISTS tour_rejections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tour_id INT NOT NULL,
    rejected_by INT NOT NULL,
    reason TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tour_id) REFERENCES tour(tour_id) ON DELETE CASCADE,
    FOREIGN KEY (rejected_by) REFERENCES users(user_id) ON DELETE CASCADE
);

-- =========================================================
-- 12. BẢNG TOUR_COMMENTS
-- =========================================================
CREATE TABLE IF NOT EXISTS tour_comments (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    tour_id INT NOT NULL,
    user_id INT NOT NULL,
    parent_id INT NULL,
    content TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (tour_id) REFERENCES tour(tour_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES tour_comments(comment_id) ON DELETE CASCADE
);

-- =========================================================
-- 13. BẢNG SAVED_TOUR
-- =========================================================
CREATE TABLE IF NOT EXISTS saved_tour (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    tour_id INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (tour_id) REFERENCES tour(tour_id) ON DELETE CASCADE
);

-- =========================================================
-- 14. BẢNG VIEWED_TOUR
-- =========================================================
CREATE TABLE IF NOT EXISTS viewed_tour (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    tour_id INT NULL,
    viewed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (tour_id) REFERENCES tour(tour_id) ON DELETE CASCADE
);
