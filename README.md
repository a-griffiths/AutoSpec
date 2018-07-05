# AutoSpec

This software aims to provide fast, automated extraction of high quality 1D spectra from astronomical datacubes with minimal user effort. AutoSpec takes an IFU datacube and a simple parameter file in order to extract a 1D spectra for each object in a supplied catalogue. A custom designed cross-correlation algorithm helps to improve signal to noise as well as isolate sources from neighbouring contaminants.

## Contents

- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Installing](#installing)
- [Usage](#usage)
  - [The Catalogue](#the-catalogue)
  - [The Parameter File](#the-parameter-file)
  - [SExtractor File](#sextractor-file)
  - [Running the Code](#running-the-code)
  - [Loading the Output](#loading-the-output)
- [Running the tests](#running-the-tests)
- [Current Issues](#current-issues)
- [Further Improvements](#further-improvements)
- [Authors](#authors)
- [How to Cite](#how-to-cite)
- [Acknowledgements](#acknowledgements)
- [License](#license)
- [Changelog](#changelog)

## Getting Started

Currently the code has only been tested on a Linux system but it should work as long as the prerequisites are met. Because of this all installation and running instructions are based on Linux systems (for now).

## Prerequisites

Before you start make sure you have the following pieces of software installed:

```
- Python 2.7 or 3.3+
- Source Extractor (https://www.astromatic.net/software/sextractor)
```

You will also need the following python pacakges:

```
- numpy
- matplotlib
- mpdaf (http://mpdaf.readthedocs.io/en/latest/) and its dependencies.
```

## Installing

AutoSpec doesn't need to be installed, just clone or download this github repository. With git clone use:
```
git clone https://github.com/a-griffiths/AutoSpec.git
```
The easiest way to run AutoSpec is to make it it executable. To do this simply navigate to the AutoSpec directory and run `chmod +x AutoSpec`. You also need to add the line `export PATH=$PATH:/installed_dir/AutoSpec/` to your .bashrc file.

## Usage

AutoSpec is designed to be as intuitive as possible, this section will provide a brief run through on the different elements of the software.

First off, create a working folder; this should contain a minimum of the **datacube**, **parameter file** and **catalogue file**. The default parameter file can be found [here](param.py), and an example [catalogue](test/catalog.txt) file can be found in the test folder on github. You can also include any **additional images**, **segmentation maps** and **SExtractor configuration files**. 

AutoSpec runs in two main operating modes which can be specified in the parameter file: 
- 'same' mode: runs the software with a constant set of parameters (defined in the param file) for every source in the catalogue. 
- 'cat' (catalogue) mode: runs AutoSpec with different parameters for each object based on values specified in the catalogue file. For more info on this see the [catalogue](#the-catalogue) section. 

Edit the parameter file with a text editor, making sure to keep the formatting correct ([as detailed below](#the-parameter-file)). The code can then be run through the command line by simple navigating to your working directory and running:
```
AutoSpec
```
_* Note: If you haven't made AutoSpec [executable](#installing) then you will need to run AutoSpec directly from the software directory_ 
```
/installed_dir/AutoSpec
```
_** Note: All output subdirectories will be automatically created._

### The Catalogue
The first thing you need to do is create a catalogue file (simple text or csv file, not fits). There are two options for this; if you run the code in constant mode (MODE = 'same' in the parameter file), you only need to supply the ID, RA and DEC for each source:
```
#ID     RA      DEC
(int)   (deg)   (deg)
```
Alternatively, if you run in catalogue mode (MODE = 'cat' in the parameter file), you will also need to specify SIZE, MODE and REF values for each source. 'Size' sets the subcube/image extraction size, this is the per object version of the [SIZE](#the-parameter-file) parameter in param.py. 'MODE' specifies the extraction mode of the initial reference spectrum and should be either IMG or APER (image or aperture mode). 'REF' specifies which weight image (for IMG mode) or aperture size (APER mode) to use for initial extraction respectively. For aperture mode or when a weight image is not specified, AutoSpec will use WEIGHT_IMG from the parameter file, further, if this is not specified it will default to using the muse white light image. The format of the catalogue in this case should follow the following format:
```
#ID     RA      DEC     SIZE       MODE     REF
(int)   (deg)   (deg)   (arcsec)   (str)    (str)
```

### The Parameter File
The parameter file provides easy user modification to AutoSpec run modes. Each parameter is briefly explained in the comments of the file, but more in depth explanation is provided below. The incorrect specification of parameters in this file is the most likely place you can go wrong. This is a python based file so make sure to follow python conventions, it might be best to edit the [example](param.py) parameter file provided. Where multiple values can be provided (APER, IMG, IMG_NAME, SEG_MAP and SEG_NAME), make sure you surround the values with square brackets and separate with a comma, i.e. ['one',two'...] or for the APER parameter [1.0,1.5,2.0....].  

**MODE:** this is the main operating mode AutoSpec will run in. For the constant parameter mode ('same'), AutoSpec will extract each source within the catalogue based only on the settings provided in the parameter file. In catalogue mode ('cat'), the software will take extraction method and reference from the catalogue file on a source by source basis. 

**REF:** this is the reference spectrum to use for cross-correlation. This can either be an aperture size or image name. If an aperture size is specified it must also exist in the APER parameter. Likewise, if you provide an image this must either exist in the IMG_NAME parameter or be set to MUSE_WHITE to use the white light image created from the datacube. 

**APER:** this is a list of aperture sizes to extract spectra from in arcseconds, this can either be a single value or a list of values (i.e. 2.0 or [1.0,1.5,2.0]). Maximum value should be less than or equal to half the SIZE parameter.

**IMG:** list of additional image file names. This is useful if you are running AutoSpec in image mode where SExtractor is run on each image file in order to define the objects extraction regions. This is either a single string ('g-band.fits') or a list of strings (['g-band.fits','r-band.fits']).

**IMG_NAME:** output names for each additional image specified by IMG parameter. This is either a single string ('G-Band') or a list of strings with no spaces (['G-Band','R-BAND']). 

**USE_WHITE:** tells AutoSpec if you would like to use the MUSE_WHITE image and segmentation maps when deriving the object and sky masks.

**OBJ_MASK:** here we define if you want to use the intersection or the union of the individual segmentation maps to produce an object mask in order to build the initial spectrum. The intersection mask only selects areas where the object overlaps in the combined segmentation maps, whereas union uses the combination. If you choose intersection and it is found to be empty, the code defaults to using the union mask in order to successfully extract a spectrum. 

**WEIGHT_IMG:** this is the image to use for spectrum weighting when not specified elsewhere, this value has to exist in IMG_NAME or be set to MUSE_WHITE to use the white light image created from the datacube.

**SEG_MAP:** similar to IMG but contains a list of additional segmentation map files.

**SEG_NAME:** output names for each additional image segmentation map specified by IMG parameter.

**OUTPUT:** name of the output directory.

**PRE_OUT:** string to prepend to the output files (will be followed by 'id.fits')

**SIZE:** this is the size of the subcube and postage stamp images the software will create (in arcseconds). If in constant mode, make sure this is at least as big as your largest source in the data. If in catalogue mode, this is defined in the catalogue file instead, this parameter however will be used as default if value is missing. Note that this size is the full size of the image/cube (i.e. 5 will produce a 5x5 arcsecond cut out centred on the RA and DEC from the catalog). You should also consider processing time when deciding on this value, a larger size will mean bigger subcubes and images and larger extraction times. 

**XCOR:** this parameter tells the code if it should perform the extra cross-correlation step or not. This produces a higher S/N final spectra but adds on a little more time for each object. 

**CONT_SUB:** here we decide if we want to perform continuum subtraction. This step is crucial if your sources are likely to have neighbouring contaminents that are likely to fall within the same cut outs. Note that this step will only run if you have set XCOR to True.

**CONT_POLY:** sets the order of the polynomial to fit the continuum, 5 tends to be a good start. 

**PLOTS:** this parameter lets the user decide if the they want to output plots or not. The software creates up to 4 plots per source; ID_IMAGES.jpg will show a postage stamp of each of the images with the corresponding segmentation map and additional segmentation maps provided, ID_MASKS.jpg shows the sky and object masks used for extraction, ID_SPECTRA.jpg shows the reference (top) and final spectra (bottom) extracted. Finally ID_XCOR.jpg will display the calculated cross-correlation map.

**OUT_XXX:** these options let the user decide which objects they want saving in the output source fits file. The average size of the output (with 2 additional images) is ~ 35Mb if you save everything. The default setting is to not save the subcubes, as for most cases I can't imagine them being overly useful, they also contribute to almost all of this file size (with the subcubes turned off the file size is only a feew hundred kB).

**CMAP:** here you can specify which of the matplotlib colour maps you would like to use. Examples of the default colourmaps can be found [here](cmaps.png). 

**ORIG_XXX:** are related to the MPDAF pacakge ([see here](http://mpdaf.readthedocs.io/en/latest/api/mpdaf.sdetect.Source.html#mpdaf.sdetect.Source.from_data)), I thought some users might find this useful.

**WARNINGS:** sometimes your datacube might have some extra headers that astropy doesn't like. MPDAF also outputs a lot of info into the terminal that isn't necessary. Can be turned on to debug any issue you may be having. 

### SExtractor File
SExtractor will use the default.nnw, default.param, default.sex and .conv files present in the working directory. If not present, default parameter files are created and used. It is best to try running SExtractor on the images first to get the settings right. If you are using multiple images where a single SExtractor file is not ideal, you can create the segmentation maps using your input images outside of AutoSpec and load them under the SEG_MAP parameter instead.

### Running the Code
My advice would be to try this on a single object first, make sure it works how you want by outputting the plots and/or all of the images etc (defined in OUT_XXX parameters explained above). If you are using AutoSpec to produce segmentation maps you should also check that the SExtractor file (default.sex) is set up correctly for your data, a simple check would be to look at the ID_IMAGES.jpg output and see how well it is defining the segmentation maps. If you haven't used SExtractor before there is much too much to explain here but the [for dummies manual](http://mensa.ast.uct.ac.za/~holwerda/SE/Manual.html) is a good place to start.

To check if the cross-correlation is doing a good job, you'll want to compare the reference and final spectra (top and bottom on the ID_SPECTRA.jpg image). The cross-correlation spectrum usually has visibly better signal to noise, and the emission/absorption features tend to be more well defined .

You can also check the output file by following the steps details [below](#loading-the-output).

### Loading the Output
The output files are created and saved via the MPDAF framework ([here](http://mpdaf.readthedocs.io/en/latest/source.html)) in fits format. You should be able to open these however you normally open fits files but some basic python commands are detailed here (see the [mpdaf page](http://mpdaf.readthedocs.io/en/latest/source.html) for more):
```
from mpdaf.sdetect import Source

# load the file.
source = Source.from_file('filename.fits')

# view the contents.
source.info()

# plot an image.
source.images['MUSE_WHITE'].plot(title='MUSE WHITE')
```

## Running the tests

Download the [test folder](test) from this github page to somewhere on your computer. Additionally, you will need to download the datacube into the test folder, the datacube can be downloaded from [here](https://drive.google.com/open?id=1FewIkG2yHgGlBq1kWE1sHtUu7_DRPbDC) (can't be uploaded to github due to filesize).

You can run the code as is by opening a terminal and navigating to the test directory and running the code with: 
```
# exacutable
AutoSpec

# non-exacutable
/installed_dir/AutoSpec
```
More information can be found in the [usage section](#usage).

I tried to choose test data in which there were a range of objects at various redshifts, some of which need deblending from a neighbouring source (look at objects ID:207 and 208). The improved spectrum from AutoSpec's cross-correlation method can be seen by comparing the top and bottom spectra in the output image ID_SPECTRA.jpg.

For more test data you could use the [HUDF data](http://muse-vlt.eu/science/hdfs-v1-0/) in which MUSE datacubes and object catalogues are publicly available. 

## Current Issues

- Only one SExtractor file for each run (over all images). This is due to the way the MPDAF module works. To avoid this issue, run SExtractor manually and import the segmentation maps via the SEG_MAP parameter instead of defining the images in the IMG parameter.

## Further Improvements

Heres a list of functionality that I'd like to add in the near future:

- [X] Test/adapt code to work with python 2?
- [X] Fix spectra that don't extract due to empty segmentation maps.
- [X] Let users specify a weight image for intial spectral extraction.
- [X] Create output for summary of results (if successful or error encountered etc).
- [X] Think of a catchy name!
- [ ] Make progress bar more persistent.
- [ ] Test on other systems (windows/mac)
- [ ] Test compatibility with other datacubes (not just MUSE).
- [X] ~~Allow user to specify number of cores to use.~~ (Now uses faster numpy method instead of multiprocessing)
- [ ] Quantify to what degree the cross-correlation spectrum is better (in regards to S/N)?
- [ ] Fix automatic MUSE naming for use with different data.
- [X] Let user import a segmentation map instead of images.
- [ ] Add more useful information to output logs.
- [ ] Let user specify wavelength ranges to extract narrow band images around emission lines. 
- [ ] Implement an itterative process to perform cross-correlation mapping. 

...and some more long term goals:

- [ ] Create GUI interface.
- [ ] Direct redshift estimation?
- [ ] Add option to output fits file for [MARZ](github.com/Samreay/Marz) redshift analysis.
- [ ] Integrate the input of MUSELET and/or LSDCat input catalogues.
- [X] Improve speed of continuum subtraction.
- [X] Adapt code to work on a per object basis.

## Authors

* **Alex Griffiths** [[Email](mailto:alex.griffiths@nottingham.ac.uk), [LinkedIn](https://www.linkedin.com/in/alex-griffiths/), [ORCID](https://orcid.org/0000-0003-1880-3509), [Google Scholar](https://scholar.google.co.uk/citations?user=dDnyc94AAAAJ&hl=en)]

## How to Cite

Information coming soon...

## Acknowledgements

This creation of this software wouldn't have been be possible without:

* MUSE Python Data Analysis Framework ([MPDAF; Bacon et al. 2016](http://adsabs.harvard.edu/abs/2016ascl.soft11003B))
* SExtractor ([Bertin & Arnouts 1996](http://adsabs.harvard.edu/abs/1996A%26AS..117..393B))

## License

Copyright (c) 2018, Alex Griffiths

AutoSpec is licenced under a [BSD 3-Clause License](LICENSE.md)

## Changelog

**v.1.0.0:** July 5, 2018 

* Increased the speed of continuum subtraction routine (now ~8x faster).
* Adapted code to work on python 2.
* Fixed a number of small issues.
* Can extract spectra from a list of user defined apertures.
* User can now import additional segmentation maps.
* User can specify extraction methods on a per object basis.

**Testing:** March 23, 2018 

* Functioning code for testing purposes.
