# Test card information

* Source: `This Is BBC HD_20130326_0120.ts`
    * Link:
      https://dl.dropbox.com/s/pk4bvdnqd6yttyn/This%20Is%20BBC%20HD_20130326_0120.zip
    * Found in: https://hummy.tv/forum/threads/lip-sync-issue.10905/page-4
    * Captured from DVB-T2 broadcast
    * Second-generation re-encodes are also available on YouTube and various
      other places. This is a high-quality
      re-encode: https://www.youtube.com/watch?v=KSFgolB7HHE - it may also be
      appropriate as a source, but frame numbers will probably need to be
      adjusted.
* Resolution: 1920x1080
* Pixel format: YUV 4:2:0 8-bit
* Color range: Limited (MPEG) - 16-235
* Color space: BT.709
    * Note: SD test cards appear to be BT.601 data shown as BT.709 without
      proper conversion

## HD test cards

### Test Card X

* Timecode: 00:24.000
* Native format: 1920x1080 BT.709
* Note: "Test Card X" is not an official designation
* Alternate source:
  https://tvark.org/media/1998i/testcards/images/169_testcards/BBCHD_testcard_big.jpg
    * The version from the TS has a different variant of the BBC HD logo
    * The version from the TS has non-linear luminance response. This JPEG
      version has been used as reference to create the correction curve in
      `extract.vpy`
    * The JPEG version has 100% color bars, and the green square above the
      photograph is also 100% green. The TS version has darker color bars, about
      85% intensity, and a matching green square. Other colors seem to match, as
      evident by the U/V gradients at the bottom, and the Carole Hersee photo.
      The U/V castellations on the left are slightly different shades though.
    * The superblack dot on the grayscale steps is missing in the TS version -
      this is probably an error related to the non-linearity and should be
      reconstructed.
    * The frequency gratings look sharper and more uniform in the JPEG version.
      This may be their desired appearance, or may be an artifact of
      oversharpening.
        * Juding from
          https://www.bbc.co.uk/blogs/bbcinternet/2008/12/a_christmas_present_from_the_h.html
          and https://www.flickr.com/photos/bbccouk/3113496466/ (reisze to
          194x554 to match), the TS version is more accurate.
        * We might try recreating the gratings locally, keeping in mind that
          they are 5, 10, 15, 20, 25 and 30 MHz, and the assumed sample rate is
          74.25 MHz (so the period of the first grating is 14.85 pixels)
* Features to reconstruct in addition to general cleanup:
    * Superblack dot on the grayscale steps. Goes all the way to absolute zero.
    * Sawtooth in the far lower-left corner goes all the way to 12 (-2%),
      mirroring how it goes on to 240 (~102%) on the brightest side.
    * Color bars on the sides are supposed to be non-antialiased

### Test Card 3D

* Timecode: 05:19.520
* Native format: 1920x1080 BT.709
* This doesn't seem to have anything interesting, it's just two Test Card X's
  side-by-side at half the horizontal resolution. Only the BBC logo in the
  corner is off-plane.
* Features to reconstruct in addition to general cleanup:
    * Superblack dot on the grayscale steps. Goes all the way to absolute zero.
    * Sawtooth in the far lower-left corner goes all the way to 11 (-2%),
      mirroring how it goes on to 240 (102%) on the brightest side.

## Mechanical TV test cards

These are not being "recovered" in any meaningful way. They were originally
crude paper cards, and these are modern recreations.

The Baird Televisor reportedly had a roughly linear transfer characteristic
between signal level and light intensity (so: gamma 1.0), as opposed to gamma
2.4 assumed for displays showing BT.601 and BT.709 content.

### Television Eye

* Timecode: 01:02.280
* Native format: 30-line mechanical
* 648x1080 -> 42x70, crop to 30x70
* Image has been apparently processed like the SD images

### Circle and line

