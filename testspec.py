# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 14:59:01 2016
@author: Alex Griffiths

Test stuff for spectral object detection.
"""
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.convolution import convolve
from astropy.convolution import Gaussian1DKernel
import numpy as np
from numpy.fft import fft, ifft, fft2, ifft2, fftshift
from scipy.stats.stats import pearsonr
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import time

def normalize(x):
    return (x-min(x))/(max(x)-min(x))
    
datacube = fits.open('/media/Elements/Clio/ESOData/MUSE/Cleaned/Fixed/DATACUBE.fits')
datacube = datacube[0].data

specAll = fits.open('/media/Elements/Clio/ESOData/MUSE/SpecExt/Results/customMarz/spectraFULL.fits')
specAll = specAll[0].data

#%%

sub = datacube[1000,304:344,347:355]
line = datacube[:,304:344,347]
gauss = Gaussian1DKernel(stddev=3)

plt.imshow(sub)

ref = convolve(datacube[:,324,347],gauss,boundary='extend')

xcor = np.zeros(40)

for i in range(0,39):
    xcor[i] = np.correlate(ref,convolve(line[:,i],gauss,boundary='extend'))
    
xcor = 7*normalize(xcor)

plt.plot(xcor,np.linspace(0,39,40),'w',linewidth=1.5)

#%%
x = 110
y = 223

gauss = Gaussian1DKernel(stddev=3)

#ref = datacube[:,x,y]

ref = np.zeros(3682)
ref[0:3681] = specAll[270,:]

xs = np.size(datacube,2)
ys = np.size(datacube,1)

xcor = np.zeros([ys,xs])

for i in range(xs):
    for j in range(ys):
        xcor[j,i] = np.correlate(ref,datacube[:,j,i],mode='valid')
        #xcor[j,i] = pearsonr(ref,datacube[:,j,i])[0]
        
lines = [0,1000,2000,3000,4000,5000,6000,7000]

plt.figure()
plt.imshow(xcor)
plt.contour(xcor,lines,cmap=cm.bone,linewidths=0.5)
plt.plot(x,y,'wx')

        
 #%%
x = 112
y = 222

ref = datacube[:,x,y]
xs = np.size(datacube,2)
ys = np.size(datacube,1)

xcor = np.zeros((ys,xs))

t0 = time.time()
xcor = np.tensordot(datacube,ref,axes=([0],[0]))
t1 = time.time()

print(t1-t0)

fig = plt.figure()
ax = Axes3D(fig)

X,Y = np.meshgrid(range(xs),range(ys))
Z = xcor
surf = ax.plot_surface(X,Y,Z,cmap=cm.bone)

        
#%%

gal1 = datacube[:,112,222]
gal2 = datacube[:,111,223]
other = datacube[:,97,215]

gauss = Gaussian1DKernel(stddev=1)

gal1 = convolve(datacube[:,112,222],gauss,boundary='extend')
gal12 = convolve(datacube[:,111,223],gauss,boundary='extend')
other = convolve(datacube[:,97,215],gauss,boundary='extend')

# normalise
gal1 = normalize(gal1)
gal2 = normalize(gal2)
bg1 = normalize(bg1)

plt.figure()

plt.subplot(2,1,1)
plt.plot(gal1)
plt.plot(gal2)
plt.plot(bg1)
plt.title('Normalized Spectra')
plt.ylim([0,1])
plt.legend(['Galaxy Spectrum 1','Galaxy Spectrum 2','Background Spectrum'])

plt.subplot(2,3,4)
plt.plot(gal1-gal2)
plt.xlabel('Galaxy Spectrum: 1 - 2')
plt.ylim([-1,1])

plt.subplot(2,3,5)
plt.plot(gal1+gal2)
plt.xlabel('Galaxy Spectrum: 1 + 2')
plt.ylim([0,2])

plt.subplot(2,3,6)
plt.plot(gal1-bg1)
plt.xlabel('Galaxy Spectrum 1 - Background')
plt.ylim([-1,1])
