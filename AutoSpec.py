# -*- coding: utf-8 -*-
"""
Datacube Spectrum Extractor
@author: Alex Griffiths
"""
# Import dependencies.
from __future__ import absolute_import, division, print_function

import numpy as np
import matplotlib.pyplot as plt
from mpdaf.obj import Cube, Spectrum, Image
from mpdaf.sdetect import Source, sea
import warnings
import os
import sys


# Main function that does the bulk of the work.
def create_source(ID, ra, dec):
    """Create source object based on input datacube and images.

    Appends images and subcube to the source and extracts object spectra.

    Parameters
    ----------
    ID : int
        ID of the source
    ra : double
        Right ascension in degrees
    dec : double
        Declination in degrees
    plot : bool
        If True (default), produces plots of images, segmentation maps,
        masks and spectra.

    """

    # This creates the source object (see MPDAF for more details).
    s = Source.from_data(ID=ID, ra=ra, dec=dec,
                         origin=(params.ORIG_FROM, params.ORIG_FROMV,
                                 params.ORIG_CUBE, params.ORIGN_CUBEV),
                         extras=extra)

    # Add subcube, create white image and add additional images.
    s = add_data(s)

    # Use SExtractor to create object and sky mask.
    s, seg = create_masks(s)

    # Set mask to user selected option.
    mask = 'MASK_'+params.OBJ_MASK

    # Sometimes SExtractor may not pick up an object in a particular image.
    # If this is the case and one of the segmentation maps are empty, the
    # intersection mask will also be empty, in these cases it is best to
    # default to the union mask.
    for i in seg:
        if np.sum(s.images[str(i.upper())].data.data) == 0:
            mask = 'MASK_UNION'

    s.extract_spectra(s.cubes['MUSE'], obj_mask=mask,
                      sky_mask='MASK_SKY', skysub=params.SKY_SUB,
                      tags_to_try='MUSE_WHITE')

    # No need to subtract continuum if we're not going to cross-correlate.
    if params.XCOR is True:

        # Continuum subtraction method depends on whether the user has
        # sky-subtraction or not, this part takes the longest but is neccessary
        # to achieve good results if there is contamination in the frame.
        if params.CONT_SUB and params.SKY_SUB is True:

            s.spectra['MUSE_TOT_SKYSUB_CONTSUB'] = \
                s.spectra['MUSE_TOT_SKYSUB'] \
                - s.spectra['MUSE_TOT_SKYSUB'].poly_spec(params.CONT_POLY)
            s.add_cube(continuum_subtraction(s, params.CONT_POLY),
                       'MUSE_CONTSUB')

        elif params.CONT_SUB is True and params.SKY_SUB is False:

            s.spectra['MUSE_TOT_CONTSUB'] = s.spectra['MUSE_TOT'] \
                - s.spectra['MUSE_TOT'].poly_spec(params.CONT_POLY)
            s.add_cube(continuum_subtraction(s, params.CONT_POLY),
                       'MUSE_CONTSUB')

        # Finally we cross correlate to get the final spectrum.
        s = cross_correlate(s)

    # If user wants them, plots are created and output here.
    if params.PLOTS is True:

        # Plot images and save file.
        plt.subplots(2, len(imgs)+1, sharex=True, sharey=True)
        for i, key in enumerate(imgs):
            plt.subplot(2, len(imgs)+1, i+1)
            s.images[key].plot(title=key)
            if i != range(0, len(imgs)-1):
                plt.xticks([])
                plt.xlabel('')
            if i != 0:
                plt.yticks([])
                plt.ylabel('')
            plt.subplot(2, len(imgs)+1, len(imgs)+i+2)
            s.images['SEG_'+str(key)].plot(title='SEG_'+str(key))
            if i != 0:
                plt.yticks([])
                plt.ylabel('')
        plt.subplot(2, len(imgs)+1, len(imgs)+1)
        s.images['MUSE_WHITE'].plot(title='MUSE_WHITE')
        plt.xticks([])
        plt.xlabel('')
        plt.yticks([])
        plt.ylabel('')
        plt.subplot(2, len(imgs)+1, 2*len(imgs)+2)
        s.images['SEG_MUSE_WHITE'].plot(title='SEG_MUSE_WHITE')
        plt.yticks([])
        plt.ylabel('')
        plt.tight_layout()
        plt.savefig(str(params.OUTPUT)+'/images/%d_IMAGES.jpg' % ID)

        # Plot masks and save file.
        plt.figure(figsize=(7, 3))
        plt.subplot(1, 3, 1)
        s.images['MASK_INTER'].plot(title='MASK_INTER')
        plt.subplot(1, 3, 2)
        s.images['MASK_UNION'].plot(title='MASK_UNION')
        plt.yticks([])
        plt.ylabel('')
        plt.subplot(1, 3, 3)
        s.images['MASK_SKY'].plot(title='MASK_SKY')
        plt.yticks([])
        plt.ylabel('')
        plt.tight_layout()
        plt.savefig(str(params.OUTPUT)+'/images/%d_MASKS.jpg' % ID)

        # Plot spectra and save file.
        f, ax = plt.subplots(1, len(s.spectra),
                             figsize=(10, 2.5*len(s.spectra)), sharex=True)
        for i, j in enumerate(s.spectra):
            plt.subplot(len(s.spectra), 1, i+1)
            s.spectra[j].plot(title=j)
            if i != len(s.spectra)-1:
                plt.xticks([])
                plt.xlabel('')
            plt.ylabel('')
            ylabel = s.spectra[j].unit
        plt.tight_layout()
        f.subplots_adjust(left=0.08)
        f.text(0.01, 0.5, ylabel, va='center', rotation='vertical')
        plt.savefig(str(params.OUTPUT)+'/images/%d_SPECTRA.jpg' % ID)

        # Plot and save cross correlation.
        if params.XCOR is True:
            plt.figure(figsize=(4, 4))
            s.images['CROSS_CORRELATION'].plot(title='CROSS_CORRELATION')
            plt.tight_layout()
            plt.savefig(str(params.OUTPUT)+'/images/%d_XCORRELATION.jpg' % ID)

    # Output file is cleaned if the user wishes.
    s = clean_output(s)

    return s


