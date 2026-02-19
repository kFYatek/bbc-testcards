#!/bin/sh
set -e
OUTDIR="${OUTDIR:=.}"
SCRIPTDIR="$(dirname "$0")"
SCALE=
TMPFILES=
export SCALE

remove_tmpfiles() {
    rm -f $TMPFILES
}

trap remove_tmpfiles EXIT

# HD testcards, never scale
env CARD=0 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - | env COLORSPACE=709 RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 1920x1080 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-709-video16-v4.icc" -define png:color-type=2 "$OUTDIR/TestCardX.png"
env CARD=13 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - | env COLORSPACE=709 RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 1920x1080 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-709-video16-v4.icc" -define png:color-type=2 "$OUTDIR/TestCard3D.png"

# Mechanical test cards, don't scale for now
env CARD=1 COLORCONV=4 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - \
| env RAW16OUT=1 "$SCRIPTDIR/convert.py" \
| magick -size 1920x1080 -depth 16 rgb:- \
    -crop 448x1064+736+8 -bordercolor '#eb00eb00eb00' -border 100x8 rgb:- \
| magick -size 648x1080 -depth 16 rgb: \
    -filter Lanczos -resize 42x1080\! -crop 30x1080+6+0 -filter Cubic -resize 30x70\! \
    +profile icc -profile "$SCRIPTDIR/../Linear-gray-video16-v4.icc" \
    -define png:color-type=0 "$OUTDIR/TelevisionEye.png"

env CARD=3 COLORCONV=4 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - \
| env RAW16OUT=1 "$SCRIPTDIR/convert.py" \
| magick -size 1920x1080 -depth 16 rgb:- \
    -crop 1420x1012+250+58 -bordercolor '#eb00eb00eb00' -border 10x1174 rgb:- \
| magick -size 1440x3360 -depth 16 rgb:- \
    -filter Lanczos -resize 30x3360\! -filter Cubic -resize 30x70\! \
    +profile icc -profile "$SCRIPTDIR/../Linear-gray-video16-v4.icc" \
    -define png:color-type=0 "$OUTDIR/CircleAndLine.png"

# Test Cards A and B are high-res reproductions, just scale them down
env CARD=4 SCALE=1 SCALER=lanczos ANTIRING=1 vspipe "$SCRIPTDIR/extract.vpy" - | env CARD=4 SCALE=2 COLORSPACE=1 RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x378 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-1886-gray-video16-v4.icc" -define png:color-type=0 "$OUTDIR/TestCardA.png"
env CARD=5 SCALE=1 SCALER=lanczos ANTIRING=1 vspipe "$SCRIPTDIR/extract.vpy" - | env CARD=5 SCALE=2 COLORSPACE=1 RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x378 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-1886-gray-video16-v4.icc" -define png:color-type=0 "$OUTDIR/TestCardB.png"

# Use Test Cards C and D from Richard T. Russell's GIFs
for CARD in C D; do
    "$SCRIPTDIR/fftresize.py" "$SCRIPTDIR/../Test Card $CARD.gif" 720 468 \
    | magick -size 720x468 -depth 16 gray:- \
        -filter Point -resize 7200x468\! -filter Gaussian -resize 7200x378\! \
        -filter Point -resize 720x378\! \
        +profile icc -profile "$SCRIPTDIR/../ITU-1886-gray-video16-v4.icc" \
        -define png:color-type=0 "$OUTDIR/TestCard$CARD.png"
done

# Compose the Tuning signal from both sources
TMPIMAGE="$(mktemp)"
TMPFILES="$TMPFILES $TMPIMAGE"
magick "$SCRIPTDIR/../d0bfa1fd2a9191224e10dafe9d9fc321dc254d80.jpg" \
    -type GrayScaleAlpha -fuzz '3%' -fill none -draw "color 3,2 floodfill" \
    -crop 764x576+2+0 png:"$TMPIMAGE"
