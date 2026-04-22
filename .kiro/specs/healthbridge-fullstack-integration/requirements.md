# Requirements Document

## Introduction

This document defines the requirements for the HealthBridge AI Full-Stack Integration feature. The feature ports four static HTML UI templates (`SymptomChecker`, `AnalysisResults`, `History`, `MedicalHistory`) into dynamic React pages and wires them to the live Express/Python backend. The result is a cohesive single-page application where symptom submission, AI-powered diagnosis, and history retrieval are all driven by real data. The patient identity is hardcoded as `"GUEST"` for this phase; no authentication infrastructure is required.

Existing files that are already complete and out of scope for implementation: `App.jsx`, `Layout.jsx`, `Home.jsx`, `api.js` (partial), `index.css`, and `server.js`.

---

## Glossary

- **SymptomChecker**: The React page at `/checker` where the user enters free-text symptoms and submits them for AI analysis.
- **AnalysisResults**: The React page at `/results` that displays the structured diagnosis result passed via React Router `location.state`.
- **History**: The React page at `/history` that fetches and renders the user's recent symptom log as a vertical timeline.
- **MedicalHistory**: The React page accessible from the History page that displays a static medical profile (conditions, medications, allergies, surgeries).
- **API_Service**: The `frontend/src/services/api.js` module that encapsulates all HTTP calls to the Express backend.
- **Express_Server**: The Node.js/Express backend running at `http://localhost:5000` (`backend/server.js`).
- **Python_Bridge**: The `api_bridge.py` script spawned by the Express server to run the AI diagnosis pipeline.
- **DiagnosisResult**: The JSON object produced by the Python pipeline and forwarded to the React frontend, containing `status`, `top_disease`, `top_score`, `urgency`, `detected_symptoms`, `report`, and related fields.
- **SymptomLogEntry**: A single row from the `symptom_log` PostgreSQL table, containing `symptom`, `weight`, `duration_days`, and `logged_at`.
- **GUEST**: The hardcoded patient identifier used for all backend requests in this phase.
- **Quick-chip**: A pre-defined symptom label button (e.g., "Fever", "Headache") that appends its text to the symptom input when clicked.

---

## Requirements

### Requirement 1: SymptomChecker Page — Input and Submission

**User Story:** As a user, I want to describe my symptoms in a free-text field and submit them for AI analysis, so that I can receive a diagnosis without navigating away from the app.

#### Acceptance Criteria

1. THE SymptomChecker SHALL render a `<textarea>` bound to a `symptomsText` state variable.
2. THE SymptomChecker SHALL render a row of quick-select chips for the labels: "Fever", "Headache", "Cough", "Nausea", "Fatigue", and "Dizziness".
3. WHEN a quick-select chip is clicked, THE SymptomChecker SHALL append the chip's label text to the current `symptomsText` value.
4. WHILE `symptomsText.trim()` is empty, THE SymptomChecker SHALL keep the submit button in a disabled state.
5. WHILE `isLoading` is true, THE SymptomChecker SHALL keep the submit button in a disabled state.
6. WHEN the user submits the form with a non-empty `symptomsText`, THE SymptomChecker SHALL call `submitDiagnosis("GUEST", symptomsText)` from the API_Service.
7. WHILE `isLoading` is true, THE SymptomChecker SHALL display a loading indicator that communicates AI processing is in progress (e.g., "Analyzing symptoms with AI…").
8. WHEN `submitDiagnosis` resolves successfully, THE SymptomChecker SHALL navigate to `/results` with the DiagnosisResult passed as `location.state`.
9. IF `submitDiagnosis` throws an error, THEN THE SymptomChecker SHALL display an inline error message: "The AI analysis failed. Please try again."
10. IF `submitDiagnosis` throws an error, THEN THE SymptomChecker SHALL preserve the current `symptomsText` value so the user does not lose their input.
11. IF `submitDiagnosis` throws an error, THEN THE SymptomChecker SHALL reset `isLoading` to `false`.

---

### Requirement 2: AnalysisResults Page — Rendering Diagnosis Output

**User Story:** As a user, I want to see a structured breakdown of my AI diagnosis after submitting symptoms, so that I can understand my potential condition, urgency level, and recommended next steps.

#### Acceptance Criteria

