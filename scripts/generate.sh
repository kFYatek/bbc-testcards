#!/bin/sh
set -e
OUTDIR="${OUTDIR:=.}"
SCRIPTDIR="$(dirname "$0")"
SCALE=
export SCALE

# HD testcards, never scale
env CARD=0 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - | env COLORSPACE=709 RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 1920x1080 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-709-video16-v4.icc" -define png:color-type=2 "$OUTDIR/TestCardX.png"
env CARD=13 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - | env COLORSPACE=709 RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 1920x1080 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-709-video16-v4.icc" -define png:color-type=2 "$OUTDIR/TestCard3D.png"

# Mechanical test cards, don't scale for now
env CARD=1 COLORCONV=4 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 1920x1080 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../Linear-gray-video16-v4.icc" -define png:color-type=0 "$OUTDIR/TelevisionEye.png"
env CARD=3 COLORCONV=4 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 1920x1080 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../Linear-gray-video16-v4.icc" -define png:color-type=0 "$OUTDIR/CircleAndLine.png"

# Test Cards A and B are high-res reproductions, just scale them down
env CARD=4 SCALE=1 SCALER=lanczos ANTIRING=1 vspipe "$SCRIPTDIR/extract.vpy" - | env CARD=4 SCALE=2 COLORSPACE=1 RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x378 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-1886-gray-video16-v4.icc" -define png:color-type=0 "$OUTDIR/TestCardA.png"
env CARD=5 SCALE=1 SCALER=lanczos ANTIRING=1 vspipe "$SCRIPTDIR/extract.vpy" - | env CARD=5 SCALE=2 COLORSPACE=1 RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x378 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-1886-gray-video16-v4.icc" -define png:color-type=0 "$OUTDIR/TestCardB.png"

# These test cards look like JPEGs, but they were originally optical, so just scale them down with more aggressive antiringing
env CARD=2 SCALE=1 SCALER=lanczos ANTIRING=1 vspipe "$SCRIPTDIR/extract.vpy" - | env CARD=2 SCALE=2 COLORSPACE=1 RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x378 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-1886-gray-video16-v4.icc" -define png:color-type=0 "$OUTDIR/TuningSignal.png"
env CARD=6 SCALE=1 SCALER=lanczos ANTIRING=1.5 vspipe "$SCRIPTDIR/extract.vpy" - | env CARD=6 SCALE=2 COLORSPACE=1 RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x378 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-1886-gray-video16-v4.icc" -define png:color-type=0 "$OUTDIR/TestCardC.png"
env CARD=7 SCALE=1 SCALER=lanczos ANTIRING=1.5 vspipe "$SCRIPTDIR/extract.vpy" - | env CARD=7 SCALE=2 COLORSPACE=1 RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x378 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-1886-gray-video16-v4.icc" -define png:color-type=0 "$OUTDIR/TestCardD.png"
env CARD=8 SCALE=1 SCALER=lanczos ANTIRING=2 vspipe "$SCRIPTDIR/extract.vpy" - | env CARD=8 SCALE=2 RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x576 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-601-625-video16-v4.icc" -define png:color-type=2 "$OUTDIR/TestCardFOpt.png"

# Electronic SD test cards
env CARD=9 SCALE=3 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 788x576 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-601-625-video16-v4.icc" -define png:color-type=2 "$OUTDIR/TestCardFElec.png"
env CARD=10 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x576 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-601-625-video16-v4.icc" -define png:color-type=2 "$OUTDIR/TestCardJ.png"
env CARD=11 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x576 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-601-625-video16-v4.icc" -define png:color-type=2 "$OUTDIR/TestCardFWide.png"
env CARD=12 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x576 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-601-625-video16-v4.icc" -define png:color-type=2 "$OUTDIR/TestCardW.png"
