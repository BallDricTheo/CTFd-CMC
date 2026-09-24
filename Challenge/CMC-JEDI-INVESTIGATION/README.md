# CMC DFIR - JEDI INVESTIGATION

Combined forensic challenge based on BSides NYC 2025 forensic artifacts.

## Stages

### Q1 - Secret Map
Analyze `map.jpg` metadata.

Expected technique:
- exiftool
- metadata analysis

### Q2 - Matryoshka Map
Continue analysis of `map.jpg`.

Expected techniques:
- binwalk
- foremost
- file carving
- embedded file extraction

### Q3 - Jedi use Windows Notepad?
Analyze `LocalState.zip`.

Expected techniques:
- Windows Notepad forensic artifacts
- TabState
- WindowState
- deleted/unsaved content reconstruction

## Flags

Q1:
flag{m47ry05hk4}

Q2:
flag{k3n081}

Q3:
flag{r5-d4_k-2so_bd-1}

## Original Source

BSides NYC 2025 CTF - Forensics
