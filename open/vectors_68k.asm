; Genesis 68000 exception/interrupt vectors (Warsong)
cpu 68000

; Owned vector targets from ROM header.
v_init_stack_pointer   equ $00FFFE00
v_reset                equ $0000450A
v_default_exception    equ $00004500
v_irq_level6_vblank    equ $0000482E
v_irq_level4_hblank    equ $0000483E
v_null                 equ $00000000

Vectors:
    dc.l v_init_stack_pointer     ; 00 Initial SSP
    dc.l v_reset                  ; 01 Reset PC
    dc.l v_default_exception      ; 02 Bus Error
    dc.l v_default_exception      ; 03 Address Error
    dc.l v_default_exception      ; 04 Illegal Instruction
    dc.l v_default_exception      ; 05 Divide by Zero
    dc.l v_default_exception      ; 06 CHK
    dc.l v_default_exception      ; 07 TRAPV
    dc.l v_default_exception      ; 08 Privilege Violation
    dc.l v_default_exception      ; 09 Trace
    dc.l v_default_exception      ; 10 Line-A
    dc.l v_default_exception      ; 11 Line-F
    dc.l v_default_exception      ; 12 Reserved
    dc.l v_default_exception      ; 13 Reserved
    dc.l v_default_exception      ; 14 Reserved
    dc.l v_default_exception      ; 15 Uninitialized IRQ
    dc.l v_default_exception      ; 16 Reserved
    dc.l v_default_exception      ; 17 Reserved
    dc.l v_default_exception      ; 18 Reserved
    dc.l v_default_exception      ; 19 Reserved
    dc.l v_default_exception      ; 20 Reserved
    dc.l v_default_exception      ; 21 Reserved
    dc.l v_default_exception      ; 22 Reserved
    dc.l v_default_exception      ; 23 Reserved
    dc.l v_default_exception      ; 24 Spurious
    dc.l v_default_exception      ; 25 IRQ 1
    dc.l v_default_exception      ; 26 IRQ 2
    dc.l v_default_exception      ; 27 IRQ 3
    dc.l v_irq_level4_hblank      ; 28 IRQ 4 / H-Blank
    dc.l v_default_exception      ; 29 IRQ 5
    dc.l v_irq_level6_vblank      ; 30 IRQ 6 / V-Blank
    dc.l v_default_exception      ; 31 IRQ 7
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

; TODO(M1): split v_default_exception into specific handler labels once verified bodies are decoded.
