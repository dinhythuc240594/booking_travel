
USE bookingtravel;

INSERT INTO users (username, email, password_hash, full_name, phone_number, role, is_active) VALUES
('staff01', 'staff01@bookingtravel.com', 'scrypt:32768:8:1$Y7ICFlFUHB1IEHA6$00e461ceb562bd73eeb3134d1b17e2875ca57fbe0357801a6ab92251c15ee233b5994fa738875c6b3dc9cafc3bca55754fbd38e371cd7fdfa8b2dfa0b96e7de9', 'Nhân Viên', '0901234567', 'staff', TRUE);