1. WHEN `location.state` is `null` or `undefined`, THE AnalysisResults SHALL render an empty state with the message "No analysis results found." and a link to `/checker`.
2. WHEN `location.state.status` is `"no_symptoms"`, THE AnalysisResults SHALL render the message "No symptoms were detected. Try describing your symptoms in more detail." and a link to `/checker`.
3. WHEN `location.state.status` is `"error"`, THE AnalysisResults SHALL render the error message from `location.state.message` and a link to `/checker`.
4. WHEN `location.state.status` is `"success"`, THE AnalysisResults SHALL render `top_disease` as the primary diagnosis with `top_score` displayed as an integer percentage.
5. WHEN `location.state.status` is `"success"` and `bert_suggestion` is a non-null string, THE AnalysisResults SHALL render `bert_suggestion` as a secondary match alongside `bert_confidence`.
6. WHEN `location.state.status` is `"success"`, THE AnalysisResults SHALL render each key from `detected_symptoms` as a symptom chip.
7. WHEN `location.state.status` is `"success"`, THE AnalysisResults SHALL render an urgency badge styled according to the urgency level: `LOW` uses teal (`#97f3e2`), `MEDIUM` uses amber (`#ffb694`), and `HIGH` uses red (`#ba1a1a`).
8. WHEN `location.state.status` is `"success"`, THE AnalysisResults SHALL render the `report` text in a summary section.
9. THE AnalysisResults urgency style function SHALL return a valid style object for any string value of `urgency`, defaulting to `LOW` styling for unrecognised values.
10. WHEN `location.state.status` is `"success"`, THE AnalysisResults SHALL render static "Recommended Next Steps" cards (e.g., Consult GP, Rest & Hydrate).
11. WHEN `location.state.status` is `"success"`, THE AnalysisResults SHALL render a static emergency banner with ER warning criteria.

---

### Requirement 3: History Page — Timeline and Filtering

**User Story:** As a user, I want to view my recent symptom history as a timeline, so that I can track patterns in my health over time.

#### Acceptance Criteria

1. WHEN the History page mounts, THE History SHALL call `fetchHistory("GUEST")` from the API_Service.
2. WHILE the history fetch is in progress, THE History SHALL display a loading skeleton or loading indicator.
3. WHEN `fetchHistory` resolves with a non-empty array, THE History SHALL group entries by date and render them as a vertical timeline ordered by date descending.
4. WHEN `fetchHistory` resolves with an empty array, THE History SHALL render an empty state message (e.g., "No history yet.").
5. IF `fetchHistory` throws an error, THEN THE History SHALL display the message "Could not load your history. Please check your connection." and a "Retry" button.
6. WHEN the "Retry" button is clicked, THE History SHALL re-trigger the `fetchHistory("GUEST")` call.
7. WHEN a search term is entered in the search input, THE History SHALL filter the displayed timeline entries client-side to only show entries whose `symptom` field contains the search term (case-insensitive).
8. THE History SHALL display each entry's `symptom` name, severity weight mapped to a percentage as `Math.round((weight / 7) * 100)`, and `duration_days` (displaying "Unknown" when `duration_days` is `-1`).
9. THE History SHALL render a link or button to navigate to the MedicalHistory view.
10. THE groupEntriesByDate utility SHALL produce groups whose total entry count equals the length of the input array, with no entries lost or duplicated.

---

### Requirement 4: MedicalHistory Page — Static Profile Display

**User Story:** As a user, I want to view my medical profile including chronic conditions, medications, allergies, and past surgeries, so that I have a consolidated health reference in the app.

#### Acceptance Criteria

1. THE MedicalHistory SHALL render hardcoded chronic conditions as chip tags.
2. THE MedicalHistory SHALL render a hardcoded medications list with each medication's name, dosage, frequency, and Active/Inactive status badge.
3. THE MedicalHistory SHALL render a hardcoded allergies section with each allergy's name and severity level (Severe, Moderate, or Mild).
4. THE MedicalHistory SHALL render a hardcoded past surgeries list with each surgery's date, procedure name, facility, and doctor.
5. THE MedicalHistory SHALL render an "Export Records" button in a disabled state (non-functional for this phase).
6. THE MedicalHistory SHALL render "Add" and "Edit" controls in a non-functional state for this phase.

