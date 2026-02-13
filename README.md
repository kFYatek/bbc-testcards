BBC Test Card Restoration Project
=================================

This is a project dedicated to restoring/recreating test card images
historically used by the BBC, as close to the originals as possible - so that
they are both authentic and suitable for generation of actual test signals that
retain properties of a proper engineering test (of broadcast quality when
programmed into a professional test signal generator, or of hobbyist quality
when displayed via consumer equipment like a DVD player or a Raspberry Pi).

The primary source for this project is an archive of the shutdown broadcast of
BBC HD, recorded on March 26th, 2013, when various historical test cards have
been shown. This project aims to both recover the original SD images from that
HD broadcast as accurately as possible (this part is largely done), and manually
edit them to further remove remaining artifacts (pending, on hold).

**NOTE:** This repository does not contain actual test card images (aside from
incomplete parts of Test Card F - at least for now), only scripts for processing
data from the transport stream recording. See [INFO.md](./INFO.md) for where to
find it.

Contents
--------

* [INFO.md](./INFO.md) - technical information about where to get the transport
  stream recording, what tests cards are in there, etc.
* `scripts`
    * [extract.vpy](./scripts/extract.vpy) -
      [VapourSynth](https://github.com/vapoursynth/vapoursynth) script used to
      extract and initially process the test cards from the transport stream
        * Requires [BestSource](https://github.com/vapoursynth/bestsource) and
          [Descale](https://github.com/Jaded-Encoding-Thaumaturgy/vapoursynth-descale)
          to be installed and auto-loaded
        * Processing includes a non-linear luminance curve to undo the
          non-linearity present in the transport stream. See the description of
          Test Card X in `INFO.md` for details.
    * [convert.py](./scripts/convert.py) - a script that converts the raw output
      from VapourSynth into a more sensible format, PNG by default. Can also
      convert between full and limited color ranges. Writes the output to
      stdout.
    * [convertsigned.py](./scripts/convertsigned.py) - converts the output of
      `convert.py` in the `RAW16OUT` mode between unsigned (0..65535, default)
      and signed (-32768..32767) formats. The conversion is symmetrical, so it
      can be used either way. Signed data is handy for viewing the waveform...
      in audio editors, like Audacity. Might be convenient for visual
      inspection.
    * [generate.sh](./scripts/generate.sh) - a quick and dirty script that
      builds images for all the supported test cards.
    * [common.py](./scripts/common.py) - some type definitions and test card
      metadata shared between scripts
    * [eqcurve601.py](./scripts/eqcurve601.py), [eqcurve709.py](./eqcurve709.py) -
      quick and dirty scripts for generating the precorrection curves used in
      `extract.vpy`. Note that they have been manually tweaked afterwards.
* [TestCardFElec_BarneyWol.xcf](./TestCardFElec_BarneyWol.xcf) - XCF (GIMP) file
  containing features of the electronic version of Test Card F recovered from
  [Barney Wol's archived website](https://web.archive.org/web/20120320034954/http://www.barney-wol.net/video/testcardf/testcardf.html)
  and arranged on a canvas that matches the output of my scripts when set to
  `SCALE=3` (square pixels). These are said to come from BBC's original data, so
  can be used as reference.

`extract.vpy` and `convert.py` can operate in several different modes that can
be configured through environment variables (which also means that `generate.sh`
passes most of them through. I'm not documenting them, but feel free to look at
the code (and its usages of `os.environ`) to see what can be customized.

Why?
----

BBC Test Cards are an important cultural artifact, recognized both inside and
outside the United Kingdom. They are well known, and the image of Carole Hersee
used in Test Card F and its successors is instantly recognizable by millions of
people around the world.

However, most reproductions of those test cards that circulate over the Internet
fall into one of the following categories:

* Photographs of a TV screen
* Low-quality videotape recordings from over-the-air analogue TV
* Images that were shared by sources inside the BBC, but in low quality - this
  includes the famous GIF version of Test Card F, as well as images shared on
  some early hobbyist websites
* Unofficial recreations made by various people, usually without any regard for
  engineering qualities - those are often pleasant to look at, but made and
  posted in wrong resolutions, have false colors etc.

Other famous test patterns such as the SMPTE color bars, the Philips circle
pattern or the Telefunken FuBK test card, have long been documented in such
detail that it is relatively easy to recreate them with a high degree of
accuracy. The PTV archive repository
(https://github.com/KarstenHervoeHansen/PTV) also contains the original data
used to program the EPROMs of Philips/PTV pattern generators with several
variants of the Philips circle and FuBK patterns, making pixel-perfect
reproductions of those feasible.

None of that is true for the BBC patterns. However, the BBC HD shutdown
broadcast provides a high-quality official source, that together with various
other artifacts scattered over the Internet, may make it feasible to create
versions of those patterns that are as definite as possible save for a release
or leak of actual data used by the BBC.

Legal disclaimer
----------------

BBC test card images may be copyrighted, and some of their features, like the
BBC logos and the Carole Hersee photograph, definitely are. The copyright owners
seem to be OK with people who play with the test cards for
non-commercial/hobbyist purposes, or reproduce them with appropriate context.
But I am not a lawyer, and don't take any responsibility for possible
consequences of unauthorized use.

Said copyright owners were listed on the famous GIF version of Test Card F as:
© BBC, ITC & BREMA 1967. [BBC](https://bbc.com/) is still active today. ITC, the
Independent Television Commission, was a commercial broadcasting regulatory body
replaced by [Ofcom](https://www.ofcom.org.uk/) in 2003. BREMA, the British Radio
Equipment Manufacturers' Association, through mergers with the Federation of the
Electronics Industry in 2001 and the Computing Software and Services Association
in 2002, formed Intellect, which then relaunched as
[techUK](https://www.techuk.org/) in 2013. Thus, the current copyright owners
are most likely BBC, Ofcom and techUK.

All the code, text and information created by me as part of this repository, is
free to use however you like, with or without attribution. Treat it as
[public domain](https://en.wikipedia.org/wiki/Public_domain),
[CC0](https://creativecommons.org/publicdomain/zero/1.0/) or
[WTFPL](https://www.wtfpl.net/about/), whatever is the most convenient or
legally appropriate for you.
