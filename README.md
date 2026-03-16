# BBC Test Card Restoration Project

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

## How to use this project

This repository does not contain actual test card images (aside from incomplete
parts of Test Card F - at least for now), only scripts for processing data from
the transport stream recording.

### Prerequisites

To run the scripts, you will need:

* A computer running Linux or macOS. Other Unix-like systems might work too, but
  have not been tested. Windows will not work natively. Use WSL or a virtual
  machine to run Linux if you're on Windows.
* The following software:
    * [Python](https://www.python.org/) 3.8 or later (Python 3.14 was used
      during development), and the following libraries:
        * [NumPy](https://numpy.org/)
        * [Pillow](https://python-pillow.github.io/)
        * [SciPy](https://scipy.org/)
        * Optionally for `plot.py`: [Matplotlib](https://matplotlib.org/)
    * [ImageMagick](https://imagemagick.org)
    * [VapourSynth](https://www.vapoursynth.com/) with the following plugins:
        * [BestSource](https://github.com/vapoursynth/bestsource)
        * [Descale](https://github.com/Irrational-Encoding-Wizardry/descale)
        * [vs-placebo](https://github.com/Lypheo/vs-placebo)
    * [Wine](https://www.winehq.org/) (for extracting test card images buried
      in the TCGEN software installer). On some platforms you might need
      specialized forks such as
      [CrossOver](https://www.codeweavers.com/crossover) (for macOS) or
      [Hangover](https://github.com/AndreRH/hangover) (for Linux on ARM).

For example, on Ubuntu 25.10 x86_64 (note: running on older versions, including
LTS, may be problematic because VapourSynth requires very new dependencies), you
can run the following commands to install all the prerequisites:

```shell
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install \
    curl cython3 git imagemagick libavformat-dev libplacebo-dev libzimg-dev \
    meson pkgconf python3-dev python3-matplotlib python3-pip unzip wine32

git clone --recursive https://github.com/vapoursynth/vapoursynth.git -b R73
(cd vapoursynth && meson setup build && ninja -C build)
sudo ninja -C vapoursynth/build install
sudo ldconfig
sudo mkdir -p /usr/local/lib/$(uname -m)-linux-gnu/vapoursynth
python3 -m pip install --break-system-packages ./vapoursynth

git clone --recursive https://github.com/vapoursynth/bestsource.git
(cd bestsource && meson setup build && ninja -C build)
sudo install \
    bestsource/build/libbestsource.so \
    /usr/local/lib/$(uname -m)-linux-gnu/vapoursynth/

git clone --recursive https://github.com/Lypheo/vs-placebo.git
# This may be necessary for running in virtual machines:
sed -i -e 's/vp = pl_vulkan_default_params;/\0 vp.allow_software = 1;/' \
    vs-placebo/src/vs-placebo.c
(cd vs-placebo && meson setup build && ninja -C build)
sudo ninja -C vs-placebo/build install

git clone --recursive https://github.com/Irrational-Encoding-Wizardry/descale.git
(cd descale && meson setup build && ninja -C build)
sudo ninja -C descale/build install
```

On macOS, install [Homebrew](https://brew.sh/) first, and then run:

```shell
brew install \
    cmake imagemagick libplacebo meson molten-vk pkgconf python-matplotlib \
    scipy vapoursynth-bestsource vapoursynth-descale gcenx/wine/wine-crossover
git clone --recursive https://github.com/Lypheo/vs-placebo.git
(cd vs-placebo && meson setup build && ninja -C build)
install vs-placebo/build/libvs_placebo.dylib /opt/homebrew/lib/vapoursynth/

# On Apple Silicon you'll also need to install Rosetta 2:
softwareupdate --install-rosetta --agree-to-license
```

### Running

#### Downloading copyrighted sources

**WARNING:** The `download.sh` script runs code downloaded from the Internet
without much care about security. If that concerns you, you might want to run it
in an isolated environment or manually reproduce the steps instead.

Run:

```shell
./scripts/download.sh
```

This will download:

* The transport stream of BBC HD's final broadcast, as originally found in the
  [Lip-Sync issue thread on hummy.tv forums](https://hummy.tv/forum/threads/lip-sync-issue.10905/page-4)
* Recreations of Test Cards C and D made by
  [Richard T. Russell](https://en.wikipedia.org/wiki/Richard_T._Russell) - these
  are being extracted from the
  [Test Card Generator programming software](http://www.rtrussell.co.uk/tccgen/download.html)
  package
* Better quality version of the pre-war tuning signal image, as found on
  [tvark.org](https://tvark.org/branding/bbc/bbc-tv/bbc-tv-1936)

#### Regenerating the test cards

Run:

```shell
./scripts/generate.sh
```

Test card images will be created in the current directory.

A more detailed rundown of the test cards and their state will be added here at
a later date.

### Other files that may be of interest

* [INFO.md](./INFO.md) - technical information about where to get the transport
  stream recording, what tests cards are in there, etc.
* [scripts/convertsigned.py](./scripts/convertsigned.py) - converts raw 16-bit
  files between unsigned (0..65535) and signed (-32768..32767) formats. The
  conversion is symmetrical, so it can be used either way. Signed data is handy
  for viewing the waveform... in audio editors, like Audacity. Might be
  convenient for visual inspection.
* [scripts/eqcurve601.py](./scripts/eqcurve601.py),
  [scripts/eqcurve709.py](./eqcurve709.py) - quick and dirty scripts for
  generating the precorrection curves used in `extract.vpy`. Note that they have
  been manually tweaked afterwards.
* [scripts/extractld.py](./scripts/extractld.py) - processes `*.tbc` files
  created by [ld-decode](https://github.com/happycube/ld-decode) into image
  files, in a way that is optimized for extracting still images that are present
  for multiple frames.
    * NOTE: In previous revisions of this repository, the `extractld.py` script
      included some hardcoded tweaks to improve the quality of Test Card F image
      extracted from the 1986 BBC Domesday Community South disc. Those tweaks
      are no longer hardcoded. To achieve a result equivalent to the old
      version, run: `scripts/extractld.py domesday.tbc domesday.png 3000 23
      --black-level 16221 --white-level 53274 --deghost -4.5 0.1333333333333333
      --u-scale 0.8333333333333333 --v-scale 0.875 --shift -12.027515649466466`
* `scripts/generate_*.sh` - alternate generate scripts that exclusively use the
  BBC HD shutdown stream as the source and perform only parts of the processing.
  May be appropriate for comparison and debugging.
* [scripts/plot.py] - plots line data from image files, much like an
  oscilloscope.
* [sources/TestCardFElec_BarneyWol.xcf](./sources/TestCardFElec_BarneyWol.xcf) -
  XCF (GIMP) file containing features of the electronic version of Test Card F
  recovered from
  [Barney Wol's archived website](https://web.archive.org/web/20120320034954/http://www.barney-wol.net/video/testcardf/testcardf.html)
  and arranged on a canvas that matches the output of my scripts when set to
  `SCALE=3` (square pixels). These are said to come from BBC's original data, so
  can be used as reference.

## Why?

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

## Legal disclaimer

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
