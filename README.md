# NCRB AI Portal - Investigation & Network Analysis

Welcome to the **NCRB AI Portal**, an advanced, case-centric dashboard designed for law enforcement to manage investigations, map criminal networks, and generate behavioral profiles.

This document serves as a comprehensive guide for the development team to understand the architecture, data flow, and key features of the application.

---

## 📌 Project Architecture (Case-Centric Model)
The core philosophy of this portal is **Case-Centric Isolation**. All data, networks, and evidence are strictly bound to a manually defined `Case ID` (e.g., `NCRB-2026-001`). 

The application routing is built around this rule:
1. Users search or select a case.
2. The user enters a dedicated "Case Workspace" (`/cases/:caseId`).
3. All subsequent modules (Network Analysis, Profiling, Evidence) pull the `:caseId` from the URL parameters (`useParams`) and filter their respective datasets to show **only** information relevant to that specific investigation.

---

## 🚀 Key Features

### 1. Dashboard & Global Case Search
* **Search Engine:** A robust search bar (using HTML forms for native accessibility) located on the Dashboard. 
* **Case Summaries:** Searching a Case ID pulls metadata and instantly displays a comprehensive summary card showing Crime Type, Assignee, Final Results (if solved), and key suspects.
* **Navigation:** From the summary, investigators can directly transition into module-specific views (like Network Analysis) via the **View & Explore** link.

### 2. Start New Investigation
* **Manual Case ID:** Auto-generation is disabled. Investigators manually define the Case ID to match physical records.
* **Duplicate Prevention:** The form checks existing datasets to prevent overwriting or duplicating active case IDs.
* **Persistent Storage:** New cases are saved to browser `localStorage` and instantly merged with static mock data, maintaining a seamless SPA experience.

### 3. Network Analysis (Graph Explorer)
* **Visualizing Crime:** Uses `react-cytoscapejs` to draw highly interactive force-directed graphs (Nodes = Suspects/Phones/Locations, Edges = Relationships).
* **Data Binding:** The graph securely filters the global `sampleGraph.json` dataset, rendering exactly the entities tied to the active Case ID in the URL. 
* **Empty States:** If an investigation is brand new and has no network data, a clean "No connected entities available" fallback UI is displayed rather than a broken or generic graph.

### 4. Criminal Profiling & AI Chatbot
* **Suspect Deep-Dives:** Detailed behavioral analysis screens for flagged entities.
* **Global Assistant:** A floating `Chatbot` component available across the app (animated with `framer-motion`) to provide context-aware AI assistance without breaking the investigator's flow.

---

## 🏗 Tech Stack

* **Core Framework:** React 18, TypeScript, Vite
* **Routing:** React Router DOM v6
* **Styling:** Tailwind CSS (Custom Design System with Material Design 3 surface colors)
* **Data Visualization:** Cytoscape.js (`react-cytoscapejs`), Recharts
* **Animations:** Framer Motion (`framer-motion`)
* **Icons:** Google Material Symbols

---

## 📂 Folder Structure

```text
src/
├── components/          # Reusable UI (Sidebar, Skeleton loaders, Chatbot, PageTransitions)
├── mockData/            # JSON databases simulating backend responses
│   ├── cases.json       # Core investigations database
│   ├── profiles.json    # Suspect/criminal profiles
│   └── sampleGraph.json # Node/Edge definitions for Network Analysis
├── pages/               # Route-level components
│   ├── Dashboard.tsx          # Main entry, search, analytics
│   ├── StartInvestigation.tsx # Creation form
│   ├── NetworkAnalysis.tsx    # Case selection for graphs
│   └── GraphExplorer.tsx      # Cytoscape integration (URL: /cases/:caseId/network)
├── App.tsx              # Router definition
└── main.tsx             # React DOM mount point
```

---

## 🔄 Data Flow (Mock Backend)

Because this project currently operates as a frontend SPA without a live backend database, data flow is managed as follows:

1. **Static Mock Data:** Read-only global data is imported from `src/mockData/`.
2. **Dynamic Creation:** When an investigator creates a new case, it is serialized and saved to `localStorage.getItem('userCases')`.
3. **Merging State:** Pages like `Dashboard.tsx` combine these sources dynamically: `[...cases, ...localCases]`.
4. **Graph Synchronization:** Cytoscape elements share the same IDs across files. A node in `sampleGraph.json` belongs to a case because of its `data.caseId` attribute. 

---

## 💻 Local Development Setup

To run the project locally, run the following commands in your terminal:

```bash
# 1. Install dependencies
npm install

# 2. Start the development server (with Hot Module Replacement)
npm run dev
```

*Note: Avoid using `npm run preview` during active development, as it serves static compiled files from `/dist` and bypasses Hot-Module Replacement (HMR). Always use `npm run dev`.*

---

## 🐛 Common Development Notes / Troubleshooting
* **Click Events & Routing:** When creating new buttons that navigate between routes, prefer React Router's native `<Link to="...">` or `<form onSubmit={...}>` over raw `onClick={navigate}` to avoid browser-level event swallowing.
* **State Updates:** Ensure that when updating network elements, you provide a strict equality check (`===`) against the `useParams().caseId` string.
* **Tailwind Safelisting:** The project uses specific semantic color variables (`bg-primary`, `text-on-surface`). Ensure any new UI components strictly follow these utility classes rather than hardcoded hex colors.
