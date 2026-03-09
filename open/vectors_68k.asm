; Genesis 68000 exception/interrupt vectors (Warsong)
cpu 68000

; Owned vector targets from ROM header.
v_init_stack_pointer   equ $00FFFE00
v_reset                equ $0000450A

; Most exception and low-priority IRQ vectors currently share the same
; ROM target ($4500). Keep individual labels to make ownership explicit and
; allow future per-vector split as handler bodies are decoded.
v_bus_error            equ $00004500
v_address_error        equ $00004500
v_illegal_instruction  equ $00004500
v_divide_by_zero       equ $00004500
v_chk_exception        equ $00004500
v_trapv_exception      equ $00004500
v_privilege_violation  equ $00004500
v_trace_exception      equ $00004500
v_line_a_emulator      equ $00004500
v_line_f_emulator      equ $00004500
v_reserved_12          equ $00004500
v_reserved_13          equ $00004500
v_reserved_14          equ $00004500
v_uninitialized_irq    equ $00004500
v_reserved_16          equ $00004500
v_reserved_17          equ $00004500
v_reserved_18          equ $00004500
v_reserved_19          equ $00004500
v_reserved_20          equ $00004500
v_reserved_21          equ $00004500
v_reserved_22          equ $00004500
v_reserved_23          equ $00004500
v_spurious_irq         equ $00004500
v_irq_level1           equ $00004500
v_irq_level2           equ $00004500
v_irq_level3           equ $00004500
v_irq_level5           equ $00004500
v_irq_level7           equ $00004500

v_irq_level6_vblank    equ $0000482E
v_irq_level4_hblank    equ $0000483E
v_null                 equ $00000000

Vectors:
    dc.l v_init_stack_pointer     ; 00 Initial SSP
    dc.l v_reset                  ; 01 Reset PC
    dc.l v_bus_error              ; 02 Bus Error
    dc.l v_address_error          ; 03 Address Error
    dc.l v_illegal_instruction    ; 04 Illegal Instruction
    dc.l v_divide_by_zero         ; 05 Divide by Zero
    dc.l v_chk_exception          ; 06 CHK
    dc.l v_trapv_exception        ; 07 TRAPV
    dc.l v_privilege_violation    ; 08 Privilege Violation
    dc.l v_trace_exception        ; 09 Trace
    dc.l v_line_a_emulator        ; 10 Line-A
    dc.l v_line_f_emulator        ; 11 Line-F
    dc.l v_reserved_12            ; 12 Reserved
    dc.l v_reserved_13            ; 13 Reserved
    dc.l v_reserved_14            ; 14 Reserved
    dc.l v_uninitialized_irq      ; 15 Uninitialized IRQ
    dc.l v_reserved_16            ; 16 Reserved
    dc.l v_reserved_17            ; 17 Reserved
    dc.l v_reserved_18            ; 18 Reserved
    dc.l v_reserved_19            ; 19 Reserved
    dc.l v_reserved_20            ; 20 Reserved
    dc.l v_reserved_21            ; 21 Reserved
    dc.l v_reserved_22            ; 22 Reserved
    dc.l v_reserved_23            ; 23 Reserved
    dc.l v_spurious_irq           ; 24 Spurious
    dc.l v_irq_level1             ; 25 IRQ 1
    dc.l v_irq_level2             ; 26 IRQ 2
    dc.l v_irq_level3             ; 27 IRQ 3
    dc.l v_irq_level4_hblank      ; 28 IRQ 4 / H-Blank
    dc.l v_irq_level5             ; 29 IRQ 5
    dc.l v_irq_level6_vblank      ; 30 IRQ 6 / V-Blank
    dc.l v_irq_level7             ; 31 IRQ 7
    dc.l v_null                   ; 32 TRAP #0
    dc.l v_null                   ; 33 TRAP #1
    dc.l v_null                   ; 34 TRAP #2
    dc.l v_null                   ; 35 TRAP #3
    dc.l v_null                   ; 36 TRAP #4
    dc.l v_null                   ; 37 TRAP #5
    dc.l v_null                   ; 38 TRAP #6
    dc.l v_null                   ; 39 TRAP #7
    dc.l v_null                   ; 40 TRAP #8
    dc.l v_null                   ; 41 TRAP #9
    dc.l v_null                   ; 42 TRAP #10
    dc.l v_null                   ; 43 TRAP #11
    dc.l v_null                   ; 44 TRAP #12
    dc.l v_null                   ; 45 TRAP #13
    dc.l v_null                   ; 46 TRAP #14
    dc.l v_null                   ; 47 TRAP #15
    dc.l v_null                   ; 48 Reserved
    dc.l v_null                   ; 49 Reserved
    dc.l v_null                   ; 50 Reserved
    dc.l v_null                   ; 51 Reserved
    dc.l v_null                   ; 52 Reserved
    dc.l v_null                   ; 53 Reserved
    dc.l v_null                   ; 54 Reserved
    dc.l v_null                   ; 55 Reserved
    dc.l v_null                   ; 56 Reserved
    dc.l v_null                   ; 57 Reserved
    dc.l v_null                   ; 58 Reserved
    dc.l v_null                   ; 59 Reserved
    dc.l v_null                   ; 60 Reserved
    dc.l v_null                   ; 61 Reserved
    dc.l v_null                   ; 62 Reserved
    dc.l v_null                   ; 63 Reserved

; NOTE(M1): vectors now have per-vector owned labels even where ROM currently points
; to shared handler code at $4500; split into distinct code labels as disassembly
; validates unique handler entry points.
