# Implementation Plan: HealthBridge AI Full-Stack Integration

## Overview

Implement the four remaining React pages (`SymptomChecker`, `AnalysisResults`, `History`, `MedicalHistory`), extend the API service, configure the test stack, and write property-based tests. All tasks build incrementally — each step integrates into the running app before the next begins. The implementation language is JavaScript/JSX (React 19 + Vite).

## Tasks

- [x] 1. Extend API service with `fetchHistorySummary`
  - Open `frontend/src/services/api.js` and add the `fetchHistorySummary(patientId)` export
  - Send a `GET` request to `${API_BASE_URL}/history/${patientId}`
  - Throw `Error("Failed to fetch history summary")` on any non-ok response
  - Return the parsed JSON body (`{ summary, total_days_sick }`) on success
  - _Requirements: 5.7, 5.8_

- [x] 2. Add MedicalHistory route to App.jsx
  - Import `MedicalHistory` from `./pages/MedicalHistory` in `frontend/src/App.jsx`
  - Add a nested `<Route path="history/medical" element={<MedicalHistory />} />` inside the Layout route
  - _Requirements: 6.1_

- [x] 3. Implement `SymptomChecker.jsx`
  - [x] 3.1 Create `frontend/src/pages/SymptomChecker.jsx` with state and form skeleton
    - Declare `symptomsText`, `isLoading`, and `error` state variables using `useState`
    - Render a `<textarea>` bound to `symptomsText` with an `onChange` handler
    - Define the `QUICK_CHIPS` constant: `["Fever", "Headache", "Cough", "Nausea", "Fatigue", "Dizziness"]`
    - Render a chip row; each chip's `onClick` appends its label to `symptomsText` (with a space separator when text is non-empty)
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 3.2 Implement submit handler and loading/error states
    - Implement `handleSubmit`: call `submitDiagnosis("GUEST", symptomsText)`, set `isLoading` true before the call, reset it in a `finally` block
    - On success: `navigate("/results", { state: result })`
    - On error: set `error` to `"The AI analysis failed. Please try again."` — do not clear `symptomsText`
    - Disable the submit button when `symptomsText.trim() === ""` or `isLoading === true`
    - Show a loading message (e.g., `"Analyzing symptoms with AI…"`) while `isLoading` is true
    - Render the `error` string as an inline error message when non-null
    - _Requirements: 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 7.3_

  - [ ]* 3.3 Write property tests for SymptomChecker submit-button guard (Property 1)
    - **Property 1: Submit button is disabled for any whitespace-only input**
    - Use `fc.string()` filtered to whitespace-only values; assert button has `disabled` attribute
    - **Validates: Requirements 1.4**

  - [ ]* 3.4 Write property test for quick-chip append (Property 2)
    - **Property 2: Quick-chip click always appends to symptomsText**
    - Use `fc.string()` for initial text and `fc.constantFrom(...QUICK_CHIPS)` for chip label; assert resulting text contains the chip label
    - **Validates: Requirements 1.3**

  - [ ]* 3.5 Write property test for error state preserving form input (Property 3)
    - **Property 3: Error state preserves form input**
    - For any non-empty `symptomsText`, mock `submitDiagnosis` to throw; assert `symptomsText` is unchanged and `isLoading` is `false` after the error
    - **Validates: Requirements 1.10, 1.11**

- [x] 4. Checkpoint — Ensure SymptomChecker works end-to-end
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement `AnalysisResults.jsx`
  - [x] 5.1 Create `frontend/src/pages/AnalysisResults.jsx` with state-routing logic
    - Read `location.state` via `useLocation()`
    - If `location.state` is `null` or `undefined`: render `"No analysis results found."` with a `<Link to="/checker">`
    - If `location.state.status === "no_symptoms"`: render `"No symptoms were detected. Try describing your symptoms in more detail."` with a `<Link to="/checker">`
    - If `location.state.status === "error"`: render `location.state.message` with a `<Link to="/checker">`
    - _Requirements: 2.1, 2.2, 2.3, 6.4_

  - [x] 5.2 Implement success state rendering
    - Render `top_disease` as the primary diagnosis heading with `top_score` displayed as `Math.round(top_score)` + `%`
    - Render `bert_suggestion` as a secondary match alongside `bert_confidence` when `bert_suggestion` is a non-null string
    - Render each key from `detected_symptoms` as a symptom chip
    - Render the `report` text in a summary section
    - Render static "Recommended Next Steps" cards (Consult GP, Rest & Hydrate)
    - Render a static emergency banner with ER warning criteria
    - _Requirements: 2.4, 2.5, 2.6, 2.8, 2.10, 2.11_

  - [x] 5.3 Implement urgency badge with `getUrgencyStyle`
    - Define `URGENCY_COLORS` map: `LOW → #97f3e2` (teal), `MEDIUM → #ffb694` (amber), `HIGH → #ba1a1a` (red)
    - Implement `getUrgencyStyle(urgency)` returning `URGENCY_COLORS[urgency] ?? URGENCY_COLORS.LOW`
    - Render the urgency badge using the returned style object's `bg`, `text`, and `border` classes
    - _Requirements: 2.7, 2.9_

  - [ ]* 5.4 Write property test for urgency style mapping totality (Property 4)
    - **Property 4: Urgency style mapping is total**
    - Use `fc.string()` to generate arbitrary urgency strings; assert `getUrgencyStyle` always returns an object with `bg`, `text`, and `border` fields — never `undefined` or `null`
    - **Validates: Requirements 2.7, 2.9**

  - [ ]* 5.5 Write property test for top_score rendering bounds (Property 5)
    - **Property 5: Success result renders top_disease and top_score**
    - Use `fc.integer({ min: 0, max: 100 })` for `top_score`; assert the rendered percentage is always an integer in [0, 100]
    - **Validates: Requirements 2.4**

