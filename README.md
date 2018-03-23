# AutoSpec (Need to come up with a catchy name)

This software aims to provide fast, automated extraction of high quality 1D spectra from astronomical datacubes with minimal effort. Autospec takes an IFU datacube, along with any suplimentary images to extract a 1D spectra for each object in the supplied catalog. A custom designed cross-correlation algorithm helps to improve signal to noise as well as deblend sources from neighbouring contaminants.

## Getting Started

Currently the code has only been tested on a linux system but it should work as long as the prerequisites are met.

## Prerequisites

Before you start make sure you have the following pieces of software installed:

```
- Python 3
- Source Extractor (https://www.astromatic.net/software/sextractor)
```

You will also need the following python pacakges:

```
- numpy
- matplotlib
- mpdaf (http://mpdaf.readthedocs.io/en/latest/)
```

## Installing

Installation is pretty simple, just copy download the AutoSpec.py and params.py files and save them wherever you want.

## Usage

I've tried to make this as simple as possible but I'd suggest having a quick read through this section before you try it for yourself....


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

**OUT_XXX:** these options let the user decide which objects they want saving in the output source fits file. The average size of the output (with 2 additional images) is ~ 35Mb if you save everything. The default setting is to not save the subcubes, as for most cases I can't imagine them being overly useful, they also contribute to almost all of this file size (with the subcubes turned off the file size is only a feew hundred kB).

**ORIG_XXX:** are related to the MPDAF pacakge ([see here](http://mpdaf.readthedocs.io/en/latest/api/mpdaf.sdetect.Source.html#mpdaf.sdetect.Source.from_data)), I thought some users might find this useful.

**WARNINGS:** when developing the code I was using a datacube that had some extra headers in that astropy didn't like. As a result I got a lot of warnings which dominated the output so I couldn't see what was happening with the code, added this parameter in incase any users had the same issue. 

### SExtractor File
SExtractor will use the default.nnw, default.param, default.sex and .conv files present in the current directory. If not present default parameter files are created. 

### Running the Code
My advice would be to try this on a single object first, make sure it works how you want by outputting the plots and/or all of the images etc (defined in OUT_XXX parameters explained above). The more supplimentary images you supply the better the results are likely to be. You should also check that the SEctractor file (default.sex) is set up correctly for your data, a simple check would be to look at the ID_IMAGES.jpg output and see how well it is defining the segmentation maps. If you haven't used SExtractor before there is much too much to explain here but the [for dummies manual](http://mensa.ast.uct.ac.za/~holwerda/SE/Manual.html) would be a good place to start. Once you have it working, change the CATALOG parameter to your full catalog and away you go. While testing you might also want to consider the extraction times with the added continuum subtraction and cross-correlation vs the imporvement in the spectra. I find that these steps provide much higher S/N and work very well at deblending the sources (this is what I designed the code for in the first place). If you have low redshift, well defined objects without much neighbouring contamination, you should be able to get away without these steps. Another alternative is to run without these steps first and have a look at the outputs, then re-run the code on a sub-catalog with only the objects that require imporvemening. 

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

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Further Improvements

Heres a list of functionality that I'd like to add in the future.

    - [] Think of a catchy name!
    - [] Test on other systems (windows/mac)
    - [] Test/adapt code to work with python 2?
    - [] Create GUI interface.
    - [] Add option to output fits file for MARZ analysis: github.com/Samreay/Marz
    - [] Integrate MUSELET and/or LSDCat input catalogs.
    - [] Direct redshift estimation.
    - [] Improve speed of continuum subtraction.
    - [] Add more options for the user (maybe on a per object basis).
    - [] Probably a lot of other stuff...

## Versions

**1.0.0: March 23, 2018** 

* Functioning code for testing purposes.

## Authors

* **Alex Griffiths**

## License

Get open source licensing sorted.

## Acknowledgments

* Probably some people in here. 
