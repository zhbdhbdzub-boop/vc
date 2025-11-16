# System Architecture Diagrams

## High-Level Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL USERS & SYSTEMS                            │
│                                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Web Users  │  │   API Users  │  │    Mobile    │  │   Webhooks   │       │
│  │   (Browser)  │  │   (Scripts)  │  │     Apps     │  │  (External)  │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                  │                  │                  │               │
└─────────┼──────────────────┼──────────────────┼──────────────────┼───────────────┘
          │                  │                  │                  │
          │                  │                  │                  │
          ▼                  ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CLOUDFLARE CDN + WAF                                   │
│                      (SSL Termination, DDoS Protection)                          │
└─────────────────────────────────────┬───────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              LOAD BALANCER (AWS ALB)                             │
│                         (Health Checks, SSL/TLS, Routing)                        │
└─────────────────────────────────────┬───────────────────────────────────────────┘
                                      │
                ┌─────────────────────┼─────────────────────┐
                │                     │                     │
                ▼                     ▼                     ▼
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│                       │  │                       │  │                       │
│   REACT FRONTEND      │  │   DJANGO API BACKEND  │  │   DJANGO API BACKEND  │
│   (Nginx + React SPA) │  │   (Gunicorn Workers)  │  │   (Gunicorn Workers)  │
│                       │  │                       │  │                       │
│   - Static Assets     │  │   - REST API          │  │   - REST API          │
│   - Service Worker    │  │   - Auth Middleware   │  │   - Auth Middleware   │
│   - PWA Manifest      │  │   - Module APIs       │  │   - Module APIs       │
│                       │  │                       │  │                       │
└───────────────────────┘  └───────────┬───────────┘  └───────────┬───────────┘
                                       │                           │
                                       └───────────┬───────────────┘
                                                   │
                    ┌──────────────────────────────┼──────────────────────────────┐
                    │                              │                              │
                    ▼                              ▼                              ▼
         ┌────────────────────┐       ┌────────────────────┐       ┌────────────────────┐
         │                    │       │                    │       │                    │
         │  CELERY WORKERS    │       │  CELERY WORKERS    │       │   CELERY BEAT      │
         │  (CV Analysis)     │       │  (Interviews)      │       │  (Scheduled Tasks) │
         │                    │       │                    │       │                    │
         │  - PDF Extraction  │       │  - Question Gen    │       │  - Trial Expiry    │
         │  - OpenAI Calls    │       │  - Answer Eval     │       │  - Subscription    │
         │  - Scoring         │       │  - Report Gen      │       │    Renewals        │
         │                    │       │                    │       │                    │
         └──────────┬─────────┘       └──────────┬─────────┘       └────────────────────┘
                    │                            │
                    └────────────┬───────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          SHARED SERVICES LAYER                                   │
│                                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐             │
│  │                  │  │                  │  │                  │             │
│  │  REDIS CLUSTER   │  │  POSTGRESQL      │  │  AWS S3          │             │
│  │                  │  │  (Primary)       │  │                  │             │
│  │  - Cache         │  │                  │  │  - CV Files      │             │
│  │  - Sessions      │  │  - All Tables    │  │  - Reports (PDF) │             │
│  │  - Celery Broker │  │  - Transactions  │  │  - Backups       │             │
│  │  - Rate Limiting │  │                  │  │                  │             │
│  │                  │  │                  │  │                  │             │
│  └──────────────────┘  └────────┬─────────┘  └──────────────────┘             │
│                                 │                                               │
│                                 ▼                                               │
│                     ┌──────────────────┐                                        │
│                     │  POSTGRESQL      │                                        │
│                     │  (Read Replicas) │                                        │
│                     │                  │                                        │
│                     │  - Analytics     │                                        │
│                     │  - Reporting     │                                        │
│                     │                  │                                        │
│                     └──────────────────┘                                        │
│                                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐             │
│  │  ELASTICSEARCH   │  │  PROMETHEUS      │  │  SENTRY          │             │
│  │                  │  │                  │  │                  │             │
│  │  - CV Search     │  │  - Metrics       │  │  - Error Track   │             │
│  │  - Full-Text     │  │  - Alerting      │  │  - Performance   │             │
│  │                  │  │                  │  │  - User Sessions │             │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICE INTEGRATIONS                            │
│                                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐             │
│  │  STRIPE API      │  │  OPENAI API      │  │  EMAIL SERVICE   │             │
│  │                  │  │                  │  │  (SendGrid/SES)  │             │
│  │  - Payments      │  │  - GPT-4o        │  │                  │             │
│  │  - Subscriptions │  │  - Embeddings    │  │  - Transactional │             │
│  │  - Webhooks      │  │  - Analysis      │  │  - Marketing     │             │
│  │                  │  │                  │  │  - Notifications │             │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Modular Monolith Internal Structure

