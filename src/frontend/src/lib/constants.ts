export const API_BASE_URL = (
    import.meta.env.PROD
        ? import.meta.env.VITE_API_URL
        : import.meta.env.VITE_LOCAL_API_URL || "http://localhost:3000"
) as string;
