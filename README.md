# open-warsong

This repository now includes a **practical reverse-engineering and modding starter kit** for the Sega Genesis ROM `Warsong (USA).md`.

> Important: a complete source-level decompilation of the game engine is a large multi-month effort. This repo is now set up so you can iteratively get there while keeping the game playable on PC from day one.

## What you can do now

- Parse and validate ROM metadata/checksum.
- Export deterministic ROM chunks and manifests for version control.
- Generate a first-pass 68000 vector-label assembly scaffold.
- Run static analysis passes (ASCII text extraction, absolute JSR/JMP target discovery, ROM fingerprint report).
- Build byte patches from JSON mod files.
- Launch the ROM from PC with a detected emulator (`retroarch`, `blastem`, `genesis-plus-gx`, `kega-fusion`).

## Quickstart

```bash
python scripts/check_rom.py --rom "Warsong (USA).md"
python scripts/bootstrap_project.py --rom "Warsong (USA).md" --out open
python scripts/build_patch.py --rom "Warsong (USA).md" --mod mods/example_header_mod.json --out mods/example_header_mod.ips --fix-checksum --out-rom open/warsong_modded.md
python scripts/analyze_rom.py --rom "Warsong (USA).md" --out open/analysis
python scripts/disasm_pass.py --rom "Warsong (USA).md" --out open/disasm
python scripts/verify_roundtrip.py --base-rom "Warsong (USA).md" --mod mods/example_header_mod.json --workdir open/verify
python scripts/run_on_pc.py --rom "Warsong (USA).md"
```

## Repo layout

- `scripts/check_rom.py`: validates local ROM path/size/hash before tooling runs.
- `scripts/bootstrap_project.py`: creates open reverse-engineering workspace.
- `scripts/build_patch.py`: JSON-based byte patcher + IPS writer.
- `scripts/analyze_rom.py`: static analysis exporter for RE artifacts.
- `scripts/disasm_pass.py`: control-flow aware first-pass 68k disassembly exporter.
- `scripts/apply_patch.py`: applies IPS to ROM with optional SHA guard/checksum repair.
- `scripts/verify_roundtrip.py`: validates JSON→IPS and IPS→ROM produce identical patched output.
- `scripts/run_on_pc.py`: emulator launcher helper.
- `open-warsong/romkit.py`: reusable ROM parsing/patching logic.
- `open-warsong/analysis.py`: analysis library for strings + control-flow hits.
- `open-warsong/disasm.py`: deterministic decoder/walker used to render pass-1 assembly.
- `mods/example_header_mod.json`: sample mod (safe header title edit).

## Next engineering steps

1. Use generated `open/vectors_68k.asm` as entry points.
2. Replace `incbin` chunks with real disassembly progressively.
3. Grow symbol map in `open/symbols.csv`.
4. Replace `dc.w` fallback regions in `open/disasm/code_pass1.asm` with hand-verified instruction decodes.
5. Add tests for each decoded subsystem (battle calc, map scripts, AI).


## Reliability improvements

- Patch specs can include `expect` bytes for safe fail-fast editing.
- `build_patch.py` supports `--fix-checksum` and optional `--out-rom` emission.
- Unit tests cover checksum writeback, patch expectations, IPS RLE handling, and round-trip (`tests/test_romkit.py`).


## ROM file policy

- The ROM binary itself is intentionally not tracked in git.
- Keep `Warsong (USA).md` locally in the repo root (or pass `--rom` paths to scripts).
- IPS outputs are also treated as build artifacts and should be generated locally.