```
┌────────────────────────────────────────────────────────────────┐
│                    DJANGO APPLICATION                          │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              API GATEWAY LAYER                           │ │
│  │  - Request Routing                                       │ │
│  │  - Authentication (JWT Middleware)                       │ │
│  │  - Rate Limiting                                         │ │
│  │  - Request/Response Logging                              │ │
│  │  - CORS Handling                                         │ │
│  └──────────────────────────────────────────────────────────┘ │
│                            │                                   │
│                            ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              CORE SERVICES LAYER                         │ │
│  │                                                          │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │ │
│  │  │   Auth     │  │  Billing   │  │  Module    │        │ │
│  │  │  Service   │  │  Service   │  │  Registry  │        │ │
│  │  │            │  │            │  │  Service   │        │ │
│  │  │ - Login    │  │ - Stripe   │  │ - License  │        │ │
│  │  │ - JWT      │  │ - Invoices │  │   Check    │        │ │
│  │  │ - RBAC     │  │ - Webhooks │  │ - Metadata │        │ │
│  │  └────────────┘  └────────────┘  └────────────┘        │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                            │                                   │
│                            ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              MODULE LAYER (PLUGINS)                      │ │
│  │                                                          │ │
│  │  ┌─────────────────────┐  ┌─────────────────────┐      │ │
│  │  │  CV Analysis Module │  │ Interview Simulation│      │ │
│  │  │                     │  │      Module         │      │ │
│  │  │  Django App:        │  │  Django App:        │      │ │
│  │  │  cv_analysis/       │  │  interview/         │      │ │
│  │  │                     │  │                     │      │ │
│  │  │  - models.py        │  │  - models.py        │      │ │
│  │  │  - views.py         │  │  - views.py         │      │ │
│  │  │  - serializers.py   │  │  - serializers.py   │      │ │
│  │  │  - tasks.py (Celery)│  │  - tasks.py (Celery)│      │ │
│  │  │  - urls.py          │  │  - urls.py          │      │ │
│  │  │                     │  │                     │      │ │
│  │  │  Endpoints:         │  │  Endpoints:         │      │ │
│  │  │  /api/cv-analysis/* │  │  /api/interviews/*  │      │ │
│  │  │                     │  │                     │      │ │
│  │  └─────────────────────┘  └─────────────────────┘      │ │
│  │                                                          │ │
│  │  ┌─────────────────────┐  ┌─────────────────────┐      │ │
│  │  │  Future Module 3    │  │  Future Module 4    │      │ │
│  │  │  (Email Campaigns)  │  │  (Candidate DB)     │      │ │
│  │  └─────────────────────┘  └─────────────────────┘      │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                            │                                   │
│                            ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │         INTEGRATION & WORKFLOW LAYER                     │ │
│  │                                                          │ │
│  │  - Module Connectors (inter-module communication)       │ │
│  │  - Workflow Engine (orchestration)                      │ │
│  │  - Event Bus (Celery signals or Redis pub/sub)         │ │
│  │  - Internal APIs (module-to-module)                     │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                            │                                   │
│                            ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              DATA ACCESS LAYER                           │ │
│  │                                                          │ │
│  │  - Django ORM                                            │ │
│  │  - Query Optimization                                    │ │
│  │  - Multi-Tenancy Filters                                 │ │
│  │  - Caching (Redis)                                       │ │
│  │  - Connection Pooling                                    │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

---

## Module Communication Patterns

### Pattern 1: Direct API Call (Synchronous)

```
┌─────────────────┐         ┌─────────────────┐
│   CV Analysis   │   HTTP  │   Interview     │
│     Module      ├────────►│   Simulation    │
│                 │         │     Module      │
│  GET /internal/ │         │                 │
│  cv-analysis/:id│         │  Uses insights  │
│                 │◄────────┤  for questions  │
└─────────────────┘  JSON   └─────────────────┘
```

### Pattern 2: Event-Driven (Asynchronous)

```
┌─────────────────┐         ┌─────────────────┐
│   CV Analysis   │         │   Event Bus     │
│     Module      │         │  (Redis/Celery) │
│                 │         │                 │
│  Analysis Done  ├────────►│  Publish Event  │
│                 │         │  "cv.completed" │
└─────────────────┘         └────────┬────────┘
                                     │
                                     │ Subscribe
                                     ▼
                            ┌─────────────────┐
                            │   Interview     │
                            │   Simulation    │
                            │                 │
                            │  Consume Event  │
                            │  Generate Qs    │
                            └─────────────────┘
