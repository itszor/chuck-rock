#!/bin/sh
# Build Chuck Rock from your own copy of the game:
#     ./build.sh "Chuck Rock (1991)(Krisalis)(Disk 1 Of 2).adf" "Chuck Rock (1991)(Krisalis)(Disk 2 Of 2).adf"
#     ./build.sh "Chuck Rock (1991)(Krisalis).zip"      (the hard disc installation)
# then: cd recomp && ./chuckrock
# The steps are recipe.json's "build", run by SuperSpider's tools/weave.py.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
SUPERSPIDER="${SUPERSPIDER:-$HOME/stuff/superspider}"
[ $# -gt 0 ] || { echo "usage: $0 DISC1.adf DISC2.adf | GAME.zip" >&2; exit 2; }
(cd "$SUPERSPIDER" && dune build)
WEAVE_RECIPES="$HERE" exec python3 -I "$SUPERSPIDER/tools/weave.py" build "$@"
