#!/bin/sh
set -e
OUTDIR="${OUTDIR:=.}"
SCRIPTDIR="$(dirname "$0")"
export EQUALIZE=0
export COLORCONV=0
export SCALE=0

# HD testcards, never scale
env CARD=0 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TestCardX.tiff"
env CARD=13 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TestCard3D.tiff"

# Mechanical test cards, don't scale for now
env CARD=1 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TelevisionEye.tiff"
env CARD=3 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/CircleAndLine.tiff"

# Test Cards A and B are high-res reproductions, just scale them down
env CARD=4 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TestCardA.tiff"
env CARD=5 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TestCardB.tiff"

# These test cards look like JPEGs, but they were originally optical, so just scale them down with more aggressive antiringing
env CARD=2 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TuningSignal.tiff"
env CARD=6 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TestCardC.tiff"
env CARD=7 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TestCardD.tiff"
env CARD=8 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TestCardFOpt.tiff"

# Electronic SD test cards
env CARD=9 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TestCardFElec.tiff"
env CARD=10 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TestCardJ.tiff"
env CARD=11 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TestCardFWide.tiff"
env CARD=12 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TestCardW.tiff"
