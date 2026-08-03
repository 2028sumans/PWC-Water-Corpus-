"""
Paper figures — four, one per argument, built from the shipped artifacts.

FIGURE PLAN
  F1  conventions   LEG 1: where it lands. Lake Anna's share of the SAME physical
                    water under every standard convention. Horizontal bar,
                    magnitude job, ONE hue (not a ramp -- the conventions are
                    nominal); non-computable rows drawn as outlined ghosts with
                    their bounds annotated, because the gaps are part of the result.
  F2  entitlement   LEG 2: whether anyone asks. Hero number (0 of 243 SUPs) plus
                    an entitlement-vintage histogram with emphasis on pre-1990.
  F3  timing        LEG 3: when it lands. Two stacked panels sharing a month axis
                    -- NEVER a dual axis. Top: dimensionless monthly factors,
                    data centers vs the municipal envelope. Bottom: the resulting
                    share of Broad Run flow, September emphasised.
  F4  broad_run     THE CASE: 2x2 small multiples, four independent sources
                    converging on one basin.

DESIGN RULES APPLIED (dataviz skill)
  - form chosen before color; color assigned by job, then validated
  - palette validated: node scripts/validate_palette.js "#2a78d6,#eb6834,#1baf7a"
    --mode light -> ALL PASS (aqua carries a contrast WARN, so every mark that
    uses it is directly labelled, which is the documented relief)
  - single hue for magnitude; emphasis (1 hue + gray) where one item is the point
  - thin marks, hairline recessive grid, no dashed gridlines, generous padding
  - direct labels on every bar (n is small enough that this is legible, not chaos)
  - no dual-axis anywhere; two measures of different scale become two panels
  - print medium, so no hover layer; direct labels carry every value instead

Writes vector PDF + SVG (for the manuscript) and 300 dpi PNG (for a poster) to
figures/.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(HERE, "public", "data")
RAW = os.path.join(HERE, "data", "water_raw")
OUT = os.path.join(HERE, "figures")
os.makedirs(OUT, exist_ok=True)

# --- palette (validated; see module docstring) ------------------------------
BLUE       = "#2a78d6"   # categorical slot 1 / sequential hue
ORANGE     = "#eb6834"   # slot 2
AQUA       = "#1baf7a"   # slot 3 -- always directly labelled (contrast relief)
INK        = "#0b0b0b"
INK_2      = "#52514e"
MUTED      = "#898781"
GRID       = "#e1e0d9"
AXIS       = "#c3c2b7"
SURFACE    = "#fcfcfb"
DEEMPH     = "#c9c8c2"   # the "rest" in an emphasis pair

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 8.5,
    "axes.edgecolor": AXIS,
    "axes.linewidth": 0.6,
    "axes.labelcolor": INK_2,
    "axes.titlesize": 9.5,
    "axes.titleweight": "bold",
    "axes.titlecolor": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelcolor": INK_2,
    "ytick.labelcolor": INK_2,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "grid.linestyle": "-",          # never dashed
    "legend.frameon": False,
    "legend.fontsize": 8,
    "pdf.fonttype": 42,             # embed as TrueType, not Type-3
    "svg.fonttype": "none",
})


def _clean(ax, spines=("top", "right")):
    for s in spines:
        ax.spines[s].set_visible(False)
    ax.tick_params(length=2.5, pad=2)


def save(fig, name):
    for ext in ("pdf", "svg", "png"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"),
                    dpi=300, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    print(f"  wrote figures/{name}.{{pdf,svg,png}}")


# ---------------------------------------------------------------------------
# F1 — THE CONVENTION FIGURE
# ---------------------------------------------------------------------------
def fig_conventions():
    d = json.load(open(os.path.join(PUB, "convention_table.json")))
    C = d["conventions"]

    # Ordered by the GEOGRAPHIC BREADTH of the accounting boundary. Lake Anna's
    # share falls monotonically as the boundary widens -- that ordering IS a
    # result, so the figure must not scramble it.
    order = ["dominion_utility_average", "egrid_serc_vacar", "pjm_rto_average",
             "market_based", "long_run_marginal", "short_run_marginal"]
    labels = {
        "dominion_utility_average": "Dominion utility-average\n(Virginia fleet only)",
        "pjm_rto_average": "PJM RTO-wide average\n(13 states + DC)",
        "egrid_serc_vacar": "eGRID SERC Virginia/Carolina\n(VA+NC+SC — the county's own basis)",
        "market_based": "Market-based\n(PPA / VPPA / REC)",
        "long_run_marginal": "Long-run marginal\n(capacity expansion)",
        "short_run_marginal": "Short-run marginal\n(PJM real-time, 2022)",
    }
    ghost_note = {
        "market_based": "≈0 for 100%-clean contract holders",
        "long_run_marginal": "attributes the entire +24 TWh VA nuclear build",
    }

    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    ys = list(range(len(order)))[::-1]

    for y, k in zip(ys, order):
        v = C[k].get("lake_anna_pct_of_scope2")
        if v is None:
            # A ghost row is a full-width TRACK, not a bar. Drawing it to a
            # finite length would read as a value -- these rows have none.
            ax.barh(y, 52, height=0.5, color="#f2f1ed", edgecolor="none", zorder=1)
            ax.text(1.0, y, ghost_note[k], va="center", ha="left",
                    fontsize=7.6, color=MUTED, style="italic", zorder=4)
        else:
            ax.barh(y, v, height=0.5, color=BLUE, zorder=3)
            ax.text(v + 0.9, y, f"{v:.2f}%", va="center", ha="left",
                    fontsize=8.5, color=INK, fontweight="bold", zorder=4)

    ax.set_yticks(ys)
    ax.set_yticklabels([labels[k] for k in order], fontsize=8.2)
    ax.set_xlim(0, 52)
    ax.set_xlabel("Share of the fleet's electricity-related water attributed to Lake Anna (York basin)")
    ax.xaxis.set_major_formatter(lambda x, p: f"{x:.0f}%")
    ax.grid(axis="x", zorder=0)
    ax.set_axisbelow(True)
    _clean(ax)
    ax.spines["left"].set_visible(False)

    ax.set_title(" ", loc="left", pad=30)     # reserve the band
    ax.text(0.0, 1.135, "Which basin is charged is set by convention, not measurement",
            fontsize=11, fontweight="bold", color=INK, ha="left", va="bottom",
            transform=ax.transAxes)
    ax.text(0.0, 1.045,
            "The same physical electricity, attributed six standard ways — ordered by how wide the accounting boundary is drawn",
            fontsize=9, color=INK_2, ha="left", va="bottom", transform=ax.transAxes)

    lo = d["lake_anna_share_range_pct"]["min"]
    hi = d["lake_anna_share_range_pct"]["max"]
    ax.legend(handles=[
        Patch(facecolor=BLUE, label="computed from the shipped model"),
        Patch(facecolor="#f2f1ed", label="documented; not computable from this corpus"),
    ], loc="upper left", bbox_to_anchor=(0.0, -0.115), ncol=2, handlelength=1.3,
        columnspacing=1.6, handletextpad=0.5)

    ax.text(0.0, -0.20,
             f"Computable conventions span {lo:.2f}%–{hi:.2f}% — a factor of "
             f"{hi/lo:.0f}. Fleet: all 243 buildings, full buildout.\n"
             "The three averages differ only in where the boundary is drawn, and Lake Anna's "
             "share falls as it widens: Virginia holds 23.2% of eGRID SERC nuclear\n"
             "(EPA eGRID2023) and 11.7% of PJM nuclear (JLARC App. H ÷ PJM SOM Table 3-63), "
             "so each convention is scaled by that share — unscaled, a Virginia-only\n"
             "plant map returns 52.3% and 45.4% and inverts the result. Short-run marginal is "
             "lowest for a different reason: nuclear is baseload and rarely responds to\n"
             "new demand. Long-run marginal is cited from JLARC/E3, not recomputed; its new "
             "nuclear is unsited SMRs, not North Anna.",
            fontsize=6.9, color=MUTED, ha="left", va="top", transform=ax.transAxes,
            linespacing=1.6)
    save(fig, "F1_conventions")




# ---------------------------------------------------------------------------
# F2 — THE ENTITLEMENT FIGURE
# ---------------------------------------------------------------------------
def fig_entitlement():
    e = json.load(open(os.path.join(PUB, "entitlement_pathway.json")))
    vint = {int(k): v for k, v in e["entitlement_vintage"]["by_year"].items()}
    pc, pa = e["planning_case"], e["price_asymmetry"]

    fig = plt.figure(figsize=(7.6, 4.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 2.35], wspace=0.32,
                          left=0.02, right=0.99, top=0.815, bottom=0.335)

    # -- (a) the stat. A single value is a stat tile, never a one-bar chart. --
    a = fig.add_subplot(gs[0, 0]); a.axis("off")
    a.text(0, 1.03, "0", fontsize=58, fontweight="bold", color=BLUE,
           ha="left", va="top", transform=a.transAxes)
    a.text(0, 0.575, "of 243 data-center buildings\nhas a Special Use Permit",
           fontsize=9.3, color=INK, ha="left", va="top", weight="bold",
           transform=a.transAxes, linespacing=1.45)
    a.text(0, 0.375,
           "The SUP is the county's only discretionary\nreview — the point at which conditions\nattach. It was never invoked.",
           fontsize=7.5, color=INK_2, ha="left", va="top",
           transform=a.transAxes, linespacing=1.55)
    a.text(0, 0.125,
           f"REZ {pc['by_type'].get('REZ',0)}   ·   PLN {pc['by_type'].get('PLN',0)}   ·   SUP 0\n"
           f"{pc['absent']} buildings ({pc['absent_pct']}%) carry no case at all\n"
           f"{e['by_right_eligibility']['inside_dcood']} of 243 sit inside the overlay,\n"
           f"where the use is permitted by right",
           fontsize=6.9, color=MUTED, ha="left", va="top",
           transform=a.transAxes, linespacing=1.6)

    # -- (b) entitlement vintage. Emphasis: one hue + gray. -------------------
    b = fig.add_subplot(gs[0, 1])
    yrs = sorted(vint)
    b.bar([str(y) for y in yrs], [vint[y] for y in yrs],
          color=[ORANGE if y < 1990 else DEEMPH for y in yrs], width=0.72, zorder=3)
    i58 = yrs.index(1958)
    b.annotate("20 buildings entitled under\nrezonings adopted in 1958",
               xy=(i58, vint[1958]), xytext=(i58 + 1.4, vint[1958] + 2.0),
               fontsize=7.3, color=INK, ha="left", va="bottom", linespacing=1.45,
               arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7,
                               shrinkA=0, shrinkB=3))
    b.set_ylabel("buildings", fontsize=8)
    b.set_ylim(0, max(vint.values()) + 4)
    b.grid(axis="y", zorder=0); b.set_axisbelow(True); _clean(b)
    plt.setp(b.get_xticklabels(), rotation=90, fontsize=6.4)
    b.legend(handles=[
        Patch(facecolor=ORANGE, label=f"pre-1990 approval — {e['entitlement_vintage']['pre_1990_buildings']} buildings, no open approval to condition"),
        Patch(facecolor=DEEMPH, label="1990 or later"),
    ], loc="upper right", bbox_to_anchor=(1.0, 0.93), ncol=1, handlelength=1.2,
        handletextpad=0.5, labelspacing=0.4, fontsize=7.2)

    fig.text(0.02, 0.965, "Nobody ever asks how much water",
             fontsize=11.5, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.02, 0.905,
             "The entitlement pathway, and the year each building's approval was granted",
             fontsize=9, color=INK_2, ha="left", va="top")

    # NB: escape dollar signs -- matplotlib parses $...$ as mathtext.
    fig.text(0.02, 0.155,
             "Data centers are permitted by right inside the Data Center Opportunity Overlay District; a SUP is triggered only by exceeding the by-right\n"
             "envelope (height or floor-area ratio), never by the use itself. Where the approval predates the industry no water condition could have been\n"
             "contemplated, and an entitlement runs with the land. Where a data-center SUP does exist in the county record — Amazon Gainesville East —\n"
             rf"water quality was charged at \${pa['water_quality_contribution_usd']:,.0f} against \${pa['fire_and_rescue_contribution_usd']:,.0f} for fire and rescue, a factor of {pa['ratio_fire_to_water']:.0f}, while a licensed acoustical study of the cooling system was required twice per building.",
             fontsize=6.9, color=MUTED, ha="left", va="top", linespacing=1.65)
    save(fig, "F2_entitlement")


# ---------------------------------------------------------------------------
# F3 — THE TIMING FIGURE  (two panels; never a dual axis)
# ---------------------------------------------------------------------------
def fig_timing():
    s = json.load(open(os.path.join(PUB, "seasonal_basin_surface.json")))
    M = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    obs = s["observed_monthly_factors"]
    tl = s["timing_leg"]
    br = s["surfaces"]["BROAD RUN"]["central"]["monthly_pct_of_flow"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.4, 5.0), sharex=True,
                                   gridspec_kw={"hspace": 0.16, "height_ratios": [1, 1]})

    # -- (a) dimensionless monthly factors. Both series share one scale. ------
    mn, mx = 0.80, 1.31          # measured municipal range, 4 suppliers, Jan & Jul
    ax1.axhspan(mn, mx, color=DEEMPH, alpha=0.5, zorder=1)
    ax1.text(11.35, (mn + mx) / 2, "municipal\n(4 suppliers)", fontsize=7,
             color=INK_2, va="center", ha="left", linespacing=1.4)
    ax1.plot(M, [obs[m] for m in M], color=BLUE, lw=2, marker="o", ms=4.5,
             mfc=BLUE, mec=SURFACE, mew=1.2, zorder=3)
    ax1.annotate(f"{obs['Aug']}×", xy=("Aug", obs["Aug"]), xytext=(0, 8),
                 textcoords="offset points", fontsize=8.5, color=INK,
                 fontweight="bold", ha="center")
    ax1.axhline(1.0, color=AXIS, lw=0.6, zorder=2)
    ax1.set_ylabel("monthly factor\n(× annual mean)", fontsize=8)
    ax1.set_ylim(0.3, 2.15); ax1.set_xlim(-0.6, 11.6)
    ax1.grid(axis="y", zorder=0); ax1.set_axisbelow(True); _clean(ax1)
    ax1.legend(handles=[
        plt.Line2D([], [], color=BLUE, lw=2, marker="o", ms=4.5, mec=SURFACE,
                   label="data centers (ICPRB observed, Loudoun + Prince William)"),
        Patch(facecolor=DEEMPH, alpha=0.5,
              label="municipal range (ICPRB Table 4-3, 11 yr of daily production)"),
    ], loc="upper left", bbox_to_anchor=(0.0, 1.30), handlelength=1.6)

    # -- (b) the consequence, in the basin that carries the fleet ------------
    cols = [BLUE if m == "Sep" else DEEMPH for m in M]
    ax2.bar(M, [br[m] for m in M], color=cols, width=0.68, zorder=3)
    ax2.annotate(f"{br['Sep']}%", xy=("Sep", br["Sep"]), xytext=(0, 5),
                 textcoords="offset points", fontsize=8.5, color=INK,
                 fontweight="bold", ha="center")
    ax2.set_ylabel("Broad Run:\n% of that month's flow", fontsize=8)
    ax2.set_ylim(0, 19)
    ax2.grid(axis="y", zorder=0); ax2.set_axisbelow(True); _clean(ax2)
    ax2.text(0.005, 0.93, "binding condition: September, not July",
             transform=ax2.transAxes, ha="left", va="top", fontsize=7.6, color=INK_2)

    fig.text(0.0, 1.34, "Demand peaks when the water isn't there",
             fontsize=11, fontweight="bold", color=INK, ha="left", va="bottom",
             transform=ax1.transAxes)
    fig.text(0.0, 1.25,
             "Data-center demand is ~6× peakier than the municipal demand the supply system was engineered around",
             fontsize=9, color=INK_2, ha="left", va="bottom", transform=ax1.transAxes)

    fig.text(0.0, -0.30,
             f"Peak-DAY factors: municipal {tl['municipal_peak_day_range'][0]}–{tl['municipal_peak_day_range'][1]}×; data centers {tl['datacenter_peak_day_ours']}× here and ~{tl['datacenter_peak_day_icprb']:.0f}× in ICPRB's independent construction — a {tl['peakiness_ratio_vs_municipal_mean']}× difference.\n"
             "The monthly shape is ICPRB's OBSERVED Table A.3-2 series, which replaced a cooling-degree-day model that was ~70% too peaky in summer (July 3.04× against\n"
             "an observed 1.5×). Correcting it moved the binding condition from July to September and roughly halved it. The load is near-constant by design: JLARC records\n"
             "that Virginia data centers \"do not currently participate in demand response programs\" because \"energy use is driven by computing activity.\"",
             fontsize=6.9, color=MUTED, ha="left", va="top",
             transform=ax2.transAxes, linespacing=1.6)
    save(fig, "F3_timing")


# ---------------------------------------------------------------------------
# F4 — BROAD RUN: four independent sources, one basin
# ---------------------------------------------------------------------------
def fig_broad_run():
    import csv
    from collections import Counter
    br = json.load(open(os.path.join(PUB, "broad_run_case.json")))

    fig, axes = plt.subplots(2, 2, figsize=(7.6, 5.4))
    (p1, p2), (p3, p4) = axes
    fig.subplots_adjust(hspace=0.62, wspace=0.30, top=0.80, bottom=0.16,
                        left=0.075, right=0.985)

    # -- (a) concentration: share of fleet vs share of land ------------------
    con = br["concentration"]
    names = ["Broad Run", "Bull Run", "Quantico Ck"]
    fleet = [con["pct_of_fleet"], con["comparison"]["BULL RUN"]["pct_fleet"],
             con["comparison"]["QUANTICO CREEK"]["pct_fleet"]]
    land = [con["pct_of_county_land"], con["comparison"]["BULL RUN"]["pct_land"],
            con["comparison"]["QUANTICO CREEK"]["pct_land"]]
    x = range(len(names)); w = 0.36
    p1.bar([i - w/2 for i in x], fleet, w, color=BLUE, zorder=3, label="% of the fleet")
    p1.bar([i + w/2 for i in x], land, w, color=DEEMPH, zorder=3, label="% of county land")
    for i, (f, l) in enumerate(zip(fleet, land)):
        p1.text(i - w/2, f + 1.6, f"{f:.1f}%", ha="center",
                fontsize=7.4, color=INK, fontweight="bold")
        p1.text(i + w/2, l + 1.6, f"{l:.0f}%", ha="center", fontsize=7.4, color=INK_2)
    p1.set_xticks(list(x)); p1.set_xticklabels(names, fontsize=7.6)
    p1.set_ylim(0, 88); p1.set_ylabel("percent", fontsize=7.6)
    p1.grid(axis="y", zorder=0); p1.set_axisbelow(True); _clean(p1)
    p1.legend(loc="upper right", fontsize=6.9, handlelength=1.1, handletextpad=0.4)
    p1.set_title("a   72.5% of the fleet on 19.9% of the land", loc="left",
                 fontsize=8.5, pad=6)

    # -- (b) the gage stopped forty years before the demand ------------------
    p2.barh(1, 1986 - 1950, left=1950, height=0.34, color=DEEMPH, zorder=3)
    p2.barh(0, 2026 - 1990, left=1990, height=0.34, color=BLUE, zorder=3)
    p2.text(1986, 1.28, "gage record ends 1986", fontsize=7.2, color=INK_2,
            ha="right", va="bottom")
    p2.text(1990, -0.36, "the fleet is built here", fontsize=7.2, color=INK,
            ha="left", va="top", fontweight="bold")
    p2.axvspan(2024.5, 2026.4, color=ORANGE, alpha=0.30, zorder=2)
    p2.text(2025.5, 0.62, "23-month\nsevere drought", fontsize=6.6, color=INK,
            ha="center", va="center", linespacing=1.4)
    p2.set_yticks([0, 1]); p2.set_yticklabels(["demand", "flow record"], fontsize=7.4)
    p2.set_xlim(1948, 2030); p2.set_ylim(-0.8, 1.7)
    p2.grid(axis="x", zorder=0); p2.set_axisbelow(True); _clean(p2)
    p2.spines["left"].set_visible(False)
    p2.set_title("b   the denominator predates the numerator", loc="left",
                 fontsize=8.5, pad=6)

    # -- (c) warming: 17 stations, Broad Run is the only significant one -----
    gj = json.load(open(os.path.join(RAW, "SURFACE_WATER_TEMPERATURE.geojson"),
                        encoding="utf-8", errors="replace"))
    pre = ("1ABR", "1ABU", "1AOC", "1AQU", "1ANE", "1ACE", "1APO",
           "1ACA", "1AHO", "1ASO", "1ACAM", "1ACAX", "1APOH", "1APOE", "1APOM")
    st = [f["properties"] for f in gj["features"]
          if str(f["properties"]["Station"]).startswith(pre)]
    st = sorted(st, key=lambda r: r["TheilSen_slope"])
    sl = [r["TheilSen_slope"] for r in st]
    sig = [r["Pvalcovs"] < 0.05 for r in st]
    cols = [ORANGE if s else DEEMPH for s in sig]
    p3.barh(range(len(sl)), sl, color=cols, height=0.62, zorder=3)
    p3.axvline(0, color=AXIS, lw=0.6, zorder=2)
    k = next(i for i, r in enumerate(st) if r["Station"].startswith("1ABRB"))
    p3.text(sl[k] + 0.006, k, "Broad Run  p=0.03", va="center", ha="left",
            fontsize=7.2, color=INK, fontweight="bold")
    p3.set_yticks([]); p3.set_xlabel("Theil-Sen slope (°C/yr)", fontsize=7.4)
    p3.set_xlim(-0.05, 0.20)
    p3.grid(axis="x", zorder=0); p3.set_axisbelow(True); _clean(p3)
    p3.spines["left"].set_visible(False)
    n_pos = sum(1 for v in sl if v > 0)
    n_neg = sum(1 for v in sl if v < 0)
    p3.set_title(f"c   {len(st)} stream stations; {n_pos} warming, {n_neg} cooling",
                 loc="left", fontsize=8.5, pad=6)

    # -- (d) the drought, observed ------------------------------------------
    pdsi = json.load(open(os.path.join(RAW, "PDSI.json")))["data"]
    ks = sorted(k for k, v in pdsi.items() if v.get("value") is not None)
    yr = [int(k[:4]) + (int(k[4:]) - 1) / 12 for k in ks]
    vv = [float(pdsi[k]["value"]) for k in ks]
    p4.fill_between(yr, vv, 0, where=[v <= 0 for v in vv], color=DEEMPH,
                    lw=0, zorder=2, interpolate=True)
    run = [(y, v) for y, v in zip(yr, vv) if y >= 2024.4]
    p4.fill_between([y for y, _ in run], [v for _, v in run], 0,
                    color=ORANGE, lw=0, zorder=3)
    p4.axhline(-3, color=INK_2, lw=0.6, zorder=4)
    p4.text(1897, -3.35, "severe drought threshold", fontsize=6.5, color=INK_2,
            va="top", ha="left")
    p4.annotate("23 unbroken months,\nstill open at data cutoff",
                xy=(2025.2, -5.2), xytext=(2003, -6.6), fontsize=6.9, color=INK,
                ha="right", va="center", linespacing=1.4,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7))
    p4.set_xlim(1895, 2028); p4.set_ylim(-7.5, 7.5)
    p4.set_ylabel("PDSI", fontsize=7.6)
    p4.grid(axis="y", zorder=0); p4.set_axisbelow(True); _clean(p4)
    p4.set_title("d   worst drought in the 132-year record", loc="left",
                 fontsize=8.5, pad=6)

    fig.text(0.02, 0.965, "Broad Run: four independent sources, one basin",
             fontsize=11.5, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.02, 0.912,
             "The basin carrying 72.5% of Prince William County's data centers",
             fontsize=9, color=INK_2, ha="left", va="top")
    fig.text(0.02, 0.085,
             "Concentration is the county's own watershed layer crossed with the building attribution. The flow denominator comes from a gage decommissioned in\n"
             "1986, which never observed any part of the drought now underway. Of 17 stream stations in the Prince William / Occoquan group, 15 have positive\n"
             "temperature trends, 1 is exactly zero and 1 negative (sign test on the 16 non-ties: p = 0.0005); Broad Run 1ABRB002.15 is the only one individually\n"
             "significant at p<0.05. Statewide only 49 of 413 stations are\n"
             "significant — but 47 of those 49 are warming and 2 cooling. The PDSI series is the observed NOAA/NCEI county record, not a projection.",
             fontsize=6.9, color=MUTED, ha="left", va="top", linespacing=1.65)
    save(fig, "F4_broad_run")


def build_all():
    print("building figures…")
    fig_conventions()
    fig_entitlement()
    fig_timing()
    fig_broad_run()


if __name__ == "__main__":
    build_all()
