# Unified API Inventory

## doctor_chatbot
- POST /api/v1/doctors/clinical-session/start/
- GET  /api/v1/doctors/clinical-session/{session_id}/
- POST /api/v1/doctors/clinical-session/{session_id}/message/
- POST /api/v1/doctors/clinical-session/{session_id}/finalize/
- POST /api/v1/doctors/diagnosis/suggest/
- GET  /api/v1/doctors/diagnosis/icd10/search/
- POST /api/v1/doctors/prescription/check/
- GET  /api/v1/doctors/drugs/interactions/
- POST /api/v1/doctors/soap/generate/
- POST /api/v1/doctors/notes/create/
- GET  /api/v1/doctors/notes/templates/
- GET  /api/v1/doctors/guidelines/search/
- GET  /api/v1/doctors/guidelines/{guideline_id}/
- POST /api/v1/doctors/guidelines/bookmark/
- GET  /api/v1/doctors/dashboard/summary/
- GET  /api/v1/doctors/patients/list/
- GET  /api/v1/doctors/appointments/today/
- GET  /api/v1/doctors/reports/generate/

## doctor_dashboard
- GET  /api/v1/doctors/dashboard/overview/
- GET  /api/v1/doctors/dashboard/stats/today/
- GET  /api/v1/doctors/dashboard/stats/week/
- GET  /api/v1/doctors/dashboard/stats/month/
- POST /api/v1/doctors/dashboard/widgets/customize/
- GET  /api/v1/doctors/appointments/
- GET  /api/v1/doctors/appointments/today/
- GET  /api/v1/doctors/appointments/upcoming/
- POST /api/v1/doctors/appointments/{id}/status/
- GET  /api/v1/doctors/appointments/calendar/
- GET  /api/v1/doctors/patients/
- GET  /api/v1/doctors/patients/{id}/profile/
- GET  /api/v1/doctors/patients/{id}/history/
- GET  /api/v1/doctors/patients/{id}/documents/
- POST /api/v1/doctors/patients/{id}/note/
- GET  /api/v1/doctors/financial/summary/
- GET  /api/v1/doctors/financial/transactions/
- GET  /api/v1/doctors/financial/earnings/
- GET  /api/v1/doctors/financial/commissions/
- POST /api/v1/doctors/financial/withdraw/
- GET  /api/v1/doctors/analytics/performance/
- GET  /api/v1/doctors/analytics/patient-satisfaction/
- GET  /api/v1/doctors/analytics/appointment-trends/
- POST /api/v1/doctors/reports/generate/
- GET  /api/v1/doctors/reports/templates/
- GET  /api/v1/doctors/profile/
- PATCH /api/v1/doctors/profile/update/
- POST /api/v1/doctors/profile/availability/
- GET  /api/v1/doctors/settings/notifications/
- PATCH /api/v1/doctors/settings/preferences/

## patient_chatbot
- POST /api/v1/patients/chat/start/
- POST /api/v1/patients/chat/{session_id}/message/
- GET  /api/v1/patients/chat/{session_id}/history/
- POST /api/v1/patients/chat/{session_id}/end/
- POST /api/v1/patients/chat/{session_id}/voice/upload/
- GET  /api/v1/patients/chat/{session_id}/voice/response/
- GET  /api/v1/patients/chat/{session_id}/recommendations/
- GET  /api/v1/patients/doctors/recommended/
- POST /api/patient-chatbot/chat/
- GET /api/patient-chatbot/history/?page=1&limit=10
- POST /api/patient-chatbot/share/
- GET /api/patient-chatbot/shared-chats/
- GET /api/patient-chatbot/session/{session_id}/
- GET /api/patient-chatbot/health/

## soapify
- POST /api/v1/patients/chat/start/
- POST /api/v1/patients/chat/{session_id}/message/
- GET  /api/v1/patients/chat/{session_id}/history/
- POST /api/v1/patients/chat/{session_id}/end/
- POST /api/v1/patients/chat/{session_id}/voice/upload/
- GET  /api/v1/patients/chat/{session_id}/voice/response/
- GET  /api/v1/patients/chat/{session_id}/recommendations/
- GET  /api/v1/patients/doctors/recommended/
