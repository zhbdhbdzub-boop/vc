# Database Schema Documentation

## Overview

The Modular Platform uses PostgreSQL 16+ with a multi-tenant architecture. Each tenant (organization) has isolated access to their data through row-level security policies and UUID-based tenant IDs.

## Entity Relationship Diagram (ERD)

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Tenants   │◄───────►│ Tenant Users│◄───────►│    Users    │
│             │  1   N  │             │  N   1  │             │
│  - id       │         │ - tenant_id │         │  - id       │
│  - name     │         │ - user_id   │         │  - email    │
│  - slug     │         │ - role      │         │  - password │
└─────┬───────┘         └─────────────┘         └─────────────┘
      │
      │ 1
      │
      │ N
┌─────▼────────────┐
│ Module Licenses  │
│                  │         ┌─────────────┐
│  - id            │         │   Modules   │
│  - tenant_id     │◄───────►│             │
│  - module_id     │  N   1  │  - id       │
│  - license_type  │         │  - name     │
│  - is_active     │         │  - slug     │
└──────────────────┘         │  - price_*  │
                             └─────┬───────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
            ┌───────▼────┐   ┌────▼──────┐   ┌──▼──────────┐
            │ Purchases  │   │Subscriptions│  │ Module      │
            │            │   │             │   │ Connectors  │
            │ - id       │   │ - id        │   │             │
            │ - tenant_id│   │ - tenant_id │   │ - source_id │
            │ - module_id│   │ - module_id │   │ - target_id │
            │ - amount   │   │ - interval  │   │ - config    │
            │ - status   │   │ - status    │   └─────────────┘
            └────────────┘   └─────────────┘
```

## Core Tables

### Tenants
Multi-tenant root entity. Each tenant represents an organization or account.

**Key Fields:**
- `id` (UUID): Primary key
- `slug`: URL-friendly unique identifier
- `subscription_tier`: free, basic, pro, enterprise
- `max_users`: License limit for user count

**Relationships:**
- Has many: `module_licenses`, `purchases`, `subscriptions`, `cv_documents`, `interview_sessions`
- Has many through: `users` (via `tenant_users`)

### Users
Individual user accounts. Users can belong to multiple tenants.

**Key Fields:**
- `id` (UUID): Primary key
- `email`: Unique, used for authentication
- `password_hash`: Bcrypt hashed password
- `is_superuser`: Platform admin flag

**Authentication:**
- JWT tokens with 15-minute access token + 7-day refresh token
- OAuth2/OIDC support via django-allauth

### Modules
Available modules in the marketplace.

**Key Fields:**
- `slug`: Unique identifier (e.g., "cv-analysis")
- `capabilities` (JSONB): Features, API endpoints, webhooks
- `dependencies` (JSONB): Required/optional module dependencies
- `settings_schema` (JSONB): JSON Schema for configuration UI

**Pricing Model:**
- `price_onetime`: One-time purchase
- `price_monthly`: Monthly subscription
- `price_annual`: Annual subscription (typically 20% discount)
- `trial_days`: Trial period length

### Module Licenses
Tracks which modules each tenant owns and their activation status.

**License Types:**
- `trial`: 14-day trial with full features
- `purchased`: Lifetime license
- `subscription`: Recurring billing

**Key Fields:**
- `is_active`: Can be disabled without deleting
- `expires_at`: NULL for lifetime licenses
- `settings` (JSONB): Module-specific configuration

**Business Rules:**
- One license per (tenant, module) pair
- Trials auto-convert to inactive after expiration
- Subscriptions require active Stripe subscription

## CV Analysis Module Tables

### CV Documents
Stores uploaded CV files and extracted metadata.

**Key Fields:**
- `file_url`: S3/storage URL
- `extracted_text`: Full text extraction from PDF
- `extracted_data` (JSONB): Structured parsing results
  ```json
  {
    "skills": ["Python", "Django", "React"],
    "experience": [
      {
        "title": "Senior Engineer",
        "company": "TechCorp",
        "years": 3
      }
    ],
    "education": [...],
    "languages": [...]
  }
  ```

**Processing Pipeline:**
1. File upload → S3
2. PDF text extraction (PyPDF2)
3. NLP parsing (spaCy + OpenAI)
4. Structured data storage
5. Elasticsearch indexing

### Job Descriptions
Job postings for CV matching.

**Key Fields:**
- `required_skills` (JSONB): Must-have skills
- `preferred_skills` (JSONB): Nice-to-have skills
- `experience_level`: entry, mid, senior, lead

### CV Analyses
Analysis results comparing CV to job description.

**Key Fields:**
- `match_score`: 0-100 percentage match
- `skill_matches` (JSONB):
  ```json
  {
    "matched": ["Python", "Django"],
    "missing": ["Kubernetes", "AWS"],
    "extra": ["Photoshop"]
  }
  ```
- `recommendations`: AI-generated hiring advice

**Scoring Algorithm:**
1. Required skills: 50% weight
2. Preferred skills: 20% weight
3. Experience level: 20% weight
4. Education: 10% weight

## Interview Module Tables

### Interview Sessions
An interview instance for a candidate.

**Key Fields:**
- `session_token`: Unique access token for candidates
- `cv_analysis_id`: Links to CV analysis (for combined workflow)
- `status`: scheduled → in_progress → completed
- `duration_minutes`: Actual interview length

**Combined Workflow:**
When `cv_analysis_id` is set, interview questions are tailored based on:
- Skill gaps identified in CV analysis
- Candidate's experience level
- Matched/unmatched requirements

### Interview Questions
Generated questions for each session.

**Generation Logic:**
1. Extract requirements from job description
2. If CV analysis exists: prioritize skill gaps
3. Use OpenAI to generate contextual questions
4. Mix technical, behavioral, and situational questions

**Key Fields:**
- `expected_keywords` (JSONB): Answer evaluation criteria
- `time_limit_seconds`: Optional timer per question

### Interview Answers
Candidate's responses to questions.

**Evaluation:**
- OpenAI evaluates answer against expected keywords
- Scores clarity, relevance, depth
- Provides constructive feedback

### Interview Reports
Final interview assessment.

**Scoring Components:**
- `technical_score`: Technical question performance
- `behavioral_score`: Soft skills assessment
- `communication_score`: Clarity and structure
- `overall_score`: Weighted average

## Integration Tables

### Module Connectors
Defines data flow between modules.

**Connector Types:**
- `data_flow`: Pass data from module A to module B
- `event_trigger`: Module A event triggers module B action
- `api_call`: Module A calls module B API

**Example Mapping Config:**
```json
{
  "source_field": "cv_analyses.match_score",
  "target_field": "interview_sessions.difficulty_level",
  "transformation": "if match_score > 80 then 'hard' else 'medium'"
}
```

### Workflows
Multi-step automated processes.

**Example Workflow: "AI Recruitment Pipeline"**
```json
{
  "steps": [
    {
      "step": 1,
      "module": "cv-analysis",
      "action": "analyze_cv",
      "config": {"min_match_score": 70}
    },
    {
      "step": 2,
      "module": "interview-simulation",
      "action": "create_session",
      "condition": "prev_step.match_score >= 70"
    },
    {
      "step": 3,
      "module": "email-module",
      "action": "send_invitation",
      "config": {"template": "interview_invite"}
    }
  ]
}
```

## Billing Tables

### Purchases
One-time module purchases.

**Payment Flow:**
1. Create purchase record (status: pending)
2. Generate Stripe payment intent
3. Confirm payment
4. Update status to completed
5. Activate module license

### Subscriptions
Recurring billing via Stripe.

**Subscription Lifecycle:**
1. Create subscription → Stripe webhook
2. Auto-renewal → Update `current_period_end`
3. Failed payment → Stripe retry logic → Suspend license
4. Cancellation → Set `cancel_at_period_end`
5. Grace period → Final expiration

**Webhooks Handled:**
- `invoice.payment_succeeded`: Renew license
- `invoice.payment_failed`: Notify tenant
- `customer.subscription.deleted`: Deactivate license

## Indexes & Performance

### Critical Indexes
1. **Tenant-scoped queries**: All tables have `idx_*_tenant` for multi-tenant filtering
2. **Status filters**: `idx_*_status` for active/inactive/pending queries
3. **JSONB searches**: GIN indexes on `extracted_data`, `capabilities`, etc.
4. **Foreign keys**: Automatic indexes on all FK columns

### Query Optimization
- Use `SELECT DISTINCT tenant_id` for tenant discovery
- JSONB queries: `WHERE extracted_data @> '{"skills": ["Python"]}'`
- Full-text search: Use `to_tsvector` on `extracted_text` or Elasticsearch

## Security & Multi-Tenancy

### Row-Level Security (RLS)
Enable RLS policies for production:

```sql
ALTER TABLE cv_documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON cv_documents
  USING (tenant_id = current_setting('app.current_tenant')::uuid);
