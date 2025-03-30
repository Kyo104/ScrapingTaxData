-- Tạo bảng với đầy đủ cột
CREATE TABLE company_information (
    id SERIAL PRIMARY KEY,
    company_id VARCHAR(255) UNIQUE,  -- Định danh công ty, có thể là số, chữ, hoặc hỗn hợp
    company_name VARCHAR(255),       -- Tên công ty
    thue_username VARCHAR(100),      -- Tên đăng nhập thuế
    thue_password VARCHAR(100),      -- Mật khẩu thuế
    hoadon_username VARCHAR(100),    -- Tên đăng nhập hóa đơn
    hoadon_password VARCHAR(100),    -- Mật khẩu hóa đơn
    bhxh_username VARCHAR(100),      -- Tên đăng nhập BHXH
    bhxh_password VARCHAR(100)       -- Mật khẩu BHXH
);

-- Insert diverse sample data with different cases
INSERT INTO company_information (company_id, company_name, thue_username, thue_password, hoadon_username, hoadon_password, bhxh_username, bhxh_password) 
VALUES 
    -- Case 1: Company using all three services (Thuế, Hóa đơn, BHXH)
    ('1001', 'Công ty Alpha', '0101652097-ql', 'At2025$$', '0101652097', 'At2026@@@', '0101850613', '@ATDT2024'),
    ('1002', 'Công ty Alpha2', '0101652097-ql', 'At2025$$', '0101652097', 'At2026@@@', '0101850613', '@ATDT2024'),
    ('1003', 'Công ty Alpha3', '0101652097-ql', 'At2025$$', '0101652097', 'At2026@@@', '0101850613', '@ATDT2024'),
    ('1004', 'Công ty Alpha4', '0101652097-ql', 'At2025$$', '0101652097', 'At2026@@@', '0101850613', '@ATDT2024');
    
