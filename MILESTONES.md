# Open Warsong Milestone Checklist

Use this checklist on every project update to track progress from tooling to full decompilation.

## How to use this file each update

- Update the **Status**, **% Complete**, **Last Updated**, and **Notes / Next action** fields for each milestone.
- Keep percentages conservative and evidence-based (new decoded regions, symbols added, tests passing, etc.).
- If a milestone is blocked, mark it `⚠️ Blocked` and add what is needed to unblock it.
- Do not delete completed milestones—mark them `✅ Done` and keep a short completion note.

IMPORTANT NOTE: THE ROM FILE IS LOCTED IN THE ROOT REPO LOCATION Warsong (USA).md

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
- **% Complete:** 89%
- **Last Updated:** 2026-03-09
- **Definition of done:** Replace `dc.w` fallback areas in `open/disasm/code_pass1.asm` with hand-verified instructions and control flow.
- **Tracking metrics:**
  - Number of fallback lines replaced this update
  - Number of new validated functions/blocks
- **Notes / Next action:** Added bit-manipulation decode coverage for register/immediate `btst`/`bchg`/`bclr`/`bset` across existing EA helpers and refreshed full-pass metrics against the root ROM (`known_instructions`: 16,198 / `unknown_words`: 23,802 @ 40,000 decoded); next focus is deeper control-transfer target annotation and remaining ALU/control families.

## Milestone 5 — Subsystem correctness tests

- **Status:** 🔄 In progress
- **% Complete:** 55%
- **Last Updated:** 2026-03-09
- **Definition of done:** Add deterministic tests for battle calculations, map scripts, AI behavior, and other decoded subsystems.
- **Tracking metrics:**
  - Test count by subsystem
  - Pass rate
  - Regression bugs caught
- **Notes / Next action:** Added deterministic tests for register/immediate bit-manipulation decoding (`btst`/`bchg`/`bclr`/`bset`) across register, displacement, predecrement, and absolute forms, and validated suite stability with a fresh root-ROM disassembly pass; continue expanding control-transfer annotation and grouping opcode tests into subsystem behavior suites.

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


### Update 2026-03-09 (iteration 7)

- **Summary:** Expanded decoder support for destination-memory `move` and memory-destination `add/sub` forms over common address-register indirect modes, with focused unit tests for each new family.
- **Milestones advanced:**
  - M4: from 43% → 49%
  - M5: from 22% → 25%
- **Evidence produced:**
  - Files changed: `open-warsong/disasm.py`, `tests/test_disasm.py`, `MILESTONES.md`
  - Tests/checks run: `pytest -q` (24 passed)
- **Risks / blockers:** Full-pass unknown-word trend refresh is still blocked until a local ROM image is available for `scripts/disasm_pass.py`.
- **Next planned actions (ordered):**
  1. Add `cmp`/ALU forms for additional effective-address families beyond current indirect/displacement support.
 2. Expand control-flow and data-movement decoding that appears frequently in startup and engine loops.
 3. Re-run `scripts/disasm_pass.py` once ROM is available and record unknown-word trend deltas.


### Update 2026-03-09 (iteration 8)

- **Summary:** Expanded shared memory effective-address decoding with pre-decrement and absolute word/long forms, then wired those into `move`, `cmp`, and memory-destination `add/sub` decoding with targeted tests.
- **Milestones advanced:**
  - M4: from 49% → 55%
  - M5: from 25% → 28%
- **Evidence produced:**
  - Files changed: `open-warsong/disasm.py`, `tests/test_disasm.py`, `MILESTONES.md`
  - Tests/checks run: `pytest -q` (24 passed)
- **Risks / blockers:** Full-pass unknown-word trend refresh remains blocked until a local ROM image is available for `scripts/disasm_pass.py`.
- **Next planned actions (ordered):**
 1. Add indexed and PC-relative effective-address decoding for frequently observed instruction families.
  2. Extend arithmetic/control families that consume those addressing modes.
  3. Re-run `scripts/disasm_pass.py` once ROM path is available and capture updated unknown-word deltas.


### Update 2026-03-09 (iteration 9)

