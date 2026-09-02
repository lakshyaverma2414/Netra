export const Skeleton = ({ className = "" }: { className?: string }) => {
    return (
        <div className={`animate-pulse bg-surface-container-highest rounded-xl ${className}`}></div>
    );
};

export const DashboardSkeleton = () => {
    return (
        <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-28" />)}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <Skeleton className="lg:col-span-2 h-64" />
                <Skeleton className="h-64" />
            </div>
            <Skeleton className="h-40" />
        </div>
    );
};

export const GraphSkeleton = () => {
    return (
        <div className="flex-1 p-4 flex items-center justify-center relative">
            <div className="absolute inset-0 flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <span className="material-symbols-outlined text-6xl text-primary animate-spin">sync</span>
                    <span className="text-primary font-bold">Loading Network Data...</span>
                </div>
            </div>
            <Skeleton className="w-full h-full opacity-30" />
        </div>
    );
};
