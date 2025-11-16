-- Database Schema for Modular Platform
-- PostgreSQL 16+
-- Multi-tenant architecture with UUID primary keys

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =======================
-- CORE PLATFORM TABLES
-- =======================

-- Tenants (Organizations)
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    max_users INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tenants_slug ON tenants(slug);
CREATE INDEX idx_tenants_active ON tenants(is_active);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);

-- Tenant Users (Many-to-Many)
CREATE TABLE tenant_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'user', -- admin, manager, user
    is_active BOOLEAN DEFAULT true,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, user_id)
);

CREATE INDEX idx_tenant_users_tenant ON tenant_users(tenant_id);
CREATE INDEX idx_tenant_users_user ON tenant_users(user_id);

-- =======================
-- MODULE SYSTEM TABLES
-- =======================

-- Modules (Available in marketplace)
CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    version VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    icon_url VARCHAR(500),
    price_onetime DECIMAL(10, 2),
    price_monthly DECIMAL(10, 2),
    price_annual DECIMAL(10, 2),
    trial_days INTEGER DEFAULT 14,
    capabilities JSONB, -- {features: [], api_endpoints: [], webhooks: []}
    dependencies JSONB, -- {required: [], optional: []}
    settings_schema JSONB, -- JSON Schema for module configuration
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_modules_slug ON modules(slug);
CREATE INDEX idx_modules_active ON modules(is_active);
CREATE INDEX idx_modules_category ON modules(category);

-- Module Licenses (Tenant ownership)
CREATE TABLE module_licenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    license_type VARCHAR(50) NOT NULL, -- trial, purchased, subscription
    is_active BOOLEAN DEFAULT true,
    activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP, -- NULL for lifetime licenses
    settings JSONB, -- Module-specific configuration
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, module_id)
);

CREATE INDEX idx_licenses_tenant ON module_licenses(tenant_id);
CREATE INDEX idx_licenses_module ON module_licenses(module_id);
CREATE INDEX idx_licenses_active ON module_licenses(is_active);
CREATE INDEX idx_licenses_expires ON module_licenses(expires_at);

-- =======================
-- BILLING TABLES
-- =======================

-- Purchases (One-time payments)
CREATE TABLE purchases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) DEFAULT 'pending', -- pending, completed, failed, refunded
    stripe_payment_id VARCHAR(255),
    stripe_payment_intent_id VARCHAR(255),
    payment_method VARCHAR(50), -- card, paypal, etc.
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    refunded_at TIMESTAMP
);

CREATE INDEX idx_purchases_tenant ON purchases(tenant_id);
CREATE INDEX idx_purchases_module ON purchases(module_id);
CREATE INDEX idx_purchases_status ON purchases(status);
CREATE INDEX idx_purchases_stripe ON purchases(stripe_payment_id);

-- Subscriptions (Recurring payments)
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    interval VARCHAR(20) NOT NULL, -- monthly, annual
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) DEFAULT 'active', -- active, cancelled, expired, suspended
    stripe_subscription_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT false,
    cancelled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_subscriptions_tenant ON subscriptions(tenant_id);
CREATE INDEX idx_subscriptions_module ON subscriptions(module_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_stripe ON subscriptions(stripe_subscription_id);

-- Invoices
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id) ON DELETE SET NULL,
    purchase_id UUID REFERENCES purchases(id) ON DELETE SET NULL,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) DEFAULT 'draft', -- draft, sent, paid, void
    stripe_invoice_id VARCHAR(255),
    pdf_url VARCHAR(500),
    due_date DATE,
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_invoices_tenant ON invoices(tenant_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_number ON invoices(invoice_number);

-- =======================
-- CV ANALYSIS MODULE TABLES
-- =======================

-- CV Documents
CREATE TABLE cv_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    uploaded_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_size INTEGER, -- bytes
    mime_type VARCHAR(100),
    extracted_text TEXT,
    extracted_data JSONB, -- {skills: [], experience: [], education: [], languages: []}
    parsing_status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cv_tenant ON cv_documents(tenant_id);
CREATE INDEX idx_cv_uploaded_by ON cv_documents(uploaded_by);
CREATE INDEX idx_cv_status ON cv_documents(parsing_status);
CREATE INDEX idx_cv_extracted_gin ON cv_documents USING gin(extracted_data);

-- Job Descriptions
CREATE TABLE job_descriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    required_skills JSONB,
    preferred_skills JSONB,
    experience_level VARCHAR(50), -- entry, mid, senior, lead
    employment_type VARCHAR(50), -- full-time, part-time, contract
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_job_tenant ON job_descriptions(tenant_id);
CREATE INDEX idx_job_created_by ON job_descriptions(created_by);
CREATE INDEX idx_job_level ON job_descriptions(experience_level);

-- CV Analysis Results
CREATE TABLE cv_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    cv_document_id UUID NOT NULL REFERENCES cv_documents(id) ON DELETE CASCADE,
    job_description_id UUID NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    match_score DECIMAL(5, 2), -- 0.00 to 100.00
    skill_matches JSONB, -- {matched: [], missing: [], extra: []}
    experience_analysis JSONB,
    education_analysis JSONB,
    recommendations TEXT,
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    error_message TEXT,
    processing_time_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_analysis_tenant ON cv_analyses(tenant_id);
CREATE INDEX idx_analysis_cv ON cv_analyses(cv_document_id);
CREATE INDEX idx_analysis_job ON cv_analyses(job_description_id);
CREATE INDEX idx_analysis_status ON cv_analyses(status);
CREATE INDEX idx_analysis_score ON cv_analyses(match_score);

-- =======================
-- INTERVIEW MODULE TABLES
-- =======================

-- Interview Sessions
CREATE TABLE interview_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    cv_document_id UUID REFERENCES cv_documents(id) ON DELETE SET NULL,
    job_description_id UUID NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    cv_analysis_id UUID REFERENCES cv_analyses(id) ON DELETE SET NULL, -- For combined workflow
    candidate_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_token VARCHAR(255) UNIQUE,
    status VARCHAR(50) DEFAULT 'scheduled', -- scheduled, in_progress, completed, cancelled
    difficulty_level VARCHAR(50), -- easy, medium, hard
    duration_minutes INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interview_tenant ON interview_sessions(tenant_id);
CREATE INDEX idx_interview_cv ON interview_sessions(cv_document_id);
CREATE INDEX idx_interview_job ON interview_sessions(job_description_id);
CREATE INDEX idx_interview_status ON interview_sessions(status);
CREATE INDEX idx_interview_token ON interview_sessions(session_token);

-- Interview Questions
CREATE TABLE interview_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_session_id UUID NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    question_number INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50), -- technical, behavioral, situational
    difficulty VARCHAR(50), -- easy, medium, hard
    expected_keywords JSONB,
    time_limit_seconds INTEGER,
    asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(interview_session_id, question_number)
);

