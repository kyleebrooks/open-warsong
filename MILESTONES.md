# Open Warsong Milestone Checklist

Use this checklist on every project update to track progress from tooling to full decompilation.

## How to use this file each update

- Update the **Status**, **% Complete**, **Last Updated**, and **Notes / Next action** fields for each milestone.
- Keep percentages conservative and evidence-based (new decoded regions, symbols added, tests passing, etc.).
- If a milestone is blocked, mark it `⚠️ Blocked` and add what is needed to unblock it.
- Do not delete completed milestones—mark them `✅ Done` and keep a short completion note.

---

## Milestone 0 — Baseline tooling health

- **Status:** ✅ Done
- **% Complete:** 100%
- **Last Updated:** _YYYY-MM-DD_
- **Definition of done:** ROM validation, project bootstrap, analysis export, disasm pass, patch build/apply, and roundtrip verification all working.
- **Evidence:** Existing scripts and unit tests are present and passing.
- **Notes / Next action:** Maintain green tests as features are added.

## Milestone 1 — Vector table ownership

- **Status:** ⬜ Not started / 🔄 In progress / ✅ Done
- **% Complete:** 0%
- **Last Updated:** _YYYY-MM-DD_
- **Definition of done:** Replace placeholder vector stubs in `open/vectors_68k.asm` with validated handlers and labels.
- **Tracking metrics:**
  - Number of vectors with verified handler code
  - Number of vectors still marked TODO
- **Notes / Next action:**

## Milestone 2 — Progressive code/data separation

- **Status:** ⬜ Not started / 🔄 In progress / ✅ Done
- **% Complete:** 0%
- **Last Updated:** _YYYY-MM-DD_
- **Definition of done:** Replace generic binary includes/fallback data blocks with identified code/data regions and labels.
- **Tracking metrics:**
  - Count of regions converted from generic blobs to structured assembly/data
  - Approximate decoded ROM coverage (%)
- **Notes / Next action:**

## Milestone 3 — Symbol map growth

- **Status:** ⬜ Not started / 🔄 In progress / ✅ Done
- **% Complete:** 0%
- **Last Updated:** _YYYY-MM-DD_
- **Definition of done:** `open/symbols.csv` contains robust subsystem labels (engine init, battle, map scripts, AI, UI, etc.).
- **Tracking metrics:**
  - Total symbol count
  - New symbols added this update
  - Number of symbols promoted from temporary names to semantic names
- **Notes / Next action:**

## Milestone 4 — Pass-1 disassembly hardening

- **Status:** 🔄 In progress
- **% Complete:** 10%
- **Last Updated:** 2026-03-09
- **Definition of done:** Replace `dc.w` fallback areas in `open/disasm/code_pass1.asm` with hand-verified instructions and control flow.
- **Tracking metrics:**
  - Number of fallback lines replaced this update
  - Number of new validated functions/blocks
- **Notes / Next action:** Expand decoder coverage further (common arithmetic/data-move instructions) and reduce unknown-word count in pass output.

## Milestone 5 — Subsystem correctness tests

- **Status:** 🔄 In progress
- **% Complete:** 5%
- **Last Updated:** 2026-03-09
- **Definition of done:** Add deterministic tests for battle calculations, map scripts, AI behavior, and other decoded subsystems.
- **Tracking metrics:**
  - Test count by subsystem
  - Pass rate
  - Regression bugs caught
- **Notes / Next action:** Keep adding deterministic tests for newly decoded instruction groups and eventually promote toward subsystem-level behavior tests.

## Milestone 6 — Rebuild and behavioral parity target

- **Status:** ⬜ Not started / 🔄 In progress / ✅ Done
- **% Complete:** 0%
- **Last Updated:** _YYYY-MM-DD_
- **Definition of done:** Rebuilt output and/or execution behavior matches original ROM expectations for defined scenarios.
- **Tracking metrics:**
  - Number of parity scenarios defined
  - Number passing
  - Remaining mismatches by subsystem
- **Notes / Next action:**

---

## Update log template (append each update)

### Update _YYYY-MM-DD_

- **Summary:**
- **Milestones advanced:**
  - M#: from __% → __%
- **Evidence produced:**
  - Files changed:
  - Tests/checks run:
- **Risks / blockers:**
- **Next planned actions (ordered):**


### Update 2026-03-09

- **Summary:** Advanced disassembly hardening by decoding additional common 68k instruction families and adding disassembly quality metrics.
- **Milestones advanced:**
  - M4: from 0% → 10%
  - M5: from 0% → 5%
- **Evidence produced:**
  - Files changed: `open-warsong/disasm.py`, `scripts/disasm_pass.py`, `tests/test_disasm.py`
  - Tests/checks run: `pytest -q` (12 passed)
- **Risks / blockers:** Decoder still has limited opcode coverage, so unknown fallback words remain substantial in real ROM output.
- **Next planned actions (ordered):**
  1. Add more 68k decoder coverage for common move/arithmetic/control instructions.
  2. Run disasm pass on ROM and track unknown-word trend over time.
  3. Start pinning decoded routines to subsystem labels for symbol growth.
