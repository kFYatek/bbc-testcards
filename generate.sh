#!/bin/sh
set -e
OUTDIR="${OUTDIR:=.}"
SCRIPTDIR="$(dirname "$0")"
SCALE=
export SCALE

# HD testcards, never scale
env CARD=0 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - | env COLORSPACE=709 RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 1920x1080 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/ITU-709-video16-v4.icc" "$OUTDIR/TestCardX.png"
env CARD=13 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - | env COLORSPACE=709 RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 1920x1080 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/ITU-709-video16-v4.icc" "$OUTDIR/TestCard3D.png"

# Test Cards A and B are high-res reproductions, just scale them down
env CARD=4 SCALER=ewa_lanczos ANTIRING=1 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x378 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/ITU-601-625-video16-v4.icc" "$OUTDIR/TestCardA.png"
env CARD=5 SCALER=ewa_lanczos ANTIRING=1 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x378 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/ITU-601-625-video16-v4.icc" "$OUTDIR/TestCardB.png"

# These test cards look like JPEGs, but they were originally optical, so just scale them down with more aggressive antiringing
env CARD=2 SCALER=ewa_lanczos ANTIRING=1 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x378 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/ITU-601-625-video16-v4.icc" "$OUTDIR/TuningSignal.png"
env CARD=6 SCALER=ewa_lanczos ANTIRING=1.5 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x378 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/ITU-601-625-video16-v4.icc" "$OUTDIR/TestCardC.png"
env CARD=7 SCALER=ewa_lanczos ANTIRING=1.5 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x378 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/ITU-601-625-video16-v4.icc" "$OUTDIR/TestCardD.png"
env CARD=8 SCALER=ewa_lanczos ANTIRING=2 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x576 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/ITU-601-625-video16-v4.icc" "$OUTDIR/TestCardFOpt.png"

# Electronic SD test cards
env CARD=9 SCALE=3 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 788x576 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/ITU-601-625-video16-v4.icc" "$OUTDIR/TestCardFElec.png"
env CARD=10 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x576 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/ITU-601-625-video16-v4.icc" "$OUTDIR/TestCardJ.png"
env CARD=11 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x576 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/ITU-601-625-video16-v4.icc" "$OUTDIR/TestCardFWide.png"
env CARD=12 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x576 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/ITU-601-625-video16-v4.icc" "$OUTDIR/TestCardW.png"
