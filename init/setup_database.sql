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

INSERT INTO company_information (company_id, company_name, thue_username, thue_password, hoadon_username, hoadon_password, bhxh_username, bhxh_password) 
VALUES 
    ('1001', 'AT_CP_1', '0101357599-ql', '@At2025', '0101357599', '$q$$1C@#', '0101357599', '@ATcp2024'),
    ('1002', 'AT_CP_2', NULL, NULL, '0101357599', '$q$$1C@#', '0101357599', '@ATcp2024'),
    ('1003', 'AT_CP_3', '0101357599-ql', '@At2025', NULL, NULL, '0101357599', '@ATcp2024'),
    ('1004', 'AT_CP_4', '0101357599-ql', '@At2025', '0101357599', '$q$$1C@#', NULL, NULL),
    ('1005', 'AT_CP_5', NULL, NULL, NULL, NULL, '0101357599', '@ATcp2024'),
    ('1006', 'AT_CP_6', '0101357599-ql', '@At2025', NULL, NULL, NULL, NULL),
    ('1007', 'AT_CP_7', NULL, NULL, '0101357599', '$q$$1C@#', NULL, NULL),
    ('1008', 'AT_CP_8', NULL, NULL, NULL, NULL, NULL, NULL);
