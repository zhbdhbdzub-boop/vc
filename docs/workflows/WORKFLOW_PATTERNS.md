# Workflow & Integration Patterns

## Overview

This document describes the workflow patterns and module integration strategies for the Modular Platform.

---

## Communication Patterns

### 1. Orchestration Pattern
**Description:** Central workflow engine coordinates module execution.

**Use Cases:**
- Multi-step processes requiring strict ordering
- Error handling and rollback requirements
- Complex conditional logic

**Example: CV Analysis → Interview Pipeline**
```
Workflow Engine (Orchestrator)
    ↓
    1. Call CV Analysis Module
    ↓
    2. Wait for completion
    ↓
    3. Evaluate match score
    ↓
    4a. If score >= 70: Call Interview Module
    4b. If score < 70: Send rejection email
    ↓
    5. Send invitation to candidate
```

**Pros:**
- Centralized control and visibility
- Easy to debug and modify
- Clear transaction boundaries

**Cons:**
- Single point of failure
- Tighter coupling
- Orchestrator can become bottleneck

---

### 2. Choreography Pattern
**Description:** Modules react to events independently.

**Use Cases:**
- Loosely coupled modules
- Asynchronous workflows
- Eventual consistency acceptable

**Example: Event-Driven CV Analysis**
```
CV Analysis Module
    ↓ (publishes event)
cv.analysis.completed
    ↓
    ├→ Interview Module (subscribes)
    │   └→ Generates questions
    │
    ├→ Notification Service (subscribes)
    │   └→ Sends email
    │
    └→ Analytics Service (subscribes)
        └→ Updates metrics
```

**Pros:**
- High scalability
- Loose coupling
- No single point of failure

**Cons:**
- Harder to debug
- Eventual consistency complexity
- Event ordering challenges

---

### 3. Hybrid Pattern (Recommended)
Combine both: orchestration for critical paths, choreography for side effects.

**Example:**
```
Orchestrated: CV Upload → Analysis → Interview Creation
Choreographed: Analysis Completed → [Email, Analytics, Audit Log]
```

---

## Standalone Workflows

### Workflow 1: CV Analysis Only

```
┌─────────────────────────────────────────────────────┐
│  1. User Action                                     │
│  - Upload CV file (PDF/DOCX)                        │
│  - Enter job title & description                    │
│  - Specify required skills                          │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  2. Frontend Processing                             │
│  - Validate file type & size                        │
│  - Show upload progress bar                         │
│  - POST /api/cv-analysis/upload                     │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  3. API Gateway                                     │
│  - Verify JWT token                                 │
│  - Check module license active                      │
│  - Rate limit check                                 │
│  - Route to CV Analysis Service                     │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  4. CV Analysis Service                             │
│  - Create CV document record (status: pending)      │
│  - Create job description record                    │
│  - Create analysis record (status: pending)         │
│  - Upload file to S3                                │
│  - Enqueue Celery task: analyze_cv(analysis_id)    │
│  - Return 201 with analysis_id                      │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  5. Celery Worker (Background)                      │
│  a) Download CV from S3                             │
│  b) Extract text from PDF                           │
│     - Use PyPDF2 or pdfplumber                      │
│  c) Parse content with NLP                          │
│     - spaCy: Extract entities (skills, companies)   │
│     - OpenAI: Structured extraction                 │
│       Prompt: "Extract skills, experience, edu..."  │
│  d) Store extracted_data in cv_documents table      │
│  e) Index content in Elasticsearch (optional)       │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  6. Match Calculation                               │
│  a) Load job requirements from job_descriptions     │
│  b) Calculate skill match                           │
│     - Required skills found: 50% weight             │
│     - Preferred skills found: 20% weight            │
│  c) Calculate experience match                      │
│     - Years of experience: 20% weight               │
│  d) Calculate education match                       │
│     - Degree level: 10% weight                      │
│  e) Generate match_score (0-100)                    │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  7. AI Analysis & Recommendations                   │
│  - Call OpenAI GPT-4 with prompt:                   │
│    "Given CV: {cv_data} and Job: {job_data},        │
│     provide detailed analysis..."                   │
│  - Parse AI response:                               │
│    * Skill gaps                                     │
│    * Strengths                                      │
│    * Hiring recommendations                         │
│  - Store in cv_analyses.recommendations             │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  8. Finalization                                    │
│  - Update cv_analyses table:                        │
│    * status = 'completed'                           │
│    * match_score = calculated_score                 │
│    * skill_matches = match_details                  │
│    * completed_at = NOW()                           │
│  - Send WebSocket event to frontend:                │
│    {type: 'analysis_complete', id: analysis_id}     │
│  - Publish event to message bus (optional):         │
│    cv.analysis.completed                            │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  9. User Views Results                              │
│  - Frontend shows notification                      │
│  - User clicks "View Results"                       │
│  - GET /api/cv-analysis/:id/report                  │
│  - Display:                                         │
│    * Match score gauge (0-100)                      │
│    * Skill comparison table                         │
│    * Experience timeline                            │
│    * Recommendations text                           │
│  - Option to download PDF report                    │
└─────────────────────────────────────────────────────┘
```

