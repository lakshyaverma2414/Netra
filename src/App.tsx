import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import StartInvestigation from './pages/StartInvestigation';
import Upload from './pages/Upload';

// New Case-centric Entry Pages
import NetworkAnalysis from './pages/NetworkAnalysis';
import CriminalProfiling from './pages/CriminalProfiling';
import CaseTracker from './pages/CaseTracker';

// Case-centric workspaces
import CaseWorkspace from './pages/CaseWorkspace';
import GraphExplorer from './pages/GraphExplorer';
import ProfilesList from './pages/ProfilesList';
import ProfileDetail from './pages/ProfileDetail';

import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/start-investigation" element={<StartInvestigation />} />
            <Route path="/upload" element={<Upload />} />
            
            {/* Entry Points */}
            <Route path="/network-analysis" element={<NetworkAnalysis />} />
            <Route path="/criminal-profiling" element={<CriminalProfiling />} />
            <Route path="/case-tracker" element={<CaseTracker />} />
            
            {/* Old graph route redirects to new entry point */}
            <Route path="/graph-explorer" element={<Navigate to="/network-analysis" replace />} />
            
            {/* Case Workspaces */}
            <Route path="/cases/:caseId" element={<CaseWorkspace />} />
            <Route path="/cases/:caseId/network" element={<GraphExplorer />} />
            <Route path="/cases/:caseId/profiling" element={<ProfilesList />} />
            <Route path="/cases/:caseId/profiling/:profileId" element={<ProfileDetail />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