```

### Pattern 3: Orchestrated Workflow

```
┌─────────────────────────────────────────────────┐
│          Workflow Engine (Orchestrator)         │
│                                                 │
│  Step 1: Call CV Analysis                      │
│  ────────► Wait for completion                 │
│  Step 2: If score >= 70, Call Interview Gen    │
│  ────────► Wait for completion                 │
│  Step 3: Send Email to Candidate               │
│                                                 │
└─────────────────────────────────────────────────┘
         │                     │                │
         ▼                     ▼                ▼
  ┌────────────┐       ┌────────────┐   ┌────────────┐
  │ CV Module  │       │ Interview  │   │   Email    │
  │            │       │  Module    │   │   Module   │
  └────────────┘       └────────────┘   └────────────┘
```

---

## Data Flow: CV Analysis Workflow

```
User              Frontend          API Gateway       CV Service        Celery Worker      OpenAI        Database
 │                   │                   │                │                   │              │              │
 │ Upload CV         │                   │                │                   │              │              │
 ├──────────────────►│                   │                │                   │              │              │
 │                   │ POST /cv-analysis │                │                   │              │              │
 │                   ├──────────────────►│                │                   │              │              │
 │                   │                   │ Verify JWT     │                   │              │              │
 │                   │                   │ Check License  │                   │              │              │
 │                   │                   ├───────────────►│                   │              │              │
 │                   │                   │                │ Upload to S3      │              │              │
 │                   │                   │                │ Create Records    │              │              │
 │                   │                   │                ├──────────────────────────────────────────────►│
 │                   │                   │                │                   │              │              │
 │                   │                   │                │ Enqueue Task      │              │              │
 │                   │                   │                ├──────────────────►│              │              │
 │                   │ 201 Created       │                │                   │              │              │
 │                   │ {analysis_id}     │                │                   │              │              │
 │                   │◄──────────────────┤                │                   │              │              │
 │ Show "Processing" │                   │                │                   │              │              │
 │◄──────────────────┤                   │                │                   │              │              │
 │                   │                   │                │                   │ Extract Text │              │
 │                   │                   │                │                   │ from PDF     │              │
 │                   │                   │                │                   │              │              │
 │                   │                   │                │                   │ Call OpenAI  │              │
 │                   │                   │                │                   ├─────────────►│              │
 │                   │                   │                │                   │              │ Extract      │
 │                   │                   │                │                   │              │ Skills       │
 │                   │                   │                │                   │◄─────────────┤              │
 │                   │                   │                │                   │              │              │
 │                   │                   │                │                   │ Calculate    │              │
 │                   │                   │                │                   │ Match Score  │              │
 │                   │                   │                │                   │              │              │
 │                   │                   │                │                   │ Update DB    │              │
 │                   │                   │                │                   ├─────────────────────────────►│
 │                   │                   │                │                   │              │              │
 │                   │                   │                │                   │ WebSocket    │              │
 │                   │◄────────────────────────────────────────────────────────analysis_complete            │
 │ Notification      │                   │                │                   │              │              │
 │◄──────────────────┤                   │                │                   │              │              │
 │                   │                   │                │                   │              │              │
 │ View Results      │                   │                │                   │              │              │
 ├──────────────────►│ GET /analysis/:id │                │                   │              │              │
 │                   ├──────────────────►├───────────────►│                   │              │              │
 │                   │                   │                │ Query DB          │              │              │
 │                   │                   │                ├──────────────────────────────────────────────►│
 │                   │                   │                │◄─────────────────────────────────────────────────┤
 │                   │ Results + Score   │                │                   │              │              │
 │ Display Report    │◄──────────────────┤                │                   │              │              │
 │◄──────────────────┤                   │                │                   │              │              │