**Processing Time:** ~20-40 seconds
**Key Metrics:**
- File upload size: Max 10MB
- Supported formats: PDF, DOCX, TXT
- Average match score: 70-75%

---

### Workflow 2: Interview Simulation Only

```
┌─────────────────────────────────────────────────────┐
│  1. User Action                                     │
│  - (Optional) Upload CV or select from library      │
│  - Enter job title & description                    │
│  - Select difficulty level (easy/medium/hard)       │
│  - Set number of questions (5-20)                   │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  2. Frontend Processing                             │
│  - Validate inputs                                  │
│  - POST /api/interviews                             │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  3. API Gateway                                     │
│  - Verify JWT & license                             │
│  - Route to Interview Service                       │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  4. Interview Service                               │
│  - Create interview_sessions record                 │
│    * status = 'scheduled'                           │
│    * session_token = random_secure_token()          │
│  - Enqueue Celery task: generate_questions()        │
│  - Return session_id + access URL                   │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  5. Question Generation (Celery Worker)             │
│  a) Load job description                            │
│  b) If CV provided: Load CV extracted data          │
│  c) Determine question types:                       │
│     - 50% Technical (role-specific)                 │
│     - 30% Behavioral (soft skills)                  │
│     - 20% Situational (problem-solving)             │
│  d) Call OpenAI API:                                │
│     Prompt: "Generate {count} interview questions   │
│              for {job_title} position.              │
│              Job description: {desc}                │
│              Difficulty: {level}                    │
│              Focus on: {extracted_skills}"          │
│  e) Parse response into structured questions        │
│  f) Store in interview_questions table              │
│     (ordered by question_number)                    │
│  g) Update session status = 'ready'                 │
│  h) Notify frontend via WebSocket                   │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  6. Interview Execution                             │
│  - User clicks "Start Interview"                    │
│  - POST /api/interviews/:id/start                   │
│  - Update status = 'in_progress'                    │
│  - Set started_at = NOW()                           │
│  - Start timer                                      │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  7. Question Loop (Repeat for each question)        │
│  a) GET /api/interviews/:id/questions?current=true  │
│  b) Display question + timer                        │
│  c) User types answer                               │
│  d) POST /api/interviews/:id/answer                 │
│     {question_id, answer_text, time_taken}          │
│  e) Backend: Evaluate answer (async)                │
│     - Call OpenAI:                                  │
│       "Evaluate this answer: {answer}               │
│        Expected: {expected_keywords}                │
│        Question: {question}"                        │
│     - Store confidence_score, feedback              │
│  f) Return next question                            │
└─────────────────────┬───────────────────────────────┘
                      │ (repeat N times)
                      ▼
┌─────────────────────────────────────────────────────┐
│  8. Interview Completion                            │
│  - POST /api/interviews/:id/complete                │
│  - Update status = 'completed'                      │
│  - Set completed_at = NOW()                         │
│  - Enqueue: generate_report(session_id)             │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  9. Report Generation (Celery Worker)               │
│  a) Load all questions + answers                    │
│  b) Calculate scores:                               │
│     - Technical score: avg(technical questions)     │
│     - Behavioral score: avg(behavioral questions)   │
│     - Communication score: clarity + relevance      │
│     - Overall score: weighted average               │
│  c) Identify strengths/weaknesses:                  │
│     - Top 3 scoring areas = strengths               │
│     - Bottom 3 scoring areas = weaknesses           │
│  d) Generate recommendations (AI):                  │
│     "Based on interview performance: {scores},      │
│      provide hiring recommendation..."              │
│  e) Store in interview_reports table                │
│  f) Publish event: interview.completed              │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  10. User Views Report                              │
│  - Frontend notification                            │
│  - GET /api/interviews/:id/report                   │
│  - Display:                                         │
│    * Overall score (large gauge)                    │
│    * Score breakdown (technical/behavioral/comm)    │
│    * Question-by-question results                   │
│    * Strengths & weaknesses                         │
│    * Recommendations                                │
│  - Option to download PDF                           │
└─────────────────────────────────────────────────────┘
```

