#!/bin/sh
set -e
OUTDIR="${OUTDIR:=.}"
SCRIPTDIR="$(dirname "$0")"
SCALE=
export SCALE

# Work around some race conditions in libplacebo on macOS
export MVK_CONFIG_MAX_ACTIVE_METAL_COMMAND_BUFFERS_PER_QUEUE=1

# HD testcards, never scale
env CARD=0 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TestCardX.png"
env CARD=13 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TestCard3D.png"

# Mechanical test cards, don't scale for now
env CARD=1 COLORCONV=4 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - \
| "$SCRIPTDIR/convert.py" rawfloat: raw16: \
| magick -size 1920x1080 -depth 16 rgb:- \
    -crop 448x1064+736+8 -bordercolor '#eb00eb00eb00' -border 100x8 rgb:- \
| magick -size 648x1080 -depth 16 rgb: \
    -filter Lanczos -resize 42x1080\! -crop 30x1080+6+0 -filter Cubic -resize 30x70\! \
    +profile icc -profile "$SCRIPTDIR/../icc/Linear-gray-video16-v4.icc" \
    -define png:color-type=0 "$OUTDIR/TelevisionEye.png"

env CARD=3 COLORCONV=4 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - \
| "$SCRIPTDIR/convert.py" rawfloat: raw16: \
| magick -size 1920x1080 -depth 16 rgb:- \
    -crop 1420x1012+250+58 -bordercolor '#eb00eb00eb00' -border 10x1174 rgb:- \
| magick -size 1440x3360 -depth 16 rgb:- \
    -filter Lanczos -resize 30x3360\! -filter Cubic -resize 30x70\! \
    +profile icc -profile "$SCRIPTDIR/../icc/Linear-gray-video16-v4.icc" \
    -define png:color-type=0 "$OUTDIR/CircleAndLine.png"

# Test Cards A and B are high-res reproductions, just scale them down
env CARD=4 SCALE=1 SCALER=lanczos ANTIRING=1 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --card 4 --scale 2 --resampler hybrid --output-colorspace 1 rawfloat: "$OUTDIR/TestCardA.png"
env CARD=5 SCALE=1 SCALER=lanczos ANTIRING=1 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --card 5 --scale 2 --resampler hybrid --output-colorspace 1 rawfloat: "$OUTDIR/TestCardB.png"

# These test cards look like JPEGs, but they were originally optical, so just scale them down with more aggressive antiringing
env CARD=2 SCALE=1 SCALER=lanczos ANTIRING=1 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --card 2 --scale 2 --resampler hybrid --output-colorspace 1 rawfloat: "$OUTDIR/TuningSignal.png"
env CARD=6 SCALE=1 SCALER=lanczos ANTIRING=1.5 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --card 6 --scale 2 --resampler hybrid --output-colorspace 1 rawfloat: "$OUTDIR/TestCardC.png"
env CARD=7 SCALE=1 SCALER=lanczos ANTIRING=1.5 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --card 7 --scale 2 --resampler hybrid --output-colorspace 1 rawfloat: "$OUTDIR/TestCardD.png"
env CARD=8 SCALE=1 SCALER=lanczos ANTIRING=2 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --card 8 --scale 2 --resampler hybrid rawfloat: "$OUTDIR/TestCardFOpt.png"

# Electronic SD test cards
env CARD=9 SCALE=3 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardFElec-788.png"
env CARD=9 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardFElec.png"
env CARD=10 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardJ.png"
env CARD=11 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardFWide.png"
env CARD=12 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardW.png"