def add_data(src):
    """Add images to the source object

    Parameters
    ----------
    src : mpdaf.sdetect.source.Source
        Input source object

    """
    src.add_cube(cube, 'MUSE', size=params.SIZE)
    src.add_white_image(cube, size=params.SIZE)

    for key in imgs:
        src.add_image(imgs[key], name=key)

    return src


def create_masks(src):
    """Create segmentation maps and masks

    Parameters
    ----------
    src : mpdaf.sdetect.source.Source
        Input source object

    """
    src.add_seg_images(del_sex=False)
    seg = ['SEG_'+i for i in list(imgs.keys())]
    seg.append('SEG_MUSE_WHITE')
    src.find_sky_mask(seg)
    src.find_union_mask(seg)
    src.find_intersection_mask(seg)

    return src, seg


def continuum_subtraction(src, poly):
    """Perform continuum subtraction from the MUSE subcube

    Parameters
    ----------
    src : mpdaf.sdetect.source.Source
        Input source object
    poly : int
        Order of the polynomial for continuum estimation

    """
    c = src.cubes['MUSE'].loop_spe_multiprocessing(f=Spectrum.poly_spec,
                                                   deg=poly)
    csub = src.cubes['MUSE'] - c

    # Print stops whatever is output next from appearing on the same line.
    print('')

    return csub


def cross_correlate(src):
    """Create cross-correlation image against reference spectrum

    Parameters
    ----------
    src : mpdaf.sdetect.source.Source
        Input source object

    """
    if params.CONT_SUB and params.SKY_SUB is True:
        ref = 'MUSE_TOT_SKYSUB_CONTSUB'
        cubeName = 'MUSE_CONTSUB'
    elif params.SKY_SUB is True:
        ref = 'MUSE_TOT_SKYSUB'
        cubeName = 'MUSE'
    else:
        ref = 'MUSE_TOT'
        cubeName = 'MUSE'

    scube = src.cubes[cubeName]
    rspec = src.spectra[ref].data.data
    rspec = np.tile(rspec[:, np.newaxis, np.newaxis],
                    (scube.shape[1], scube.shape[2]))

    xc = (rspec * scube.data.data).sum(axis=0)
    xc = xc/np.sum(xc)

    xc_img = src.images['MUSE_WHITE'].clone(data_init=np.zeros)
    xc_img.data.data[:, :] = xc

    src.images['CROSS_CORRELATION'] = xc_img

    xcmask = np.array(xc_img.data.data)
    xcmask[xcmask < xc_img.background()[0]] = 0

    xcspec = sea.compute_spectrum(src.cubes['MUSE'], xcmask)

    if params.SKY_SUB is True:
        xcspec -= src.spectra['MUSE_SKY'].data.data
        src.spectra['MUSE_CCWEIGHTED_SKYSUB'] = xcspec
    else:
        src.spectra['MUSE_CCWEIGHTED'] = xcspec

    return src


