# API Design Specification

## Overview

The Modular Platform exposes RESTful APIs for all operations. APIs follow OpenAPI 3.0 specification.

**Base URL:** `https://api.modularplatform.com/v1`

**Authentication:** JWT Bearer tokens

**Rate Limiting:** 
- Anonymous: 10 requests/minute
- Authenticated: 100 requests/minute
- Premium tier: 1000 requests/minute

## API Conventions

### HTTP Methods
- `GET`: Retrieve resources (idempotent)
- `POST`: Create new resources
- `PUT`: Replace entire resource
- `PATCH`: Partial update
- `DELETE`: Remove resource

### Response Format
All responses return JSON with consistent structure:

```json
{
  "data": {...},
  "meta": {
    "timestamp": "2025-11-07T12:00:00Z",
    "version": "1.0.0"
  },
  "links": {
    "self": "/api/resource/123",
    "related": "/api/related/456"
  }
}
```

### Error Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": [
      {
        "field": "email",
        "message": "Email is required"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-11-07T12:00:00Z",
    "request_id": "abc-123-def"
  }
}
```

### Status Codes
- `200 OK`: Successful GET/PUT/PATCH
- `201 Created`: Successful POST
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Missing/invalid auth
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource doesn't exist
- `409 Conflict`: Resource conflict (e.g., duplicate)
- `422 Unprocessable Entity`: Validation failed
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Pagination
List endpoints support cursor-based pagination:

```
GET /api/resources?limit=20&cursor=eyJpZCI6IjEyMyJ9
```

Response:
```json
{
  "data": [...],
  "meta": {
    "has_next": true,
    "next_cursor": "eyJpZCI6IjE0MyJ9"
  }
}
```

### Filtering & Sorting
```
GET /api/resources?filter[status]=active&sort=-created_at
```

### Field Selection (Sparse Fieldsets)
```
GET /api/resources?fields=id,name,created_at
```

---

## Authentication Endpoints

### POST /auth/register
Create new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "tenant_name": "Acme Corp"
}
```

**Response:** `201 Created`
```json
{
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    },
    "tenant": {
      "id": "uuid",
      "name": "Acme Corp",
      "slug": "acme-corp"
    },
    "tokens": {
      "access": "eyJ...",
      "refresh": "eyJ..."
    }
  }
}
```

### POST /auth/login
Authenticate user and get tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "data": {
    "user": {...},
    "tokens": {
      "access": "eyJ...",
      "refresh": "eyJ...",
      "expires_in": 900
    }
  }
}
```

### POST /auth/refresh
Refresh access token.

**Request:**
```json
{
  "refresh": "eyJ..."
}
```

**Response:** `200 OK`
```json
{
  "data": {
    "access": "eyJ...",
    "expires_in": 900
  }
}
```

### POST /auth/logout
Invalidate tokens.

**Headers:** `Authorization: Bearer <token>`

**Response:** `204 No Content`

---

## Module Marketplace API

### GET /marketplace/modules
List available modules.

**Query Params:**
- `category`: Filter by category
- `search`: Full-text search
- `sort`: `name`, `-created_at`, `price_monthly`

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "CV Analysis",
      "slug": "cv-analysis",
      "description": "AI-powered CV matching...",
      "version": "1.0.0",
      "category": "Recruitment",
      "icon_url": "https://...",
      "pricing": {
        "onetime": 299.00,
        "monthly": 49.00,
        "annual": 490.00
      },
      "trial_days": 14,
      "capabilities": ["cv_parsing", "job_matching"],
      "is_owned": false,
      "popularity": 4.5,
      "user_count": 1234
    }
  ],
  "meta": {
    "total": 2,
    "has_next": false
  }
}
```

### GET /marketplace/modules/:slug
Get module details.

**Response:** `200 OK`
```json
{
  "data": {
    "id": "uuid",
    "name": "CV Analysis",
    "slug": "cv-analysis",
    "description": "Detailed description...",
    "long_description": "Markdown content...",
    "screenshots": ["url1", "url2"],
    "video_url": "https://...",
    "pricing": {...},
    "features": [
      {
        "name": "CV Parsing",
        "description": "Extract structured data..."
      }
    ],
    "dependencies": {
      "required": [],
      "optional": ["interview-simulation"]
    },
    "reviews": {
      "average_rating": 4.5,
      "total_reviews": 89
    }
  }
}
```

---

## Purchase & Billing API

### POST /purchases
Purchase a module (one-time).

**Request:**
```json
{
  "module_id": "uuid",
  "payment_method_id": "pm_xxx" // Stripe payment method
}
```

