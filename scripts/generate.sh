#!/bin/sh
set -e
OUTDIR="${OUTDIR:=.}"
SCRIPTDIR="$(dirname "$0")"
SCALE=
TMPFILES=
export SCALE

# Work around some race conditions in libplacebo on macOS
export MVK_CONFIG_MAX_ACTIVE_METAL_COMMAND_BUFFERS_PER_QUEUE=1

remove_tmpfiles() {
    rm -f $TMPFILES
}

trap remove_tmpfiles EXIT

# HD testcards, never scale
env CARD=0 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TestCardX.tiff"
env CARD=13 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --output-colorspace 709 rawfloat: "$OUTDIR/TestCard3D.tiff"

# Mechanical test cards, don't scale for now
env CARD=1 COLORCONV=4 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - \
| "$SCRIPTDIR/convert.py" rawfloat: rgb:- \
| magick -size 1920x1080 -define quantum:format=floating-point -depth 64 rgb:- \
    -crop 448x1064+736+8 -bordercolor white -border 100x8 gray:- \
| magick -size 648x1080 -define quantum:format=floating-point -depth 64 gray: \
    -filter Lanczos -resize 42x1080\! -crop 30x1080+6+0 -filter Cubic -resize 30x70\! \
    +profile icc -profile "$SCRIPTDIR/../icc/Linear-gray.icc" -compress lzw \
    "$OUTDIR/TelevisionEye.tiff"

env CARD=3 COLORCONV=4 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - \
| "$SCRIPTDIR/convert.py" rawfloat: rgb:- \
| magick -size 1920x1080 -define quantum:format=floating-point -depth 64 rgb:- \
    -crop 1420x1012+250+58 -bordercolor white -border 10x1174 gray:- \
| magick -size 1440x3360 -define quantum:format=floating-point -depth 64 gray: \
    -filter Lanczos -resize 30x3360\! -filter Cubic -resize 30x70\! \
    +profile icc -profile "$SCRIPTDIR/../icc/Linear-gray.icc" -compress lzw \
    "$OUTDIR/CircleAndLine.tiff"

# Test Cards A and B are high-res reproductions, just scale them down
env CARD=4 SCALE=1 SCALER=lanczos ANTIRING=1 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --card 4 --scale 2 --resampler hybrid --output-colorspace 1 rawfloat: "$OUTDIR/TestCardA.tiff"
env CARD=5 SCALE=1 SCALER=lanczos ANTIRING=1 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" --card 5 --scale 2 --resampler hybrid --output-colorspace 1 rawfloat: "$OUTDIR/TestCardB.tiff"

# Use Test Cards C and D from Richard T. Russell's GIFs
for CARD in C D; do
    "$SCRIPTDIR/resize.py" "$SCRIPTDIR/../sources/Test Card $CARD.gif" 720 468 tiff:- \
        --resampler hybrid \
    | magick tiff:- \
        -filter Point -resize 7200x468\! -filter Gaussian -resize 7200x378\! \
        -filter Point -resize 720x378\! \
        +profile icc -profile "$SCRIPTDIR/../icc/ITU-1886-gray.icc" -compress lzw \
        "$OUTDIR/TestCard$CARD.tiff"
done

# Compose the Tuning signal from both sources
TMPIMAGE="$(mktemp)"
TMPFILES="$TMPFILES $TMPIMAGE"
env CARD=2 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - \
| "$SCRIPTDIR/convert.py" --output-colorspace 1 rawfloat: tiff:- \
| magick tiff:- -crop 1400x1080+260+0 -filter Lanczos -resize 844x595\! \
    -evaluate Add 7.30593607305936% -evaluate Multiply 0.9798462330650822 -evaluate Pow 1.15 \
    -evaluate Add -7.30593607305936% -evaluate Max 0.0% tiff:"$TMPIMAGE"
magick "$SCRIPTDIR/../sources/d0bfa1fd2a9191224e10dafe9d9fc321dc254d80.jpg" \
    -define quantum:format=floating-point -depth 64 -evaluate Add -6.250095368886854% \
    -evaluate Multiply 1.1689319349315068 -type GrayScaleAlpha -fuzz '3%' -fill none \
    -draw "color 3,2 floodfill" -crop 764x576+2+0  tiff:- \
