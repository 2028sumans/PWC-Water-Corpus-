"use client";

/**
 * Portfolios + saved-searches management lives in the Decision Terminal's
 * left rail. Two stacked sections:
 *   - Portfolios: list, create, switch active, delete
 *   - Saved searches: list (snapshot of filter state), apply, delete
 *
 * The "+ to portfolio" row affordance in the table writes into the ACTIVE
 * portfolio (auto-creates "My pipeline" if none is active yet). This avoids
 * a modal/picker on every add — analysts who run with one pipeline at a time
 * get zero-click adds; analysts who run with multiple just switch the active
 * portfolio here first.
 */
import { useState } from "react";
import { useViraStore } from "@/store/useViraStore";
import { Briefcase, Plus, X, Bookmark } from "lucide-react";

export function PortfolioBar() {
  const portfolios = useViraStore((s) => s.portfolios);
  const activePortfolioId = useViraStore((s) => s.activePortfolioId);
  const setActivePortfolio = useViraStore((s) => s.setActivePortfolio);
  const createPortfolio = useViraStore((s) => s.createPortfolio);
  const deletePortfolio = useViraStore((s) => s.deletePortfolio);
  const renamePortfolio = useViraStore((s) => s.renamePortfolio);

  const savedSearches = useViraStore((s) => s.savedSearches);
  const saveCurrentSearch = useViraStore((s) => s.saveCurrentSearch);
  const deleteSavedSearch = useViraStore((s) => s.deleteSavedSearch);
  const applySavedSearch = useViraStore((s) => s.applySavedSearch);

  const [creating, setCreating] = useState(false);
  const [newName, setNewName] = useState("");
  const [savingSearch, setSavingSearch] = useState(false);
  const [newSearchName, setNewSearchName] = useState("");
  const [renameId, setRenameId] = useState<string | null>(null);
  const [renameText, setRenameText] = useState("");

  const handleCreate = () => {
    if (!newName.trim()) return;
    createPortfolio(newName);
    setNewName("");
    setCreating(false);
  };

  const handleSaveSearch = () => {
    if (!newSearchName.trim()) return;
    saveCurrentSearch(newSearchName);
    setNewSearchName("");
    setSavingSearch(false);
  };

  return (
    <div className="mt-6">
      {/* Portfolios */}
      <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-2 flex items-center justify-between">
        <span className="flex items-center gap-1.5">
          <Briefcase className="h-3 w-3" />
          Portfolios
        </span>
        <button
          onClick={() => setCreating((v) => !v)}
          className="text-amber-400 hover:text-amber-300 normal-case text-[9px]"
        >
          {creating ? "cancel" : "+ new"}
        </button>
      </div>

      {creating && (
        <div className="mb-2 flex gap-1">
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleCreate();
              if (e.key === "Escape") {
                setCreating(false);
                setNewName("");
              }
            }}
            placeholder="Portfolio name…"
            autoFocus
            className="flex-1 rounded-sm border border-neutral-800 bg-black px-2 py-1 text-[11px] text-neutral-100 placeholder:text-neutral-600 focus:outline-none focus:border-amber-500"
          />
          <button
            onClick={handleCreate}
            disabled={!newName.trim()}
            className="rounded bg-amber-500 px-2 py-1 text-[10px] font-medium text-neutral-950 hover:bg-amber-400 disabled:bg-neutral-700 disabled:text-neutral-500"
          >
            ok
          </button>
        </div>
      )}

      {portfolios.length === 0 && !creating ? (
        <div className="text-[11px] text-neutral-600 italic leading-relaxed mb-2">
          No portfolios yet. Save shortlists of parcels here to compare side-by-side and get alerts when their sub-scores shift.
        </div>
      ) : (
        <div className="space-y-0.5 mb-2">
          {portfolios.map((p) => {
            const isActive = p.id === activePortfolioId;
            return (
              <div key={p.id} className="group flex items-center gap-1 text-[11px]">
                {renameId === p.id ? (
                  <input
                    type="text"
                    value={renameText}
                    onChange={(e) => setRenameText(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        renamePortfolio(p.id, renameText);
                        setRenameId(null);
                      }
                      if (e.key === "Escape") setRenameId(null);
                    }}
                    onBlur={() => {
                      renamePortfolio(p.id, renameText);
                      setRenameId(null);
                    }}
                    autoFocus
                    className="flex-1 rounded-sm border border-neutral-800 bg-black px-1.5 py-0.5 text-[11px] text-neutral-100 focus:outline-none focus:border-amber-500"
                  />
                ) : (
                  <button
                    onClick={() => setActivePortfolio(p.id)}
                    onDoubleClick={() => {
                      setRenameId(p.id);
                      setRenameText(p.name);
                    }}
                    className={`flex-1 min-w-0 rounded px-1.5 py-1 text-left truncate ${
                      isActive
                        ? "bg-amber-500/15 text-amber-200"
                        : "text-neutral-300 hover:bg-neutral-900"
                    }`}
                    title="Click to set active · double-click to rename"
                  >
                    {p.name}
                    <span className="ml-1 text-neutral-600 text-[10px]">
                      {p.gpins.length}
                    </span>
                  </button>
                )}
                <button
                  onClick={() => {
                    if (confirm(`Delete portfolio "${p.name}"?`)) deletePortfolio(p.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 transition-opacity text-neutral-600 hover:text-red-400"
                  aria-label={`Delete ${p.name}`}
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Saved searches */}
      <div className="mt-6 text-[10px] uppercase tracking-wider text-neutral-500 mb-2 flex items-center justify-between">
        <span className="flex items-center gap-1.5">
          <Bookmark className="h-3 w-3" />
          Saved Searches
        </span>
        <button
          onClick={() => setSavingSearch((v) => !v)}
          className="text-amber-400 hover:text-amber-300 normal-case text-[9px]"
        >
          {savingSearch ? "cancel" : "+ save current"}
        </button>
      </div>

      {savingSearch && (
        <div className="mb-2 flex gap-1">
          <input
            type="text"
            value={newSearchName}
            onChange={(e) => setNewSearchName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSaveSearch();
              if (e.key === "Escape") {
                setSavingSearch(false);
                setNewSearchName("");
              }
            }}
            placeholder="Search name…"
            autoFocus
            className="flex-1 rounded-sm border border-neutral-800 bg-black px-2 py-1 text-[11px] text-neutral-100 placeholder:text-neutral-600 focus:outline-none focus:border-amber-500"
          />
          <button
            onClick={handleSaveSearch}
            disabled={!newSearchName.trim()}
            className="rounded bg-amber-500 px-2 py-1 text-[10px] font-medium text-neutral-950 hover:bg-amber-400 disabled:bg-neutral-700 disabled:text-neutral-500"
          >
            ok
          </button>
        </div>
      )}

      {savedSearches.length === 0 && !savingSearch ? (
        <div className="text-[11px] text-neutral-600 italic leading-relaxed">
          Save the current filter + search so you can re-run it later — alerts will fire when the match count changes.
        </div>
      ) : (
        <div className="space-y-0.5">
          {savedSearches.map((s) => (
            <div key={s.id} className="group flex items-center gap-1 text-[11px]">
              <button
                onClick={() => applySavedSearch(s.id)}
                className="flex-1 min-w-0 rounded px-1.5 py-1 text-left text-neutral-300 hover:bg-neutral-900 truncate"
                title={`Apply: q="${s.searchQuery || "—"}", DC building=${s.filters.dcBuildingsOnly}, no NPDES=${s.filters.noNpdesCoverage}, …`}
              >
                {s.name}
                {s.lastMatchCount !== undefined && (
                  <span className="ml-1 text-neutral-600 text-[10px]">
                    {s.lastMatchCount.toLocaleString()}
                  </span>
                )}
              </button>
              <button
                onClick={() => deleteSavedSearch(s.id)}
                className="opacity-0 group-hover:opacity-100 transition-opacity text-neutral-600 hover:text-red-400"
                aria-label={`Delete ${s.name}`}
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/** Compact add-to-portfolio button used inline in each terminal row. */
export function AddToPortfolioButton({ gpin }: { gpin: string }) {
  const activePortfolioId = useViraStore((s) => s.activePortfolioId);
  const portfolios = useViraStore((s) => s.portfolios);
  const addToActivePortfolio = useViraStore((s) => s.addToActivePortfolio);
  const removeFromPortfolio = useViraStore((s) => s.removeFromPortfolio);

  const activePortfolio = portfolios.find((p) => p.id === activePortfolioId);
  const isInActive = !!activePortfolio?.gpins.includes(gpin);

  return (
    <button
      onClick={(e) => {
        e.stopPropagation();
        if (isInActive && activePortfolio) {
          removeFromPortfolio(activePortfolio.id, gpin);
        } else {
          addToActivePortfolio(gpin);
        }
      }}
      className={`rounded p-0.5 transition-colors ${
        isInActive
          ? "text-amber-400 hover:text-amber-300"
          : "text-neutral-600 hover:text-amber-400"
      }`}
      title={
        isInActive
          ? `Remove from "${activePortfolio?.name}"`
          : activePortfolio
            ? `Add to "${activePortfolio.name}"`
            : "Add to portfolio (creates 'My pipeline')"
      }
      aria-label={isInActive ? "Remove from active portfolio" : "Add to active portfolio"}
    >
      <Plus
        className={`h-3.5 w-3.5 transition-transform ${
          isInActive ? "rotate-45" : ""
        }`}
      />
    </button>
  );
}