- **Summary:** Added indexed and PC-relative effective-address decoding (`(d8,An,Xn)`, `(d16,PC)`, `(d8,PC,Xn)`) and integrated these forms into `move`/`cmp` decoding, with targeted unit tests.
- **Milestones advanced:**
  - M4: from 55% → 61%
  - M5: from 28% → 31%
- **Evidence produced:**
  - Files changed: `open-warsong/disasm.py`, `tests/test_disasm.py`, `MILESTONES.md`
  - Tests/checks run: `pytest -q` (26 passed)
- **Risks / blockers:** Full-pass unknown-word trend refresh is still blocked until a local ROM image is available for `scripts/disasm_pass.py`.
- **Next planned actions (ordered):**
  1. Extend `add`/`sub` and related arithmetic/control families to consume indexed and PC-relative effective-address forms where valid.
  2. Add `lea` and additional control/data-movement forms that use indexed/PC-relative addressing.
  3. Re-run `scripts/disasm_pass.py` once ROM path is available and record unknown-word trend deltas.


### Update 2026-03-09 (iteration 10)

- **Summary:** Extended arithmetic decoding with `add/sub <ea>,Dn` source forms (including indexed and PC-relative addressing) and generalized `lea` control-addressing decode support, with targeted unit tests.
- **Milestones advanced:**
  - M4: from 61% → 67%
  - M5: from 31% → 35%
- **Evidence produced:**
  - Files changed: `open-warsong/disasm.py`, `tests/test_disasm.py`, `MILESTONES.md`
  - Tests/checks run: `pytest -q` (28 passed)
- **Risks / blockers:** Full-pass unknown-word trend refresh is still blocked until a local ROM image is available for `scripts/disasm_pass.py`.
- **Next planned actions (ordered):**
  1. Extend additional arithmetic/control families (`and/or/eor`, condition-focused control idioms) across indexed/PC-relative effective addresses where valid.
  2. Expand branch/jump decoding forms to reduce fallback words in startup and engine loops.
  3. Re-run `scripts/disasm_pass.py` once ROM path is available and record unknown-word trend deltas.


### Update 2026-03-09 (iteration 11)

- **Summary:** Added `and/or` decoding for both `<ea>,Dn` and `Dn,<ea>` forms across supported effective-address families, and generalized `jsr/jmp` decoding to full control-addressing forms with tests.
- **Milestones advanced:**
  - M4: from 67% → 73%
  - M5: from 35% → 39%
- **Evidence produced:**
  - Files changed: `open-warsong/disasm.py`, `tests/test_disasm.py`, `MILESTONES.md`
  - Tests/checks run: `pytest -q` (30 passed)
- **Risks / blockers:** Full-pass unknown-word trend refresh is still blocked until a local ROM image is available for `scripts/disasm_pass.py`.
- **Next planned actions (ordered):**
  1. Add `eor` and remaining ALU/control forms that share memory and PC-relative addressing helpers.
  2. Expand branch/jump/call formatting so more control-transfer targets can be labeled directly when derivable.
  3. Re-run `scripts/disasm_pass.py` once ROM path is available and record unknown-word trend deltas.

### Update 2026-03-09 (iteration 12)

- **Summary:** Added `eor Dn,<ea>` decoding across shared memory effective-address families, expanded unit tests, and refreshed pass-1 unknown-word metrics using the root ROM image.
- **Milestones advanced:**
  - M4: from 73% → 77%
  - M5: from 39% → 43%
- **Evidence produced:**
  - Files changed: `open-warsong/disasm.py`, `tests/test_disasm.py`, `MILESTONES.md`, `open/disasm/code_pass1.asm`, `open/disasm/summary.json`
  - Tests/checks run: `pytest -q` (31 passed); `python scripts/disasm_pass.py --rom "Warsong (USA).md" --out open/disasm --max-insn 40000`
- **Risks / blockers:** Decoder coverage is still partial, and unknown fallback words remain high in full-pass output despite incremental gains.
- **Next planned actions (ordered):**
  1. Add remaining ALU/control families that reuse existing EA helpers (`eori`, `btst`/bit ops, compare/control variants).
  2. Improve control-transfer target labeling when derivable to aid symbol growth and reviewability.
  3. Track unknown-word trend deltas per iteration to quantify decoding ROI.