```

### Data Isolation
- Application-level: Django ORM filters by `tenant_id`
- Database-level: RLS policies (production)
- API-level: JWT contains tenant_id claim

### Encryption
- **At rest**: AWS RDS encryption (AES-256)
- **In transit**: TLS 1.3 for all connections
- **Passwords**: Bcrypt with 12 rounds
- **API keys**: Encrypted using `pgcrypto`

## Migration Strategy

### Phase 1: Initial Schema
- Core tables (tenants, users, modules)
- CV Analysis module tables
- Interview module tables

### Phase 2: Integrations
- Module connectors
- Workflows
- Webhooks

### Phase 3: Analytics
- Usage metrics tables
- Reporting aggregates
- Materialized views for dashboards

### Phase 4: Scale
- Partition large tables (activity_logs, cv_documents)
- Read replicas for reporting
- Time-series DB for metrics (TimescaleDB extension)

## Backup & Disaster Recovery

### Backup Strategy
- **Frequency**: Daily automated backups
- **Retention**: 30 days
- **Type**: Full + incremental
- **Storage**: S3 with versioning

### Point-in-Time Recovery
PostgreSQL WAL archiving enables PITR up to 30 days.

### Testing
- Monthly restore drills
- Automated integrity checks
- Cross-region replication (production)

## Monitoring Queries

### Check License Expirations
```sql
SELECT t.name, m.name, ml.expires_at
FROM module_licenses ml
JOIN tenants t ON ml.tenant_id = t.id
JOIN modules m ON ml.module_id = m.id
WHERE ml.expires_at < NOW() + INTERVAL '7 days'
  AND ml.is_active = true;
```

### Find Orphaned Records
```sql
SELECT COUNT(*) FROM cv_documents cd
LEFT JOIN tenants t ON cd.tenant_id = t.id
WHERE t.id IS NULL;
```

### Module Usage Statistics
```sql
SELECT m.name, COUNT(DISTINCT ml.tenant_id) as tenant_count
FROM module_licenses ml
JOIN modules m ON ml.module_id = m.id
WHERE ml.is_active = true
GROUP BY m.name
ORDER BY tenant_count DESC;
```

## Future Enhancements

1. **Audit Trail**: Immutable audit log using temporal tables
2. **Soft Deletes**: Add `deleted_at` columns for data recovery
3. **Versioning**: Track CV/job description versions
4. **Analytics Tables**: Pre-aggregated metrics for dashboards
5. **Graph Relationships**: Module dependency graph in PostgreSQL graph extension
