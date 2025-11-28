import { writable } from "svelte/store";
import { browser } from "$app/environment";

export interface WeeklyStats {
  reps_per_day: number[];
  days: string[];
  total_reps: number;
  total_calories: number;
  workouts_completed: number;
}

export interface WorkoutHistory {
  id: number;
  exercise_name: string;
  date: string;
  duration: number; // seconds
  reps: number;
  calories: number;
  weight_lbs?: number | null;
  sets_completed?: number;
  reps_per_set?: number;
}

export interface Achievement {
  id: string;
  name: string;
  icon: string;
  date?: string; // For unlocked achievements
  requirement?: string; // For locked achievements
}

export interface AchievementsData {
  unlocked: Achievement[];
  locked: Achievement[];
  total: number;
  unlocked_count: number;
}

export interface TodayStats {
  reps_today: number;
  streak: number;
  calories: number;
}

interface ProgressState {
  weeklyStats: WeeklyStats | null;
  workoutHistory: WorkoutHistory[];
  achievements: AchievementsData | null;
  todayStats: TodayStats | null;
  loading: boolean;
  error: string | null;
}

const initialState: ProgressState = {
  weeklyStats: null,
  workoutHistory: [],
  achievements: null,
  todayStats: null,
  loading: false,
  error: null,
};

function createProgressStore() {
  const { subscribe, set, update } = writable<ProgressState>(initialState);

  return {
    subscribe,

    async loadWeeklyStats() {
      update((state) => ({ ...state, loading: true, error: null }));

      try {
        const headers: HeadersInit = {};
        if (browser) {
          const token = localStorage.getItem("token");
          if (token) headers["Authorization"] = `Bearer ${token}`;
        }

        const res = await fetch("/api/stats/weekly", { headers });
        if (!res.ok) throw new Error("Failed to load weekly stats");

        const stats = await res.json();
        update((state) => ({ ...state, weeklyStats: stats, loading: false }));
      } catch (err: any) {
        update((state) => ({ ...state, error: err.message, loading: false }));
      }
    },

    async loadWorkoutHistory(limit: number = 10) {
      update((state) => ({ ...state, loading: true, error: null }));

      try {
        const headers: HeadersInit = {};
        if (browser) {
          const token = localStorage.getItem("token");
          if (token) headers["Authorization"] = `Bearer ${token}`;
        }

        const res = await fetch(`/api/workouts/history?limit=${limit}`, {
          headers,
        });
        if (!res.ok) throw new Error("Failed to load workout history");

        const history = await res.json();
        // Convert date strings to Date objects for formatting
        const formattedHistory = history.map((workout: any) => ({
          ...workout,
          date: workout.date, // Keep as string, will format in component
        }));

        update((state) => ({
          ...state,
          workoutHistory: formattedHistory,
          loading: false,
        }));
      } catch (err: any) {
        update((state) => ({ ...state, error: err.message, loading: false }));
      }
    },

    async loadAchievements() {
      update((state) => ({ ...state, loading: true, error: null }));

      try {
        const headers: HeadersInit = {};
        if (browser) {
          const token = localStorage.getItem("token");
          if (token) headers["Authorization"] = `Bearer ${token}`;
        }

        const res = await fetch("/api/achievements", { headers });
        if (!res.ok) throw new Error("Failed to load achievements");

        const achievements = await res.json();
        update((state) => ({
          ...state,
          achievements: achievements,
          loading: false,
        }));
      } catch (err: any) {
        update((state) => ({ ...state, error: err.message, loading: false }));
      }
    },

    async loadTodayStats() {
      update((state) => ({ ...state, loading: true, error: null }));

      try {
        const headers: HeadersInit = {};
        if (browser) {
          const token = localStorage.getItem("token");
          if (token) headers["Authorization"] = `Bearer ${token}`;
        }

        const res = await fetch("/api/stats/today", { headers });
        if (!res.ok) throw new Error("Failed to load today stats");

        const stats = await res.json();
        update((state) => ({ ...state, todayStats: stats, loading: false }));
      } catch (err: any) {
        update((state) => ({ ...state, error: err.message, loading: false }));
      }
    },

    async loadAll() {
      await Promise.all([
        this.loadWeeklyStats(),
        this.loadWorkoutHistory(),
        this.loadAchievements(),
        this.loadTodayStats(),
      ]);
    },

    reset() {
      set(initialState);
    },
  };
}

export const progressStore = createProgressStore();
