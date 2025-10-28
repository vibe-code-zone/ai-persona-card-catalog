<!-- Generated with Claude Code (claude-sonnet-4) via collaborative "vibe-coding" sessions -->

# CP1610 Assembly Programming Guide

## Overview
The CP1610 is the 16-bit microprocessor at the heart of the Intellivision console. This guide covers essential programming techniques for game development.

## Register Set
- **R0-R7**: 8 general-purpose 16-bit registers
- **R6**: Stack pointer (by convention)
- **R7**: Program counter

## Memory Map
```
$0000-$004F   System RAM (scratch pad)
$0100-$035F   System RAM (variables)
$0200-$02EF   Graphics RAM (BACKTAB)
$3800-$39FF   Graphics ROM (GROM)
$5000-$6FFF   Cartridge ROM space
$F000-$FFFF   Executive ROM (BIOS)
```

## Basic Instructions

### Data Movement
- `MVI addr, Rx` - Move immediate from memory to register
- `MVO Rx, addr` - Move from register to memory  
- `MVII #data, Rx` - Move immediate data to register

### Arithmetic
- `ADDR Rx, Ry` - Add register to register
- `SUBR Rx, Ry` - Subtract register from register
- `INCR Rx` - Increment register
- `DECR Rx` - Decrement register

### Branching
- `B addr` - Branch unconditionally
- `BC addr` - Branch if carry set
- `BNC addr` - Branch if carry clear
- `CALL addr` - Call subroutine
- `JR R5` - Return from subroutine

## Game Programming Patterns

### Initialization Sequence
```assembly
_init:  MVII    #$200, R6      ; Set stack pointer
        MVII    #$0, R0        ; Clear accumulator
        MVO     R0, $20        ; Clear interrupt enable
        
        ; Initialize graphics
        CALL    clear_screen
        CALL    setup_sprites
```

### Main Game Loop
```assembly
_game_loop:
        CALL    read_input     ; Get controller input
        CALL    update_game    ; Update game state
        CALL    draw_frame     ; Render graphics
        CALL    play_sound     ; Update audio
        B       _game_loop     ; Loop forever
```

### Sprite Animation
```assembly
_animate_sprite:
        MVI     frame_counter, R0
        INCR    R0
        CMPI    #8, R0         ; 8 frames per animation
        BNC     _no_reset
        MVII    #0, R0         ; Reset to frame 0
_no_reset:
        MVO     R0, frame_counter
        ADDR    R0, R0         ; Double for word addressing
        MVII    #sprite_frames, R1
        ADDR    R0, R1
        MVI@    R1, R0         ; Get frame data
        MVO     R0, $18        ; Write to MOB register
        JR      R5
```

## Memory Optimization Techniques

### Efficient Data Structures
- Pack multiple flags into single bytes
- Use lookup tables instead of calculations
- Align data on word boundaries for faster access

### Code Optimization
- Unroll small loops when memory permits
- Use register variables for frequently accessed data
- Combine operations where possible

## Common Pitfalls
- Forgetting to preserve registers in subroutines
- Stack overflow from nested calls
- Timing-sensitive code affected by interrupts
- Sprite collision detection edge cases