**Processing Time:**
- Question generation: ~15-30 seconds
- Per-answer evaluation: ~3-5 seconds
- Report generation: ~10-15 seconds

---

## Combined Workflow: CV Analysis + Interview Simulation

### Integration Points

When both modules are owned, they communicate via:
1. **Database foreign key**: `interview_sessions.cv_analysis_id`
2. **Event bus**: `cv.analysis.completed` → Interview service listens
3. **Internal API**: Interview service calls CV service

### Workflow: AI-Enhanced Interview

```
┌─────────────────────────────────────────────────────┐
│  1. User Action                                     │
│  - Select "AI-Enhanced Interview" workflow          │
│  - Upload CV file                                   │
│  - Enter job description                            │
│  - Click "Start"                                    │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  2. Workflow Engine Initialization                  │
│  - Check licenses: cv-analysis ✓, interview ✓      │
│  - Check connector: cv→interview enabled            │
│  - Create workflow_execution record                 │
│  - POST /api/workflows/cv-interview/execute         │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  3. Step 1: CV Analysis                             │
│  - Execute CV Analysis workflow (see above)         │
│  - Wait for completion                              │
│  - Store analysis_id in workflow context            │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  4. Context Enrichment                              │
│  - Load CV analysis results:                        │
│    * match_score                                    │
│    * skill_matches.missing (skill gaps)             │
│    * experience_analysis                            │
│    * strengths from CV                              │
│  - Store in workflow context                        │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  5. Step 2: Enhanced Question Generation            │
│  - Create interview session                         │
│  - Link: cv_analysis_id = analysis_id               │
│  - Generate questions with CV insights:             │
│                                                      │
│    Prompt to OpenAI:                                │
│    "Generate interview questions for {job_title}.   │
│     CV Analysis Results:                            │
│     - Match Score: {score}                          │
│     - Skill Gaps: {missing_skills}                  │
│     - Strengths: {strengths}                        │
│     - Experience: {years} years                     │
│                                                      │
│     Focus questions on:                             │
│     1. Assessing missing skills: {gaps}             │
│     2. Validating claimed strengths: {strengths}    │
│     3. Appropriate difficulty for {experience}"     │
│                                                      │
│  - Result: Tailored questions targeting gaps        │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  6. Interview Execution with Context                │
│  - Each question evaluation includes CV context:    │
│                                                      │
│    Prompt to OpenAI:                                │
│    "Evaluate answer: {answer}                       │
│     Question: {question}                            │
│     Candidate Background (from CV):                 │
│     - Skills: {extracted_skills}                    │
│     - Experience: {experience}                      │
│     Expected: {expected_keywords}                   │
│                                                      │
│     Consider if answer aligns with CV claims."      │
│                                                      │
│  - Detect inconsistencies between CV and answers    │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  7. Combined Report Generation                      │
│  - Include both CV analysis and interview results   │
│  - Cross-reference:                                 │
│    * Did candidate demonstrate claimed skills?      │
│    * Skill gaps confirmed or closed?                │
│    * Experience level matches CV?                   │
│  - Enhanced recommendations:                        │
│    "Candidate's CV shows strong Python skills,      │
│     confirmed in interview with 90% score on        │
│     technical questions. However, missing           │
│     PostgreSQL knowledge (CV gap) was evident       │
│     in database design question (60% score).        │
│     Recommend: Hire with SQL training plan."        │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  8. Unified Dashboard Display                       │
│  ┌───────────────────────────────────────────────┐  │
│  │  Combined Candidate Assessment                │  │
│  ├───────────────────────────────────────────────┤  │
│  │  CV Match Score:        85%  ████████░░       │  │
│  │  Interview Score:       78%  ███████░░░       │  │
│  │  Overall Recommendation: ⭐⭐⭐⭐☆ (Strong)   │  │
│  ├───────────────────────────────────────────────┤  │
│  │  Key Insights:                                │  │
│  │  ✓ Technical skills verified                  │  │
│  │  ⚠ PostgreSQL gap confirmed (trainable)      │  │
│  │  ✓ Communication excellent                    │  │
│  │  ✓ Experience matches claims                  │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Connector Configuration

```json
{
  "connector_id": "uuid",
  "source_module": "cv-analysis",
  "target_module": "interview-simulation",
  "mapping_config": {
    "skill_gap_focus": true,
    "difficulty_adjustment": {
      "match_score_ranges": {
        "0-50": "easy",
        "51-75": "medium",
        "76-100": "hard"
      }
    },
    "question_distribution": {
      "missing_skills": 0.4,    // 40% focus on gaps
      "claimed_strengths": 0.3, // 30% verify claims
      "general_role": 0.3       // 30% standard questions
    },
    "evaluation_context": {
      "include_cv_data": true,
      "detect_inconsistencies": true
    }
  }
}
```

### Event Flow (Choreography Part)

```
CV Analysis Completed Event
    ↓
    ├→ Interview Service
    │   └→ Check if interview scheduled
    │       └→ If yes: Enrich questions with CV data
    │
    ├→ Notification Service
    │   └→ Email: "CV analysis complete, interview ready"
    │
    ├→ Analytics Service
    │   └→ Log: cv_to_interview_conversion
    │
    └→ Audit Service
        └→ Record: workflow_step_completed
