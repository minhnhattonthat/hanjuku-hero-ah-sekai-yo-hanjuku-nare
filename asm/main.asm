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

; --- title screen: English mode-7 tiles $01-$E2 and logo map (tools/title_logo.py)
org $09F2CE
    jsl TitlePatch
    nop

; --- labels the game wrote as LDA #tile / STA code (tools/immtext.py); English in Labels (tools/rawtext.py LABELS)
Labels = $209E00          ; 16 bytes per label, 00-terminated
RtlInBank04 = $048025
; battle command windows: tile row at X+$40 (stride 2) in $7E, X preserved
org $03D5CC
    lda #$03             ; きりふだ
    jsl BtlLabel
    rts
org $03D5E6
    lda #$02             ; たまごをつかう
    jsl BtlLabel
    rts
org $03D633
    lda #$04             ; たいきゃく
    jsl BtlLabel
    rts
org $03D64D
    lda #$05             ; たまごにもどれ
    jsl BtlLabel
    rts
org $03D67B
    lda #$01             ; もうこうげき (its tail at $D685 was a second entry: こうげき)
    jsl BtlLabel
    rts
org $03D685
    lda #$00
    jsl BtlLabel
    rts
org $03D69F
    lda #$06             ; おくのて
    jsl BtlLabel
    rts
; branch targets in the game's code (asar needs labels for branches, a bare $address assembles wrong)
org $03CE2A
InsTroopsDone:
org $03CFB8
BtlCharNext:
org $04C356
PanelEggDone:
org $04E713
AuditionEggDone:
; battle message name insert when the target is the troops: X advances past the label
org $03CE15
    lda #$07             ; へいし
    jsl BtlLabelAdv
    bra InsTroopsDone
; after a name insert the printer took the per-character exit ($CFB6: INX INX, INY), leaving a blank cell after
; every name ("Beets  attacks!"). English text has its own spaces: skip to the INY.
org $03CE2E
    brl BtlCharNext
org $03CE80
    brl BtlCharNext
; general panels: egg yes/no
org $04C33A
    lda #$08             ; あり (Dismiss panel, buffer $7E:8800)
    jsl PanelLabel
    bra PanelEggDone
org $04C349
    lda #$09             ; なし
    jsl PanelLabel
    bra PanelEggDone
org $04E6FA
    lda #$08             ; あり (audition stat block, putchar $04:E71C)
    jsl PutcLabel
    bra AuditionEggDone
org $04E709
    lda #$09             ; なし
    jsl PutcLabel
    bra AuditionEggDone

; --- episode title cards: English glyph strips (tools/cards.py at $3F:8000) instead of the kanji font in $7E
Cards = $3F8000           ; 24 x 4 bytes: glyph address, count, 0, 0; titles 0-11 then labels 12-23
org $09F613               ; label sprites: count and x (was 3 or 4 glyphs at x $68/$60)
    jsl CardLabelPos
    bra CardLabelPosDone
