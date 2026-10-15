; Hanjuku Hero English: engine hooks. Applied by build.py with asar 1.91 (--fix-checksum=off).
; ROM grows to 2 MiB (LoROM). New code/tables in bank $20; text data in banks $21+ (written by build.py).
lorom

ScriptTab = $208800      ; 256 x 3 bytes (ptr16, bank) per event-script id
MsgTab    = $208B00      ; 72 x 3 bytes, menu/system messages
BtlTab    = $209000      ; 1152 x 3 bytes, battle messages

org $00FFD7
    db $0B               ; ROM size: 2 MiB

; --- event-script loader ($04:8871: id $08D0 -> bank/pointer). Exit to $04:88F0 with A16=ptr, DB=bank.
org $048871
    jsl ScriptLoad
    jmp $88F0

; --- menu/system message loader ($04:E40B: A=id). Exit to $04:E424 with M8, Y=ptr, DB=bank.
org $04E40B
    jsl MsgLoad
    jmp $E424

; --- battle message pointer ($03:CCE5): $F4-$F6 = long pointer of message $E0.
org $03CCE5
    jsl BtlLoad
    nop #17

; The battle printer assumed text and names share bank $17: the per-char delay ($03:D016) and panel updates
; reset $F6 to $17. Re-load the message bank before each character fetch, and read inserted names from $17.
MsgBank = $7FFFF0
MsgFlag = $7FFFF1
RtlInBank03 = $038027      ; any $6B byte in bank $03, used as a trampoline back to bank $20
org $03CD1B
    jsl BtlFetch         ; was: JSR $D016 / LDA [$F4],y
    nop
org $03CE77
    jsl BtlName          ; was: STY $F4 / JSR $D112
    nop

; --- system-string printer ($00:F086, bank $01): new code 01 lo hi bank = continue reading at that long address.
org $00F09A
    jml SysFetch
    nop

; --- title screen: English mode-7 tiles $01-$E2 over the decompressed block at $7F:8000 before its DMA
org $09F2CE
    jsl TitlePatch
    nop

org $208000
TitlePatch:
    php
    phb
    rep #$30
    lda.l $7F84BC        ; signature of the title block (tile $13), so other users of this DMA are untouched
    cmp #$0606
    bne .skip
    lda.l $7F84BE
    cmp #$0107
    bne .skip
    phx
    phy
    lda #$387F
    ldx #$8000
    ldy #$8000
    db $54, $7F, $3E     ; mvn dest $7F, src $3E (assets/title_m7_en.bin at $3E:8000)
    ply
    plx
    plb
    plp
    jsl $03FAA3          ; the copy took most of a frame: wait for vblank again before the game's DMA
    ; copyright sprite tiles (two lines = top/bottom halves of 16x16 sprites, VRAM $5E00 / $5F00, 14 tiles each)
    rep #$10
    lda #$01
    sta $4300
    lda #$18
    sta $4301
    lda #$3E
    sta $4304
    ldx #$5E00
    stx $2116
    ldx #$B880
    stx $4302
    ldx #$01C0
    stx $4305
    lda #$01
    sta $420B
    ldx #$5F00
    stx $2116
    ldx #$BA40
    stx $4302
    ldx #$01C0
    stx $4305
    lda #$01
    sta $420B
    ldx #$0040           ; restore the VRAM address the game's next DMA expects
    stx $2116
    lda #$00
    sta $4300
    rtl
.skip:
    plb
    plp
    lda #$00
    sta $4300
    rtl

SysFetch:
    lda $0000,y
    cmp #$01
    bne .chk
    lda $0003,y
    pha
    rep #$20
    lda $0001,y
    tay
    sep #$20
    plb
    lda $0000,y
.chk:
    cmp #$00
    beq .end
    jml $00F0A4
.end:
    jml $00F09F

ScriptLoad:
    rep #$30
    lda $08D0
    and #$00FF
    pha
    asl
    clc
    adc $01,s
    tax
    pla
    sep #$20
    lda.l ScriptTab+2,x
    sta $094D
    pha
    plb
    rep #$20
    lda.l ScriptTab,x
    ldy #$0000
    rtl

MsgLoad:
    rep #$20
    and #$00FF
    pha
    asl
    clc
    adc $01,s
    tax
    pla
    lda.l MsgTab,x
    tay
    sta $0948
    sep #$20
    lda.l MsgTab+2,x
    sta $094D
    pha
    plb
    rtl

BtlLoad:
    rep #$20
    lda $E0
    and #$07FF
    pha
    asl
    clc
    adc $01,s
    tax
    pla
    lda.l BtlTab,x
    sta $F4
    sep #$20
    lda.l BtlTab+2,x
    sta $F6
    sta.l MsgBank
    lda #$A5             ; magic value (WRAM is not cleared at power-on)
    sta.l MsgFlag
    rtl

BtlFetch:                ; call $03:D016 (ends in RTS) via the RTL trampoline, then fetch from the message bank
    phk
    per .back-1
    pea.w RtlInBank03-1
    jml $03D016
.back:
    lda.l MsgFlag        ; only while a message started by BtlLoad is printing (the loop also prints names)
    cmp #$A5
    bne .plain
    lda.l MsgBank
    sta $F6
    lda [$F4],y
    bne .done
    lda #$00             ; end of message: leave message mode (A=0, Z set for the caller's BNE)
    sta.l MsgFlag
.done:
    rtl
.plain:
    lda [$F4],y
    rtl

BtlName:                 ; name insert: names live in bank $17
    sty $F4
    lda #$17
    sta $F6
    phk
    per .back-1
    pea.w RtlInBank03-1
    jml $03D112
.back:
    rtl