```

---

## Advanced Workflows

### 1. Automated Recruitment Pipeline

```
Trigger: New CV uploaded
    ↓
Step 1: CV Analysis
    ↓
Decision: match_score >= 70?
    ├→ Yes: Continue
    └→ No: Send rejection email → End
    ↓
Step 2: Create Interview Session
    ↓
Step 3: Send Email Invitation
    ↓
Wait: Candidate completes interview
    ↓
Step 4: Generate Combined Report
    ↓
Step 5: Notify hiring manager
    ↓
Decision: overall_score >= 80?
    ├→ Yes: Send offer letter
    └→ No: Store for future positions
```

### 2. Batch Processing Workflow

```
Trigger: Admin uploads CSV of candidates
    ↓
For each row in CSV:
    ├→ Download CV from URL
    ├→ Run CV Analysis
    ├→ If score >= threshold:
    │   └→ Create interview session
    └→ Store results in batch_results table
    ↓
Generate Summary Report (Excel)
    ↓
Email to admin with results
```

### 3. Continuous Improvement Workflow

```
Trigger: Interview completed
    ↓
Step 1: Analyze interview patterns
    ├→ Which questions had lowest scores?
    ├→ Which questions took longest?
    └→ Any technical issues?
    ↓
Step 2: Update question bank
    ├→ Flag poor-performing questions
    └→ Suggest improvements (AI)
    ↓
Step 3: Update ML model training data
    └→ Feed results to improve future matching
```

---

## Error Handling

### Retry Strategy
1. **Transient errors** (API timeouts): Exponential backoff (1s, 2s, 4s, 8s)
2. **Rate limits**: Wait + retry with jitter
3. **Permanent errors**: Mark failed, notify user, manual review

### Rollback Strategy
```
CV Analysis Failed
    ↓
Cleanup:
    ├→ Delete uploaded file from S3
    ├→ Mark analysis as failed
    └→ Refund credits (if paid per-use)
    ↓
Notify user with error details
```

### Circuit Breaker
If OpenAI API fails 5 times in 60 seconds:
- Open circuit: Stop calling API
- Fallback: Use local NLP model (lower quality)
- Half-open after 5 minutes: Try one request
- Close if successful

---

## Performance Optimization

### Parallel Processing
```
CV Analysis (can parallelize):
    ├→ PDF text extraction
    ├→ Elasticsearch indexing
    └→ OpenAI skill extraction
All complete → Calculate match score
```

### Caching Strategy
- **Module capabilities**: Redis, 1-hour TTL
- **Job descriptions**: Redis, 24-hour TTL (if reused)
- **OpenAI responses**: Deduplicate similar prompts (hash-based)

### Queue Prioritization
Celery queues:
1. `high_priority`: Paid customers, small jobs
2. `normal`: Free tier, standard jobs
3. `low_priority`: Batch processing, analytics

---

## Monitoring & Observability

### Key Metrics
- **CV Analysis**: Time to complete, match score distribution
- **Interview**: Question generation time, completion rate
- **Combined**: Conversion rate (CV → Interview → Hire)

### Alerts
- Queue depth > 100: Scale workers
- Processing time > 2x average: Investigate
- Error rate > 5%: Page on-call

### Tracing
Use distributed tracing (Jaeger) to follow requests across modules:
```
Trace ID: abc-123
  ├─ API Gateway (5ms)
  ├─ CV Service (28s)
  │   ├─ S3 Upload (2s)
  │   ├─ PDF Extract (3s)
  │   ├─ OpenAI Call (18s)
  │   └─ DB Write (5s)
  └─ Return to user (1ms)
```

---

## Summary

| Pattern | Use Case | Pros | Cons |
|---------|----------|------|------|
| Orchestration | Critical paths | Control, visibility | Coupling, SPOF |
| Choreography | Side effects | Scalable, decoupled | Complex debugging |
| Hybrid | Production (recommended) | Best of both | Moderate complexity |

**Recommendation:** Start with orchestration for MVP (simpler), add choreography for scale.
