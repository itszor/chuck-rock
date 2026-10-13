#!/usr/bin/env python3
"""The hard disc installation the game's Read_Me describes: disc 2's CHUCK
directory inside !Chuck (game/!Chuck/CHUCK). GAME then finds
<Chuck$Dir>.CHUCK.DRIVETEST and loads everything from there, rather than
asking for disc 2 and reading :0.CHUCK.

    install.py          (after weave.py extract: game/!Chuck and game/CHUCK)

The TOSEC zip already holds the installed copy, CHUCK inside !Chuck.

The TOSEC dump of disc 2 has a damaged CHUCK.EGFX5 (level 5's enemy
graphics): ninety-odd bytes are off, and it fails its decruncher's checksum.
The zip's copy is whole. The build goes ahead with either, but says so.
"""
import hashlib
import os
import shutil

GAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'game')
src, app = os.path.join(GAME, 'CHUCK'), os.path.join(GAME, '!Chuck')
if os.path.isdir(src):
    shutil.copytree(src, os.path.join(app, 'CHUCK'), dirs_exist_ok=True)
    shutil.rmtree(src)
assert os.path.isdir(os.path.join(app, 'CHUCK')), 'no CHUCK directory (disc 2) in game/!Chuck'

DAMAGED_EGFX5 = '4a5d15515b952cef4413c65cdb4dba0b274f93d20cbe5bd0dcbcbdcb6fade66b'
for f in os.listdir(os.path.join(app, 'CHUCK')):
    p = os.path.join(app, 'CHUCK', f)
    if f.split(',')[0].upper() == 'EGFX5' and hashlib.sha256(open(p, 'rb').read()).hexdigest() == DAMAGED_EGFX5:
        print('install.py: warning: this CHUCK.EGFX5 (the TOSEC disc 2 dump\'s) is damaged - some of\n'
              '    level 5\'s enemies will look wrong. The TOSEC zip "Chuck Rock (1991)(Krisalis).zip"\n'
              '    has an intact copy.')
