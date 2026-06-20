USE `BookingTravel`;

-- Cập nhật kiểu dữ liệu của cột booking_status trong bảng bookings để đảm bảo có đầy đủ các giá trị:
-- 'pending' (Chờ duyệt), 'confirmed' (Đã duyệt), 'completed' (Hoàn thành), 'cancelled' (Đã hủy)
ALTER TABLE `bookings` 
    MODIFY COLUMN `booking_status` ENUM('pending', 'confirmed', 'cancelled', 'completed') DEFAULT 'pending';
