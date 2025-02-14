-- Create the table
CREATE TABLE company_information (
    id SERIAL PRIMARY KEY,
    company VARCHAR(255) UNIQUE,
    thue_username VARCHAR(100),
    thue_password VARCHAR(100),
    hoadon_username VARCHAR(100),
    hoadon_password VARCHAR(100),
    bhxh_username VARCHAR(100),
    bhxh_password VARCHAR(100)
);

-- Insert data into the table
INSERT INTO company_information (id, company, thue_username, thue_password, hoadon_username, hoadon_password, bhxh_username, bhxh_password) 
VALUES 
    (1, 'Công ty A', '', '', '0101652097', 'At2025@@@', '', ''),
    (2, 'Công ty B', '0101652097-ql', 'At2025$$', '0101652097', 'At2025@@@', '', ''),
    (3, 'Công ty C', '0101652097-ql', 'At2025$$', '', '', '0101850613', '@ATDT2024'),
    (4, 'Công ty D', '', '', '', '', '0101850613', '@ATDT2024');
