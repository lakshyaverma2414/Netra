export interface GraphRequestParams {
    caseId: string;
    entityId: string;
    depth: number;
}

export const getInvestigationGraph = async (params: GraphRequestParams) => {
    const { caseId, entityId, depth } = params;
    const url = `/api/v1/graph/explore?case_id=${encodeURIComponent(caseId)}&entity_id=${encodeURIComponent(entityId)}&depth=${depth}`;
    
    const response = await fetch(url);
    if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
            throw new Error("You may not have access to this case.");
        }
        if (response.status === 404) {
            throw new Error("Case or Entity not found.");
        }
        throw new Error("Unable to load investigation network.");
    }
    
    return await response.json();
};

export const getInvestigationAnalytics = async (caseId: string) => {
    const url = `/api/v1/analytics/cases/${encodeURIComponent(caseId)}/network`;
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error("Unable to load investigation analytics.");
    }
    return await response.json();
};