CREATE INDEX idx_question_session ON interview_questions(interview_session_id);
CREATE INDEX idx_question_number ON interview_questions(interview_session_id, question_number);

-- Interview Answers
CREATE TABLE interview_answers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_question_id UUID NOT NULL REFERENCES interview_questions(id) ON DELETE CASCADE,
    answer_text TEXT NOT NULL,
    confidence_score DECIMAL(5, 2), -- 0.00 to 100.00
    evaluation JSONB, -- {keywords_found: [], clarity: 0-10, relevance: 0-10, feedback: ""}
    time_taken_seconds INTEGER,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_answer_question ON interview_answers(interview_question_id);

-- Interview Reports
CREATE TABLE interview_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interview_session_id UUID NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
    overall_score DECIMAL(5, 2), -- 0.00 to 100.00
    question_scores JSONB, -- [{question_id, score, feedback}]
    strengths JSONB,
    weaknesses JSONB,
    recommendations TEXT,
    technical_score DECIMAL(5, 2),
    behavioral_score DECIMAL(5, 2),
    communication_score DECIMAL(5, 2),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_report_session ON interview_reports(interview_session_id);
CREATE INDEX idx_report_score ON interview_reports(overall_score);

-- =======================
-- MODULE INTEGRATION TABLES
-- =======================

-- Module Connectors (Links between modules)
CREATE TABLE module_connectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    source_module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    target_module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    connector_type VARCHAR(50), -- data_flow, event_trigger, api_call
    mapping_config JSONB, -- Field mappings and transformation rules
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_connector_tenant ON module_connectors(tenant_id);
CREATE INDEX idx_connector_source ON module_connectors(source_module_id);
CREATE INDEX idx_connector_target ON module_connectors(target_module_id);

-- Workflows (Automated multi-module processes)
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    steps JSONB NOT NULL, -- [{module_id, action, config, next_step}]
    trigger_type VARCHAR(50), -- manual, scheduled, event
    trigger_config JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workflow_tenant ON workflows(tenant_id);
CREATE INDEX idx_workflow_active ON workflows(is_active);

-- Workflow Executions
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    triggered_by UUID REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'running', -- running, completed, failed, cancelled
    current_step INTEGER,
    execution_log JSONB,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_execution_workflow ON workflow_executions(workflow_id);
CREATE INDEX idx_execution_tenant ON workflow_executions(tenant_id);
CREATE INDEX idx_execution_status ON workflow_executions(status);

-- =======================
-- AUDIT & LOGGING TABLES
-- =======================

-- Activity Logs
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_tenant ON activity_logs(tenant_id);
CREATE INDEX idx_logs_user ON activity_logs(user_id);
CREATE INDEX idx_logs_action ON activity_logs(action);
CREATE INDEX idx_logs_created ON activity_logs(created_at);

-- Webhooks
CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    url VARCHAR(500) NOT NULL,
    secret VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_webhooks_tenant ON webhooks(tenant_id);
CREATE INDEX idx_webhooks_event ON webhooks(event_type);

-- =======================
-- TRIGGERS & FUNCTIONS
-- =======================

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_modules_updated_at BEFORE UPDATE ON modules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_module_licenses_updated_at BEFORE UPDATE ON module_licenses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =======================
-- SAMPLE DATA (Optional)
-- =======================

-- Insert default modules
INSERT INTO modules (name, slug, description, version, category, price_onetime, price_monthly, capabilities) VALUES
('CV Analysis', 'cv-analysis', 'AI-powered CV matching and analysis for job descriptions', '1.0.0', 'Recruitment', 299.00, 49.00, 
'{"features": ["cv_parsing", "job_matching", "skill_analysis"], "api_endpoints": ["/api/cv-analysis"]}'),
('Interview Simulation', 'interview-simulation', 'AI-driven interview question generation and evaluation', '1.0.0', 'Recruitment', 399.00, 69.00,
'{"features": ["question_generation", "answer_evaluation", "interview_reports"], "api_endpoints": ["/api/interviews"]}');

-- Comments for documentation
COMMENT ON TABLE tenants IS 'Organization accounts (multi-tenant)';
COMMENT ON TABLE module_licenses IS 'Tracks which modules each tenant owns';
COMMENT ON TABLE module_connectors IS 'Defines how modules communicate with each other';
COMMENT ON TABLE workflows IS 'Automated multi-module processes';
COMMENT ON COLUMN cv_analyses.match_score IS 'Percentage match between CV and job description (0-100)';
COMMENT ON COLUMN interview_reports.overall_score IS 'Combined interview performance score (0-100)';
