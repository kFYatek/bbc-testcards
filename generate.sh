#!/bin/sh
set -e
OUTDIR="${OUTDIR:=.}"
SCRIPTDIR="$(dirname "$0")"
EXT=png
RAW16="${RAW16:=0}"
if [ "$RAW16" -gt 0 ]; then
    EXT=data
fi

# HD testcards, never scale
env CARD=0 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - | env COLORSPACE=709 "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardX.$EXT"
env CARD=13 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - | env COLORSPACE=709 "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCard3D.$EXT"

# Test Cards A and B are high-res reproductions, just scale them down
env CARD=4 SCALER=ewa_lanczos ANTIRING=1 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardA.$EXT"
env CARD=5 SCALER=ewa_lanczos ANTIRING=1 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardB.$EXT"

# These test cards look like JPEGs, but they were originally optical, so just scale them down with more aggressive antiringing
env CARD=2 SCALER=ewa_lanczos ANTIRING=1 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TuningSignal.$EXT"
env CARD=6 SCALER=ewa_lanczos ANTIRING=1.5 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardC.$EXT"
env CARD=7 SCALER=ewa_lanczos ANTIRING=1.5 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardD.$EXT"
env CARD=8 SCALER=ewa_lanczos ANTIRING=2 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardFOpt.$EXT"

# Electronic SD test cards
env CARD=9 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardFElec.$EXT"
env CARD=10 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardJ.$EXT"
env CARD=11 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardFWide.$EXT"
env CARD=12 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardW.$EXT"
