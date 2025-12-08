export const API_BASE_URL = (
    import.meta.env.PROD
        ? import.meta.env.VITE_API_URL
        : import.meta.env.VITE_LOCAL_API_URL || "http://localhost:3000"
) as string;

// WebSocket URL for real-time connections (must point to backend, not frontend)
export const WS_BASE_URL = (
    import.meta.env.PROD
        ? import.meta.env.VITE_WS_URL || "wss://backend.sudhanshudairy.store"
        : "ws://localhost:8001"
) as string;

