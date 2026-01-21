# Test card information

* Source: `This Is BBC HD_20130326_0120.ts`
  * Link: https://dl.dropbox.com/s/pk4bvdnqd6yttyn/This%20Is%20BBC%20HD_20130326_0120.zip
  * Found in: https://hummy.tv/forum/threads/lip-sync-issue.10905/page-4
  * Captured from DVB-T2 broadcast
  * Second-generation re-encodes are also available on YouTube and various other
    places. This is a high-quality re-encode:
    https://www.youtube.com/watch?v=KSFgolB7HHE - it may also be appropriate as
    a source, but frame numbers will probably need to be adjusted.
* Resolution: 1920x1080
* Pixel format: YUV 4:2:0 8-bit
* Color range: Limited (MPEG) - 16-235
* Color space: BT.709
  * Note: SD test cards appear to be BT.601 data shown as BT.709 without proper
    conversion

## HD test cards

### Test Card X

* Timecode: 00:24.000
* Native format: 1920x1080 BT.709
* Note: "Test Card X" is not an official designation
* Alternate source: https://tvark.org/media/1998i/testcards/images/169_testcards/BBCHD_testcard_big.jpg
  * The version from the TS has a different variant of the BBC HD logo
  * The version from the TS has non-linear luminance response. This JPEG version
    has been used as reference to create the correction curve in `extract.vpy`
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
    * Juding from https://www.bbc.co.uk/blogs/bbcinternet/2008/12/a_christmas_present_from_the_h.html
      and https://www.flickr.com/photos/bbccouk/3113496466/ (reisze to 194x554
      to match), the TS version is more accurate.
    * We might try recreating the gratings locally, keeping in mind that they
      are 5, 10, 15, 20, 25 and 30 MHz, and the assumed sample rate is 74.25 MHz
      (so the period of the first grating is 14.85 pixels)

### Test Card 3D

* Timecode: 05:19.520
* Native format: 1920x1080 BT.709
* This doesn't seem to have anything interesting, it's just two Test Card X's
  side-by-side at half the horizontal resolution. Only the BBC logo in the
  corner is off-plane.

## Mechanical TV test cards

These are not being "recovered" in any meaningful way. They were originally
crude paper cards, and these are modern recreations. Ideas for converting into
an appropriate signal are TBD. Note: hacktv supports this system.

### Television Eye

* Timecode: 01:02.280
* Native format: 30-line mechanical

### Circle and line

* Timecode: 01:40.200
* Native format: 30-line mechanical

## 405-line test cards - high-res recreations

These are clearly modern high-res recreations, with limited engineering
applicability - most notably, the frequency gratings are about 12.5% too dense.
However, they seem to match the available pictures of the originals, so maybe
they were always like that?

They are probably OK to just resize and use like that - they won't get more
accurate than optical slides that were originally used.

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

### Test Card C

* Timecode: 02:40.280
* Native format: 405 lines (4:3)
* 1920x1080 -> 936x378, crop to 720x378

### Test Card D

* Timecode: 03:00.440
* Native format: 405 lines (4:3)
* 1920x1080 -> 936x378, crop to 720x378

## 625-line test cards

### Test Card F (optical)

* Timecode: 03:20.440
* Native format: 625 lines PAL (4:3)
* 1920x1080 -> 936x576, crop to 720x576
* This looks like a digital recreation of the original slide. A simple resize
  should outmatch the quality of the original slide. The digital color bars
  overlaid at the top should probably be remade.

### Test Card F (electronic)

* Timecode: 03:40.600
* Native format: 625 lines PAL (4:3)
* 1920x1080 -> 936x576, crop to 720x576
* Comparison reference source: https://www.domesday86.com/?page_id=1332
  (Community South test-card 2) - sampled at 4fSC (17734475 Hz, or perhaps
  17734375 Hz)
* Closeups: https://web.archive.org/web/20120320034954/http://www.barney-wol.net/video/testcardf/testcardf.html -
  apparently sampled at square pixels (14769230.(769230) Hz, or perhaps
  14765625 Hz) - recovered and arranged on
  [TestCardFElec_BarneyWol.xcf](./TestCardFElec_BarneyWol.xcf)
* Note: `src_left` is deliberately set to offset the center by half-pixel,
  to match the closeups mentioned above.

### Test Card J

* Timecode: 04:00.600
* Native format: 625 lines PAL (4:3)
* 1920x1080 -> 936x576, crop to 720x576
* Maybe use Test Card X for detail reconstruction
  * castellation colors are raw data in different formats (BT.601 vs. BT.709)
  * photograph colors are supposed to be properly converted
* Animation reference: https://www.youtube.com/watch?v=IcN52H9x2oU

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

### Test Card G

* Needs to be sourced elsewhere
* Description: https://web.archive.org/web/20160304070245/http://www.pembers.freeserve.co.uk/Test-Cards/Test-Card-Technical.html#PM5544
* Capture: https://tvark.org/bbc2-trade-test-transmission - sampled at square
  pixels (14769230.(769230) Hz, or perhaps 14765625 Hz)
* Reference for the frequency gratings:
  https://www.domesday86.com/?page_id=1332 (Jason test-card 5) - sampled at 4fSC
  (17734475 Hz, or perhaps 17734375 Hz)

### Test Card J (525-line)

* Needs to be remade
* Description and reference: https://web.archive.org/web/20120321124821/http://www.barney-wol.net/video/testcardj/testcardj.html
* Additional description and reference: https://web.archive.org/web/20160304070245/http://www.pembers.freeserve.co.uk/Test-Cards/Test-Card-Technical.html#TCJ-W
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
