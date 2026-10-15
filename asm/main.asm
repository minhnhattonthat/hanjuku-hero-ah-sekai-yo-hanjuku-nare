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

; --- system-string printer ($00:F086, bank $01): new code 01 lo hi bank = continue reading at that long address.
org $00F09A
    jml SysFetch
    nop

org $208000
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
    rtl
