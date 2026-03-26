#!/bin/sh
set -e
OUTDIR="${OUTDIR:=.}"
SCRIPTDIR="$(dirname "$0")"
SCALE=0
export SCALE

# HD testcards, never scale
env CARD=0 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TestCardX.tiff"
env CARD=13 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TestCard3D.tiff"

# Mechanical test cards, don't scale for now
env CARD=1 COLORCONV=4 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 1 rawfloat: rgb:- | magick -size 1920x1080 -define quantum:format=floating-point -depth 64 rgb:- +profile icc -profile "$SCRIPTDIR/../icc/Linear-gray.icc" "$OUTDIR/TelevisionEye.tiff"
env CARD=3 COLORCONV=4 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 1 rawfloat: rgb:- | magick -size 1920x1080 -define quantum:format=floating-point -depth 64 rgb:- +profile icc -profile "$SCRIPTDIR/../icc/Linear-gray.icc" "$OUTDIR/CircleAndLine.tiff"

# Test Cards A and B are high-res reproductions, just scale them down
env CARD=4 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 1 rawfloat: "$OUTDIR/TestCardA.tiff"
env CARD=5 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 1 rawfloat: "$OUTDIR/TestCardB.tiff"

# These test cards look like JPEGs, but they were originally optical, so just scale them down with more aggressive antiringing
env CARD=2 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 1 rawfloat: "$OUTDIR/TuningSignal.tiff"
env CARD=6 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 1 rawfloat: "$OUTDIR/TestCardC.tiff"
env CARD=7 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 1 rawfloat: "$OUTDIR/TestCardD.tiff"
env CARD=8 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardFOpt.tiff"

# Electronic SD test cards
env CARD=9 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardFElec.tiff"
env CARD=10 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardJ.tiff"
env CARD=11 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardFWide.tiff"
env CARD=12 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardW.tiff"
