import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { PageTransition } from '../components/PageTransition';
import Sidebar from '../components/Sidebar';

const Upload = () => {
    const [isDragging, setIsDragging] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'complete'>('idle');
    const [progress, setProgress] = useState(0);

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setIsDragging(true);
        } else if (e.type === 'dragleave') {
            setIsDragging(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            startUpload();
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            startUpload();
        }
    };

    const startUpload = () => {
        setUploadStatus('uploading');
        setProgress(0);
        const interval = setInterval(() => {
            setProgress(p => {
                if (p >= 100) {
                    clearInterval(interval);
                    setTimeout(() => {
                        setUploadStatus('complete');
                    }, 500);
                    return 100;
                }
                return p + 5;
            });
        }, 100);
    };

    return (
        <PageTransition>
      <div className="bg-surface text-on-surface h-screen flex flex-row font-body-md antialiased selection:bg-saffron-accent selection:text-white overflow-hidden">
            <Sidebar />

            <main className="flex-1 overflow-y-auto p-4 md:p-8 flex items-center justify-center">
                <div className="max-w-2xl w-full bg-surface-container-lowest border border-outline-variant rounded-xl shadow-lg p-8">
                    <div className="text-center mb-8">
                        <h2 className="text-headline-md font-bold text-primary mb-2">Upload Evidence & Intel Data</h2>
                        <p className="text-on-surface-variant">Upload CSV, JSON, or TXT files to automatically parse and add to the knowledge graph.</p>
                    </div>

                    {uploadStatus === 'idle' ? (
                        <div 
                            onDragEnter={handleDrag}
                            onDragLeave={handleDrag}
                            onDragOver={handleDrag}
                            onDrop={handleDrop}
                            className={`border-4 border-dashed rounded-2xl p-16 flex flex-col items-center justify-center transition-all cursor-pointer ${isDragging ? 'border-saffron-accent bg-saffron-accent/10' : 'border-outline-variant hover:border-primary hover:bg-surface-container-low'}`}
                        >
                            <input type="file" id="file-upload" className="hidden" onChange={handleFileSelect} multiple />
                            <label htmlFor="file-upload" className="flex flex-col items-center cursor-pointer">
                                <div className={`w-20 h-20 rounded-full flex items-center justify-center mb-4 transition-colors ${isDragging ? 'bg-saffron-accent text-white' : 'bg-primary-container text-primary'}`}>
                                    <span className="material-symbols-outlined text-4xl">cloud_upload</span>
                                </div>
                                <h3 className="text-xl font-bold text-primary mb-1">Drag and drop files here</h3>
                                <p className="text-on-surface-variant mb-6">or click to browse your computer</p>
                                <div className="px-6 py-2 bg-primary text-on-primary rounded-lg font-bold hover:bg-opacity-90">Browse Files</div>
                            </label>
                        </div>
                    ) : uploadStatus === 'uploading' ? (
                        <div className="border border-outline-variant rounded-2xl p-16 flex flex-col items-center justify-center bg-surface-container-low">
                            <span className="material-symbols-outlined text-5xl text-primary animate-spin mb-6" style={{ fontVariationSettings: "'FILL' 0, 'wght' 300" }}>sync</span>
                            <h3 className="text-xl font-bold text-primary mb-2">Processing Data...</h3>
                            <p className="text-on-surface-variant mb-8 text-center max-w-md">Extracting entities and generating relationships for the Graph Explorer.</p>
                            
                            <div className="w-full max-w-md bg-surface-container-highest rounded-full h-3 mb-2 overflow-hidden border border-outline-variant">
                                <div className="bg-saffron-accent h-full transition-all duration-300 ease-out" style={{ width: progress + "%" }}></div>
                            </div>
                            <div className="w-full max-w-md flex justify-between text-sm font-bold">
                                <span className="text-on-surface-variant">Uploading</span>
                                <span className="text-primary">{progress}%</span>
                            </div>
                        </div>
                    ) : (
                        <div className="border border-outline-variant rounded-2xl p-16 flex flex-col items-center justify-center bg-surface-container-low">
                            <div className="w-20 h-20 bg-india-green/20 rounded-full flex items-center justify-center mb-6">
                                <span className="material-symbols-outlined text-5xl text-india-green">check_circle</span>
                            </div>
                            <h3 className="text-2xl font-bold text-india-green mb-2">Processing Complete</h3>
                            <p className="text-on-surface-variant mb-8 text-center max-w-md">Data has been successfully extracted and added to the network graph.</p>
                            
                            <div className="flex gap-4">
                                <button onClick={() => setUploadStatus('idle')} className="px-6 py-2 border border-outline-variant rounded-lg font-bold hover:bg-surface-container-highest transition-colors">
                                    Upload Another
                                </button>
                                <NavLink to="/graph-explorer" className="px-6 py-2 bg-saffron-accent text-white rounded-lg font-bold hover:bg-opacity-90 shadow-sm transition-colors">
                                    View Graph Explorer
                                </NavLink>
                            </div>
                        </div>
                    )}
                </div>
            </main>
        </div>
    </PageTransition>
  );
};

export default Upload;
