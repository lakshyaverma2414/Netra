import { useState } from 'react';

const Chatbot = () => {
    const [isOpen, setIsOpen] = useState(false);

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
                        <span className="text-on-primary font-bold">NCRB AI Assistant</span>
                    </div>
                    <button 
                        onClick={() => setIsOpen(false)} 
                        className="text-on-primary hover:bg-primary rounded-full p-1 transition-colors"
                    >
                        <span className="material-symbols-outlined">close</span>
                    </button>
                </div>
                {/* Body */}
                <div className="h-80 overflow-y-auto p-4 bg-surface flex flex-col gap-4">
                    <div className="flex items-start gap-2">
                        <div className="w-8 h-8 bg-primary-container rounded-full flex items-center justify-center shrink-0">
                            <span className="material-symbols-outlined text-on-primary text-sm">smart_toy</span>
                        </div>
                        <div className="bg-surface-container-high p-3 rounded-lg rounded-tl-none max-w-[80%]">
                            <p className="text-sm text-on-surface">Hello Officer. How can I assist with your investigation today?</p>
                        </div>
                    </div>
                </div>
                {/* Footer */}
                <div className="p-4 border-t border-outline-variant bg-surface-container-lowest">
                    <div className="flex gap-2">
                        <input 
                            type="text" 
                            placeholder="Type your question..." 
                            className="flex-1 bg-surface-container-low border border-outline-variant rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary" 
                        />
                        <button className="bg-primary text-on-primary px-3 rounded-lg hover:bg-primary-container transition-colors flex items-center justify-center">
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
