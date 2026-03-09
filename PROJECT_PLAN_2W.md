# Open Warsong — Prioritized 2-Week Execution Plan

This plan turns current milestone status into a focused two-week implementation schedule.

## Planning assumptions

- Baseline tooling remains green (`pytest -q`).
- The local ROM file is available for disassembly runs.
- Priority is reducing disassembly fallback output while building reusable validation tests.

## Goal by end of week 2

- Reduce pass-1 fallback unknowns with targeted high-frequency family coverage and a stable weekly trend table (`known`, `unknown`, `% unknown`).
- Convert initial vector handlers from placeholder ownership to validated ownership (first concrete M1 movement).
- Land first true subsystem correctness fixtures (battle/map/script behavior) so M5 progress reflects gameplay logic rather than decoder-only tests.

## Current baseline snapshot

- M0 (tooling): 100%
- M1 (vector ownership): 0%
- M2 (code/data separation): 0%
- M3 (symbol map growth): 0%
- M4 (disasm hardening): 66%
- M5 (subsystem tests): 34%
- M6 (parity): 0%

Approximate weighted project completion baseline: ~33% (recalibrated).

---

## Week 1 (Days 1–5): Decoder throughput and measurement

### Priority 1 — High-impact decoder additions

1. Add destination-memory `move` forms and common ALU forms (`add/sub/cmp`) for frequently observed addressing modes.
2. Add/verify related control-flow idioms that appear in startup and core loops.
3. Refactor decoding helpers only where it reduces test surface duplication.

**Deliverables**
- Extended opcode coverage in `open-warsong/disasm.py`.
- New deterministic unit tests in `tests/test_disasm.py` for each newly decoded family.

### Priority 2 — Full-pass quality trend instrumentation

1. Run `scripts/disasm_pass.py` against the ROM.
2. Capture unknown fallback metrics and summary deltas vs. prior run.
3. Record trend data in milestone notes.

**Deliverables**
- Refreshed `open/disasm/summary.json` and/or disassembly outputs.
- Milestone note update with unknown-word delta.

### Priority 3 — Metrics discipline + symbol promotion

1. Record one canonical trend snapshot per day (`known`, `unknown`, `% unknown`, decoded count) to avoid progress-percent drift.
2. Promote a first batch of temporary labels to semantic names based on newly decoded routines.

**Deliverables**
- Short trend table entry in `MILESTONES.md` updates.
- Initial updates to `open/symbols.csv` with evidence-backed naming.

### Week 1 exit criteria

- Decoder tests stay green.
- One full-pass trend measurement is recorded.
- At least one symbol-promotion batch is landed.

---

## Week 2 (Days 6–10): Vector ownership and subsystem scaffolding

### Priority 1 — Vector table ownership kickoff

1. Validate reset/exception vector handlers from existing disassembly context.
2. Replace placeholder vector entries with verified labels/comments.
3. Document unresolved vectors with explicit TODO rationale.

**Deliverables**
- Updates to `open/vectors_68k.asm` with verified handler ownership.

### Priority 2 — Progressive code/data separation (initial regions)

1. Select 1–2 high-confidence regions and convert from fallback blobs to structured code/data.
2. Add labels and boundaries needed for future incremental replacement.

**Deliverables**
- First converted regions with reduced generic fallback use.

### Priority 3 — Subsystem test scaffolding

1. Group existing decoder tests toward subsystem buckets (startup/battle/map/AI where possible).
2. Add at least one deterministic subsystem behavior fixture (even if narrow).

**Deliverables**
- Expanded test organization and at least one subsystem-level deterministic check.

### Week 2 exit criteria

- Vector ownership is visibly progressed with concrete verified handlers.
- First code/data region conversions are merged.
- Subsystem-level deterministic test scaffolding is present and passing.

---

## Target milestone movement by end of this plan

- M1: 0% → 10–20%
- M2: 0% → 8–15%
- M3: 0% → 8–12%
- M4: 66% → 72–78%
- M5: 34% → 42–50%
- M6: 0% (define parity scenarios but no completion claim yet)

Expected overall project completion after this plan: ~38–45% (conservative).

## Risk management

- **Risk:** ROM-dependent trend checks fail due to path/environment drift.
  - **Mitigation:** keep ROM-path validation in pre-run check step and capture failure mode in milestone notes.
- **Risk:** Decoder scope creeps into low-yield opcode families.
  - **Mitigation:** prioritize by frequency in disasm output and stop after measurable unknown-word reduction.
- **Risk:** Symbol naming churn.
  - **Mitigation:** batch symbol promotion with short rationale notes.

## Daily operating cadence (lightweight)

1. Implement one decoder/symbol/vector slice.
2. Run targeted tests + full `pytest -q`.
3. If ROM available, run disasm pass and note unknown trend.
4. Update `MILESTONES.md` with evidence and next ordered actions.


## Execution progress updates

### 2026-03-09 (iteration 25)

- Completed another Week 1 decoder-throughput slice by adding shift/rotate instruction-family coverage in `open-warsong/disasm.py` with deterministic tests.
- Refreshed full-pass quality metrics: `known_instructions` improved to `19,147` and `unknown_words` reduced to `17,072` (`max_instructions: 40,000`).
- Next in plan order: begin Week 2 Priority 1 by validating and claiming the first vector handlers, then add the first true subsystem fixture to unblock meaningful M5 movement.

### 2026-03-09 (iteration 26)

- Started Week 2 Priority 1 (vector ownership kickoff) by replacing placeholder vector labels with explicit owned targets in `open/vectors_68k.asm`.
- Claimed and documented concrete handler ownership for reset/default exception/H-Blank/V-Blank targets (`$450A`, `$4500`, `$483E`, `$482E`) and normalized null TRAP/reserved vectors to `v_null`.
- Next in plan order: split the shared `$4500` exception target into verified per-exception handler labels and add first subsystem-level deterministic fixture work.