def clean_output(src):
    """Clean the output based on user defined parameters

    Parameters
    ----------
    src : mpdaf.sdetect.source.Source
        Input source object

    """
    # Remove images.
    if params.OUT_IMG is False:
        print('Removing images')
        for key in imgs:
            del src.images[key]
        del src.images['MUSE_WHITE']

    # Remove image segmentation maps.
    if params.OUT_SEG is False:
        print('Removing segmentation maps')
        for key in imgs:
            del src.images['SEG_'+key]
        del src.images['SEG_MUSE_WHITE']

    # Remove object mask, sky mask and cross-correlation map.
    if params.OUT_MASK is False:
        print('Removing masks')
        del src.images['MASK_INTER']
        del src.images['MASK_UNION']
        del src.images['MASK_SKY']
        if params.XCOR is True:
            del src.images['CROSS_CORRELATION']

    # Remove additional spectra.
    if params.OUT_SPEC is False:
        print('Removing additional spectra')
        if params.SKY_SUB and params.CONT_SUB is True:
            del src.spectra['MUSE_SKY']
            del src.spectra['MUSE_TOT_SKYSUB_CONTSUB']
            if params.XCOR is True:
                del src.spectra['MUSE_TOT_SKYSUB']

        elif params.SKY_SUB and params.CONT_SUB is False:
            if params.XCOR is True:
                del src.spectra['MUSE_TOT']

        elif params.SKY_SUB is False and params.CONT_SUB is True:
            del src.spectra['MUSE_TOT_CONTSUB']
            if params.XCOR is True:
                del src.spectra['MUSE_TOT']

        elif params.SKY_SUB is True and params.CONT_SUB is False:
            del src.spectra['MUSE_SKY']
            if params.XCOR is True:
                del src.spectra['MUSE_TOT_SKYSUB']

    # Remove subcubes.
    if params.OUT_SUB is False:
        print('Removing subcubes')
        src.cubes.clear()

    return src


# Create progress bar to show for catalog processing.
def print_progress(iteration, total, prefix='', suffix='', decimals=1,
                   bar_length=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent
                                  complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = '{0:.' + str(decimals) + 'f}'
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s \n\n' % (prefix, bar, percents,
                                                 '%', suffix))
    sys.stdout.flush()


def main():

    # Set up global variables.
    global cube, params, imgs, extra

    # Set current working directory.
    cwd = os.getcwd()+'/'

    # First check that the parameter file exists and is named correctly.
    # If it exists import the file.
    try:
        sys.path.append(str(cwd))
        import param as params
    except Exception:
        raise ImportError('No parameter file found, please ensure file name'
                          ' is param.py and located in the working directory.')

    # Sometimes if the datacube has some odd headers in, astropy gives off
    # a load of warnings that dominate the output, if this is the case the
    # user can choose to ignore them.
    if params.WARNINGS is True:
        warnings.filterwarnings('default')
    else:
        warnings.filterwarnings('ignore')

    # Check that the defined catalogue file exists and import it.
    try:
        cat = np.genfromtxt(cwd+params.CATALOG, comments='#')
    except Exception:
        raise ImportError('No catalog file ('+str(params.CATALOG)+') found.')

    # Import any additional images defined in the parameter file.
    imgs = {}
    for i, j in zip(params.IMG, params.IMG_NAME):
        imgs['{0}'.format(j.upper())] = Image(cwd+i)

    # Check the datacube exists and import it.
    try:
        cube = Cube(cwd+params.DATACUBE)
    except Exception:
        raise ImportError('No datacube file ('+str(params.DATACUBE)+') found.')

    # If all files load successfully, create output directory structure.
    file_path = cwd+params.OUTPUT
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    # If image output is set to true, create subdirectories.
    if params.PLOTS is True:
        img_path = file_path+'/images'
        if not os.path.exists(img_path):
            os.makedirs(img_path)

    # Define additional headers to be stored in fits.
    extra = {'EXT': ('NAME', 'extraction software'),
             'EXT_V': ('1.0', 'version of the extraction software')}

    # Need to check if there is one or more object in the input catalog.
    # This code calls the functions to create the source object and output
    # the results. The user can decide (via the param.py file) if they want to
    # perform cross correlation, continuum subtraction and sky subtraction.
    # The user can also decide if they want the images, segmentation maps and
    # cross-correlation maps to be included in the output file.

    # Run code for a single object catalog.
    if cat.size == 3:
        # Turn interactive plotting on.
        plt.ion()
        try:
            S = create_source(ID=int(cat[0]), ra=cat[1], dec=cat[2])
            S.write(file_path+'/'+params.PRE_OUT+'%d.fits' % cat[0])
            del S
        except Exception as e:
            print('Error: '+str(e))
            pass

    # Run code over multi-object catalog.
    else:
        # Turn interactive plotting off.
        plt.ioff()
        # Find catalog length for progress bar.
        length = len(cat)
        for n, m in enumerate(cat):

            try:
                S = create_source(ID=int(m[0]), ra=m[1], dec=m[2])
                S.write(file_path+'/'+params.PRE_OUT+'%d.fits' % m[0])
                del S
            except Exception as e:
                print('Error : Source '+str(int(m[0]))+' '+str(e))
                pass
            # Show current progress.
            print('\nSource  : '+str(n+1)+'/'+str(length))
            print_progress(n+1, length, prefix='Progress:', suffix='Complete',
                           decimals=0, bar_length=50)


# Run the code.
if __name__ == '__main__':
    main()
