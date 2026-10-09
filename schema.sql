-- AccessMitra: Indian Accessibility & Government Schemes Portal
-- Database Schema for MySQL 8.0+

CREATE DATABASE IF NOT EXISTS accessmitra CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE accessmitra;

-- 1. Government Schemes Table
CREATE TABLE IF NOT EXISTS schemes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    ministry VARCHAR(255) NOT NULL,
    implementing_agency VARCHAR(255) DEFAULT '',
    category VARCHAR(100) NOT NULL,
    level VARCHAR(50) NOT NULL DEFAULT 'Central', -- 'Central', 'State', 'Both'
    state_name VARCHAR(100) DEFAULT 'All India',
    target_disability VARCHAR(255) NOT NULL, -- 'All Disabilities', 'Locomotor', 'Visual', 'Hearing', etc.
    min_disability_pct INT DEFAULT 40,
    min_age INT DEFAULT 0,
    max_age INT DEFAULT 120,
    max_annual_income INT DEFAULT 0, -- 0 means no explicit limit
    brief_description TEXT NOT NULL,
    eligibility TEXT NOT NULL,
    benefits TEXT NOT NULL,
    application_process TEXT NOT NULL,
    documents_required TEXT NOT NULL,
    contact_details TEXT NOT NULL,
    helpline_number VARCHAR(100) DEFAULT '',
    official_portal_url VARCHAR(500) NOT NULL,
    application_url VARCHAR(500) NOT NULL,
    tags VARCHAR(255) DEFAULT '',
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_target_disability (target_disability),
    INDEX idx_level (level),
    INDEX idx_is_featured (is_featured),
    FULLTEXT INDEX idx_fulltext_search (name, brief_description, eligibility, benefits, tags)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Verified Helplines Table
CREATE TABLE IF NOT EXISTS helplines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,
    phone_number VARCHAR(100) NOT NULL,
    toll_free BOOLEAN DEFAULT TRUE,
    operational_hours VARCHAR(100) NOT NULL,
    languages VARCHAR(255) NOT NULL,
    services TEXT NOT NULL,
    official_url VARCHAR(500) NOT NULL,
    category VARCHAR(100) NOT NULL DEFAULT 'Emergency & Crisis',
    priority_order INT DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Grievance & Legal Redressal Authorities Table
CREATE TABLE IF NOT EXISTS grievance_authorities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    jurisdiction VARCHAR(255) NOT NULL,
    official_designation VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(100) NOT NULL,
    portal_url VARCHAR(500) NOT NULL,
    address TEXT NOT NULL,
    act_reference VARCHAR(255) DEFAULT 'RPwD Act 2016',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Accessibility Resources & Digital Tools
CREATE TABLE IF NOT EXISTS accessibility_resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL, -- 'Assistive Software', 'Guidelines', 'Library', 'Audio Repository'
    description TEXT NOT NULL,
    cost VARCHAR(50) NOT NULL DEFAULT 'Free / Open Source',
    platform VARCHAR(100) NOT NULL,
    official_link VARCHAR(500) NOT NULL,
    developer_organization VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Feedback and Accessibility Reports
CREATE TABLE IF NOT EXISTS feedback_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(150),
    user_email VARCHAR(150),
    feedback_type VARCHAR(100) NOT NULL, -- 'Accessibility Issue', 'Scheme Inquiry', 'General Feedback'
    subject VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    accessibility_mode VARCHAR(100) DEFAULT 'Standard',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(50) DEFAULT '',
    contrast_mode VARCHAR(50) DEFAULT 'standard',
    font_size VARCHAR(50) DEFAULT 'base',
    dyslexia_font BOOLEAN DEFAULT FALSE,
    reading_ruler BOOLEAN DEFAULT FALSE,
    disability_type VARCHAR(100) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. User Saved Schemes (Bookmarks)
CREATE TABLE IF NOT EXISTS user_bookmarks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    scheme_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_user_scheme (user_id, scheme_id),
    INDEX idx_user_id (user_id),
    INDEX idx_scheme_id (scheme_id),
    CONSTRAINT fk_user_bookmarks_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_user_bookmarks_scheme FOREIGN KEY (scheme_id) REFERENCES schemes(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

