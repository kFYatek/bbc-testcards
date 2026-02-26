#!/bin/sh
set -e
OUTDIR="${OUTDIR:=.}"
SCRIPTDIR="$(dirname "$0")"
export EQUALIZE=0
export COLORCONV=0
export COLORSPACE=709
export SCALE=0

# HD testcards, never scale
env CARD=0 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardX.png"
env CARD=13 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCard3D.png"

# Mechanical test cards, don't scale for now
env CARD=1 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TelevisionEye.png"
env CARD=3 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/CircleAndLine.png"

# Test Cards A and B are high-res reproductions, just scale them down
env CARD=4 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardA.png"
env CARD=5 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardB.png"

# These test cards look like JPEGs, but they were originally optical, so just scale them down with more aggressive antiringing
env CARD=2 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TuningSignal.png"
env CARD=6 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardC.png"
env CARD=7 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardD.png"
env CARD=8 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardFOpt.png"

# Electronic SD test cards
env CARD=9 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardFElec.png"
env CARD=10 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardJ.png"
env CARD=11 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardFWide.png"
env CARD=12 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardW.png"
