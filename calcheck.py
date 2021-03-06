from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
###### Some values: V4046   range = [9, 120]
######                      PA = 76, incl = 33
######              MWC480  range = [8, 160]
######                      PA = -34, incl = 36

def calcheck(sbfile,lbfile,rangemin,rangemax,pos_angle,incl,binsize,samples):
    plt.clf()
    filenames = [sbfile,lbfile]
    newuvdistances = []
    newamplitudes = []
    errors = []

    for name in filenames:
###### Extract useful variables from the FITS file.
        image = fits.open(name)
        u = image[0].data['UU']
        v = image[0].data['VV']
        u *= image[0].header['crval4']/1e3
        v *= image[0].header['crval4']/1e3

        vis = image[0].data['data']
        real = (vis[:,0,0,0,:,0,0] + vis[:,0,0,0,:,1,0])/2.
        real = np.mean(real,axis=1)
        imag = (vis[:,0,0,0,:,0,1] + vis[:,0,0,0,:,1,1])/2.
        imag = np.mean(imag,axis=1)

        amp = np.sqrt(real**2 + imag**2)
        amp = amp.squeeze()
        uvdist = np.sqrt(u**2 + v**2)

###### Calculate deprojected uv-distances.
        phi = np.radians(np.degrees(np.arctan2(v,u)) - pos_angle)
        da = uvdist*np.sin(phi)
        db = uvdist*np.cos(phi)*np.cos(np.radians(incl))
        deprojuvdist = np.sqrt(da**2 + db**2)

###### Bin for the calibration check with a set range of 10-900 klambda.
        newuvdist = []
        newreal = []
        newimag = []
        newamp = []
        rstdevs = []
        istdevs = []
        rNs = []
        iNs = []
        amperrs = []
        calmin = 10
        calmax = 900

        for minimum in range(calmin,calmax,binsize):
            maximum = minimum + binsize
            uvsubarray = (deprojuvdist > minimum) & (deprojuvdist < maximum)
            addition = (maximum-minimum)/2.
            median = minimum + addition
            newuvdist.append(median)

            realsubarray = (real[uvsubarray] != 0)
            real2 = real[uvsubarray][realsubarray]
            realav = np.nanmean(real2)
            newreal.append(realav)

            imagsubarray = (imag[uvsubarray] != 0)
            imag2 = imag[uvsubarray][imagsubarray]
            imagav = np.nanmean(imag2)
            newimag.append(imagav)

            rstdev = np.nanstd(real2)
            istdev = np.nanstd(imag2)
            rlist = list(real2[~np.isnan(real2)])
            ilist = list(imag2[~np.isnan(imag2)])
            rN = len(rlist)
            iN = len(ilist)
            denom = realav**2+imagav**2
            amperr = np.sqrt((rstdev**2/rN)*(realav**2/denom)+(istdev**2/iN)*(imagav**2/denom))
            amperrs.append(amperr)

        newuvdist = np.asarray(newuvdist)
        newuvdist = newuvdist[~np.isnan(newuvdist)]
###### This next line removes uv-distances I generated that aren't useful.
        newuvdist = [i for i in newuvdist if i <= max(deprojuvdist)]
        rilength = len(newuvdist)
        newuvdist = np.asarray(newuvdist)
###### These lines impose a uniform structure so plotting works later.
        r = newreal[:rilength]
        r = np.asarray(r)
        i = newimag[:rilength]
        i = np.asarray(i)
        remove = (np.isnan(r)) & (np.isnan(i))
        newuvdist = newuvdist[~remove]
        newamp = np.sqrt(r**2 + i**2)
        newamp = newamp[~remove]
        amperrs = amperrs[:rilength]
        amperrs = np.asarray(amperrs)
        amperrs = amperrs[~remove]

        f1 = plt.figure(1)
        plt.errorbar(newuvdist,newamp,yerr=amperrs,fmt='.')
        plt.xlabel('Deprojected uv-distance (klambda)')
        plt.ylabel('Amplitude (Jy)')
        plt.title('Amplitude versus deprojected uv-distance')
        plt.grid(True)

