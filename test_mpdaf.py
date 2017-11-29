#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 29 10:04:01 2017
@author: Alex Griffiths

Test stuff for spectral object detection with mpdaf.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import astropy.units as u
from mpdaf.obj import Cube,WCS,WaveCoord,iter_spe,Spectrum
from mpdaf.sdetect import Source
from astropy.io import fits
from scipy import signal

#cube = Cube('./DATACUBE-HDFS-1.34.fits')
cube = Cube('./CLIO.fits')
#cube = cube[:-1,:,:]

#%%
# ra = x = p
# dec = y = q

# select source from catalogue. 
#s = Source.from_data(ID=92,ra=338.2284,dec=-60.57059,origin=('test','v0.0','DATACUBE-HDFS.fits','v1.34'))
s = Source.from_data(ID=208,ra=130.5786783,dec=1.6421026,origin=('test','v0.0','DATACUBE-HDFS.fits','v1.34'))

# get x and y image locations from cube.
s.y,s.x = cube.wcs.sky2pix((s.dec,s.ra),nearest='True')[0]

# set padding either side of object.
p = 20

# select object spectra as reference.
ref = cube[:,s.y,s.x]
ref_cont = ref.poly_spec(5).data.data
ref_contsub = ref.data.data - ref_cont 

# extract subcube and whitelight image.
sub = cube[:,s.y-p:s.y+p,s.x-p:s.x+p]
img = sub.sum(axis=0)

# get size of subcube.
z,y,x = sub.shape

# create empty array.
xcor = np.zeros([x*y])

i = 0

# loop over each spectrum in subcube.
for sp in iter_spe(sub):

    spe = sp
    cont = spe.poly_spec(5).data.data
    spe = spe.data.data
    
    xcor[i] = signal.correlate(ref_contsub,spe-cont,mode='valid')           # perform cross-correlation.
    i = i + 1                                                           # move to next spectrum.
    
# normalise cross-correlation
#xcor[xcor < 0] = 0
xcor = (xcor-min(xcor))/(max(xcor)-min(xcor))  

# reshape 1D back to shape of subcube.
xcor = np.reshape(xcor,(x,y))

# plot whitelight image.
plt.figure()
img.plot(scale='arcsinh',cmap=cm.gray)

# overplot contours of cross-correlation.
lines = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]
plt.contour(xcor,lines,cmap=cm.PuBuGn,linewidths=1)

# create new figure for 3D.
fig = plt.figure()

# create x,y mesh.
X,Y = np.meshgrid(range(2*p),range(2*p))

# plot 3D surface of cross-correlation.
ax = Axes3D(fig)
ax.plot_surface(X,Y,xcor,cmap=cm.viridis)

# plot cut off limit (3sigma above the mean)
co = np.mean(xcor) + 2*np.std(xcor)
ax.plot_surface(X,Y,co,cmap=cm.gray,alpha=0.5)

mask = np.array(xcor)
mask[mask < 0.25] = 0
weight = np.array(mask)
mask[mask != 0] = 1

masked = sub*mask
m_img = masked.sum(axis=0)

plt.figure()
m_img.plot(scale='arcsinh',cmap=cm.gray)#plt.imshow(masked)

plt.figure()
spe = masked.mean(axis=(1,2),weights=weight)
spe.plot(linewidth=0.5)

from astropy.convolution import convolve, Box1DKernel
spectra = spe.data.data
specsmooth = convolve(spectra, Box1DKernel(3.2))

wl = 4750 + np.multiply(1.25,range(0,np.size(spectra)))

plt.figure()
plt.plot(wl,specsmooth,linewidth=0.5)
plt.xlim([min(wl),max(wl)]);

