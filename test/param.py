# Default configuration file for Spectrum Extractor 1.0.0
# DATE: 20-03-2018

# ------------------------- Data Files --------------------------------------------------------------------------------------

DATACUBE       = 'datacube.fits'               # name of datacube file (string).
IMG            = ['g-band.fits','r-band.fits'] # name of additional image files (comma seperated list of strings).
IMG_NAME       = ['G-Band','R-Band']           # additional image names for output, no spaces (comma seperated list of strings).
WEIGHT_IMG     = 'G-Band'                      # image to weight spectrum by, must be one of 'IMG_NAME' or 'MUSE_WHITE'.
OUTPUT         = 'output'                      # name of output directory (string).
PRE_OUT        = 'Source_'                     # string to prepend to output data files (string).

# ------------------------- Additional Files --------------------------------------------------------------------------------

CATALOG        = 'catalog.txt'                 # name of catalog file (string).

# ------------------------- Parameters --------------------------------------------------------------------------------------

SIZE           = 5                             # image extraction size in arcseconds (float).
XCOR           = True                          # perform cross correlation (True or False).
CONT_SUB       = True                          # preform continuum subtraction, only runs if XCOR is True (True or False).
CONT_POLY      = 5                             # degree of polynomial for contiuum fitting (integer).
SKY_SUB        = True                          # Perform sky subtraction when extracting spectra (True or False).
PLOTS          = True                          # output plots (True or False).
OBJ_MASK       = 'INTER'                       # object mask from union (UNION) or intersection (INTER) of segmentation maps. 

# ------------------------- Outputs -----------------------------------------------------------------------------------------

OUT_SUB        = False                         # Output extracted source subcubes (True or False).
OUT_IMG        = True                          # Output extracted source images (True or False).
OUT_SEG        = True                          # Output segmentation maps (True or False).
OUT_MASK       = True                          # Output object and sky mask and cross-correlation map if set (True or False).
OUT_SPEC       = True                          # Output additional spectra (True) or final only (False).

# ------------------------- MISCELLANEOUS -----------------------------------------------------------------------------------

ORIG_FROM      = ''                            # Name of the detector software which creates this object (string).
ORIG_FROMV     = ''                            # Version of the detector software which creates this object (string).
ORIG_CUBE      = ''                            # Name of the FITS data cube from which this object has been extracted (string).
ORIGN_CUBEV    = ''                            # Version of the FITS data cube (string).
WARNINGS       = False                         # Turn warnings on (True) or off (False).
