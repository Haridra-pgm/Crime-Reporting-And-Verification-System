-- ============================================================
-- UPDATE ADMIN_USER TABLE FOR CRIME REPORTING SYSTEM
-- ============================================================
-- Run this SQL query to verify/update the admin_user table

-- Check if table exists, if not create it
CREATE TABLE IF NOT EXISTS crime.admin_user (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique admin identifier',
    fullname VARCHAR(255) NOT NULL COMMENT 'Full name of the admin',
    email VARCHAR(255) NOT NULL UNIQUE COMMENT 'Email address (unique)',
    phone VARCHAR(20) NOT NULL COMMENT '10-digit phone number',
    gender ENUM('Male', 'Female', 'Other') COMMENT 'Gender',
    password LONGTEXT NOT NULL COMMENT 'Encrypted password (Fernet)',
    status ENUM('Active', 'Inactive') DEFAULT 'Active' COMMENT 'Admin status',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Account creation timestamp',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
    
    -- Indexes for better query performance
    INDEX idx_email (email),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- ALTER TABLE IF IT ALREADY EXISTS (to add missing columns)
-- ============================================================
-- Uncomment these if the table already exists and is missing columns

-- ALTER TABLE crime.admin_user ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
-- ALTER TABLE crime.admin_user ADD COLUMN IF NOT EXISTS gender ENUM('Male', 'Female', 'Other');
-- ALTER TABLE crime.admin_user ADD COLUMN IF NOT EXISTS status ENUM('Active', 'Inactive') DEFAULT 'Active';
-- ALTER TABLE crime.admin_user ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
-- ALTER TABLE crime.admin_user ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- ============================================================
-- VERIFY TABLE STRUCTURE
-- ============================================================
-- Run this query to verify the table structure:
-- DESCRIBE crime.admin_user;

-- ============================================================
-- INSERT SAMPLE DATA (Optional - for testing)
-- ============================================================
-- Uncomment the following lines if you want to insert sample data

/*
INSERT INTO crime.admin_user 
(fullname, email, phone, gender, password, status)
VALUES 
('Super Admin', 'superadmin@police.gov.in', '9999999999', 'Male', 'encrypted_password_here', 'Active'),
('John Administrator', 'john.admin@police.gov.in', '9876543210', 'Male', 'encrypted_password_here', 'Active'),
('Jane Manager', 'jane.admin@police.gov.in', '8765432109', 'Female', 'encrypted_password_here', 'Active');
*/

-- ============================================================
-- USEFUL QUERIES
-- ============================================================

-- Get all active admins:
-- SELECT * FROM crime.admin_user WHERE status = 'Active' ORDER BY created_at DESC;

-- Get all admins:
-- SELECT * FROM crime.admin_user ORDER BY created_at DESC;

-- Get admin by email:
-- SELECT * FROM crime.admin_user WHERE email = 'admin@police.gov.in';

-- Count total admins:
-- SELECT COUNT(*) as total_admins FROM crime.admin_user;

-- Get recently created admins:
-- SELECT * FROM crime.admin_user ORDER BY created_at DESC LIMIT 10;

-- Search admin by name:
-- SELECT * FROM crime.admin_user WHERE fullname LIKE '%John%';

-- Get inactive admins:
-- SELECT * FROM crime.admin_user WHERE status = 'Inactive';

-- Update admin status:
-- UPDATE crime.admin_user SET status = 'Inactive' WHERE id = 1;

-- Delete admin (use with caution):
-- DELETE FROM crime.admin_user WHERE id = 1;
