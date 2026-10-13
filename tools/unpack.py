#!/usr/bin/env python3
"""Each level's code, unpacked by GAME's own decruncher.

    unpack.py           game/!Chuck/CHUCK/CODE1-5 -> unpacked/code1-5, and
                        unpacked/level1-5 (GAME with the level's code after
                        it) and their roots, unpacked/level1-5.roots

A level's CODEn holds the level's own routines (its objects' handlers: GAME
calls them through the object records, ldr pc,[r6,#&2C]) and their tables,
crunched. GAME loads it into its buffer at &4BF78 and unpacks it to &25928
(&8F5C, then &8E14 -> &D524, a backwards decruncher from the Amiga original:
a big-endian length, the data, then its unpacked length and a checksum). Here
that routine runs under SuperSpider's tools/arm2.py.

The level's code calls GAME's routines, among them its literal thunks (bl to
one consumes the word after the call), so it is analysed together with GAME:
GAME ends at &25928, where the level's code goes, and the two make one image
at &8000 (unpacked/level<n>). Only the level's part of it is translated
(superspider gen --range: recomp/genlevel<n>/). Its entry points are the
handlers its tables (the words before its first instruction) point to.
"""
import os
import struct
import sys

SS = os.environ.get('SUPERSPIDER', os.path.expanduser('~/stuff/superspider'))
sys.path.insert(0, os.path.join(SS, 'tools'))
import arm2  # noqa: E402

TOP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
APP = os.path.join(TOP, 'game', '!Chuck')
OUT = os.path.join(TOP, 'unpacked')
BUFFER, LEVEL_CODE, UNPACK = 0x4BF78, 0x25928, 0xD524
STACK, DONE = 0x7F000, 0x3FFFFF0
LEVELS = 5


def find(d, name):
    """a RISC OS file in a host directory: any case, any ,load-exec suffix"""
    for f in os.listdir(d):
        if f.split(',')[0].lower() == name.lower():
            return os.path.join(d, f)
    raise FileNotFoundError(os.path.join(d, name))


def unpack(game, packed):
    m = arm2.ARM(memsize=0x4000000)
    m.mem[0x8000:0x8000 + len(game)] = game
    m.mem[BUFFER:BUFFER + len(packed)] = packed
    m.r[9], m.r[10] = BUFFER, LEVEL_CODE
    m.r[13], m.r[14] = STACK - 4, DONE
    struct.pack_into('<I', m.mem, STACK - 4, DONE)      # (it returns with ldmia sp!,{pc})
    m.r[15] = UNPACK
    while m.r[15] != DONE:
        m.step()
        if m.steps > 50_000_000:
            raise RuntimeError('unpack: no end, pc=&%X' % m.r[15])
    n = struct.unpack_from('>I', packed, 4 + struct.unpack_from('>I', packed, 0)[0] - 4)[0]
    return bytes(m.mem[LEVEL_CODE:LEVEL_CODE + n])


def handlers(data):
    """the handlers: words in the level's code that point into it at an
    instruction (one always executed) - its object types' handler fields
    (records of six words from &25FBC) and the handlers its code installs
    (bl to a literal thunk, the handler, str r1,[r11,#&2C])"""
    w = struct.unpack('<%dI' % (len(data) // 4), data[:len(data) & ~3])
    return sorted({x for x in w if LEVEL_CODE <= x < LEVEL_CODE + 4 * len(w) and x & 3 == 0
                   and w[(x - LEVEL_CODE) // 4] >> 28 == 0xE})


def main():
    os.makedirs(OUT, exist_ok=True)
    game = open(find(APP, 'GAME'), 'rb').read()
    assert 0x8000 + len(game) == LEVEL_CODE, 'GAME is %d bytes' % len(game)
    for k in range(1, LEVELS + 1):
        data = unpack(game, open(find(os.path.join(APP, 'CHUCK'), 'CODE%d' % k), 'rb').read())
        open(os.path.join(OUT, 'code%d' % k), 'wb').write(data)
        open(os.path.join(OUT, 'level%d' % k), 'wb').write(game + data)
        hs = handlers(data)
        with open(os.path.join(OUT, 'level%d.roots' % k), 'w') as f:
            f.write('# CODE%d\'s handlers, from its tables (tools/unpack.py)\n' % k)
            f.writelines('%x\n' % a for a in hs)
        print('code%d: %d bytes at &%X, %d handlers' % (k, len(data), LEVEL_CODE, len(hs)))


if __name__ == '__main__':
    main()
