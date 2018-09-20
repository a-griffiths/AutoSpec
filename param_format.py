# Default configuration file for AutoSpec v 1.1.2
# DATE: 20-09-2018

# ----------- Operating Mode -------------------------------------------------------------------------------------------------------------------------------------------------------------
 
MODE           = 'param'                       # 'param' or 'cat' to use configuration or catalogue file respectively for extraction mode (string). 

# ----------- Reference Spectra -----------------------------------------------------------------------------------------------------------------------------------------------------------

REF            = ''                            # reference spectrum to use for cross correlation, must also be in image (IMG), aperture (APER) parameters or '' to use white light image.

# ----------- Required Files --------------------------------------------------------------------------------------------------------------------------------------------------------------

DATACUBE       = ''                            # name of datacube file (string).
CATALOG        = ''                            # name of catalog file (string).

# ----------- Datacube Extension: Use if datacube extensions are not specified in fits headers --------------------------------------------------------------------------------------------

DATA_EXT       = ()                            # The number/name of the data (int or str), or data and variance extensions (int, int or str, str), () if none.

# ----------- Spectral Extractions --------------------------------------------------------------------------------------------------------------------------------------------------------

APER           = ''                            # aperture sizes (in arcseconds) for spectrum extraction (float or array or floats).
IMG            = ''                            # name of additional image files for weighted spectra and segmentation extractions (string or comma seperated list of strings), '' if none.

# ----------- Object Masks ----------------------------------------------------------------------------------------------------------------------------------------------------------------

USE_IMGS       =  True                         # if AutoSpec should also use the segmentation maps created from the images in IMG parameter to create final masks (True or False).
OBJ_MASK       = 'INTER'                       # object mask from union (UNION) or intersection (INTER) of segmentation maps (string).
SEG            = ''                            # name of additional segmentation maps files to be used (string or comma seperated list of strings).

# ----------- Output Formatting -----------------------------------------------------------------------------------------------------------------------------------------------------------

OUTPUT         = 'output'                      # name of output directory (string).
PRE_OUT        = 'Source_'                     # string to prepend to output data files (string), '' if none.

# ----------- Extraction Parameters -------------------------------------------------------------------------------------------------------------------------------------------------------

SIZE           = 5                             # sub image/cube extraction size in arcseconds (float).
XCOR           = True                          # perform cross correlation (True or False).
CONT_SUB       = True                          # preform continuum subtraction, only runs if XCOR is True (True or False).
CONT_POLY      = 5                             # degree of polynomial for contiuum fitting (integer).
SKY_SUB        = True                          # Perform sky subtraction when extracting spectra (True or False).
PLOTS          = True                          # output plots (True or False). 

# ----------- Outputs ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

OUT_SUB        = False                         # output extracted source subcubes (True or False), these make up the bulk of the output filesize.
OUT_IMG        = True                          # output extracted source images (True or False).
OUT_SEG        = True                          # output segmentation maps (True or False).
OUT_MASK       = True                          # output object and sky masks (True or False).
OUT_XCOR       = True                          # output cross-correlation map (True or False).
OUT_SPEC       = True                          # output additional spectra (True) or final only (False).

# ----------- MISCELLANEOUS ---------------------------------------------------------------------------------------------------------------------------------------------------------------

CMAP           = 'viridis'                     # colour map to use for image plots.
ORIG_FROM      = ''                            # name of the detector software which creates this object (string).
ORIG_FROMV     = ''                            # version of the detector software which creates this object (string).
ORIG_CUBE      = ''                            # name of the FITS data cube from which this object has been extracted (string).
ORIGN_CUBEV    = ''                            # version of the FITS data cube (string).
WARNINGS       = False                         # turn warnings on (True) or off (False).
