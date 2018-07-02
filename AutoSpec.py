# -*- coding: utf-8 -*-
"""
Datacube Spectrum Extractor
@author: Alex Griffiths
"""
# Import dependencies.
from __future__ import absolute_import, division, print_function

from mpdaf.obj import Cube, Image  # Spectrum, iter_spe
from mpdaf.sdetect import Source, sea
import matplotlib.pyplot as plt
import astropy.units as u
import seaborn as sns
import numpy as np
import warnings
import mpdaf
import time
import sys
import os

# Set up seaborn plot
sns.set_style("ticks")   # white, dark, whitegrid, darkgrid, ticks
sns.set_context("paper")  # paper, notebook, talk, poster

SOFTWARE = 'AutoSpec'
VERSION = 'v.1.0.0'
AUTHOR = 'Alex Griffiths'


# Main function that does the bulk of the work.
def create_source(ID, ra, dec, mode='', ref=''):
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
    mode : Str
        If img, spectra will be extracted based on morphology using SExtractor
        segmentation maps carried out on images provided. If aper, will extract
        based on provided aperture size in ref
    ref : Str
        If mode is img, ref should be name of reference image for spectrum
        weighting. If mode is aper, should be the size of aperture to extract
        the spectrum from.

    """
    weight_img = params.WEIGHT_IMG.upper()
    refspec = ext_mode = ''

    if mode == '':
        if params.REF.replace('.', '').isdigit() is True:
            ref = str(params.REF)
            ext_mode = 'APER'
            refspec = 'MUSE_APER_%.1f' % float(params.REF)
        elif params.REF.replace('.', '').isdigit() is False:
            ref = str(params.REF.upper())
            ext_mode = 'IMG'
            refspec = 'MUSE_TOT'
    elif mode != '':
        ext_mode = mode.upper()
        ref = ref.upper()
        if ext_mode == 'APER':
            refspec = 'MUSE_APER_%.1f' % float(ref)
        elif ext_mode == 'IMG':
            refspec = 'MUSE_TOT'
            weight_img = ref.upper()

    # This creates the source object (see MPDAF for more details).
    s = Source.from_data(ID=ID, ra=ra, dec=dec,
                         origin=(params.ORIG_FROM, params.ORIG_FROMV,
                                 params.ORIG_CUBE, params.ORIGN_CUBEV),
                         extras=extra)

    # Add subcube, create white image and add additional images.
    s = add_data(s)

    if ext_mode == 'IMG':
        s, seg = create_masks(s)
        mask = 'MASK_'+params.OBJ_MASK

        # Sometimes SExtractor may not pick up an object in a particular image.
        # If this is the case and one of the segmentation maps are empty, the
        # intersection mask will also be empty, in these cases it is best to
        # default to the union mask.
        if np.sum(s.images[mask].data.data) == 0:
            mask = 'MASK_UNION'

    # produce masks for aperture mode using given aperture size. The code also
    # reverts to aperture mode if is set to image mode and masks are empty.
    elif ext_mode == 'APER' or np.sum(s.images[mask].data.data) == 0:
        # if using aperture as reference, create sky and object mask
        temp = s.images['MUSE_WHITE'].copy()
        pxsz = temp.get_step(unit=u.arcsec)[0]
        cntr = [temp.shape[0]/2, temp.shape[0]/2]
        rds = float(ref)/pxsz

        temp.mask_region(center=cntr, radius=rds, unit_center=None,
                         unit_radius=None, inside=False)

        s.images['MASK_SKY'] = temp.new_from_obj(temp, data=temp.mask*1)
        s.images['MASK_APER_'+ref] = \
            temp.new_from_obj(temp, data=abs((temp.mask*1)-1))
        mask = 'MASK_APER_'+ref

        del temp

    # select weight image, default to muse white if not in suuplied images
    if weight_img in list(imgs.keys()):
        subcub = s.cubes['MUSE']
        wcsref = subcub.wcs

        w_img = imgs[weight_img]
        w_img = w_img.resample(newdim=subcub.shape[1:],
                               newstart=wcsref.get_start(unit=u.deg),
                               newstep=wcsref.get_step(unit=u.arcsec),
                               order=0, unit_start=u.deg,
                               unit_step=u.arcsec)
    else:
        print('Weight image not found/specified, using Muse white')
        weight_img = 'MUSE_WHITE'
        w_img = s.images['MUSE_WHITE'].copy()

    # normalise image so unmasked area totals 1
    w_img.mask_selection(s.images[mask].data.data == 0)
    w_img.norm(typ='sum', value=1.0)
    w_img.unmask()

    # extract spectra
    s.extract_spectra(s.cubes['MUSE'], obj_mask=mask,
                      sky_mask='MASK_SKY', skysub=params.SKY_SUB,
                      tags_to_try=weight_img, apertures=params.APER)

    # No need to subtract continuum if we're not going to cross-correlate.
    if params.XCOR is True:
        csfx = '_CONTSUB'

        # Continuum subtraction method depends on whether the user has
        # sky-subtraction or not, this part takes the longest but is neccessary
        # to achieve good results if there is contamination in the frame.
        if params.SKY_SUB is True:
            ssfx = '_SKYSUB'
        else:
            ssfx = ''

        s.spectra[refspec+ssfx+csfx] = \
            s.spectra[refspec+ssfx] - \
            s.spectra[refspec+ssfx].poly_spec(params.CONT_POLY)
        s.add_cube(continuum_subtraction(s, params.CONT_POLY), 'MUSE'+csfx)

    else:
        csfx = ''

    # Finally we cross correlate to get the final spectrum.
    s = cross_correlate(s, refspec, csfx, ssfx)

    # If user wants them, plots are created and output here.
    if params.PLOTS is True:

        if ext_mode == 'APER':
            # Plot images and save file.
            r = 1
            c = len(imgs)+1
            plt.subplots(r, c, figsize=(3*c, 3*r), sharex=True, sharey=True)
            for i, key in enumerate(imgs):
                plt.subplot(r, c, i+1)
                s.images[key].plot(title=key, cmap=params.CMAP)
            plt.subplot(r, c, len(imgs)+1)
            s.images['MUSE_WHITE'].plot(title='MUSE_WHITE', cmap=params.CMAP)
        else:
            # Plot images and save file.
            r = int(2+np.ceil(len(smaps)/(len(imgs)+1)))
            c = len(imgs)+1
            rm = int(np.ceil(len(smaps) /
                             (len(imgs)+1))*(len(imgs)+1)-len(smaps))
            plt.subplots(r, c, figsize=(3*c, 3*r), sharex=True, sharey=True)
            for i, key in enumerate(imgs):
                plt.subplot(r, c, i+1)
                s.images[key].plot(title=key, cmap=params.CMAP)
                plt.subplot(r, c, len(imgs)+i+2)
                s.images['SEG_'+str(key)].plot(title='SEG_'+str(key),
                                               cmap=params.CMAP)
            plt.subplot(r, c, len(imgs)+1)
            s.images['MUSE_WHITE'].plot(title='MUSE_WHITE', cmap=params.CMAP)
            plt.subplot(r, c, 2*len(imgs)+2)
            s.images['SEG_MUSE_WHITE'].plot(title='SEG_MUSE_WHITE',
                                            cmap=params.CMAP)
            for i, key in enumerate(smaps):
                plt.subplot(r, c, 3*len(imgs)+i+1)
                s.images['SEG_'+str(key)].plot(title='SEG_'+key,
                                               cmap=params.CMAP)
            for i in range(0, rm):
                plt.subplot(r, c, (r*c)-i)
                plt.axis('off')
        plt.tight_layout(h_pad=1, w_pad=1)
        plt.savefig(str(params.OUTPUT)+'/images/images/%d_IMAGES.jpg' % ID)

        # Plot masks and save file.
        plt.figure(figsize=(5, 3))
        plt.subplot(1, 2, 1)
        s.images[mask].plot(title=mask, cmap=params.CMAP)
        plt.subplot(1, 2, 2)
        s.images['MASK_SKY'].plot(title='MASK_SKY', cmap=params.CMAP)
        plt.yticks([])
        plt.ylabel('')
        plt.tight_layout()
        plt.savefig(str(params.OUTPUT)+'/images/masks/%d_MASKS.jpg' % ID)

        # Plot spectra and save file.
        f, ax = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
        plt.subplot(2, 1, 1)
        s.spectra[refspec+ssfx].plot(title=refspec+ssfx)
        plt.xticks([])
        plt.xlabel('')
        plt.ylabel('')
        plt.subplot(2, 1, 2)
        s.spectra['MUSE_CCWEIGHTED'+ssfx].plot(title='MUSE_CCWEIGHTED'+ssfx)
        plt.ylabel('')
        ylabel = s.spectra[refspec+ssfx+csfx].unit
        plt.tight_layout()
        f.subplots_adjust(left=0.08)
        f.text(0.01, 0.5, ylabel, va='center', rotation='vertical')
        plt.savefig(str(params.OUTPUT)+'/images/spectra/%d_SPECTRA.jpg' % ID)

        # Plot and save cross correlation.
        if params.XCOR is True:
            plt.figure(figsize=(4, 4))
            s.images['CROSS_CORRELATION'].plot(title='CROSS_CORRELATION',
                                               cmap=params.CMAP)
            plt.tight_layout()
            plt.savefig(str(params.OUTPUT) +
                        '/images/xcorrelation/%d_XCORRELATION.jpg' % ID)

    # Output file is cleaned if the user wishes.
    s = clean_output(s, refspec, csfx, ssfx)

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

    subcub = src.cubes['MUSE']
    wcsref = subcub.wcs

    # add images
    for key in imgs:
        src.add_image(imgs[key], name=key)

    # add extra segmentation maps and resample to match white image
    for key in smaps:
        temp = smaps[key]
        temp = temp.resample(newdim=subcub.shape[1:],
                             newstart=wcsref.get_start(unit=u.deg),
                             newstep=wcsref.get_step(unit=u.arcsec),
                             order=0, unit_start=u.deg, unit_step=u.arcsec)

        src.add_image(smaps[key], name='SEG_'+key)

    return src


def create_masks(src):
    """Create segmentation maps and masks

    Parameters
    ----------
    src : mpdaf.sdetect.source.Source
        Input source object

    """
    src.add_seg_images(del_sex=False)
    seg = [i for i in src.images.keys() if 'SEG_' in i]
    src.find_sky_mask(seg)
    src.find_union_mask(seg)
    for key in seg:
        if np.sum(src.images[key].data.data) == 0:
            seg.remove(key)
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
    cube = src.cubes['MUSE']
    nl = cube.shape
    x = np.arange(nl[0])
    data = cube.data.filled(0).reshape(nl[0], -1)

    res = np.polynomial.polynomial.polyfit(x, data, deg=poly)
    res2 = np.polynomial.polynomial.polyval(x, res, tensor=True).transpose()
    res3 = np.subtract(data, res2)
    res4 = np.reshape(res3, [nl[0], nl[1], nl[2]])

    csub = cube.new_from_obj(cube, data=res4, var=cube.var)

    return csub


def cross_correlate(src, refspec, csfx, ssfx):
    """Create cross-correlation image against reference spectrum

    Parameters
    ----------
    src : mpdaf.sdetect.source.Source
        Input source object
    refspec : Str
        String representing reference spectra for cross correlation
    csfx : Str
        Continuum subtraction suffix string
    ssfx : Str
        Sky subtraction suffix string

    """
    ref = refspec+ssfx+csfx
    cubeName = 'MUSE'+csfx

    scube = src.cubes[cubeName]
    rspec = src.spectra[ref]

    # create cross correlation image
    xc = rspec * scube
    xc = (xc.data.data).sum(axis=0)
    xc /= np.sum(xc)

    # add image to source
    xc_img = src.images['MUSE_WHITE'].clone(data_init=np.zeros)
    xc_img.data.data[:, :] = xc
    src.images['CROSS_CORRELATION'] = xc_img

    # do not mask any data when using cross-correlation
    xcmask = np.array(xc_img.data.data)
    xcmask[:] = 1

    # create sky subtracted cube if true
    if params.SKY_SUB is True:
        tcube = src.cubes['MUSE'] - src.spectra['MUSE_SKY']
    else:
        tcube = src.cubes['MUSE']

    # calculate spectrum
    src.spectra['MUSE_CCWEIGHTED'+ssfx] = \
        sea.compute_optimal_spectrum(tcube, xcmask, xc)

    return src


def clean_output(src, refspec, csfx, ssfx):
    """Clean the output based on user defined parameters

    Parameters
    ----------
    src : mpdaf.sdetect.source.Source
        Input source object
    refspec : Str
        String representing reference spectra for cross correlation
    csfx : Str
        Continuum subtraction suffix string
    ssfx : Str
        Sky subtraction suffix string

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
        rm = [i for i in src.images.keys() if 'SEG_' in i]
        for n in rm:
            del src.images[n]

    # Remove object mask, sky mask.
    if params.OUT_MASK is False:
        print('Removing masks')
        rm = [i for i in src.images.keys() if 'MASK_' in i]
        for n in rm:
            del src.images[n]

    if params.OUT_XCOR is False:
        print('Removing cross-correlation')
        del src.images['CROSS_CORRELATION']

    # Remove additional spectra.
    if params.OUT_SPEC is False:
        print('Removing additional spectra')
        rm = [i for i in src.spectra.keys() if 'MUSE_CCWEIGHTED'+ssfx not in i]
        rm = [i for i in rm if refspec+ssfx+csfx not in i]
        for n in rm:
            del src.spectra[n]

    # Remove subcubes.
    if params.OUT_SUB is False:
        print('Removing subcubes')
        src.cubes.clear()

    return src