**Response:** `201 Created`
```json
{
  "data": {
    "purchase_id": "uuid",
    "module": {...},
    "amount": 299.00,
    "currency": "USD",
    "status": "pending",
    "client_secret": "pi_xxx_secret_yyy" // Stripe confirm
  }
}
```

**3D Secure Flow:**
Client confirms payment with Stripe, then calls confirm endpoint.

### POST /purchases/:id/confirm
Confirm payment after Stripe confirmation.

**Response:** `200 OK`
```json
{
  "data": {
    "purchase_id": "uuid",
    "status": "completed",
    "license": {
      "id": "uuid",
      "module_id": "uuid",
      "license_type": "purchased",
      "activated_at": "2025-11-07T12:00:00Z",
      "expires_at": null
    }
  }
}
```

### POST /subscriptions
Subscribe to module (recurring).

**Request:**
```json
{
  "module_id": "uuid",
  "interval": "monthly", // or "annual"
  "payment_method_id": "pm_xxx"
}
```

**Response:** `201 Created`
```json
{
  "data": {
    "subscription_id": "uuid",
    "module": {...},
    "interval": "monthly",
    "amount": 49.00,
    "status": "active",
    "current_period_start": "2025-11-07T00:00:00Z",
    "current_period_end": "2025-12-07T00:00:00Z",
    "stripe_subscription_id": "sub_xxx"
  }
}
```

### POST /subscriptions/:id/cancel
Cancel subscription (at period end).

**Response:** `200 OK`
```json
{
  "data": {
    "subscription_id": "uuid",
    "status": "active",
    "cancel_at_period_end": true,
    "cancelled_at": "2025-11-07T12:00:00Z",
    "access_until": "2025-12-07T00:00:00Z"
  }
}
```

### POST /trials
Start free trial.

**Request:**
```json
{
  "module_id": "uuid"
}
```

**Response:** `201 Created`
```json
{
  "data": {
    "license": {
      "id": "uuid",
      "module_id": "uuid",
      "license_type": "trial",
      "activated_at": "2025-11-07T12:00:00Z",
      "expires_at": "2025-11-21T12:00:00Z",
      "days_remaining": 14
    }
  }
}
```

---

## Dashboard API

### GET /dashboard/modules
List user's owned modules.

**Response:** `200 OK`
```json
{
  "data": [
    {
      "license_id": "uuid",
      "module": {
        "id": "uuid",
        "name": "CV Analysis",
        "slug": "cv-analysis"
      },
      "license_type": "subscription",
      "is_active": true,
      "activated_at": "2025-11-07T12:00:00Z",
      "expires_at": "2025-12-07T00:00:00Z",
      "settings": {
        "api_enabled": true,
        "webhooks": []
      }
    }
  ]
}
```

### PATCH /dashboard/modules/:license_id
Update module settings.

**Request:**
```json
{
  "is_active": false,
  "settings": {
    "api_enabled": false,
    "max_cv_uploads": 100
  }
}
```

**Response:** `200 OK`

### GET /dashboard/analytics
Usage analytics.

**Query Params:**
- `start_date`: ISO 8601 date
- `end_date`: ISO 8601 date
- `module_id`: Filter by module

**Response:** `200 OK`
```json
{
  "data": {
    "cv_analysis": {
      "total_analyses": 145,
      "avg_match_score": 72.5,
      "analyses_by_day": [
        {"date": "2025-11-01", "count": 12},
        {"date": "2025-11-02", "count": 15}
      ]
    },
    "interview_simulation": {
      "total_sessions": 89,
      "avg_score": 78.2,
      "completion_rate": 0.87
    }
  }
}
```

---

## CV Analysis Module API

### POST /cv-analysis/upload
Upload CV and start analysis.

**Request:** `multipart/form-data`
```
file: (binary)
job_title: "Senior Python Developer"
job_description: "We are looking for..."
required_skills: ["Python", "Django", "PostgreSQL"]
experience_level: "senior"
```

**Response:** `201 Created`
```json
{
  "data": {
    "cv_id": "uuid",
    "job_id": "uuid",
    "analysis_id": "uuid",
    "status": "pending",
    "estimated_time_seconds": 30
  }
}
```

### GET /cv-analysis/:id
Get analysis status and results.