```

---

## Deployment Architecture (AWS)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            AWS CLOUD (US-EAST-1)                             │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                          VPC (10.0.0.0/16)                             │ │
│  │                                                                        │ │
│  │  ┌──────────────────────────────────────────────────────────────────┐ │ │
│  │  │                 Public Subnet (10.0.1.0/24)                      │ │ │
│  │  │                                                                  │ │ │
│  │  │  ┌─────────────────┐      ┌─────────────────┐                  │ │ │
│  │  │  │  ALB            │      │  NAT Gateway    │                  │ │ │
│  │  │  │  (Load Balancer)│      │                 │                  │ │ │
│  │  │  └────────┬────────┘      └─────────────────┘                  │ │ │
│  │  │           │                                                     │ │ │
│  │  └───────────┼─────────────────────────────────────────────────────┘ │ │
│  │              │                                                       │ │
│  │  ┌───────────┼───────────────────────────────────────────────────┐ │ │
│  │  │           │      Private Subnet (10.0.2.0/24)                 │ │ │
│  │  │           ▼                                                    │ │ │
│  │  │  ┌─────────────────┐      ┌─────────────────┐                │ │ │
│  │  │  │  ECS Service    │      │  ECS Service    │                │ │ │
│  │  │  │  (API)          │      │  (Workers)      │                │ │ │
│  │  │  │                 │      │                 │                │ │ │
│  │  │  │  - Task 1       │      │  - Worker 1     │                │ │ │
│  │  │  │  - Task 2       │      │  - Worker 2     │                │ │ │
│  │  │  │  - Task 3       │      │  - Worker 3     │                │ │ │
│  │  │  └─────────────────┘      └─────────────────┘                │ │ │
│  │  │                                                                │ │ │
│  │  └────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                      │ │
│  │  ┌────────────────────────────────────────────────────────────────┐ │ │
│  │  │           Private Subnet (10.0.3.0/24) - Data Tier            │ │ │
│  │  │                                                                │ │ │
│  │  │  ┌─────────────────┐      ┌─────────────────┐                │ │ │
│  │  │  │  RDS PostgreSQL │      │  ElastiCache    │                │ │ │
│  │  │  │  (Multi-AZ)     │      │  (Redis)        │                │ │ │
│  │  │  │                 │      │                 │                │ │ │
│  │  │  │  Primary +      │      │  Cluster Mode   │                │ │ │
│  │  │  │  Read Replica   │      │                 │                │ │ │
│  │  │  └─────────────────┘      └─────────────────┘                │ │ │
│  │  │                                                                │ │ │
│  │  └────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                      External Services                             │  │
│  │                                                                    │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │  │
│  │  │     S3      │  │ CloudFront  │  │   Route53   │              │  │
│  │  │  (Storage)  │  │    (CDN)    │  │    (DNS)    │              │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Security Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                           │
│                                                              │
│  Layer 1: Network Security                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  - CloudFlare WAF (DDoS, Bot Protection)              │ │
│  │  - VPC Security Groups (Firewall Rules)               │ │
│  │  - Private Subnets for Data Tier                      │ │
│  │  - NAT Gateway for Outbound Traffic                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Layer 2: Application Security                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  - JWT Authentication (15min expiry)                  │ │
│  │  - OAuth2/OIDC for Social Login                       │ │
│  │  - RBAC (Role-Based Access Control)                   │ │
│  │  - CSRF Protection (Django Middleware)                │ │
│  │  - XSS Protection (Content Security Policy)           │ │
│  │  - Rate Limiting (per user, per endpoint)             │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Layer 3: Data Security                                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  - Encryption at Rest (RDS: AES-256)                  │ │
│  │  - Encryption in Transit (TLS 1.3)                    │ │
│  │  - Row-Level Security (Multi-Tenancy)                 │ │
│  │  - Password Hashing (Bcrypt, 12 rounds)               │ │
│  │  - Secrets Management (AWS Secrets Manager)           │ │
│  │  - Database Backups (Encrypted, 30-day retention)     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  Layer 4: Compliance                                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  - GDPR Compliance (Data Deletion, Consent)           │ │
│  │  - SOC 2 Type II (Audit Trail, Access Logs)           │ │
│  │  - PCI DSS (Stripe handles card data)                 │ │
│  │  - Activity Logging (All API calls, user actions)     │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## Scalability Strategy

```
Stage 1: MVP (< 1,000 users)
┌────────────────────────────────────────┐
│  Single ECS Task (API)                │
│  Single Worker                         │
│  RDS: db.t3.small                      │
│  Redis: cache.t3.micro                 │
└────────────────────────────────────────┘

