# BintyPOS status

Version: 0.2.0 (framework documentation milestone)
Date: 2026-11-02
Canonical repository: Kenway-Creative/BintyPOS
Default branch: main
Demo: GitHub Pages workflow present; successful public deployment not independently confirmed.

## Evidence
- Existing index.html and README.md committed.
- Architecture specification and proposed OpenAPI contract added.
- No backend, authenticated manager access, secure stock reservation, Dojo/Spektrix connection or live card processing.
- Verification in this milestone: document commits acknowledged by GitHub; no automated application tests or API implementation yet.
- Prior application JS was syntax-checked; full browser regression checks remain pending.

## Quality policy
One feature per cycle. No false pass reports. Preserve exact commit SHA and changelog. Prefer tests and modular code to cosmetic changes. Treat all UI demo PINs as publicly known.
Next: introduce independently testable catalog projection/permissions functions, add regression tests, and retain static GitHub Pages compatibility.