- [x] 6. Checkpoint — Ensure AnalysisResults works end-to-end
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement `History.jsx`
  - [x] 7.1 Create `frontend/src/pages/History.jsx` with fetch-on-mount and state
    - Declare `entries`, `isLoading`, `error`, and `searchTerm` state variables
    - On mount, call `fetchHistory("GUEST")` and store results in `entries`; set `isLoading` true before the call, false after
    - On error, set `error` to `"Could not load your history. Please check your connection."`
    - Render a loading skeleton (e.g., pulsing placeholder divs) while `isLoading` is true
    - _Requirements: 3.1, 3.2_

  - [x] 7.2 Implement `groupEntriesByDate` utility and timeline rendering
    - Implement `groupEntriesByDate(entries)` inline: iterate entries, key by `new Date(entry.logged_at).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" })`, sort groups by date descending
    - Render each date group as a timeline section with a date heading
    - For each entry render: `symptom` name, severity as `Math.round((weight / 7) * 100)` + `%`, and duration as `"Unknown"` when `duration_days === -1` or `duration_days` + `" days"` otherwise
    - Format `logged_at` as a human-readable date (e.g., `"Jan 15, 2024"`)
    - _Requirements: 3.3, 3.8, 8.1, 8.2, 8.3, 8.4_

  - [x] 7.3 Implement empty state, error/retry, search, and MedicalHistory link
    - Render `"No history yet."` empty state when `entries` is empty and not loading
    - Render the error message and a "Retry" button that re-calls `fetchHistory("GUEST")` when `error` is non-null
    - Render a search `<input>` bound to `searchTerm`; filter displayed entries client-side so only entries whose `symptom` contains `searchTerm` (case-insensitive) are shown
    - Render a `<Link to="/history/medical">` button to navigate to MedicalHistory
    - _Requirements: 3.4, 3.5, 3.6, 3.7, 3.9_

  - [ ]* 7.4 Write property test for date grouping invariant (Property 7)
    - **Property 7: Date grouping preserves all entries**
    - Use `fc.array(fc.record({ symptom: fc.string(), weight: fc.integer({ min: 1, max: 7 }), duration_days: fc.integer({ min: -1, max: 365 }), logged_at: fc.date().map(d => d.toISOString()) }))` to generate arbitrary entry arrays; assert total count across all groups equals input array length
    - **Validates: Requirements 3.3, 3.10**

  - [ ]* 7.5 Write property test for client-side search filter correctness (Property 8)
    - **Property 8: Client-side search filter is correct**
    - Use `fc.array(fc.record({ symptom: fc.string(), ... }))` and `fc.string()` for search term; assert filtered result contains exactly those entries whose `symptom` includes the search term (case-insensitive), no more and no less
    - **Validates: Requirements 3.7**

  - [ ]* 7.6 Write property test for severity weight percentage bounds (Property 9)
    - **Property 9: Severity weight percentage is bounded**
    - Use `fc.integer({ min: 1, max: 7 })` for weight; assert `Math.round((weight / 7) * 100)` is always in [0, 100]
    - **Validates: Requirements 8.1**

- [x] 8. Checkpoint — Ensure History works end-to-end
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implement `MedicalHistory.jsx`
  - [x] 9.1 Create `frontend/src/pages/MedicalHistory.jsx` with hardcoded data
    - Define a `MEDICAL_PROFILE` constant with hardcoded `conditions`, `medications`, `allergies`, and `surgeries` arrays matching the design interfaces
    - Render chronic conditions as teal chip tags
    - Render medications list with name, dosage, frequency, and Active/Inactive status badge
    - _Requirements: 4.1, 4.2_

  - [x] 9.2 Render allergies, surgeries, and non-functional controls
    - Render allergies section with each allergy's name and severity level (Severe/Moderate/Mild) with severity-coded styling
    - Render past surgeries list with date, procedure name, facility, and doctor
    - Render a disabled `"Export Records"` button (`disabled` attribute set)
    - Render `"Add"` and `"Edit"` buttons in a non-functional state (no `onClick` handlers or handlers that are no-ops)
    - _Requirements: 4.3, 4.4, 4.5, 4.6_

- [x] 10. Install test dependencies and configure Vitest
  - Run `npm install -D fast-check @testing-library/react @testing-library/user-event vitest jsdom` in `frontend/`
  - Update `frontend/vite.config.js` to add a `test` block: `{ globals: true, environment: "jsdom", setupFiles: "./src/test/setup.js" }`
  - Create `frontend/src/test/setup.js` importing `@testing-library/jest-dom` for extended matchers
  - Add `"test": "vitest --run"` to the `scripts` section of `frontend/package.json`
  - _Requirements: (testing infrastructure for all property tests above)_

  - [ ]* 10.1 Write property test for API error propagation (Property 10)
    - **Property 10: API throws for any HTTP error status**
    - Use `fc.integer({ min: 400, max: 599 })` to generate error status codes; mock `fetch` to return a response with that status; assert both `submitDiagnosis` and `fetchHistory` throw rather than resolve
    - **Validates: Requirements 5.3, 5.6**

- [x] 11. Final checkpoint — Ensure all tests pass
  - Run `npm run test` in `frontend/` and confirm all property-based and unit tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at each major milestone
- Property tests validate universal correctness properties using `fast-check`
- Unit tests validate specific examples and edge cases
- The `MedicalHistory` route is `/history/medical` (nested under the existing Layout route)
- All pages use the existing Tailwind V4 design tokens from `index.css` — no new CSS variables needed
- Visual references for each page are in `Healthbridge_Ai_UI/` — match the dark glassmorphism aesthetic
