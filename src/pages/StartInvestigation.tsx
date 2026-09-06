import { PageTransition } from '../components/PageTransition';
import Sidebar from '../components/Sidebar';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchWithAuth } from '../api/apiClient';

const StartInvestigation = () => {
    const navigate = useNavigate();
    const [caseId, setCaseId] = useState('');
    const [crimeType, setCrimeType] = useState('');
    const [date, setDate] = useState('');
    const [location, setLocation] = useState('');
    const [description, setDescription] = useState('');
    const [suspectName, setSuspectName] = useState('');
    const [suspectPhone, setSuspectPhone] = useState('');
    const [suspectAddress, setSuspectAddress] = useState('');

    const handleStart = async (e: React.FormEvent) => {
        e.preventDefault();
        
        const trimmedId = caseId.trim();
        if (!trimmedId) return;

        try {
            // Build the full description combining all the fields
            const fullDescription = `Crime Type: ${crimeType}\nDate: ${date}\nLocation: ${location}\nSuspect Name: ${suspectName}\nSuspect Phone: ${suspectPhone}\nSuspect Address: ${suspectAddress}\n\nDescription:\n${description}`;

            const currentOfficer = JSON.parse(localStorage.getItem('officer') || '{}').officerId || 'OFFICER_001';

            const response = await fetchWithAuth('/api/cases', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    caseId: trimmedId,
                    title: description ? description.substring(0, 30) + "..." : "New Investigation",
                    description: fullDescription,
                    status: "ACTIVE",
                    assignedTo: currentOfficer
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || "Failed to create case");
            }

            // Save the last created case ID to localStorage for the upload screen to default to
            localStorage.setItem('currentCaseId', trimmedId);
            
            // Navigate to upload screen
            navigate('/upload');
        } catch (error: any) {
            alert(`Error creating investigation: ${error.message}`);
        }
    };

    return (
        <PageTransition>
      <div className="bg-surface text-on-surface h-screen flex flex-row font-body-md antialiased selection:bg-saffron-accent selection:text-white overflow-hidden">
            <Sidebar />

            <main className="flex-1 overflow-y-auto p-4 md:p-8">
                <div className="max-w-3xl mx-auto bg-surface-container-lowest border border-outline-variant rounded-xl shadow-sm overflow-hidden">
                    <div className="bg-primary-container text-on-primary-container p-6 border-b border-outline-variant flex items-center gap-3">
                        <span className="material-symbols-outlined text-3xl text-primary">policy</span>
                        <div>
                            <h2 className="text-title-lg font-bold">Start New Investigation</h2>
                            <p className="text-label-sm opacity-80">Enter case details to initialize the network tracking.</p>
                        </div>
                    </div>

                    <form onSubmit={handleStart} className="p-6 space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="flex flex-col gap-1">
                                <label className="text-label-sm font-bold text-on-surface">Case ID</label>
                                <input 
                                    type="text" 
                                    value={caseId} 
                                    onChange={(e) => setCaseId(e.target.value)}
                                    placeholder="Enter Case ID"
                                    required 
                                    className="px-3 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary" 
                                />
                            </div>
                            <div className="flex flex-col gap-1">
                                <label className="text-label-sm font-bold text-on-surface">Crime Type</label>
                                <select required value={crimeType} onChange={(e) => setCrimeType(e.target.value)} className="px-3 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary focus:border-primary">
                                    <option value="">Select Crime Type</option>
                                    <option value="cyber">Cybercrime</option>
                                    <option value="financial">Financial Fraud</option>
                                    <option value="narcotics">Narcotics</option>
                                    <option value="organized">Organized Crime</option>
                                </select>
                            </div>
                            <div className="flex flex-col gap-1">
                                <label className="text-label-sm font-bold text-on-surface">Date of Incident</label>
                                <input type="date" required value={date} onChange={(e) => setDate(e.target.value)} className="px-3 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary" />
                            </div>
                            <div className="flex flex-col gap-1">
                                <label className="text-label-sm font-bold text-on-surface">Location</label>
                                <input type="text" placeholder="e.g. Mumbai Port" required value={location} onChange={(e) => setLocation(e.target.value)} className="px-3 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary" />
                            </div>
                        </div>

                        <div className="flex flex-col gap-1">
                            <label className="text-label-sm font-bold text-on-surface">Case Description</label>
                            <textarea rows={4} placeholder="Brief summary of the incident..." required value={description} onChange={(e) => setDescription(e.target.value)} className="px-3 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary resize-none"></textarea>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div className="flex flex-col gap-1">
                                <label className="text-label-sm font-bold text-on-surface">Initial Suspect Name</label>
                                <input type="text" placeholder="Enter full name" value={suspectName} onChange={(e) => setSuspectName(e.target.value)} className="px-3 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary" />
                            </div>
                            <div className="flex flex-col gap-1">
                                <label className="text-label-sm font-bold text-on-surface">Initial Suspect Phone Number</label>
                                <input type="tel" placeholder="Enter phone number" value={suspectPhone} onChange={(e) => setSuspectPhone(e.target.value)} className="px-3 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary" />
                            </div>
                            <div className="flex flex-col gap-1">
                                <label className="text-label-sm font-bold text-on-surface">Initial Suspect Address</label>
                                <input type="text" placeholder="Enter address details" value={suspectAddress} onChange={(e) => setSuspectAddress(e.target.value)} className="px-3 py-2 bg-surface-container-lowest border border-outline-variant rounded-lg focus:ring-2 focus:ring-primary" />
                            </div>
                        </div>

                        <div className="pt-4 border-t border-outline-variant flex justify-end gap-4">
                            <button type="button" onClick={() => navigate('/dashboard')} className="px-6 py-2 border border-outline-variant rounded-lg font-bold hover:bg-surface-container-low">Cancel</button>
                            <button type="submit" className="px-8 py-2 bg-saffron-accent text-white rounded-lg font-bold text-lg hover:bg-opacity-90 shadow-sm flex items-center gap-2">
                                <span className="material-symbols-outlined">play_arrow</span>
                                Start Investigation
                            </button>
                        </div>
                    </form>
                </div>
            </main>
        </div>
    </PageTransition>
  );
};

export default StartInvestigation;