| magick tiff:"$TMPIMAGE" tiff:- -geometry +41+9 -composite -define quantum:format=floating-point \
    -depth 64 rgb:- \
| "$SCRIPTDIR/resize.py" rawf64:844x595 720 595 tiff:- --resampler hybrid \
| magick tiff:- \
    -filter Point -resize 7200x595\! -filter Gaussian -resize 7200x378\! \
    -filter Point -resize 720x378\! \
    +profile icc -profile "$SCRIPTDIR/../icc/ITU-1886-gray.icc" -compress lzw \
    "$OUTDIR/TuningSignal.tiff"

# Recreation of the optical Test Card F
env CARD=8 SCALE=1 SCALER=lanczos ANTIRING=2 vspipe "$SCRIPTDIR/extract.vpy" - \
| "$SCRIPTDIR/convert.py" --card 8 --scale 2 --resampler hybrid rawfloat: tiff:"$TMPIMAGE"
CARDIMAGE="$(mktemp)"
TMPFILES="$TMPFILES $CARDIMAGE"
magick tiff:"$TMPIMAGE" -crop 720x1+0+26 -filter Point -resize 720x2\! tiff:- \
| magick tiff:"$TMPIMAGE" -crop 720x552+0+24 \
    tiff:- -geometry +0+0 -composite tiff:"$CARDIMAGE"
magick tiff:"$TMPIMAGE" -crop 31x4+344+548 -flip tiff:- \
| magick tiff:"$CARDIMAGE" tiff:- -geometry +344+0 -composite tiff:"$CARDIMAGE"
magick tiff:"$TMPIMAGE" -crop 720x14+0+6 -filter Box -resize 720x1\! -filter Box -resize 720x23\! \
    tiff:"$TMPIMAGE"
"$SCRIPTDIR/tcfopt_firstline.py" \
| magick -size 720x1 -define quantum:format=floating-point -depth 64 gray:- \
    tiff:"$TMPIMAGE" -append tiff:"$CARDIMAGE" -append \
    +profile icc -profile "$SCRIPTDIR/../icc/BT.601_625-line.icc" \
    -compress lzw "$OUTDIR/TestCardFOpt.tiff"

# Recreation of the electronic Test Card F
env CARD=9 SCALE=3 vspipe "$SCRIPTDIR/extract.vpy" - \
| "$SCRIPTDIR/convert.py" rawfloat: tiff:- \
| magick tiff: "$SCRIPTDIR/../sources/TestCardFElec_reconstruction.tiff" -composite tiff:- \
| magick tiff:- \
    +profile icc -profile "$SCRIPTDIR/../icc/BT.601_625-line.icc" \
    -compress lzw "$OUTDIR/TestCardFElec-788.tiff"
magick "$OUTDIR/TestCardFElec-788.tiff" -bordercolor black -border 118x0 \
    -define quantum:format=floating-point -depth 64 rgb:- \
| "$SCRIPTDIR/resize.py" rawf64:1024x576 936 576 tiff:- --resampler hybrid \
| magick tiff:- \
    -crop 720x576+108+0 +profile icc -profile "$SCRIPTDIR/../icc/BT.601_625-line.icc" \
    -compress lzw "$OUTDIR/TestCardFElec.tiff"

# Recreation of the early widescreen version of Test Card F
env CARD=11 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: tiff:"$TMPIMAGE"
"$SCRIPTDIR/tcfwide.py" "$OUTDIR/TestCardFElec-788.tiff" tiff:"$TMPIMAGE" "$OUTDIR/TestCardFWide.tiff"

# Electronic SD test cards
env CARD=10 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardJ.tiff"
env CARD=12 vspipe "$SCRIPTDIR/extract.vpy" - | "$SCRIPTDIR/convert.py" rawfloat: "$OUTDIR/TestCardW.tiff"
"$SCRIPTDIR/tcg.py" "$OUTDIR/TestCardG_AP1.tiff" "$OUTDIR/TestCardG_AP2.tiff"
