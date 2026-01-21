#!/bin/sh
set -e
OUTDIR="${OUTDIR:=.}"
SCRIPTDIR="$(dirname "$0")"

# HD testcards, never scale
env CARD=0 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - | env COLORSPACE=709 "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardX.png"
env CARD=13 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - | env COLORSPACE=709 "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCard3D.png"

# Test Cards A and B are high-res reproductions, just scale them down
env CARD=4 SCALER=Lanczos vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardA.png"
env CARD=5 SCALER=Lanczos vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardB.png"

# These test cards look like JPEGs, but they were originally optical, so just scale them down
env CARD=2 SCALER=Lanczos vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TuningSignal.png"
env CARD=6 SCALER=Lanczos vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardC.png"
env CARD=7 SCALER=Lanczos vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardD.png"
env CARD=8 SCALER=Lanczos vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardFOpt.png"

# Electronic SD test cards
env CARD=9 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardFElec.png"
env CARD=10 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardJ.png"
env CARD=11 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardFWide.png"
env CARD=12 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" > "$OUTDIR/TestCardW.png"