org $09F62C
CardLabelPosDone:
org $09F6D8               ; title x and line break: no episode-9 two-line case (cmp #$09)
    db $FF
org $09F76E
    db $FF
org $09F8B0               ; label glyphs (第N話), after the buffer clear
    jml CardLabel
org $09F8ED
CardLabelDone:
org $09F921               ; title glyphs, after the buffer clear
    jml CardTitle
org $09F960
CardTitleDone:

org $208000
TitlePatch:
    php
    phb
    rep #$30
    lda.l $7F84BC        ; signature of the title block (tile $13), so other users of this DMA are untouched
    cmp #$0606
    beq .sig2
    brl .skip
.sig2:
    lda.l $7F84BE
    cmp #$0107
    beq .matched
    brl .skip
.matched:
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
    ; Redraw only the title's 32x11 map, using the original tile budget $01-$C1.
    ; Mode 7 map is the low VRAM byte, stride 128 words; subtitle rows 13-14 stay intact.
    phy
    lda #$00
    sta $4300
    sta $2115
    lda #$18
    sta $4301
    ldx #$BC00           ; tools/title_logo.py MAP at $3E:BC00
    stx $4302
    ldy #$0000
.maprow:
    sty $2116
    ldx #$0020
    stx $4305
    lda #$01
    sta $420B
    rep #$20
    tya
    clc
    adc #$0080
    tay
    sep #$20
    cpy #$0580
    bne .maprow
    ply
    lda #$80
    sta $2115
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

LabelPtr:                ; A8 = label id -> Y = its address in bank $20, DB = $20 (caller saved Y and DB)
    rep #$20
    and #$00FF
    asl #4
    clc
    adc.w #Labels
    tay
    sep #$20
    phk
    plb
    rts

BtlLabel:                ; A8 = id, X = tile buffer base: tiles to $7E:0040+X, +2 per char; X, Y kept
    phx
    jsr BtlLabelLoop
    plx
    rtl

BtlLabelAdv:             ; same, X ends past the label
    jsr BtlLabelLoop
    rtl

BtlLabelLoop:
    phy
    phb
    jsr LabelPtr
.loop:
    lda $0000,y
    beq .end
    sta.l $7E0040,x
    inx #2
    iny
    bra .loop
.end:
    plb
    ply
    rts

PanelLabel:              ; A8 = id, X = column in the $7E:8800 panel buffer (+1 per char); Y kept
    phy
    phb
    jsr LabelPtr
.loop:
    lda $0000,y
    beq .end
    sta.l $7E8800,x
    inx
    iny
    bra .loop
.end:
    plb
    ply
    rtl

PutcLabel:               ; A8 = id, each char through the bank-$04 putchar $04:E71C; X, Y kept
    phy
    phb
    jsr LabelPtr
.loop:
    lda $0000,y
    beq .end
    phy
    xba
    lda $03,s            ; the caller's DB: the putchar reads its WRAM variables through DB
    pha
    plb
    xba
    phk
    per .back-1
    pea.w RtlInBank04-1
    jml $04E71C
.back:
    phk
    plb
    ply
    iny
    bra .loop
.end:
    plb
    ply
    rtl

BtlName:                 ; name insert: names live in bank $17; A = name index for $03:D112
    sty $F4
    pha
    lda #$17
    sta $F6
    pla
    phk
    per .back-1
    pea.w RtlInBank03-1
    jml $03D112
.back:
    rtl

CardLabelPos:            ; A8 = label glyph count, $F0 = x of the first sprite (centred: (16 - count) * 8); X kept
    phx
    lda $0308            ; episode 1-12
    clc
    adc #11
    jsr CardEntry
    lda.l Cards+2,x
    plx
    pha
    eor #$FF
    sec
    adc #16
    asl #3
    sta $F0
    pla
    rtl

CardLabel:               ; DB = $7E, buffer at $7E:D000 cleared
    lda $0308
    clc
    adc #11
    jsr CardEntry
    jsr CardCopy
    jml CardLabelDone

CardTitle:
    lda $0308
    dec
    jsr CardEntry
    lda.l Cards+2,x
    sta $030D            ; glyph count: the sprite placement centres and loops on it
    jsr CardCopy
    jml CardTitleDone

CardEntry:               ; A8 = entry -> X = entry * 4
    rep #$20
    and #$00FF
    asl #2
    tax
    sep #$20
    rts

CardCopy:                ; X = entry offset; glyphs to $7E:D000 like $09:F962 (16x16 sprite, 8 per row)
    lda.l Cards+2,x
    pha
    rep #$20
    lda.l Cards,x
    tax
    ldy #$D000
.glyph:
    lda #$000F
    db $54, $7E, $3F     ; mvn dest $7E, src $3F: tile TL
    tya
    clc
    adc #$0010
    tay
    lda #$000F
    db $54, $7E, $3F     ; TR
    tya
    clc
    adc #$01D0
    tay
    lda #$000F
    db $54, $7E, $3F     ; BL
    tya
    clc
    adc #$0010
    tay
    lda #$000F
    db $54, $7E, $3F     ; BR
    tya
    sec
    sbc #$01F0
    tay
    and #$01FF           ; 8 glyphs done: next sprite row
    bne +
    tya
    clc
    adc #$0200
    tay
+
    sep #$20
    lda 1,s
    dec
    sta 1,s
    rep #$20
    bne .glyph
    sep #$20
    pla
    rts

warnpc $208800
