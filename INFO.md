Test card information
=====================

* Source: `This Is BBC HD_20130326_0120.ts`
  * Link: https://dl.dropbox.com/s/pk4bvdnqd6yttyn/This%20Is%20BBC%20HD_20130326_0120.zip
  * Found in: https://hummy.tv/forum/threads/lip-sync-issue.10905/page-4
  * Captured from DVB-T2 broadcast
* Resolution: 1920x1080
* Pixel format: YUV 4:2:0 8-bit
* Color range: Limited (MPEG) - 16-235
* Color space: BT.709

Test Card X
-----------

* Timecode: 00:24.000
* Native format: 1920x1080 BT.709

Television Eye
--------------

* Timecode: 01:02.280
* Native format: 30-line mechanical

Tuning Signal
-------------

* Timecode: 01:21.240
* Native format: 405 lines (5:4)
* 1400x1080 -> 728x378, crop to 720x378

Circle and line
---------------

* Timecode: 01:40.200
* Native format: 30-line mechanical

Test Card A
-----------

* Timecode: 02:00.360
* Native format: 405 lines (4:3)
* 1920x1080 -> 936x378, crop to 720x378

Test Card B
-----------

* Timecode: 02:20.280
* Native format: 405 lines (4:3)
* 1920x1080 -> 936x378, crop to 720x378

Test Card C
-----------

* Timecode: 02:40.280
* Native format: 405 lines (4:3)
* 1920x1080 -> 936x378, crop to 720x378

Test Card D
-----------

* Timecode: 03:00.440
* Native format: 405 lines (4:3)
* 1920x1080 -> 936x378, crop to 720x378

Test Card F (optical)
---------------------

* Timecode: 03:20.440
* Native format: 625 lines PAL (4:3)
* 1920x1080 -> 936x576, crop to 720x576

Test Card F (electronic)
------------------------

* Timecode: 03:40.600
* Native format: 625 lines PAL (4:3)
* 1920x1080 -> 936x576, crop to 720x576
* Comparison reference source: https://www.domesday86.com/?page_id=1332
  (Community South test-card 2) - sampled at 4fSC (17734475 Hz, or perhaps
  17734375 Hz)
* Closeups: https://web.archive.org/web/20120320034954/http://www.barney-wol.net/video/testcardf/testcardf.html -
  apparently sampled at square pixels (14769230.(769230) Hz, or perhaps
  14765625 Hz)

Test Card J
-----------

* Timecode: 04:00.600
* Native format: 625 lines PAL (4:3)
* 1920x1080 -> 936x576, crop to 720x576
* Maybe use Test Card X for detail reconstruction
  * castellation colors are raw data in different formats (BT.601 vs. BT.709)
  * photograph colors are supposed to be properly converted

Test Card F widescreen
----------------------

* Timecode: 04:20.680
* Native format: 625 lines PAL (16:9)
* Extend to 2560x1080
* Add the missing side reflections
* 2560x1080 -> 936x576, crop to 720x576
* Maybe use Test Card F for detail reconstruction?

Test Card W
-----------

* Timecode: 04:40.680
* Native format: 625 lines PAL (16:9)
* Extend to 2560x1080
* Add the missing side reflections
* 2560x1080 -> 936x576, crop to 720x576
* Maybe use Test Card X for detail reconstruction
  * castellation colors are raw data in different formats (BT.601 vs. BT.709)
  * photograph colors are supposed to be properly converted

Test Card 3D
------------

* Timecode: 05:19.520
* Native format: 1920x1080 BT.709

Test Card G
-----------

* Needs to be sourced elsewhere
* Description: https://web.archive.org/web/20160304070245/http://www.pembers.freeserve.co.uk/Test-Cards/Test-Card-Technical.html#PM5544
* Capture: https://tvark.org/bbc2-trade-test-transmission - sampled at square
  pixels (14769230.(769230) Hz, or perhaps 14765625 Hz)
* Reference for the frequency gratings:
  https://www.domesday86.com/?page_id=1332 (Jason test-card 5) - sampled at 4fSC
  (17734475 Hz, or perhaps 17734375 Hz)

Test Card J (525-line)
----------------------

* Needs to be remade
* Description and reference: https://web.archive.org/web/20120321124821/http://www.barney-wol.net/video/testcardj/testcardj.html
* Additional description and reference: https://web.archive.org/web/20160304070245/http://www.pembers.freeserve.co.uk/Test-Cards/Test-Card-Technical.html#TCJ-W
* This is a full (not DV) frame signal: 720x486

Digitizing 405-line system
==========================

Sample rate: 8.748 MHz

|                    | 405 lines | 625 lines |
|--------------------|-----------|-----------|
| Total line period  | 864       | 864       |
| Active line period | 702       | 702       |
| Front porch        | 15        | 22        |
| Sync pulse width   | 78        | 63        |
| Back porch         | 69        | 77        |
