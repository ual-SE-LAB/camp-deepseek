-- Create enum for user roles
CREATE TYPE user_role AS ENUM ('admin', 'parent');

-- Users table (parents and admins)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    role user_role NOT NULL DEFAULT 'parent',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Campers table
CREATE TABLE campers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20),
    allergies TEXT,
    medical_conditions TEXT,
    medications TEXT,
    doctor_name VARCHAR(255),
    doctor_phone VARCHAR(20),
    insurance_provider VARCHAR(255),
    insurance_policy_number VARCHAR(100),
    special_needs TEXT,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Parent-Camper relationship table
CREATE TABLE parent_camper (
    parent_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    camper_id INTEGER REFERENCES campers(id) ON DELETE CASCADE,
    relationship VARCHAR(50), -- e.g., 'mother', 'father', 'guardian'
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (parent_id, camper_id)
);

-- Emergency contacts table
CREATE TABLE emergency_contacts (
    id SERIAL PRIMARY KEY,
    camper_id INTEGER REFERENCES campers(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    alternate_phone VARCHAR(20),
    email VARCHAR(255),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_campers_name ON campers(last_name, first_name);
CREATE INDEX idx_campers_is_active ON campers(is_active);
CREATE INDEX idx_emergency_contacts_camper ON emergency_contacts(camper_id);
CREATE INDEX idx_parent_camper_parent ON parent_camper(parent_id);
CREATE INDEX idx_parent_camper_camper ON parent_camper(camper_id);

-- Insert default admin user (password: admin123)
INSERT INTO users (email, hashed_password, full_name, role) VALUES 
('admin@camp.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36JBQGhxiKfjiM9Kv3s8vYm', 'Camp Administrator', 'admin');