**Response:** `200 OK`
```json
{
  "data": {
    "id": "uuid",
    "cv_document": {
      "id": "uuid",
      "filename": "john_doe_cv.pdf",
      "uploaded_at": "2025-11-07T12:00:00Z",
      "extracted_data": {
        "skills": ["Python", "Django", "React", "Docker"],
        "experience": [
          {
            "title": "Senior Developer",
            "company": "TechCorp",
            "duration_years": 3,
            "skills_used": ["Python", "Django"]
          }
        ],
        "education": [
          {
            "degree": "B.S. Computer Science",
            "institution": "University",
            "year": 2015
          }
        ],
        "total_experience_years": 8
      }
    },
    "job_description": {
      "id": "uuid",
      "title": "Senior Python Developer",
      "required_skills": ["Python", "Django", "PostgreSQL"],
      "experience_level": "senior"
    },
    "match_score": 85.5,
    "status": "completed",
    "skill_matches": {
      "matched": [
        {
          "skill": "Python",
          "cv_proficiency": "expert",
          "required": true
        },
        {
          "skill": "Django",
          "cv_proficiency": "advanced",
          "required": true
        }
      ],
      "missing": [
        {
          "skill": "PostgreSQL",
          "required": true,
          "alternative_found": "MySQL"
        }
      ],
      "extra": ["React", "Docker"]
    },
    "experience_analysis": {
      "meets_requirements": true,
      "years_required": 5,
      "years_candidate": 8,
      "relevant_experience_years": 6
    },
    "recommendations": "Strong candidate with excellent Python/Django skills. Consider PostgreSQL training...",
    "created_at": "2025-11-07T12:00:00Z",
    "completed_at": "2025-11-07T12:00:28Z"
  }
}
```

### GET /cv-analysis/:id/report.pdf
Download PDF report.

**Response:** `200 OK` (Content-Type: application/pdf)

### GET /cv-analysis/history
List past analyses.

**Query Params:**
- `limit`, `cursor`: Pagination
- `min_score`: Filter by match score

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "uuid",
      "cv_filename": "candidate.pdf",
      "job_title": "Senior Developer",
      "match_score": 85.5,
      "created_at": "2025-11-07T12:00:00Z"
    }
  ]
}
```

---

## Interview Simulation Module API

### POST /interviews
Create interview session.

**Request:**
```json
{
  "cv_document_id": "uuid", // optional
  "job_description_id": "uuid",
  "cv_analysis_id": "uuid", // optional, for combined workflow
  "difficulty_level": "medium", // easy, medium, hard
  "question_count": 10,
  "duration_minutes": 45
}
```

**Response:** `201 Created`
```json
{
  "data": {
    "session_id": "uuid",
    "session_token": "abc123xyz", // for candidate access
    "status": "scheduled",
    "access_url": "https://app.modularplatform.com/interview/abc123xyz",
    "created_at": "2025-11-07T12:00:00Z"
  }
}
```

### GET /interviews/:id
Get interview session details.

**Response:** `200 OK`
```json
{
  "data": {
    "id": "uuid",
    "status": "in_progress",
    "job_title": "Senior Developer",
    "cv_filename": "candidate.pdf",
    "difficulty_level": "medium",
    "duration_minutes": 45,
    "started_at": "2025-11-07T12:00:00Z",
    "questions_total": 10,
    "questions_answered": 5,
    "time_remaining_seconds": 1350
  }
}
```

### GET /interviews/:id/questions
Get interview questions (paginated).

**Query Params:**
- `current`: Get next unanswered question

**Response:** `200 OK`
```json
{
  "data": {
    "question": {
      "id": "uuid",
      "question_number": 1,
      "question_text": "Explain the differences between Django's ORM and raw SQL queries...",
      "question_type": "technical",
      "difficulty": "medium",
      "time_limit_seconds": 300
    },
    "total_questions": 10,
    "current_number": 1
  }
}
```

### POST /interviews/:id/answer
Submit answer to question.

**Request:**
```json
{
  "question_id": "uuid",
  "answer_text": "Django ORM provides an abstraction layer...",
  "time_taken_seconds": 245
}
```

**Response:** `201 Created`
```json
{
  "data": {
    "answer_id": "uuid",
    "question_id": "uuid",
    "confidence_score": 82.5,
    "evaluation": {
      "keywords_found": ["abstraction", "SQL", "performance"],
      "clarity": 8,
      "relevance": 9,
      "feedback": "Good explanation of ORM benefits. Consider mentioning N+1 query issues."
    },
    "next_question": {
      "id": "uuid",
      "question_number": 2,
      "question_text": "..."
    }
  }
}
```

### POST /interviews/:id/complete
Complete interview session.

**Response:** `200 OK`
```json
{
  "data": {
    "session_id": "uuid",
    "status": "completed",
    "completed_at": "2025-11-07T12:45:00Z",
    "report_id": "uuid",
    "preview": {
      "overall_score": 78.5,
      "questions_answered": 10,
      "average_time_per_question": 240
    }
  }
}
```

### GET /interviews/:id/report
Get full interview report.

**Response:** `200 OK`
```json
{
  "data": {
    "id": "uuid",
    "session_id": "uuid",
    "overall_score": 78.5,
    "technical_score": 82.0,
    "behavioral_score": 75.0,
    "communication_score": 78.0,
    "question_scores": [
      {
        "question_number": 1,
        "question_text": "...",
        "score": 82.5,
        "feedback": "...",
        "time_taken": 245
      }
    ],
    "strengths": [
      "Strong technical knowledge",
      "Clear communication",
      "Good problem-solving approach"
    ],
    "weaknesses": [
      "Could improve on system design questions",
      "Time management on complex questions"
    ],
    "recommendations": "Overall strong performance. Recommended for next round...",
    "generated_at": "2025-11-07T12:45:30Z"
  }
}
```

### GET /interviews/:id/report.pdf
Download PDF report.

---

## Module Integration API

### GET /integrations/available
List available module connectors for tenant.

**Response:** `200 OK`
```json
{
  "data": [
    {
      "source_module": "cv-analysis",
      "target_module": "interview-simulation",
      "connector_type": "data_flow",
      "description": "Use CV analysis insights to tailor interview questions",
      "is_enabled": false
    }
  ]
}
```

### POST /integrations/connectors
Create module connector.

**Request:**
```json
{
  "source_module_id": "uuid",
  "target_module_id": "uuid",
  "connector_type": "data_flow",
  "mapping_config": {
    "match_score_threshold": 70,
    "use_skill_gaps": true,
    "adjust_difficulty": true
  }
}
```

**Response:** `201 Created`

### GET /workflows
List workflows.

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "AI Recruitment Pipeline",
      "description": "Automated CV analysis → Interview generation → Email invite",
      "steps": [
        {"module": "cv-analysis", "action": "analyze_cv"},
        {"module": "interview-simulation", "action": "create_session"},
        {"module": "email", "action": "send_invite"}
      ],
      "trigger_type": "manual",
      "is_active": true
    }
  ]
}
```

