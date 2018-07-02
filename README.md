# AutoSpec

This software aims to provide fast, automated extraction of high quality 1D spectra from astronomical datacubes with minimal user effort. Autospec takes an IFU datacube and a simple parameter file in order to extract a 1D spectra for each object in a supplied catalog. A custom designed cross-correlation algorithm helps to improve signal to noise as well as deblend sources from neighbouring contaminants.

## Contents

- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Installing](#installing)
- [Usage](#usage)
  - [The Catalog](#the-catalog)
  - [The Parameter File](#the-parameter-file)
  - [SExtractor File](#sextractor-file)
  - [Running the Code](#running-the-code)
  - [Loading the Output](#loading-the-output)
- [Running the tests](#running-the-tests)
- [Current Issues](#current-issues)
- [Further Improvements](#further-improvements)
- [Versions](#versions)
- [Authors](#authors)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Getting Started

Currently the code has only been tested on a linux system but it should work as long as the prerequisites are met. Thus, all installation and running instructions are based on linux systems (for now).

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

AutoSpec doesn't need to be installed, just clone or download the github repository. With git clone use:
```
git clone https://github.com/a-griffiths/AutoSpec.git
```
The easiest way to run AutoSpec is to make it it executable. To do this simply navigate to the AutoSpec directory and run `chmod +x AutoSpec`. You also need to add the line `export PATH=$PATH:/installed_directory/AutoSpec/` to your .bashrc file.

## Usage

AutoSpec is designed to be as intuitive as possible, this section will provide a brief run through on the different elements of the software.

First off, create a working folder; this should contain a minimum of the datacube, parameter file and catalogue file. The default parameter file can be found [here](param.py), an example [catalog](test/catalog.txt) file can be found in the test folder on github. You can also include any additional images, segmentation maps and sextractor configuration files. 

Edit the parameter file with a text editor, making sure to keep the formatting correct ([as detailed below](#the-parameter-file)). The code can then be run through the command line by simple navigating to your working directory and running:
```
AutoSpec
```
_# Note: If you haven't made AutoSpec [bootable](#installing) then you will need to run AutoSpec directly from the software directory `/installed_directory/AutoSpec`_

_## Note: All output subdirectories will be automatically created._

### The Catalog
The first thing you need to do is create a catalog file (simple text or csv file, not fits). An example is supplied in the test data folder and should be in the following format:
```
#ID     RA      DEC
(int)   (deg)   (deg)
```

### The Parameter File
Then you just need to edit the parameter file to your liking. Everything is explained in the comments of the file but I shall expand on the not so obvious ones here.

**SIZE:** this is the size of the subcube and postage stamp images the software will create (in arcseconds), make sure this is atleast as big as your largest source in the data. Note that this size is the full size of the image/cube (i.e. 5 will produce a 5x5 arcsecond cut out centred on the RA and DEC from the catalog). 

**XCOR:** this parameter tells the code if it should perform the extra cross-correlation step or not. This produces a higher S/N final spectra but adds on a little more time for each object. 

**CONT_SUB:** here we decide if we want to perform continuum subtraction, be warned that this increases the processing time for each object about 7 fold. This step is however crucial if your sources are likely to have neighbours that are likely to fall within the same cut outs. Note that this step will only run if you have set XCOR to True.

**CONT_POLY:** just sets the order of the polynomial to fit the continuum, 5 tends to be a good start but if this doesn't work so well it might be an idea to have a play with the value. 

**PLOTS:** this parameter lets the user decide if the they want to output plots or not. The software creates up to 4 plots per source; ID_IMAGES.jpg will show a postage stamp of each of the images with the corresponding segmentation map, ID_MASKS.jpg shows the sky and object masks, ID_SPECTRA.jpg shows each of the spectra extracted and finally ID_XCORRELATION.jpg will display the calculated cross-correlation map (file size of the output images is a few hundred kB per source).

**OBJ_MASK:** here we define if you want to use the intersection or the union of the individual segmentation maps to produce an object mask in order to build the initial spectrum. The intersection mask only selects areas where the object overlaps in the combined images, union puts all the areas together. If you choose intersection and SExtractor doesn't find the object in one of the images, the code defaults to using the union mask in order to successfully extract a spectrum. 

**OUT_XXX:** these options let the user decide which objects they want saving in the output source fits file. The average size of the output (with 2 additional images) is ~ 35Mb if you save everything. The default setting is to not save the subcubes, as for most cases I can't imagine them being overly useful, they also contribute to almost all of this file size (with the subcubes turned off the file size is only a feew hundred kB).

**ORIG_XXX:** are related to the MPDAF pacakge ([see here](http://mpdaf.readthedocs.io/en/latest/api/mpdaf.sdetect.Source.html#mpdaf.sdetect.Source.from_data)), I thought some users might find this useful.

**WARNINGS:** when developing the code I was using a datacube that had some extra headers in that astropy didn't like. As a result I got a lot of warnings which dominated the output so I couldn't see what was happening with the code, added this parameter in incase any users had the same issue. 

### SExtractor File
SExtractor will use the default.nnw, default.param, default.sex and .conv files present in the working directory. If not present, default parameter files are created and used. 

### Running the Code
My advice would be to try this on a single object first, make sure it works how you want by outputting the plots and/or all of the images etc (defined in OUT_XXX parameters explained above). You should also check that the SExtractor file (default.sex) is set up correctly for your data, a simple check would be to look at the ID_IMAGES.jpg output and see how well it is defining the segmentation maps. If you haven't used SExtractor before there is much too much to explain here but the [for dummies manual](http://mensa.ast.uct.ac.za/~holwerda/SE/Manual.html) is a good place to start.

To check if the cross-correlation is doing a good job, you'll want to compare the 'MUSE_TOT_SKYSUB' spectrum (or 'MUSE_TOT' if you don't do the sky subtraction) to the 'MUSE_CCWEIGHTED_SKYSUB' spectrum (again, 'MUSE_CCWEIGHTED' if you didn't sky subtract). The cross-correlation spectrum usually has visibly less noise, and the emission/absorption features tend to be more well defined (I'm yet to figure out a way to quantify by what degree this happens but it's on the to-do list).

Once you have it working, change the CATALOG parameter to your full catalog and away you go. While testing you might also want to consider the extraction times with the added continuum subtraction and cross-correlation vs the imporvement in the spectra. I find that these steps provide much higher S/N and work very well at deblending the sources (this is what I designed the code for in the first place). If you have low redshift, well defined objects without much neighbouring contamination, you should be able to get away without these steps. Another alternative is to run without these steps first and have a look at the outputs, then re-run the code on a sub-catalog with only the objects that require imporvement. 

### Loading the Output
The output files are created and saved via the MPDAF framework ([here](http://mpdaf.readthedocs.io/en/latest/source.html)) in fits format. You should be able to open these however you normally open fits files but I will explain some basic commands for python here (see the mpdaf page for more):

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

Download the test folder from this github page to somewhere on your computer. Also download the main code AutoSpec.py to somewhere you'll remember. Additionally, you will need to download the datacube and put it in the test folder, the datacube can be downloaded from [here](https://drive.google.com/open?id=1FewIkG2yHgGlBq1kWE1sHtUu7_DRPbDC) (can't upload to github due to filesize).

You can run the code as is by opening a terminal and typing: 
```
cd /data/directory/test
python /installed/directory/Autospec.py
```
Obviously replace "/data/directory/test" and "/installed/directory/" with the directories in which the test data is stored and the AutoSpec.py file is saved respectively.

I tried to choose test data in which there were a range of objects at various redshifts, some with deblending needed. The improved spectrum from the cross-correlation algorithm can be see by comparing the 'MUSE_CCWEIGHTED_SKYSUB' to 'MUSE_TOT_SKYSUB' spectra in the output images. This is improvement is most obvious in object 207, the galaxy is in close proximity to another at a different redshift (object id:208). Here the continuum subtraction and cross-correlation algorithms implemented within this code successfully isolate the source and subtract a much higher S/N spectrum. 

## Current Issues

- Only one SExtractor file for each run (all images and objects). This is due to the way the MPDAF module works, I may be able to find a work around for this in the future but for now you will need to run the code on seperate catalogs if you want to use multiple Sextractor settings. As for the different images, it is best to just try and find a good comprimise. 
- Currently a lot of parameters are set for every object, such as extraction size and continuum subtraction, in future releases I will impliment a way to set these on a object to object basis, maybe using additional columns in the catalog. 

## Further Improvements

Heres a list of functionality that I'd like to add in the near future:

- [X] Test/adapt code to work with python 2?
- [X] Fix spectra that don't extract due to empty segmentation maps.
- [X] Let users specify a weight image for intial spectral extraction.
- [X] Create output for summary of results (if successful or error encountered etc).
- [ ] Think of a catchy name!
- [ ] Make progress bar more persistent.
- [ ] Test on other systems (windows/mac)
- [ ] Test compatibility with other datacubes (not just MUSE).
- [ ] Allow user to specify number of cores to use.
- [ ] Quantify to what degree the cross-correlation is better?
- [ ] Fix automatic MUSE naming for use with different data.
- [ ] Let user import a segmentation map instead of images.
- [ ] Probably a lot of other stuff...

...and some more long term goals:

- [ ] Create GUI interface.
- [ ] Direct redshift estimation.
- [ ] Add option to output fits file for MARZ analysis: github.com/Samreay/Marz
- [ ] Integrate MUSELET and/or LSDCat input catalogs.
- [ ] Improve speed of continuum subtraction.
- [ ] Add more options for the user (maybe on a per object basis).

## Versions

**v.1.0.0:** March 23, 2018 

* Functioning code for testing purposes.

## Authors

* **Alex Griffiths**

## License

Get open source licensing sorted.

## Acknowledgments

* Probably some people in here. 
