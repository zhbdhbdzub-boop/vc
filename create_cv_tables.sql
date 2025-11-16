-- Create missing cv_analysis tables

-- CV table
CREATE TABLE IF NOT EXISTS cv_analysis_cvs (
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    tenant_id UUID NOT NULL REFERENCES core_tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES accounts_users(id) ON DELETE CASCADE,
    file VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    file_size INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'uploaded',
    raw_text TEXT NOT NULL DEFAULT '',
    processed_at TIMESTAMP WITH TIME ZONE NULL,
    processing_error TEXT NOT NULL DEFAULT ''
);

-- CVAnalysisUsageTracker table
CREATE TABLE IF NOT EXISTS cv_analysis_usage_trackers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    tenant_id UUID NOT NULL REFERENCES core_tenants(id) ON DELETE CASCADE,
    module_type VARCHAR(50) NOT NULL,
    free_limit INTEGER NOT NULL DEFAULT 3,
    used_count INTEGER NOT NULL DEFAULT 0,
    UNIQUE(tenant_id, module_type)
);

-- ATSAnalysis table
CREATE TABLE IF NOT EXISTS ats_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    tenant_id UUID NOT NULL REFERENCES core_tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES accounts_users(id) ON DELETE CASCADE,
    cv_id UUID NOT NULL REFERENCES cv_analysis_cvs(id) ON DELETE CASCADE,
    ats_score INTEGER NOT NULL,
    keyword_matches JSONB NOT NULL DEFAULT '[]'::jsonb,
    missing_keywords JSONB NOT NULL DEFAULT '[]'::jsonb,
    quick_suggestions JSONB NOT NULL DEFAULT '[]'::jsonb,
    has_detailed_report BOOLEAN NOT NULL DEFAULT false,
    detailed_report TEXT NOT NULL DEFAULT '',
    is_free_detailed_report BOOLEAN NOT NULL DEFAULT false
);

-- CVJobMatch table
CREATE TABLE IF NOT EXISTS cv_job_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    tenant_id UUID NOT NULL REFERENCES core_tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES accounts_users(id) ON DELETE CASCADE,
    cv_id UUID NOT NULL REFERENCES cv_analysis_cvs(id) ON DELETE CASCADE,
    job_title VARCHAR(255) NOT NULL DEFAULT '',
    job_description TEXT NOT NULL,
    match_score INTEGER NOT NULL,
    matched_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
    missing_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
    matching_report TEXT NOT NULL DEFAULT '',
    recommendations JSONB NOT NULL DEFAULT '[]'::jsonb,
    is_free_match BOOLEAN NOT NULL DEFAULT false
);

-- AdvancedCVAnalysis table
CREATE TABLE IF NOT EXISTS advanced_cv_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    tenant_id UUID NOT NULL REFERENCES core_tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES accounts_users(id) ON DELETE CASCADE,
    cv_id UUID NOT NULL REFERENCES cv_analysis_cvs(id) ON DELETE CASCADE,
    full_analysis TEXT NOT NULL,
    strengths JSONB NOT NULL DEFAULT '[]'::jsonb,
    weaknesses JSONB NOT NULL DEFAULT '[]'::jsonb,
    improvement_suggestions JSONB NOT NULL DEFAULT '[]'::jsonb,
    career_recommendations JSONB NOT NULL DEFAULT '[]'::jsonb
);

-- ChatMessage table
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    analysis_id UUID NOT NULL REFERENCES advanced_cv_analyses(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ats_analyses_tenant ON ats_analyses(tenant_id);
CREATE INDEX IF NOT EXISTS idx_ats_analyses_created ON ats_analyses(created_at);
CREATE INDEX IF NOT EXISTS idx_cv_job_matches_tenant ON cv_job_matches(tenant_id);
CREATE INDEX IF NOT EXISTS idx_advanced_analyses_tenant ON advanced_cv_analyses(tenant_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_analysis ON chat_messages(analysis_id);
