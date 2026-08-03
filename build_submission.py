"""Assemble AGU26_SUBMISSION.txt from the source files.

Replaces a dozen rounds of ad-hoc string surgery on the packet, which on the
last pass silently deleted the abstract body while leaving its header and note
in place. Counts are recomputed here, so they cannot drift from the text.

Run: python3 build_submission.py
"""
import re

TITLE = ("Accounting conventions can shift the apparent water burden of data centers "
         "across watersheds: a verifiable evidence base for Prince William County, Virginia")

ASCII_MAP = {"±": "+/-", "—": "--", "–": "-", "×": "x"}


def nospace(t):
    return len(re.sub(r"\s", "", t))


def to_ascii(t):
    for k, v in ASCII_MAP.items():
        t = t.replace(k, v)
    return t


def main():
    abs_ = open("ABSTRACT_AGU26.txt").read().strip()
    pls = open("PLAIN_SUMMARY_AGU26.txt").read().strip()
    n_abs, n_ascii = nospace(abs_), nospace(to_ascii(abs_))
    nonascii = [c for c in abs_ if ord(c) > 127]
    spare = 2000 - n_abs

    out = f"""=== TITLE ({len(TITLE)} chars incl. spaces / {len(TITLE.split())} words) ===

{TITLE}


=== ABSTRACT ({n_abs}/2000 chars, excl. spaces) ===
[Paste this block ONLY into the abstract-body field. Do not include the title.]

{abs_}

[{len(nonascii)} non-ASCII character(s). ASCII fallback: {n_ascii}/2000. {spare} spare.]


=== PLAIN-LANGUAGE SUMMARY ({len(pls.split())}/200 words) ===

{pls}


=== COUPLINGS -- if you edit one, check the other ===

  "consumptive" (opening)  <->  "under 3% of our estimate"
      Since the fit-out ramp (METHODOLOGY 62) this holds on BOTH bases --
      2.9% delivered, 2.2% consumptive. It used to hold only on the
      consumptive basis (3.2% delivered), so this coupling is now slack
      rather than binding. Keep "consumptive" anyway: it is what makes the
      88% and the ICPRB comparison like-for-like.

  "completed" (NOT "operating")  <->  the fit-out ramp
      BuildingStatus is a CONSTRUCTION status; all 54 are Completed/Finaled.
      NO field indicates energization. Stronger than that: PWC's own building
      policy grants the Certificate of Occupancy with unfitted floor area
      permitted as Storage (S-1) and defers data-hall fit-out to a separate
      Alteration/Repair permit. So a CO marks the START of fit-out. The model
      now carries installed capacity to energized load on Dominion's
      contractual 4-year ramp. "Operating" would turn an estimate of
      installed capacity into an apparent measurement of live facilities.
      METHODOLOGY 57.1, 62.

  the ramp  <->  every share in the abstract
      The ramp multiplies IT power and every scope is proportional to IT
      power, so it moves VOLUMES and leaves SHARES untouched (verified,
      harness 20 + validate_occupancy_ramp.py step 6). If anyone ever makes
      it scope-specific, 88% / under 3% / >40% / under 2% all become live
      again and must be rechecked. METHODOLOGY 62.3.

  "Whether a given watershed is implicated"  <->  destination is undetermined
      Marginal accounting establishes Lake Anna ~= 1%. It does NOT establish
      where the water goes instead (Roanoke swings 0.00-11.11 MGD, and that
      is an upper bound). Do not let this drift back to "each approach
      identifies different watersheds". METHODOLOGY 57.2.

  "under 2%"  <->  which year's PJM marginal shares
      Nuclear is 0.39% of PJM real-time marginal resources in 2022 and
      0.62% in 2023 -> York 0.87% and 1.38%. But it was 1.00-1.35% in
      2019-21 -> York 2.2-2.9%. "Under 2%" is true only for recent years.
      Name the year (2022) or widen to "under 3%".

  "short-run marginal"  <->  the ~1% result
      Long-run marginal (retirement deferral, license renewal, uprates,
      North Anna Unit 3) implicates North Anna far more. Drop "short-run"
      and the stated definition no longer yields a small number.
      METHODOLOGY 54.


=== NUMBERS -- RECOMPUTED, SEE audit_framings.py FOR FRAMINGS ===

Scope 2 share, 54 completed   88.0% delivered / 88.7% consumptive -> "88%"
On-site share, 54 completed    2.9% delivered /  2.2% consumptive -> "under 3%"
absolute volumes              54 occupied = 7.09 MGD (7.03 consumptive);
                              all 243 = 46.19 (45.74). POST-RAMP. Pre-ramp
                              these were 10.49 and 49.60 -- if anyone quotes
                              the old numbers they are quoting installed
                              capacity as if it were energized load.
fleet level, cross-checked    54 occupied = 921 MW energized of 1,359 MW
                              installed. Vintage-matched to 2024 this is
                              0.93x JLARC's independent ~842 MW anchor
                              (1.23x before the ramp). METHODOLOGY 62.2.
>40% to Lake Anna             43% of Scope 2. Share of a consumption total,
                              so invariant to fleet size and basis.
+/-60% uncertainty            tier-4 median (generic fitted curve, n=141).
                              Tier 1 (permit-observed, n=45) is +/-26%. Keep
                              it scoped to "inferred from floor area".
80 km                         Lake Anna is ~50 miles from the county.
under 2% to Lake Anna         NOT definitional. Nuclear IS a PJM marginal
                              resource: 0.39% (2022), 0.62% (2023),
                              1.00-1.35% (2019-21) of real-time marginal
                              units -- SOM Table 3-69, printed p.200. York
                              works out at 0.87% on 2022 shares. The old
                              "0%" came from the p.125 summary sentence,
                              which does not enumerate every fuel.


=== OPEN QUESTIONS -- have answers ready, do not bluff ===

"243 / 54 buildings"   Classification is a judgement from county GIS +
                       permits. No independent list exists. Honest answer:
                       "this is what the county records show".
"88%"                  Denominator includes Scope 3 -- a literature range
                       (5-15%, Privette et al.), no PDF in corpus, ledgered
                       as not machine-verifiable. Scope 2/(Scope 1+2) alone
                       is ~97%. Know which denominator you mean.
ICPRB comparison       Their assessment is basin-wide; ours is one county.
                       The SCOPE claim is sound, the geography is not
                       like-for-like.
JLARC validation       Currently NOT in the abstract (author's choice).
                       {spare} chars spare if wanted back. It is the only
                       external check on any number here.
"""
    open("AGU26_SUBMISSION.txt", "w").write(out)
    print(f"abstract {n_abs}/2000 (ascii {n_ascii}), {spare} spare | "
          f"plain {len(pls.split())}/200 | title {len(TITLE)}")
    # the packet must actually contain the abstract -- the failure this replaces
    assert abs_ in open("AGU26_SUBMISSION.txt").read(), "abstract missing from packet"
    print("verified: abstract body present in packet")


if __name__ == "__main__":
    main()
