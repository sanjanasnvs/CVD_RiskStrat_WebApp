-- Create the database
CREATE DATABASE CVD_RiskDB;
USE CVD_RiskDB;

-- Patients Table
CREATE TABLE Patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    gender ENUM('Male', 'Female', 'Other'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clinicians Table
CREATE TABLE Clinicians (
    clinician_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    specialty VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admins Table
CREATE TABLE Admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('SuperAdmin', 'Manager', 'Support'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Questionnaire Table
CREATE TABLE Questionnaire (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    question_text TEXT NOT NULL,
    category VARCHAR(100),
    dependencies TEXT NULL
);

-- Responses Table (Linking Patients and Questionnaire)
CREATE TABLE Responses (
    response_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    question_id INT,
    response_text TEXT NOT NULL,
    response_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES Questionnaire(question_id) ON DELETE CASCADE
);

-- Risk Stratification Table
CREATE TABLE Risk_Stratification (
    stratification_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    risk_score DECIMAL(5,2),
    recommendation TEXT,
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE
);

-- Patient Outcomes Table (Self-Reported Follow-ups)
CREATE TABLE Patient_Outcomes (
    outcome_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    outcome_description TEXT NOT NULL,
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE
);

-- Clinician-Patient Relationship (Many-to-Many)
CREATE TABLE Clinician_Patient (
    clinician_id INT,
    patient_id INT,
    PRIMARY KEY (clinician_id, patient_id),
    FOREIGN KEY (clinician_id) REFERENCES Clinicians(clinician_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE
);
