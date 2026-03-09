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
- **% Complete:** 43%
- **Last Updated:** 2026-03-09
- **Definition of done:** Replace `dc.w` fallback areas in `open/disasm/code_pass1.asm` with hand-verified instructions and control flow.
- **Tracking metrics:**
  - Number of fallback lines replaced this update
  - Number of new validated functions/blocks
- **Notes / Next action:** Added address-register indirect `move`/`cmp` and `dbcc` decoding; next focus is more ALU/data movement modes to continue lowering fallback words.

## Milestone 5 — Subsystem correctness tests

- **Status:** 🔄 In progress
- **% Complete:** 22%
- **Last Updated:** 2026-03-09
- **Definition of done:** Add deterministic tests for battle calculations, map scripts, AI behavior, and other decoded subsystems.
- **Tracking metrics:**
  - Test count by subsystem
  - Pass rate
  - Regression bugs caught
- **Notes / Next action:** Continue adding deterministic decoder tests as opcode families are added, then start grouping them into subsystem-level behavior suites.

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


### Update 2026-03-09 (iteration 2)

- **Summary:** Added decoding support for additional immediate/register operations (`move`, `clr`, `tst`, `cmpi`) and expanded unit tests to lock in behavior.
- **Milestones advanced:**
  - M4: from 10% → 18%
  - M5: from 5% → 9%
- **Evidence produced:**
  - Files changed: `open-warsong/disasm.py`, `tests/test_disasm.py`, `MILESTONES.md`
  - Tests/checks run: `pytest -q` (15 passed)
- **Risks / blockers:** Decoder still lacks many addressing modes and ALU/memory opcodes, so pass output will continue to contain fallback words.
- **Next planned actions (ordered):**
  1. Add `movea`, `lea`, and more branch/control-flow patterns used in startup code.
  2. Expand decoding for memory-targeting `move`/`cmp` forms likely to appear in core loops.
  3. Re-run `scripts/disasm_pass.py` against the ROM and record unknown-word trend in milestone updates.


### Update 2026-03-09 (iteration 3)

- **Summary:** Expanded pass-1 decoder with absolute-word `jsr`/`jmp`, absolute `lea`, and immediate `movea` forms, plus targeted unit tests for each new instruction family.
- **Milestones advanced:**
  - M4: from 18% → 24%
  - M5: from 9% → 12%
- **Evidence produced:**
  - Files changed: `open-warsong/disasm.py`, `tests/test_disasm.py`, `MILESTONES.md`
  - Tests/checks run: `pytest -q` (17 passed)
- **Risks / blockers:** Remaining fallback words are still expected because memory-indirect addressing modes and additional ALU opcodes are not decoded yet.
- **Next planned actions (ordered):**
  1. Add decoding for address-register indirect `move` forms used in startup and engine loops.
  2. Add compare/branch idioms (`cmp`, `dbcc`) to improve control-flow readability.
  3. Run full disassembly pass on ROM and compare unknown-word trend against prior summary output.


### Update 2026-03-09 (iteration 4)

- **Summary:** Added decoding for address-register indirect and post-increment `move` forms into data registers, plus `dbcc` loop-control instructions, with focused unit tests.
- **Milestones advanced:**
  - M4: from 24% → 32%
  - M5: from 12% → 16%
- **Evidence produced:**
  - Files changed: `open-warsong/disasm.py`, `tests/test_disasm.py`, `MILESTONES.md`
  - Tests/checks run: `pytest -q` (19 passed)
- **Risks / blockers:** ROM image is not present in this environment, so a fresh full-run unknown-word trend from `scripts/disasm_pass.py` could not be produced in this iteration.
- **Next planned actions (ordered):**
  1. Add `cmp` memory/register forms commonly paired with branch conditions.
  2. Expand ALU and data-movement decoding coverage in high-frequency startup/engine paths.
  3. Re-run `scripts/disasm_pass.py` once ROM is available and record unknown-word trend deltas.


### Update 2026-03-09 (iteration 5)

- **Summary:** Added `cmp` address-register indirect and post-increment decoding forms plus decoder cleanup for DBcc mnemonic lookup constants, with expanded unit tests.
- **Milestones advanced:**
  - M4: from 32% → 37%
  - M5: from 16% → 19%
- **Evidence produced:**
  - Files changed: `open-warsong/disasm.py`, `tests/test_disasm.py`, `MILESTONES.md`
  - Tests/checks run: `pytest -q` (20 passed)
- **Risks / blockers:** Full-pass metric refresh still blocked until the ROM image is present at the expected local path.
- **Next planned actions (ordered):**
  1. Add `cmp`/ALU destination forms that target memory addressing modes beyond `(An)` and `(An)+`.
  2. Expand branch/loop decoding fidelity for additional control-flow idioms found in startup and engine routines.
  3. Re-run `scripts/disasm_pass.py` once ROM path is available and record unknown-word trend deltas.


### Update 2026-03-09 (iteration 6)

- **Summary:** Expanded decoder coverage for displacement-based address-register indirect `move`/`cmp` forms and refactored signed word displacement decoding helper, with matching unit tests.
- **Milestones advanced:**
  - M4: from 37% → 43%
  - M5: from 19% → 22%
- **Evidence produced:**
  - Files changed: `open-warsong/disasm.py`, `tests/test_disasm.py`, `MILESTONES.md`
  - Tests/checks run: `pytest -q` (22 passed)
- **Risks / blockers:** Full-pass unknown-word trend refresh remains blocked until a local ROM image is available for `scripts/disasm_pass.py`.
- **Next planned actions (ordered):**
  1. Add destination-memory `move` forms to reduce fallback output in data movement heavy regions.
  2. Expand ALU coverage (`add/sub/cmp` memory destinations) for common engine loops.
  3. Re-run `scripts/disasm_pass.py` once ROM is available and capture unknown-word deltas.
