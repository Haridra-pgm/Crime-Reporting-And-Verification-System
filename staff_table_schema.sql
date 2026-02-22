-- ============================================================
-- CREATE STAFF TABLE FOR CRIME REPORTING SYSTEM
-- ============================================================
-- Run this SQL query in your MySQL database to create the staff_table

CREATE TABLE IF NOT EXISTS crime.staff_table (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique staff identifier',
    fullname VARCHAR(255) NOT NULL COMMENT 'Full name of the staff member',
    email VARCHAR(255) NOT NULL UNIQUE COMMENT 'Email address (unique)',
    staff_id VARCHAR(100) NOT NULL UNIQUE COMMENT 'Unique staff ID (e.g., PO-12345)',
    phone VARCHAR(20) NOT NULL COMMENT '10-digit phone number',
    gender ENUM('Male', 'Female', 'Other') COMMENT 'Gender',
    dob DATE COMMENT 'Date of birth (optional)',
    rank VARCHAR(100) NOT NULL COMMENT 'Police rank (Constable, Inspector, DSP, SP, etc.)',
    police_station VARCHAR(255) NOT NULL COMMENT 'Assigned police station',
    posting VARCHAR(255) NOT NULL COMMENT 'Department/posting (e.g., Crime Branch, Traffic)',
    location VARCHAR(255) NOT NULL COMMENT 'Location/city',
    state VARCHAR(100) NOT NULL COMMENT 'State name',
    password LONGTEXT NOT NULL COMMENT 'Encrypted password (Fernet)',
    status ENUM('Active', 'Inactive', 'On Leave') DEFAULT 'Active' COMMENT 'Staff status',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Account creation timestamp',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update timestamp',
    
    -- Indexes for better query performance
    INDEX idx_email (email),
    INDEX idx_staff_id (staff_id),
    INDEX idx_rank (rank),
    INDEX idx_police_station (police_station),
    INDEX idx_state (state),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- INSERT SAMPLE DATA (Optional - for testing)
-- ============================================================
-- Uncomment the following lines if you want to insert sample data

/*
INSERT INTO crime.staff_table 
(fullname, email, staff_id, phone, gender, dob, rank, police_station, posting, location, state, password, status)
VALUES 
('Rajesh Kumar', 'rajesh@police.gov.in', 'PO-001', '9876543210', 'Male', '1990-05-15', 'Constable', 'Central Police Station', 'Crime Branch', 'New Delhi', 'Delhi', 'encrypted_password_here', 'Active'),
('Priya Singh', 'priya@police.gov.in', 'PO-002', '8765432109', 'Female', '1992-07-20', 'Head Constable', 'South Police Station', 'Traffic', 'Bangalore', 'Karnataka', 'encrypted_password_here', 'Active'),
('Amit Sharma', 'amit@police.gov.in', 'PO-003', '7654321098', 'Male', '1988-03-10', 'Inspector', 'North Police Station', 'Investigation', 'Mumbai', 'Maharashtra', 'encrypted_password_here', 'Active');
*/

-- ============================================================
-- USEFUL QUERIES
-- ============================================================

-- Get all active staff:
-- SELECT * FROM crime.staff_table WHERE status = 'Active' ORDER BY created_at DESC;

-- Get all staff by rank:
-- SELECT * FROM crime.staff_table WHERE rank = 'Inspector' ORDER BY fullname;

-- Get staff by police station:
-- SELECT * FROM crime.staff_table WHERE police_station = 'Central Police Station';

-- Get all staff by state:
-- SELECT * FROM crime.staff_table WHERE state = 'Delhi' ORDER BY rank;

-- Search staff by name or email:
-- SELECT * FROM crime.staff_table WHERE fullname LIKE '%Kumar%' OR email LIKE '%@police%';

-- Count staff by rank:
-- SELECT rank, COUNT(*) as count FROM crime.staff_table GROUP BY rank;

-- Count active staff by police station:
-- SELECT police_station, COUNT(*) as active_count FROM crime.staff_table 
-- WHERE status = 'Active' GROUP BY police_station;
