# Default configuration file for AutoSpec v 1.0.0
# DATE: 20-03-2018

# ----------- Operating Mode ------------------------------------------------------------------------------------------------------------------

MODE           = 'cat'                        # 'same' or 'cat' to use configuration or catalogue file respectively for object extraction mode. 

# ----------- Reference Spectra ---------------------------------------------------------------------------------------------------------------

REF            = '1.0'                        # reference spectrum to use for cross correlation, weight image names or aperture size (string).

# ----------- Required Files ------------------------------------------------------------------------------------------------------------------

DATACUBE       = 'datacube.fits'               # name of datacube file (string).
CATALOG        = 'catalog.txt'                 # name of catalog file (string).

# ----------- Aperture Mode -------------------------------------------------------------------------------------------------------------------

APER           = [1.0, 1.5, 2.0, 2.5]          # aperture sizes (in arcseconds) for spectrum extraction (float or array or floats).

# ----------- Images ---------------------------------------------------------------------------------------------------------------------------

IMG            = ['g-band.fits','r-band.fits'] # name of additional image files (comma seperated list of strings), '' if none.
IMG_NAME       = ['G-Band','R-Band']           # additional image names for output, no spaces (comma seperated list of strings), '' if none.
WEIGHT_IMG     = 'G-Band'                      # image to weight spectrum by (must exist in IMG_NAME), defaults to MUSE_WHITE if not specified.

# ----------- Segmentation Maps ---------------------------------------------------------------------------------------------------------------

USE_WHITE      =  True                         # if AutoSpec should also use the MUSE_WHITE segmentation map to create masks (True or False).
OBJ_MASK       = 'INTER'                       # object mask from union (UNION) or intersection (INTER) of segmentation maps.
SEG_MAP        = ['g-seg.fits','r-seg.fits']   # name of segmentation maps files (comma seperated list of strings).
SEG_NAME       = ['G','R']                     # segmentation map names for output, no spaces (comma seperated list of strings).

# ----------- Output Formatting ---------------------------------------------------------------------------------------------------------------

OUTPUT         = 'output'                      # name of output directory (string).
PRE_OUT        = 'Source_'                     # string to prepend to output data files (string), '' if none.

# ----------- Extraction Parameters -----------------------------------------------------------------------------------------------------------

SIZE           = 5                             # sub image/cube extraction size in arcseconds (float).
XCOR           = True                          # perform cross correlation (True or False).
CONT_SUB       = True                          # preform continuum subtraction, only runs if XCOR is True (True or False).
CONT_POLY      = 5                             # degree of polynomial for contiuum fitting (integer).
SKY_SUB        = True                          # Perform sky subtraction when extracting spectra (True or False).
PLOTS          = True                          # output plots (True or False). 

# ----------- Outputs -------------------------------------------------------------------------------------------------------------------------

OUT_SUB        = False                         # output extracted source subcubes (True or False).
OUT_IMG        = True                          # output extracted source images (True or False).
OUT_SEG        = True                          # output segmentation maps (True or False).
OUT_MASK       = True                          # output object and sky masks (True or False).
OUT_XCOR       = True                          # output cross-correlation map (True or False).
OUT_SPEC       = True                          # output additional spectra (True) or final only (False).

# ----------- MISCELLANEOUS -------------------------------------------------------------------------------------------------------------------

CMAP           = 'cubehelix'                   # colour map to use for image plots
ORIG_FROM      = ''                            # name of the detector software which creates this object (string).
ORIG_FROMV     = ''                            # version of the detector software which creates this object (string).
ORIG_CUBE      = ''                            # name of the FITS data cube from which this object has been extracted (string).
ORIGN_CUBEV    = ''                            # version of the FITS data cube (string).
WARNINGS       = False                         # turn warnings on (True) or off (False).
