// Helper to convert HTTP URL to WS URL
function getWsUrl(apiUrl: string): string {
    return apiUrl.replace(/^http/, 'ws');
}

// API Base URL
export const API_BASE_URL = (
    import.meta.env.PROD
        ? import.meta.env.VITE_API_URL || "https://aitrainer.at0.app"
        : import.meta.env.VITE_LOCAL_API_URL || "http://localhost:8001"
) as string;

// WebSocket URL -> Auto-derives from API URL if VITE_WS_URL is missing
export const WS_BASE_URL = (
    import.meta.env.PROD
        ? import.meta.env.VITE_WS_URL || getWsUrl(API_BASE_URL)
        : "ws://localhost:8001"
) as string;

export const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID as string;