### POST /workflows/:id/execute
Execute workflow.

**Request:**
```json
{
  "inputs": {
    "cv_file": "base64...",
    "job_description_id": "uuid",
    "candidate_email": "candidate@example.com"
  }
}
```

**Response:** `202 Accepted`
```json
{
  "data": {
    "execution_id": "uuid",
    "workflow_id": "uuid",
    "status": "running",
    "current_step": 1
  }
}
```

---

## Internal Module API

Modules use internal APIs to communicate (not exposed publicly).

### POST /internal/events/publish
Publish event to message bus.

**Request:**
```json
{
  "event_type": "cv.analysis.completed",
  "tenant_id": "uuid",
  "data": {
    "analysis_id": "uuid",
    "match_score": 85.5
  }
}
```

### GET /internal/modules/:slug/capabilities
Get module capabilities.

**Response:**
```json
{
  "features": ["cv_parsing", "job_matching"],
  "api_endpoints": ["/api/cv-analysis/upload"],
  "webhooks": ["analysis.completed"],
  "events": {
    "published": ["cv.analysis.completed"],
    "subscribed": []
  }
}
```

---

## Webhooks

Tenants can configure webhooks for real-time notifications.

### POST /webhooks
Register webhook.

**Request:**
```json
{
  "event_type": "cv.analysis.completed",
  "url": "https://customer.com/webhook",
  "secret": "whsec_xxx" // for signature verification
}
```

### Event Payload Example
```json
{
  "event_type": "cv.analysis.completed",
  "event_id": "uuid",
  "timestamp": "2025-11-07T12:00:00Z",
  "data": {
    "analysis_id": "uuid",
    "match_score": 85.5,
    "status": "completed"
  }
}
```

**Signature:** `X-Webhook-Signature: sha256=...`

---

## Rate Limiting

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1699368000
```

**429 Response:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "retry_after": 60
  }
}
```

---

## OpenAPI Specification

Full OpenAPI 3.0 spec available at:
- **JSON**: `https://api.modularplatform.com/v1/openapi.json`
- **YAML**: `https://api.modularplatform.com/v1/openapi.yaml`
- **Interactive**: `https://api.modularplatform.com/docs`