---

### Requirement 5: API Service — HTTP Communication and Error Propagation

**User Story:** As a developer, I want the API service module to reliably communicate with the Express backend and propagate errors clearly, so that page components can handle failures without implementing HTTP logic themselves.

#### Acceptance Criteria

1. WHEN `submitDiagnosis(patientId, symptoms)` is called, THE API_Service SHALL send a `POST` request to `/api/diagnose` with a JSON body containing `patient_id` and `symptoms`.
2. WHEN the `/api/diagnose` response has HTTP status `200`, THE API_Service SHALL return the parsed JSON body as a `DiagnosisResult`.
3. IF the `/api/diagnose` response has HTTP status ≥ 400, THEN THE API_Service SHALL throw an `Error` with the message `"Diagnosis failed"`.
4. WHEN `fetchHistory(patientId)` is called, THE API_Service SHALL send a `GET` request to `/api/history/{patientId}/recent`.
5. WHEN the `/api/history/{patientId}/recent` response has HTTP status `200`, THE API_Service SHALL return the parsed JSON array of `SymptomLogEntry` objects.
6. IF the `/api/history/{patientId}/recent` response has HTTP status ≥ 400, THEN THE API_Service SHALL throw an `Error` with the message `"Failed to fetch history"`.
7. THE API_Service SHALL export a `fetchHistorySummary(patientId)` function that sends a `GET` request to `/api/history/{patientId}` and returns the parsed `HistorySummary` object on success.
8. IF the `fetchHistorySummary` response has HTTP status ≥ 400, THEN THE API_Service SHALL throw an `Error` with the message `"Failed to fetch history summary"`.

---

### Requirement 6: Application Routing and Navigation

**User Story:** As a user, I want consistent navigation between all pages of the app, so that I can move between symptom checking, results, history, and my profile without confusion.

#### Acceptance Criteria

1. THE App SHALL define routes for `/`, `/checker`, `/results`, `/history`, and `/profile` nested under the `Layout` component.
2. WHEN a user navigates to any defined route, THE Layout SHALL highlight the corresponding bottom navigation item as active.
3. WHEN a user navigates to `/results` via the SymptomChecker submit flow, THE AnalysisResults SHALL receive the DiagnosisResult in `location.state`.
4. WHEN a user navigates directly to `/results` without prior submission, THE AnalysisResults SHALL render the empty state described in Requirement 2.1.

---

### Requirement 7: Error Handling — Python Pipeline Failure

**User Story:** As a user, I want to receive a clear error message when the AI analysis fails, so that I can retry without losing my input.

#### Acceptance Criteria

1. WHEN the Express_Server receives a `POST /api/diagnose` request and the Python_Bridge process exits with a non-zero code, THE Express_Server SHALL respond with HTTP status `500` and a JSON body containing `{ "error": "Diagnosis pipeline failed.", "details": "<stderr output>" }`.
2. WHEN the Express_Server receives a `POST /api/diagnose` request and the Python_Bridge produces no valid JSON on stdout, THE Express_Server SHALL respond with HTTP status `500` and a JSON body containing `{ "error": "Invalid diagnosis response." }`.
3. IF the SymptomChecker receives an HTTP 500 response from `/api/diagnose`, THEN THE SymptomChecker SHALL display the inline error message defined in Requirement 1.9 and preserve the form state as defined in Requirements 1.10 and 1.11.

---

### Requirement 8: Data Display — Severity Weight and Duration Formatting

**User Story:** As a user, I want symptom severity and duration displayed in a human-readable format, so that I can quickly understand the significance of each logged symptom.

#### Acceptance Criteria

1. THE History SHALL map each `SymptomLogEntry.weight` value to a display percentage using the formula `Math.round((weight / 7) * 100)`, producing a value in the range [0, 100] for any weight in [1, 7].
2. WHEN `SymptomLogEntry.duration_days` is `-1`, THE History SHALL display the string "Unknown" in place of a numeric duration.
3. WHEN `SymptomLogEntry.duration_days` is a positive integer, THE History SHALL display the value followed by the label "days".
4. THE History SHALL display each entry's `logged_at` timestamp formatted as a human-readable date (e.g., "Jan 15, 2024").