Stage 2: Growth (1,000 - 10,000 users)
┌────────────────────────────────────────┐
│  3 ECS Tasks (API) + Auto-scaling     │
│  3 Workers + Auto-scaling              │
│  RDS: db.t3.medium + Read Replica      │
│  Redis: cache.m5.large (cluster)       │
│  Elasticsearch: 3-node cluster         │
└────────────────────────────────────────┘

Stage 3: Scale (10,000 - 100,000 users)
┌────────────────────────────────────────┐
│  10+ ECS Tasks (API)                   │
│  10+ Workers (multiple queues)         │
│  RDS: db.r5.xlarge + 2 Read Replicas   │
│  Redis: cache.r5.xlarge (cluster)      │
│  Elasticsearch: 5-node cluster         │
│  CloudFront CDN for static assets      │
└────────────────────────────────────────┘

Stage 4: Enterprise (100,000+ users)
┌────────────────────────────────────────┐
│  Kubernetes (EKS) with 20+ pods        │
│  Microservices architecture            │
│  RDS: db.r5.4xlarge Multi-AZ            │
│  Aurora Serverless (read scaling)      │
│  Redis: r6g.2xlarge cluster            │
│  Elasticsearch: 10+ node cluster       │
│  Multi-region deployment (DR)          │
└────────────────────────────────────────┘
```

---

This architecture provides:
✅ **Scalability:** Horizontal scaling at every tier
✅ **Security:** Defense in depth, multiple security layers
✅ **Reliability:** Multi-AZ, redundancy, automated backups
✅ **Performance:** Caching, CDN, read replicas, async processing
✅ **Modularity:** Clear separation of concerns, plugin architecture
✅ **Observability:** Centralized logging, metrics, tracing
