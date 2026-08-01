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
      On the DELIVERED basis the on-site share of the 54 is 3.2%, not under
      3% (2.4% consumptive). Drop "consumptive" and this must become
      "under 4%". METHODOLOGY 53.

  "completed" (NOT "operating")  <->  the 0.8 utilization factor
      BuildingStatus is a CONSTRUCTION status; all 54 are Completed/Finaled.
      NO field in the dataset indicates energization, commissioning or IT
      load. "Operating" turns an estimate of installed capacity into an
      apparent measurement of live facilities. METHODOLOGY 57.1.

  "Whether a given watershed is implicated"  <->  destination is undetermined
      Marginal accounting establishes Lake Anna = 0. It does NOT establish
      where the water goes instead (Roanoke swings 0.00-11.11 MGD, and that
      is an upper bound). Do not let this drift back to "each approach
      identifies different watersheds". METHODOLOGY 57.2.

  "short-run marginal"  <->  the 0% result
      Long-run marginal (retirement deferral, license renewal, uprates,
      North Anna Unit 3) DOES implicate North Anna. Drop "short-run" and
      the stated definition no longer yields 0%. METHODOLOGY 54.


=== NUMBERS -- RECOMPUTED, SEE audit_framings.py FOR FRAMINGS ===

Scope 2 share, 54 completed   87.7% delivered / 88.5% consumptive -> "88%"
On-site share, 54 completed    3.2% delivered /  2.4% consumptive -> "under 3%"
>40% to Lake Anna             43% of Scope 2. Share of a consumption total,
                              so invariant to fleet size and basis.
+/-60% uncertainty            tier-4 median (generic fitted curve, n=141).
                              Tier 1 (permit-observed, n=45) is +/-26%. Keep
                              it scoped to "inferred from floor area".
80 km                         Lake Anna is ~50 miles from the county.
0% to Lake Anna               Definitional: nuclear is absent from PJM's
                              marginal fuel-share list (SOM 2023 p.125).


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