env CARD=2 SCALE=0 vspipe "$SCRIPTDIR/extract.vpy" - \
| env LIMITED=1 RAW16OUT= "$SCRIPTDIR/convert.py" \
| magick png:- -crop 1400x1080+260+0 -filter Lanczos -resize 844x595\! \
    -evaluate Pow 1.15 -evaluate Max 6.275% png:"$TMPIMAGE" -geometry +41+9 -composite \
    png:"$TMPIMAGE"
"$SCRIPTDIR/fftresize.py" "$TMPIMAGE" 720 595 \
| magick -size 720x595 -depth 16 gray:- \
    -filter Point -resize 7200x595\! -filter Gaussian -resize 7200x378\! \
    -filter Point -resize 720x378\! \
    +profile icc -profile "$SCRIPTDIR/../ITU-1886-gray-video16-v4.icc" \
    -define png:color-type=0 "$OUTDIR/TuningSignal.png"

# Recreation of the optical Test Card F
env CARD=8 SCALE=1 SCALER=lanczos ANTIRING=2 vspipe "$SCRIPTDIR/extract.vpy" - \
| env CARD=8 SCALE=2 RAW16OUT=1 "$SCRIPTDIR/convert.py" \
| magick -size 720x576 -depth 16 rgb:- -define png:color-type=2 png:"$TMPIMAGE"
CARDIMAGE="$(mktemp)"
TMPFILES="$TMPFILES $CARDIMAGE"
magick png:"$TMPIMAGE" -crop 720x1+0+26 -filter Point -resize 720x2\! png:- \
| magick png:"$TMPIMAGE" -crop 720x552+0+24 \
    png:- -geometry +0+0 -composite png:"$CARDIMAGE"
magick png:"$TMPIMAGE" -crop 31x4+344+548 -flip png:- \
| magick png:"$CARDIMAGE" png:- -geometry +344+0 -composite png:"$CARDIMAGE"
magick png:"$TMPIMAGE" -crop 720x14+0+6 -filter Box -resize 720x1\! -filter Box -resize 720x23\! \
    png:"$TMPIMAGE"
"$SCRIPTDIR/tcfopt_firstline.py" \
| magick -size 720x1 -depth 16 gray:- png:"$TMPIMAGE" -append png:"$CARDIMAGE" -append \
    +profile icc -profile "$SCRIPTDIR/../ITU-601-625-video16-v4.icc" \
    -define png:color-type=2 "$OUTDIR/TestCardFOpt.png"

# Recreation of the electronic Test Card F
env CARD=9 SCALE=3 vspipe "$SCRIPTDIR/extract.vpy" - \
| env RAW16OUT=1 "$SCRIPTDIR/convert.py" \
| magick -size 788x576 -depth 16 rgb:- -define png:color-type=2 \
    "$SCRIPTDIR/../TestCardFElec_reconstruction.png" -composite png:- \
| magick png:- \
    +profile icc -profile "$SCRIPTDIR/../ITU-601-625-video16-v4.icc" \
    -define png:color-type=2 "$OUTDIR/TestCardFElec-788.png"
magick "$OUTDIR/TestCardFElec-788.png" -bordercolor '#100010001000' -border 118x0 rgb:- \
| "$SCRIPTDIR/fftresize.py" raw16:1024x576 936 576 \
| magick -size 936x576 -depth 16 rgb:- \
    -crop 720x576+108+0 +profile icc -profile "$SCRIPTDIR/../ITU-601-625-video16-v4.icc" \
    -define png:color-type=2 "$OUTDIR/TestCardFElec.png"

# Electronic SD test cards
env CARD=10 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x576 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-601-625-video16-v4.icc" -define png:color-type=2 "$OUTDIR/TestCardJ.png"
env CARD=11 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x576 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-601-625-video16-v4.icc" -define png:color-type=2 "$OUTDIR/TestCardFWide.png"
env CARD=12 vspipe "$SCRIPTDIR/extract.vpy" - | env RAW16OUT=1 "$SCRIPTDIR/convert.py" | magick -size 720x576 -depth 16 rgb:- +profile icc -profile "$SCRIPTDIR/../ITU-601-625-video16-v4.icc" -define png:color-type=2 "$OUTDIR/TestCardW.png"
