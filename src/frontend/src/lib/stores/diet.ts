import { writable } from "svelte/store";
import { browser } from "$app/environment";
import { API_BASE_URL } from "../constants";

export interface DietEntry {
    id: number;
    meal_name: string;
    food_item: string;
    date: string;
    protein: number;
    carbs: number;
    fats: number;
    calories: number;
    omega3: number;
    magnesium: number;
    vitamin_b1: number;
    vitamin_d3: number;
    zinc: number;
    notes?: string;
}

export interface DietStats {
    date: string;
    total_protein: number;
    total_carbs: number;
    total_fats: number;
    total_calories: number;
    total_omega3: number;
    total_magnesium: number;
    total_vitamin_b1: number;
    total_vitamin_d3: number;
    total_zinc: number;
    protein_goal: number;
    entries_count: number;
}

interface DietState {
    entries: DietEntry[];
    stats: DietStats | null;
    loading: boolean;
    error: string | null;
}

const initialState: DietState = {
    entries: [],
    stats: null,
    loading: false,
    error: null,
};

function createDietStore() {
    const { subscribe, set, update } = writable<DietState>(initialState);

    return {
        subscribe,

        async loadEntries(startDate?: string, endDate?: string) {
            update((state) => ({ ...state, loading: true, error: null }));

            try {
                let url = `${API_BASE_URL}/api/diet/entries`;
                const params = new URLSearchParams();
                if (startDate) params.append("start_date", startDate);
                if (endDate) params.append("end_date", endDate);
                if (params.toString()) url += "?" + params.toString();

                const headers: HeadersInit = {};
                if (browser) {
                    const token = localStorage.getItem("token");
                    if (token) headers["Authorization"] = `Bearer ${token}`;
                }

                const res = await fetch(url, { headers });
                if (!res.ok) throw new Error("Failed to load entries");

                const entries = await res.json();
                update((state) => ({ ...state, entries, loading: false }));
            } catch (err: any) {
                update((state) => ({
                    ...state,
                    error: err.message,
                    loading: false,
                }));
            }
        },

        async loadStats(targetDate?: string) {
            update((state) => ({ ...state, loading: true, error: null }));

            try {
                let url = `${API_BASE_URL}/api/diet/stats`;
                if (targetDate) url += "?target_date=" + targetDate;

                const headers: HeadersInit = {};
                if (browser) {
                    const token = localStorage.getItem("token");
                    if (token) headers["Authorization"] = `Bearer ${token}`;
                }

                const res = await fetch(url, { headers });
                if (!res.ok) throw new Error("Failed to load stats");

                const stats = await res.json();
                update((state) => ({ ...state, stats, loading: false }));
            } catch (err: any) {
                update((state) => ({
                    ...state,
                    error: err.message,
                    loading: false,
                }));
            }
        },

        async addEntry(entry: Omit<DietEntry, "id" | "date">) {
            update((state) => ({ ...state, loading: true, error: null }));

            try {
                const headers: HeadersInit = {
                    "Content-Type": "application/json",
                };
                if (browser) {
                    const token = localStorage.getItem("token");
                    if (token) headers["Authorization"] = `Bearer ${token}`;
                }

                const res = await fetch(`${API_BASE_URL}/api/diet/entries`, {
                    method: "POST",
                    headers,
                    body: JSON.stringify(entry),
                });

                if (!res.ok) throw new Error("Failed to add entry");

                const newEntry = await res.json();
                update((state) => ({
                    ...state,
                    entries: [newEntry, ...state.entries],
                    loading: false,
                }));

                // Reload stats
                await this.loadStats();
            } catch (err: any) {
                update((state) => ({
                    ...state,
                    error: err.message,
                    loading: false,
                }));
            }
        },

        async deleteEntry(entryId: number) {
            update((state) => ({ ...state, loading: true, error: null }));

            try {
                const headers: HeadersInit = {};
                if (browser) {
                    const token = localStorage.getItem("token");
                    if (token) headers["Authorization"] = `Bearer ${token}`;
                }

                const res = await fetch(
                    `${API_BASE_URL}/api/diet/entries/${entryId}`,
                    {
                        method: "DELETE",
                        headers,
                    },
                );

                if (!res.ok) throw new Error("Failed to delete entry");

                update((state) => ({
                    ...state,
                    entries: state.entries.filter((e) => e.id !== entryId),
                    loading: false,
                }));

                // Reload stats
                await this.loadStats();
            } catch (err: any) {
                update((state) => ({
                    ...state,
                    error: err.message,
                    loading: false,
                }));
            }
        },

        reset() {
            set(initialState);
        },
    };
}

export const dietStore = createDietStore();