###### Bin for the amplitude ratio separately so we can specify a range of uv-distances.
        newuvdist = []
        newreal = []
        newimag = []
        newamp = []
        rstdevs = []
        istdevs = []
        rNs = []
        iNs = []
        amperrs = []

        for minimum in range(rangemin,rangemax,binsize):
            maximum = minimum + binsize
            uvsubarray = (deprojuvdist > minimum) & (deprojuvdist < maximum)
            addition = (maximum-minimum)/2.
            median = minimum + addition
            newuvdist.append(median)

            realsubarray = (real[uvsubarray] != 0)
            real2 = real[uvsubarray][realsubarray]
            realav = np.nanmean(real2)
            newreal.append(realav)

            imagsubarray = (imag[uvsubarray] != 0)
            imag2 = imag[uvsubarray][imagsubarray]
            imagav = np.nanmean(imag2)
            newimag.append(imagav)

            rstdev = np.nanstd(real2)
            istdev = np.nanstd(imag2)
            rlist = list(real2[~np.isnan(real2)])
            ilist = list(imag2[~np.isnan(imag2)])
            rN = len(rlist)
            iN = len(ilist)
            denom = realav**2+imagav**2
            amperr = np.sqrt((rstdev**2/rN)*(realav**2/denom)+(istdev**2/iN)*(imagav**2/denom))
            amperrs.append(amperr)

        newuvdist = np.asarray(newuvdist)
        newuvdist = newuvdist[~np.isnan(newuvdist)]
        newuvdist = [i for i in newuvdist if i <= max(deprojuvdist)]
        rilength = len(newuvdist)
        newuvdist = np.asarray(newuvdist)
        r = newreal[:rilength]
        r = np.asarray(r)
        i = newimag[:rilength]
        i = np.asarray(i)
        newuvdistances.append(newuvdist)
        newamp = np.sqrt(r**2 + i**2)
        newamplitudes.append(newamp)
        amperrs = np.asarray(amperrs)
        errors.append(amperrs)

###### Calculate the ratio between the amplitude arrays.
    remove = (np.isnan(r)) & (np.isnan(i))
    newuvdist = newuvdistances[1][~remove]
    newampsb = newamplitudes[0][~remove]
    newamplb = newamplitudes[1][~remove]
    amperrssb = errors[0][~remove]
    amperrslb = errors[1][~remove]
    ampquot = newampsb/newamplb
    ampquoterr = ampquot*np.sqrt((amperrssb**2/newampsb**2)+(amperrslb**2/newamplb**2))

    f2 = plt.figure(2)
    plt.errorbar(newuvdist,ampquot,yerr=ampquoterr,fmt='.',color='b')
    plt.xlabel('Deprojected uv-distance (klambda)')
    plt.axhline(1,color='g')
    plt.ylabel('Short-baseline amplitude divided by long-baseline amplitude')
    plt.title('Ratio of short/long baseline amplitudes versus deprojected uv-distance')
    plt.grid(True)

    x = newuvdist
    y = ampquot
    sigma = ampquoterr
    ymodel = 1

    def chisqr(y,ymodel,sigma):
        chisqr = np.sum((y - ymodel)**2/sigma**2)
        return chisqr

    def redchisqr(y,ymodel,sigma):
        chisqr = np.sum((y - ymodel)**2/sigma**2)
        nu = len(sigma)
###### nu should be the number of data points over the number of parameters.
        return chisqr/nu

    print "chi squared =",chisqr(y,ymodel,sigma)
    print "reduced chi squared =",redchisqr(y,ymodel,sigma)

###### Perform a grid search to find a representative ratio.
    brange = np.linspace(0.8,1.4,num=samples)
    values = []
    for b in brange:
        ymodel = b
        k = chisqr(y,ymodel,sigma)
        values.append(k)

    minimumchisqr = min(values)
    i = values.index(minimumchisqr)
    length = float(len(brange))

    n = np.ceil((i+1)/length)
    brange = np.tile(brange,n)
    bvalue = brange[i]

    print "ratio =",bvalue
    plt.axhline(bvalue,color='r')
    plt.show