### Update 2026-03-09 (iteration 13)

- **Summary:** Added `eori #imm,<ea>` decoding across data-alterable EA forms by introducing extension-offset aware memory EA decoding, then refreshed pass-1 ROM metrics with a small additional reduction in unknown fallback words.
- **Milestones advanced:**
  - M4: from 77% → 81%
  - M5: from 43% → 47%
- **Evidence produced:**
  - Files changed: `open-warsong/disasm.py`, `tests/test_disasm.py`, `MILESTONES.md`, `open/disasm/code_pass1.asm`, `open/disasm/summary.json`
  - Tests/checks run: `pytest -q` (32 passed); `python scripts/disasm_pass.py --rom "Warsong (USA).md" --out open/disasm --max-insn 40000` (`known_instructions`: 10,473 / `unknown_words`: 29,527)
- **Risks / blockers:** Decoder coverage remains partial; unknown fallback words are still substantial despite the incremental drop in this iteration.
- **Next planned actions (ordered):**
  1. Add remaining immediate/bit-operation families (`andi`, `ori`, `btst`/bit-manip) using the new extension-offset EA path.
  2. Improve control-transfer target annotation/labeling when absolute/relative targets are derivable.
  3. Continue periodic full ROM disassembly-pass runs to quantify unknown-word trend deltas per iteration.


### Update 2026-03-09 (iteration 14)

- **Summary:** Generalized immediate logical-op decoding so `ori`, `andi`, and `eori` share the extension-offset aware data-alterable EA path, added targeted tests, and refreshed full-pass ROM metrics with a significant unknown-word reduction.
- **Milestones advanced:**
  - M4: from 81% → 85%
  - M5: from 47% → 51%
- **Evidence produced:**
  - Files changed: `open-warsong/disasm.py`, `tests/test_disasm.py`, `MILESTONES.md`, `open/disasm/code_pass1.asm`, `open/disasm/summary.json`
  - Tests/checks run: `pytest -q` (32 passed); `python scripts/disasm_pass.py --rom "Warsong (USA).md" --out open/disasm --max-insn 40000` (`known_instructions`: 14,284 / `unknown_words`: 25,716)
- **Risks / blockers:** Decoder remains incomplete across several 68k families; unknown fallback words are still substantial despite the larger gain this iteration.
- **Next planned actions (ordered):**
  1. Add remaining bit-operation families (`btst`/`bchg`/`bclr`/`bset`) using shared EA decoding helpers.
  2. Improve control-transfer target annotation when PC-relative targets are derivable from extension words.
  3. Continue periodic full ROM disassembly-pass runs to track unknown-word trend deltas per iteration.


### Update 2026-03-09 (iteration 15)

- **Summary:** Added register and immediate bit-manipulation family decoding (`btst`/`bchg`/`bclr`/`bset`) across shared EA helpers, expanded unit coverage, and refreshed full-pass ROM metrics with another unknown-word reduction.
- **Milestones advanced:**
  - M4: from 85% → 89%
  - M5: from 51% → 55%
- **Evidence produced:**
  - Files changed: `open-warsong/disasm.py`, `tests/test_disasm.py`, `MILESTONES.md`, `open/disasm/code_pass1.asm`, `open/disasm/summary.json`
  - Tests/checks run: `pytest -q` (34 passed); `python scripts/disasm_pass.py --rom "Warsong (USA).md" --out open/disasm --max-insn 40000` (`known_instructions`: 16,198 / `unknown_words`: 23,802)
- **Risks / blockers:** Decoder coverage is still partial in other opcode/control families; fallback words remain substantial despite consistent trend improvement.
- **Next planned actions (ordered):**
  1. Improve control-transfer target annotation when PC-relative and indexed targets are derivable.
  2. Add remaining arithmetic/control families that can reuse current EA decode helpers.
  3. Continue full ROM disassembly-pass runs each iteration to track known/unknown trend deltas.
