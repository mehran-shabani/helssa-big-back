# Helssa Apps List

## Backend Apps
- `auth_otp` — OTP authentication with Kavenegar, token management
- `rbac` — Roles and permissions, least-privilege model
- `patient` — Patient profile, medical records, consent forms
- `doctor` — Doctor profile, schedules, shifts, dashboard
- `encounters` — Visit/session management, session state machine
- `soap` — Versioned SOAP notes with HMAC signatures
- `triage` — Symptom triage, initial differential diagnosis
- `chat` — Patient–doctor messaging/tickets, history
- `stt` — Speech-to-text (Whisper), quality control
- `ai_helsabrain` — Agent orchestrator, prompts/guardrails
- `ai_guardrails` — Policy enforcement, safety SOPs, red-flag detection
- `search` — Full-text + pgvector for session and document history
- `files` — Uploads, MinIO/S3, documents/attachments
- `exports` — Generating MD/PDF outputs, secure sharing
- `notifications` — SMS/Push/Email, templates and queues
- `payments` — Wallet/BoxMoney, subscriptions and billing
- `billing` — Invoices, transactions, financial reports
- `analytics` — Metrics, performance and quality reporting
- `audit` — Structured logs, audit trail, signatures
- `privacy` — PII/PHI redaction, data policies
- `integrations` — External integrations (TalkBot/LLM, Kavenegar, others)
- `fhir_adapter` — FHIR mapping, standard input/output
- `feedback` — Session rating and survey forms
- `checklist` — Dynamic checklists during visits, real-time alerts
- `scheduler` — Jobs, Celery/Redis, task scheduling
- `webhooks` — Event ingestion and dispatch, signatures
- `admin_portal` — Internal support and operator tools
- `api_gateway` — Unified API, versioning, rate-limiting
- `compliance` — SOPs/policies, documentation and compliance
- `devops` — Environment/secrets configuration, CI/CD

## Frontends
- `helssa_patient_app` — Flutter Web/Mobile (patient UI)
- `helssa_doctor_dashboard` — Flutter Web (doctor portal)
- `medogram_site` — React/Next (marketing and blog)