* Timecode: 01:40.200
* Native format: 30-line mechanical
* 1440x1080, pad to 1440x3360 -> 30x70
* Image has been apparently processed like the SD images

## 405-line test cards - high-res recreations

These are clearly modern high-res recreations, with limited engineering
applicability - most notably, the frequency gratings are about 12.5% too dense.
However, they seem to match the available pictures of the originals, so maybe
they were always like that?

They are probably OK to just resize and use like that - they won't get more
accurate than optical slides that were originally used.

They were processed the same way as SD images.

### Test Card A

* Timecode: 02:00.360
* Native format: 405 lines (4:3)
* 1920x1080 -> 936x378, crop to 720x378

### Test Card B

* Timecode: 02:20.280
* Native format: 405 lines (4:3)
* 1920x1080 -> 936x378, crop to 720x378

## 405-line test cards - low-res images

Test Cards C and D are also clearly modern reproductions, but they are also
clearly sourced from lossily compressed images such as JPEGs. The Tuning Signal
may be an actual scan of an original, but it's also clearly sourced from a
low-resolution computer image.

The frequency gratings again seem to be too dense when measures, but match the
available pictures of the originals.

### Tuning Signal

* Timecode: 01:21.240
* Native format: 405 lines (5:4)
* 1400x1080 -> 728x378, crop to 720x378
* Alternate source:
  https://tvark.org/media/1998i/2020-05-15/d0bfa1fd2a9191224e10dafe9d9fc321dc254d80.jpg
    * When resized to 1274x1046, this perfectly matches the transport stream,
      origin at (324, 17)
    * Pixel values are already in the right (16-235) range
    * Reconstruction idea: resize 1400x1080 to 844x595, paste the alternative
      source onto that, resize from there to 728x378, crop to 720x378

### Test Card C

