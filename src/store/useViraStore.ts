import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

interface ViraState {
  // Selection — the GPIN of the facility (building or campus) currently
  // shown in the right panel. Named for the underlying join key, not a
  // reference to parcel-level browsing (there is none in this app).
  selectedGpin: string | null;
  setSelectedGpin: (gpin: string | null) => void;

  // Right panel
  rightPanelOpen: boolean;
  openRightPanel: () => void;
  closeRightPanel: () => void;
}

export const useViraStore = create<ViraState>()(
  persist(
    (set) => ({
      selectedGpin: null,
      setSelectedGpin: (gpin) =>
        set({ selectedGpin: gpin, rightPanelOpen: gpin !== null }),

      rightPanelOpen: false,
      openRightPanel: () => set({ rightPanelOpen: true }),
      closeRightPanel: () => set({ rightPanelOpen: false }),
    }),
    {
      name: "water-atlas-state",
      storage: createJSONStorage(() => localStorage),
      // Selection/panel are session-only — nothing to persist across reloads.
      partialize: () => ({}),
    }
  )
);
