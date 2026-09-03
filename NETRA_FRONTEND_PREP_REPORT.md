# NETRA — FRONTEND MANUAL VALIDATION PREP REPORT

## Frontend validation preparation: PASS

### Routes verified:
- `/dashboard`
- `/start-investigation`
- `/case-tracker`
- `/network-analysis` (and legacy redirect `/graph-explorer`)
- `/criminal-profiling`
- `/cases/:caseId` (Case Workspace)
- `/cases/:caseId/network` (Graph Explorer)
- `/cases/:caseId/profiling` (Profiles List)
- `/cases/:caseId/profiling/:profileId` (Profile Detail)
- Invalid case handling (e.g., `/cases/C-999/network`) successfully catches and renders a 404 "Case Not Found" page.

### Cases supported:
- **C-001**: Operation Black Web
- **C-002**: Syndicate Ghost
- **C-003**: Border Route

The frontend `cases.json`, `profiles.json`, and `sampleGraph.json` mock layers have been fully aligned to the Step 9.1 database logic. The frontend can run independently via `React -> Local Mock State -> UI` for offline demonstration.

### Graph functionality:
- Graph Explorer has been refactored to read from the local `sampleGraph.json` without failing over to `localhost:8000` (which is unavailable until Step 10).
- **Case Isolation**: Graph loads nodes/edges filtered dynamically by the `caseId` parameter in the URL.
- **Node Data & Display**: Risk scores (Critical, High, Medium, Low), Entity Types (Person, Phone, Location, Vehicle, Organization), and Node Labels render flawlessly.
- **Network Bridges**: The canonical relationship `P-003 --OWNS--> UPI-001` is strictly implemented. No `OWNED_BY` exists in the codebase.
- **Interaction**: Zoom, pan, search, entity detail panel rendering, and date-range slider bounds have been verified to not throw exceptions.

### Known limitations:
- **Upload Progress**: The upload flow in `Start Investigation` is strictly a frontend simulation using `setTimeout` state sequences, as backend ingestion is deferred to Step 10.
- **Direct Backend Connect**: API fetches are currently mocked in the React layers. It will not execute dynamic Python-driven LangGraph analytics until Spring Boot API proxy wiring.

### Console errors:
- No known console runtime exceptions. 
- All React strict-mode warnings and Typescript build-time errors (`TS6133: 'NavLink' is declared but its value is never read`) have been identified and patched. `npm run build` succeeds cleanly.

### Files changed:
- `src/mockData/cases.json`
- `src/mockData/profiles.json`
- `src/mockData/sampleGraph.json`
- `src/pages/GraphExplorer.tsx`
- `src/pages/Dashboard.tsx`
- `src/pages/StartInvestigation.tsx`
- `src/pages/ProfilesList.tsx`
- `src/pages/CaseWorkspace.tsx`
- `src/pages/ProfileDetail.tsx`

The frontend UI is technically stabilized and prepped. You can now manually inspect the React application and navigate between the 3 specific investigations in the browser.