* Timecode: 02:40.280
* Native format: 405 lines (4:3)
* 1920x1080 -> 936x378, crop to 720x378
* Alternate source: software for
  [Richard T. Russell](https://en.wikipedia.org/wiki/Richard_T._Russell)'s
  [Programmable Colour Test Card Generator](https://www.bbcbasic.co.uk/tccgen/tccgen.html)
  from 2003 includes a 640x468 GIF file that is very clearly the same
  reproduction

### Test Card D

* Timecode: 03:00.440
* Native format: 405 lines (4:3)
* 1920x1080 -> 936x378, crop to 720x378
* Alternate source: software for
  [Richard T. Russell](https://en.wikipedia.org/wiki/Richard_T._Russell)'s
  [Programmable Colour Test Card Generator](https://www.bbcbasic.co.uk/tccgen/tccgen.html)
  from 2003 includes a 640x468 GIF file that is very clearly the same
  reproduction, with minor differences in frequency gratings

## 625-line test cards

### Test Card F (optical)

* Timecode: 03:20.440
* Native format: 625 lines PAL (4:3)
* 1920x1080 -> 936x576, crop to 720x576
* This looks like a digital recreation of the original slide. A simple resize
  should outmatch the quality of the original slide.
* Features to reconstruct in addition to general cleanup:
    * Electronic color bars overlaid at the top
        * Judging from https://tvark.org/bbc2-trade-test-transmission-2 and
          https://tvark.org/bbc2-testcard-illustration, the electronic color
          bars shall occupy the first 24 lines of the picture and have a hard
          cutoff.
        * It seems that the very first line is pure white and starts late
          (note that it is normally a half-line, but active picture still starts
          in the left half of the picture). This white line seems to start at
          about 75% of the magenta bar's width - that's sample 445.

### Test Card F (electronic)

* Timecode: 03:40.600
* Native format: 625 lines PAL (4:3)
* 1920x1080 -> 936x576, crop to 720x576
* Comparison reference source: https://www.domesday86.com/?page_id=1332
  (Community South test-card 2) - sampled at 4fSC (17734475 Hz)
* Closeups:
  https://web.archive.org/web/20120320034954/http://www.barney-wol.net/video/testcardf/testcardf.html -
  apparently sampled at square pixels (14769230.(769230) Hz) - recovered and
  arranged on [TestCardFElec_BarneyWol.xcf](./TestCardFElec_BarneyWol.xcf)
* Note: `src_left` is deliberately set to offset the center by half-pixel,
  to match the closeups mentioned above.
* The very top and very bottom lines are seemingly supposed to be empty.

### Test Card J

* Timecode: 04:00.600
* Native format: 625 lines PAL (4:3)
* 1920x1080 -> 936x576, crop to 720x576
* Maybe use Test Card X for detail reconstruction
    * castellation colors are raw data in different formats (BT.601 vs. BT.709)
    * photograph colors are supposed to be properly converted
* Animation reference: https://www.youtube.com/watch?v=IcN52H9x2oU
* Sample 534 is 0.3 samples before peak of the frequency test
* Features to reconstruct in addition to general cleanup:
    * Superblack dot on the grayscale steps. Goes all the way to absolute zero.

### Test Card F widescreen

* Timecode: 04:20.680
* Native format: 625 lines PAL (16:9)
* Extend to 2560x1080
* Add the missing side reflections
* 2560x1080 -> 936x576, crop to 720x576
* Maybe use Test Card F for detail reconstruction?

### Test Card W

* Timecode: 04:40.680
* Native format: 625 lines PAL (16:9)
* Extend to 2560x1080
* Add the missing side reflections
* 2560x1080 -> 936x576, crop to 720x576
* Maybe use Test Card X for detail reconstruction
    * castellation colors are raw data in different formats (BT.601 vs. BT.709)
    * photograph colors are supposed to be properly converted
* Features to reconstruct in addition to general cleanup:
    * Superblack dot on the grayscale steps. Goes all the way to absolute zero.
    * The grayscale swipes in the bottom-left corner extend linearly all the
      way, including the leftmost digital edge.
    * The top and bottom lines are spaced way more densely, see
      https://www.youtube.com/watch?v=Xqn-EeRawmQ - that's about 10% denser than
      WSS signaling.
    * Color bars on the sides are supposed to be non-antialiased
    * Detailed information:
      https://web.archive.org/web/20060207093007/http://www.barney-wol.net/video/testcardw/testcardw.html

## Missing but notable

### Test Card G

* Needs to be sourced elsewhere
* Description:
  https://web.archive.org/web/20160304070245/http://www.pembers.freeserve.co.uk/Test-Cards/Test-Card-Technical.html#PM5544
* Various low-quality captures:
  * https://tvark.org/bbc2-engineering-test-transmission (square pixels)
  * https://rewind.thetvroom.com/26762/test-cards/bbc-two-test-card-g-bbc-scotland-generator-1980s/
  * https://www.domesday86.com/?page_id=1332 (Jason test-card 5) - sampled at
    4fSC (17734475 Hz) - not Test Card G, both colors and frequencies are wrong
* Wikipedia's recreation at
  https://en.wikipedia.org/wiki/File:PM5544_(Testcard_G_variation).png has many
  inaccuracies, but the frequency gratings seem to be accurate in frequency
  and timing

### Test Card J (525-line)

* Needs to be remade
* Description and reference:
  https://web.archive.org/web/20120321124821/http://www.barney-wol.net/video/testcardj/testcardj.html
* Additional description and reference:
  https://web.archive.org/web/20160304070245/http://www.pembers.freeserve.co.uk/Test-Cards/Test-Card-Technical.html#TCJ-W
* This is a full (not DV) frame signal: 720x486

# Digitizing 405-line system

Sample rate: 8.748 MHz

|                    | 405 lines | 625 lines |
|--------------------|-----------|-----------|
| Total line period  | 864       | 864       |
| Active line period | 702       | 702       |
| Front porch        | 15        | 22        |
| Sync pulse width   | 78        | 63        |
| Back porch         | 69        | 77        |