# Create progress bar to show for catalog processing.
def print_progress(ID, iteration, total, bar_length=100):
    """
    Call in a loop to create terminal progress bar

    Parameters
    ----------
    ID : int
        id of current interation
    iteration : int
        current iteration
    total : int
        total iterations
    suffix : Str
        suffix string
    decimals : int
        number of decimals in percent complete
    bar_length : int
        character length of bar

    """
    str_format = '{0:.1f}'
    percents = str_format.format(100*(iteration/float(total)))
    filled_length = int(round(bar_length*iteration/float(total)))
    bar = '█'*filled_length+'-'*(bar_length-filled_length)

    sys.stdout.write('Source  :  %s/%s (ID: %s) \nProgress: |%s| %s%s Complete'
                     '\n\n' % (iteration, total, ID, bar, percents, '%'))
    sys.stdout.flush()


def main():

    # Set up global variables.
    global cube, params, imgs, smaps, extra

    # create log file and directory
    if not os.path.exists('logs'):
        os.makedirs('logs')

    log = open(time.strftime('logs/%d%b%Y_%H%M%S.log'), 'w')
    log.write('# Log file: '+time.strftime("%c")+'\n')
    log.write('# '+str(SOFTWARE)+': '+str(VERSION)+'\n\n')

    # Set current working directory.
    cwd = os.getcwd()+'/'

    # First check that the parameter file exists and is named correctly.
    # If it exists import the file.
    print('Getting parameter file...')
    try:
        sys.path.append(str(cwd))
        import param as params
    except Exception:
        log.write('Error: No parameter file found')
        log.close()
        raise ImportError('No parameter file found, please ensure file name'
                          ' is param.py and located in the working directory.')

    # Sometimes if the datacube has some odd headers in, astropy gives off
    # a load of warnings that dominate the output, if this is the case the
    # user can choose to ignore them.
    if params.WARNINGS is True:
        warnings.filterwarnings('default')
    else:
        warnings.filterwarnings('ignore')
        mpdaf.log.setup_logging(level='INFO')

    # Check that the defined catalogue file exists and import it.
    print('Loading catalog...')
    try:
        cat = np.genfromtxt(params.CATALOG, comments='#', dtype=str)
    except Exception:
        log.write('Error: No catalog file found')
        log.close()
        raise ImportError('No catalog file ('+str(params.CATALOG)+') found.')

    # Import any additional images defined in the parameter file.
    # Check if user has added any images.
    imgs = {}
    if params.IMG != '':
        print('Importing images...')
        # add check here
        for i, j in zip(params.IMG, params.IMG_NAME):
            imgs['{0}'.format(j.upper())] = Image(i)

    # Import any additional segmentation maps defined in the parameter file.
    # Check if user has added any images.
    smaps = {}
    if params.SEG_MAP != '':
        print('Importing segmentation maps...')
        # add check here
        for i, j in zip(params.SEG_MAP, params.SEG_NAME):
            smaps['{0}'.format(j.upper())] = Image(i)

    # Check the datacube exists and import it.
    print('Importing datacube...')
    try:
        cube = Cube(params.DATACUBE)
    except Exception:
        log.write('Error: No datacube file found')
        log.close()
        raise ImportError('No datacube file ('+str(params.DATACUBE)+') found.')

    # If all files load successfully, create output directory structure.
    print('Creating output directories...')
    file_path = params.OUTPUT
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    # If image output is set to true, create subdirectories.
    if params.PLOTS is True:
        img_path = file_path+'/images'
        if not os.path.exists(img_path):
            os.makedirs(img_path)
        # create subdirectory structure for output images
        for i in {'images', 'masks', 'spectra', 'xcorrelation'}:
            imgsub_path = img_path+'/'+i
            if not os.path.exists(imgsub_path):
                os.makedirs(imgsub_path)

    # Define additional headers to be stored in fits.
    extra = {'EXT': (SOFTWARE, 'extraction software'),
             'EXT_V': (VERSION, 'version of the extraction software'),
             'AUTH': (AUTHOR, 'author of extraction software')}

    # Need to check if there is one or more object in the input catalog.
    # This code calls the functions to create the source object and output
    # the results. The user can decide (via the param.py file) if they want to
    # perform cross correlation, continuum subtraction and sky subtraction.
    # The user can also decide if they want the images, segmentation maps and
    # cross-correlation maps to be included in the output file.

    # Run code for a single object catalog.
    if cat.size <= 5:
        print('Extracting source '+str(int(cat[0]))+'...\n')
        try:
            ts = time.time()
            if params.MODE.upper() == 'SAME' or cat.size == 3:
                S = create_source(ID=int(cat[0]), ra=float(cat[1]),
                                  dec=float(cat[2]))
            elif params.MODE.upper() == 'CAT':
                S = create_source(ID=int(cat[0]), ra=float(cat[1]),
                                  dec=float(cat[2]), mode=str(cat[3]),
                                  ref=str(cat[4]))
            S.write(file_path+'/'+params.PRE_OUT+'%d.fits' % int(cat[0]))
            rt = time.time()-ts
            log.write(str(int(cat[0])) +
                      ': Extracted Successfully in %.2fs \n' % rt)
            del S
        except Exception as e:
            print('Error: '+str(e))
            log.write(str(int(cat[0]))+': Error, '+str(e)+'\n')
            pass

    # Run code over multi-object catalog.
    else:
        print('Extracting sources...\n')
        # Find catalog length for progress bar.
        length = len(cat)
        for n, m in enumerate(cat):
            try:
                ts = time.time()
                if params.MODE.upper() == 'SAME' or cat[0].size == 3:
                    S = create_source(ID=int(m[0]), ra=float(m[1]),
                                      dec=float(m[2]))
                elif params.MODE.upper() == 'CAT':
                    S = create_source(ID=int(m[0]), ra=float(m[1]),
                                      dec=float(m[2]), mode=str(m[3]),
                                      ref=str(m[4]))
                S.write(file_path+'/'+params.PRE_OUT+'%d.fits' % int(m[0]))
                rt = time.time()-ts
                log.write(str(int(m[0])) +
                          ': Extracted Successfully in %.2fs \n' % rt)
                del S
            except Exception as e:
                print('Error : Source '+str(int(m[0]))+' '+str(e), end='\r')
                log.write(str(int(m[0]))+': Error, '+str(e)+'\n')
                pass
            # Show current progress.
            print_progress(int(m[0]), n+1, length, bar_length=50)

    # close the log file
    log.close()


# Run the code.
if __name__ == '__main__':
    main()
