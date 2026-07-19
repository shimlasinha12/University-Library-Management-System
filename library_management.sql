-- ============================================================
-- University Library Management System
-- Database Schema File
-- ============================================================
-- Import this file using MySQL Workbench:
--   File > Open SQL Script > select this file > Execute
-- ============================================================

DROP DATABASE IF EXISTS library_management;
CREATE DATABASE library_management
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE library_management;

-- ============================================================
-- Table: users
-- Stores all user accounts (admin, librarian, student)
-- ============================================================
CREATE TABLE users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(100) NOT NULL UNIQUE,
    role          ENUM('admin', 'librarian', 'student') NOT NULL DEFAULT 'student',
    status        ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- Table: students
-- Student-specific information linked to users table
-- ============================================================
CREATE TABLE students (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL UNIQUE,
    student_id_no VARCHAR(20) NOT NULL UNIQUE,
    phone         VARCHAR(20),
    address       VARCHAR(200),
    department    VARCHAR(50),
    year          VARCHAR(20),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- Table: categories
-- Book categories
-- ============================================================
CREATE TABLE categories (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- Table: authors
-- Book authors
-- ============================================================
CREATE TABLE authors (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- Table: publishers
-- Book publishers
-- ============================================================
CREATE TABLE publishers (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    address   VARCHAR(200),
    contact   VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- Table: books
-- Book catalog with links to category, author, publisher
-- ============================================================
CREATE TABLE books (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    isbn             VARCHAR(20) NOT NULL UNIQUE,
    title            VARCHAR(200) NOT NULL,
    category_id      INT,
    author_id        INT,
    publisher_id     INT,
    quantity         INT NOT NULL DEFAULT 1,
    available_copies INT NOT NULL DEFAULT 1,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id)  REFERENCES categories(id)  ON DELETE SET NULL,
    FOREIGN KEY (author_id)    REFERENCES authors(id)      ON DELETE SET NULL,
    FOREIGN KEY (publisher_id) REFERENCES publishers(id)   ON DELETE SET NULL,
    CONSTRAINT chk_quantity CHECK (quantity >= 0),
    CONSTRAINT chk_available CHECK (available_copies >= 0 AND available_copies <= quantity)
) ENGINE=InnoDB;

-- ============================================================
-- Table: borrow_records
-- Tracks book issue and return transactions
-- ============================================================
CREATE TABLE borrow_records (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    book_id      INT NOT NULL,
    user_id      INT NOT NULL,
    issue_date   DATE NOT NULL,
    due_date     DATE NOT NULL,
    return_date  DATE DEFAULT NULL,
    status       ENUM('issued', 'returned') NOT NULL DEFAULT 'issued',
    fine_amount  DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE RESTRICT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ============================================================
-- Indexes for performance
-- ============================================================
CREATE INDEX idx_users_role         ON users(role);
CREATE INDEX idx_users_status       ON users(status);
CREATE INDEX idx_books_title        ON books(title);
CREATE INDEX idx_books_category      ON books(category_id);
CREATE INDEX idx_books_author        ON books(author_id);
CREATE INDEX idx_books_publisher     ON books(publisher_id);
CREATE INDEX idx_borrow_book         ON borrow_records(book_id);
CREATE INDEX idx_borrow_user         ON borrow_records(user_id);
CREATE INDEX idx_borrow_status       ON borrow_records(status);

-- ============================================================
-- Default Admin Account
-- Username: admin
-- Password: Admin@123
-- Password is hashed using Werkzeug (generate_password_hash)
-- ============================================================
INSERT INTO users (username, password_hash, full_name, email, role, status)
VALUES (
    'admin',
    'scrypt:32768:8:1$BM4uuXB0wczkHFQH$d522ba528719c9e02a1a66c063eee2fc7afb73898e7d7a8b5221c252d723a7777d1f2eae656d3cc4b17d3129b47d52af6d39ad44e5bd211570be365163d9e2cc',
    'System Administrator',
    'admin@university.edu',
    'admin',
    'active'
);

-- ============================================================
-- End of schema
-- ============================================================
