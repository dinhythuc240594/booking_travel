-- Sử dụng cơ sở dữ liệu BookingTravel
USE `BookingTravel`;

-- ---------------------------------------------------------
-- 1. CẬP NHẬT BẢNG `users`
-- Gộp chung các lệnh ADD COLUMN vào một câu lệnh ALTER TABLE duy nhất
-- ---------------------------------------------------------
ALTER TABLE `users` 
    ADD COLUMN `date_of_birth` DATE NULL AFTER `avatar`,
    ADD COLUMN `gender` VARCHAR(10) NULL AFTER `date_of_birth`,
    ADD COLUMN `address` VARCHAR(500) NULL AFTER `gender`;

-- ---------------------------------------------------------
-- 2. CẬP NHẬT BẢNG `tour`
-- ---------------------------------------------------------
ALTER TABLE `tour` 
    ADD COLUMN `discount_price` DECIMAL(10, 2) NULL AFTER `price_per_child`;
    
