import { useState } from 'react';
import { fetchWithAuth } from '../api/apiClient';

interface ChatbotProps {
    caseId?: string;
}

const Chatbot = ({ caseId }: ChatbotProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState("");
    const [messages, setMessages] = useState<Array<{role: string, text: string, trace?: any}>>([
        { role: 'assistant', text: "Hello Investigator. What would you like to know about this case?" }
    ]);
    const [isLoading, setIsLoading] = useState(false);
    const [threadId, setThreadId] = useState<string | null>(null);

    const handleSend = async () => {
        if (!query.trim()) return;
        
        const userMsg = { role: 'user', text: query };
        setMessages(prev => [...prev, userMsg]);
        setQuery("");
        setIsLoading(true);

        try {
            const res = await fetchWithAuth('/api/v1/investigations/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    case_id: caseId || "GLOBAL",
                    question: userMsg.text,
                    thread_id: threadId
                })
            });

            if (!res.ok) throw new Error("Agent failed to respond.");

            const data = await res.json();
            if (data.thread_id && !threadId) setThreadId(data.thread_id);
            setMessages(prev => [...prev, { 
                role: 'assistant', 
                text: data.answer,
                trace: data.trace 
            }]);
        } catch (e: any) {
            setMessages(prev => [...prev, { role: 'assistant', text: `Error: ${e.message}` }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed bottom-6 right-6 z-[60] flex flex-col items-end">
            {/* Chat Window */}
            <div 
                className={`mb-2 w-80 md:w-96 bg-surface-container-lowest rounded-xl shadow-2xl border border-outline-variant overflow-hidden flex flex-col transition-all duration-300 origin-bottom-right ${
                    isOpen ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-95 translate-y-4 pointer-events-none'
                }`}
            >
                {/* Header */}
                <div className="bg-primary-container p-4 flex justify-between items-center">
                    <div className="flex items-center gap-2">
                        <span className="material-symbols-outlined text-on-primary">smart_toy</span>
                        <span className="text-on-primary font-bold">NETRA Assistant</span>
                    </div>
                    <button 
                        onClick={() => setIsOpen(false)} 
                        className="text-on-primary hover:bg-primary rounded-full p-1 transition-colors"
                    >
                        <span className="material-symbols-outlined">close</span>
                    </button>
                </div>
                {/* Body */}
                <div className="h-96 overflow-y-auto p-4 bg-surface flex flex-col gap-4 text-sm">
                    {messages.map((m, idx) => (
                        <div key={idx} className={`flex items-start gap-2 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${m.role === 'user' ? 'bg-surface-container-high' : 'bg-primary-container'}`}>
                                <span className={`material-symbols-outlined text-sm ${m.role === 'user' ? 'text-on-surface' : 'text-on-primary'}`}>
                                    {m.role === 'user' ? 'person' : 'smart_toy'}
                                </span>
                            </div>
                            <div className={`p-3 rounded-lg max-w-[80%] whitespace-pre-wrap ${m.role === 'user' ? 'bg-surface-container-high rounded-tr-none text-on-surface' : 'bg-primary-container/20 rounded-tl-none border border-primary/20 text-on-surface'}`}>
                                <p>{m.text}</p>
                                {m.trace && m.trace.length > 0 && (
                                    <div className="mt-3 pt-2 border-t border-primary/10 text-[10px] text-on-surface-variant font-mono">
                                        <strong>Investigation Trace:</strong>
                                        <ul className="list-disc pl-3 mt-1 space-y-1">
                                            {m.trace.map((t: any, tidx: number) => (
                                                <li key={tidx}>{t.tool}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                    {isLoading && (
                        <div className="flex items-start gap-2">
                            <div className="w-8 h-8 bg-primary-container rounded-full flex items-center justify-center shrink-0">
                                <span className="material-symbols-outlined text-on-primary text-sm animate-spin">sync</span>
                            </div>
                            <div className="p-3 bg-primary-container/20 rounded-lg rounded-tl-none border border-primary/20 text-on-surface flex gap-1">
                                <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce"></span>
                                <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{animationDelay: '150ms'}}></span>
                                <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" style={{animationDelay: '300ms'}}></span>
                            </div>
                        </div>
                    )}
                </div>
                {/* Footer */}
                <div className="p-4 border-t border-outline-variant bg-surface-container-lowest">
                    <div className="flex gap-2">
                        <input 
                            type="text" 
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            placeholder="Ask about this case..." 
                            className="flex-1 bg-surface-container-low border border-outline-variant rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary" 
                        />
                        <button onClick={handleSend} disabled={isLoading} className="bg-primary text-on-primary px-3 rounded-lg hover:bg-primary-container transition-colors flex items-center justify-center disabled:opacity-50">
                            <span className="material-symbols-outlined text-sm">send</span>
                        </button>
                    </div>
                </div>
            </div>
            
            {/* Floating Button */}
            <button 
                onClick={() => setIsOpen(!isOpen)} 
                className="group relative flex items-center gap-2 bg-primary-container text-on-primary rounded-full px-4 py-3 shadow-[0_0_20px_rgba(255,153,51,0.6)] hover:shadow-[0_0_30px_rgba(255,153,51,0.8)] transition-all active:scale-95 z-10"
            >
                <span className="material-symbols-outlined text-xl">smart_toy</span>
                <span className="font-bold tracking-wider uppercase text-sm">Ask AI</span>
                <div className="absolute inset-0 rounded-full border-2 border-saffron-accent opacity-50"></div>
            </button>
        </div>
    );
};

export default Chatbot;
