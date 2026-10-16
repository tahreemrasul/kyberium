"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, errorMessage } from "./api";
import {
  DEFAULT_PREFERENCES,
  type Garment,
  type Generation,
  type Health,
  type Inspiration,
  type StylePreferences,
} from "./types";

export interface StudioState {
  inspiration: Inspiration | null;
  prefs: StylePreferences;
  generation: Generation | null;
  activeLookId: string | null;
}

const EMPTY_STUDIO: StudioState = { inspiration: null, prefs: DEFAULT_PREFERENCES, generation: null, activeLookId: null };
const STUDIO_KEY = "rewear.studio";

interface AppState {
  wardrobe: Garment[] | null;
  wardrobeError: string | null;
  refreshWardrobe: () => Promise<void>;
  setWardrobe: (items: Garment[]) => void;
  health: Health | null;
  studio: StudioState;
  updateStudio: (patch: Partial<StudioState>) => void;
  resetStudio: () => void;
}

const AppContext = createContext<AppState | null>(null);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [wardrobe, setWardrobe] = useState<Garment[] | null>(null);
  const [wardrobeError, setWardrobeError] = useState<string | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [studio, setStudio] = useState<StudioState>(EMPTY_STUDIO);

  const refreshWardrobe = useCallback(async () => {
    try {
      setWardrobe(await api.listGarments());
      setWardrobeError(null);
    } catch (err) {
      setWardrobeError(errorMessage(err));
    }
  }, []);

  useEffect(() => {
    // Restore the styling session so a reload or navigation never loses work.
    try {
      const saved = window.sessionStorage.getItem(STUDIO_KEY);
      // eslint-disable-next-line react-hooks/set-state-in-effect -- hydrate from browser storage after mount
      if (saved) setStudio({ ...EMPTY_STUDIO, ...JSON.parse(saved) });
    } catch {
      /* storage unavailable */
    }
    void refreshWardrobe();
    api.health().then(setHealth).catch(() => setHealth(null));
  }, [refreshWardrobe]);

  const updateStudio = useCallback((patch: Partial<StudioState>) => {
    setStudio((prev) => {
      const next = { ...prev, ...patch };
      try {
        window.sessionStorage.setItem(STUDIO_KEY, JSON.stringify(next));
      } catch {
        /* storage unavailable */
      }
      return next;
    });
  }, []);

  const resetStudio = useCallback(() => {
    setStudio(EMPTY_STUDIO);
    try {
      window.sessionStorage.removeItem(STUDIO_KEY);
    } catch {
      /* storage unavailable */
    }
  }, []);

  const value = useMemo(
    () => ({ wardrobe, wardrobeError, refreshWardrobe, setWardrobe, health, studio, updateStudio, resetStudio }),
    [wardrobe, wardrobeError, refreshWardrobe, health, studio, updateStudio, resetStudio],
  );
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp(): AppState {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used inside <AppProvider>");
  return ctx;
}
