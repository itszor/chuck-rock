Chuck Rock (Core Design, 1991; Archimedes conversion by Krisalis) - static recompilation
======================================================================================

A recipe: this repository holds no game data. It rebuilds the game as a
native executable from your own copy, recognised by content (recipe.json),
so it can be shared without distributing the game.

    ./build.sh "Chuck Rock (1991)(Krisalis)(Disk 1 Of 2).adf" "Chuck Rock (1991)(Krisalis)(Disk 2 Of 2).adf"
    ./build.sh "Chuck Rock (1991)(Krisalis).zip"          (the TOSEC zip: a hard disc installation)
    cd recomp && ./chuckrock

build.sh runs recipe.json's steps with SuperSpider's tools/weave.py
(~/stuff/superspider, or $SUPERSPIDER; $SS below): it extracts the discs,
installs disc 2's CHUCK directory inside !Chuck (tools/install.py), runs
the game's own decruncher on the levels' code (tools/unpack.py), analyses
and translates everything, and links it with libroger (~/stuff/libroger,
or make ROGER=...). Needs python3, OCaml/dune, gcc and SDL3.

The inputs, either form:

- the two ADFS E discs (TOSEC "Chuck Rock (1991)(Krisalis)(Disk 1 Of 2).adf"
  and "(Disk 2 Of 2).adf"): !Chuck on disc 1, CHUCK (the levels) on disc 2.
  This dump of disc 2 has a damaged CHUCK.EGFX5 (level 5's enemy graphics):
  about 90 bytes are off, it fails its decruncher's checksum, and the
  first 5,000 of its 32,000 unpacked bytes come out wrong (the cruncher
  works backwards from the end). The build goes ahead, and
  tools/install.py says so.
- the TOSEC zip "Chuck Rock (1991)(Krisalis).zip": !Chuck with CHUCK
  copied inside it, as the Read_Me tells hard disc users to, and RISC OS
  filetypes. Its EGFX5 is intact.

    extracted/disc1, disc2   the discs (or extracted/zip, zip-chuck), via weave.py
    game/!Chuck              libroger's appdir (../game), CHUCK inside it
    unpacked/                tools/unpack.py: each level's code (code1-5) and
                             GAME with it (level1-5), and their roots
    analysis/                SuperSpider's analyses; *.roots: gap entries (make roots)
    recomp/gen*/             the C translations
    recomp/chuckrock         the game

Committed: recipe.json, build.sh, tools/install.py, tools/unpack.py,
recomp/Makefile, recomp/game.c, recomp/chuckrock.ini, analysis/*.roots (when there are any),
this file.

How the game is put together
----------------------------

It's the Amiga game, converted: the graphics are still Amiga bitplanes
(converted to Archimedes pixels as they're loaded), the level files are
crunched with an Amiga-style backwards cruncher, and they hold big-endian
words.

!Run sets Chuck$Dir, RMLoads TequeMemory (MemMod: *TequeMem, which frees
memory) and MusicModule 1.02 (MUSMOD2: Krisalis' tracker player, also in
Lemmings, a later build here), runs JSTest (is a joystick module loaded?)
and then `ChuckProg 8000`:

- ChuckProg, the loader (absolute, &8000): the Krisalis logo (KRIS), the
  intro sequence (CHSEQ1-4), then it copies a stub to &28800 that
  OS_File-loads GAME over it at &8000 and jumps there.
- GAME (absolute, &8000-&25928): the game. It looks for
  <Chuck$Dir>.CHUCK.DRIVETEST: found (a hard disc), it loads everything
  from <Chuck$Dir>.CHUCK, otherwise it asks for disc 2 and reads :0.CHUCK.
  Each level n loads LGFXn, DGFXn (crunched: into a buffer at &4BF78, then
  decrunched by &D524), DINSDTn and CODEn.
- CODEn is the level's own code, crunched: its object types (records of
  six words from &25FBC: animations and a handler) and their handlers. GAME
  decrunches it to &25928, just past its own end, and calls the handlers
  through each object's field, `stmdb sp!,{pc}; ldr pc,[r6,#&2C]`.

What's translated (recomp/Makefile, make regen):

- GAME (gen/), ChuckProg (genprog/) and MusicModule (genmus/, as a module at
  &1800000).
- Each level's code (genlevel1-5/). tools/unpack.py runs GAME's decruncher
  under $SS/tools/arm2.py. The level's code calls GAME's routines,
  including its literal thunks (`bl &8178; DCD value`: the thunk loads the
  word after the call and returns past it), so it is analysed as part of
  one image with GAME (unpacked/level<n>: GAME is exactly &1D928 bytes, so
  the level's code follows at &25928), and `superspider gen --range
  25928-28c9c` translates only the level's part; its calls into GAME are
  dispatched to GAME's translation. Its roots are the handlers: words in
  the level that point at an instruction in it.
- libroger selects a level's image when GAME loads CODEn into its buffer
  (roger_program.at: a packed file's load address, not its image's base).
- ChuckProg's stub at &28800 (7 instructions) is interpreted.

Everything else is translated: headless runs of each level (--level=N),
walking, jumping and fighting, and a game played to game over and back to
the title, reach no untranslated code.

What SuperSpider and libroger needed
------------------------------------

- SuperSpider gen: `stmdb sp!,{pc}` was always taken to be followed by an
  NV filler (`stmdb sp!,{pc}; movnv; b X`, a call). Chuck Rock also has
  `stmdb sp!,{pc}; ldr pc,[r6,#&2C]; movnv`, a call through an object, and
  the translation jumped over the ldr. Now the filler is only skipped when
  it is one.
- SuperSpider gen --range FROM-TO: translate part of an analysed image (an
  overlay analysed together with the program it's loaded beside).
- tools/adf_extract.py: a '/' in a RISC OS name (disc 1's Serport/JS)
  becomes '.' on the host, instead of stopping the extraction.
- libroger: roger_program.at, for overlays loaded somewhere else and
  unpacked into place.

Running it
----------

    ./chuckrock                 as !Run: logo, intro, title
    ./chuckrock --level=3       a new game starts at level 3 (1-5)

Keys (from the game's Read_Me): Z left, X right, P up (jump), L down,
Space fire. F1 pauses, F4 turns the internal speaker on and off, F5/F6 set
the title music's volume, Escape abandons the game, and Ctrl-Escape on the
title screen quits. Fire skips the intro. A game controller: the stick or
D-pad moves, A fires, B jumps, Start pauses.

Not supported: the RTFM and serial port joystick interfaces (JoyMod, the
Serport module); a controller stands in for them.
