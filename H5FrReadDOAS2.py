import sys, os, glob
import h5py, datetime
import numpy as np
import ephem
#import pysolar as sun
#import statistics


def h5_rw(infilename,outfilename,wlfile, CIname):
    obsr = ephem.Observer()
    #obsr.lon =  144.6950
    #obsr.lat = -40.683
    obsr.lon = '144:41:22'
    obsr.lat = '-40:41:00'
    obsr.elevation = 80    # in m
     
    tzone = 10.0               # time zone of the measurements
    azView = 210.
    wl1 = 330.
    wl2 = 390.
    CIlsig = 100.

    
    # Load the wl data
    wl=[]
    wl = getwl_data(infilename,wlfile)
    if len(wl) < 5 :  #Failed to get wl data - cannot proceed!
        return
        
    wl11=wl1 - 0.5
    wl12 = wl1 + 0.5
    wl21 = wl2 - 0.5
    wl22 = wl2 + 0.5
    for i in range(len(wl)):
        if float(wl[i]) < wl11 :
            CL11 = i+1

        if float(wl[i]) < wl21 :
            CL21 = i+1

        if float(wl[i]) < wl12 :
            CL12 = i
        if float(wl[i]) < wl22 :
            CL22 = i

    f = h5py.File(infilename,"r")
    of = open(outfilename,"w")               # where we will write to
    CIf = open(CIname,"w")
    CIf.write('date,dec_time,obs_a,sun_za,CI,' )  # Header line
    CIf.write('%.2f, ' % wl1)
    CIf.write('%.2f \n ' % wl2)
    

    # for item in f.attrs.keys():       # stub for top level attributes
    #    if item
    basename = os.path.basename(infilename)
    #dstamp = basename[6:8] + '/' + basename[4:6] + '/' + basename[0:4]
    dyr = int(basename[0:4])
    dmon = int(basename[4:6])
    dday = int(basename[6:8])
    dark= [];  spec =[]; spec2 = []
    # CL1 = [2]; CL2 = [2];
    # up = False
    
    for name in f:
        try:
            dhr= int(name[0:2])
            dmin = int(name[2:4])
            dsec = int(name[4:6])
            t = float(name[0:2])+float(name[2:4])/60+float(name[4:6])/3600  # time stamp
        except:
            print(("wavelength? " + name))
            #if name == 'Wavlength scale' :
                #wl11=wl1 - 0.5
                #wl12 = wl1 + 0.5
                #wl21 = wl2 - 0.5
                #wl22 = wl2 + 0.5
                #
                #
                #gh = f[name] 
                #wl = np.zeros(len(gh))
                #gh.read_direct(wl)

#                for i in range(len(wl)):
#                    if float(wl[i]) < wl11 :
#                        CL11 = i+1
#
#                    if float(wl[i]) < wl21 :
#                        CL21 = i+1
#
#                    if float(wl[i]) < wl12 :
#                        CL12 = i
#                    if float(wl[i]) < wl22 :
#                        CL22 = i
#                                                  
                        
            return
            
        gh = f[name]
        elev = gh.attrs.get('Elevation_angle')
        if gh.__contains__('Dark spectrum') :
            dark = np.array(gh.__getitem__('Dark spectrum'))
        spec= np.array(gh.__getitem__('Spectrum'))
        #if elev == 90 :
        #    ref = spec - dark
        #    up = True
        #else :    
        try:
            #if up :
                d = datetime.datetime(dyr,dmon,dday,dhr,dmin,dsec) 
                d = d - datetime.timedelta(hours=int(tzone))
                d = d - datetime.timedelta(minutes = int((tzone-int(tzone))*60))
                obsr.date = d
                sun = ephem.Sun()
                sun.compute(obsr)
                Selev = sun.alt*57.2957795      #Altitude above horizon including refraction
                of.write('{0:.3f} ' .format(90 - Selev))
                of.write('{0:.3f} ' .format(azView)) 
                spec2= (spec - dark)
#                   spec2= (spec - dark)/ref
                of.write('%g '% elev)             
                of.write(d.strftime( '%d/%m/%Y '  ))
                t = float(d.hour)+float(d.minute)/60.+float(d.second)/3600
                of.write(' %g ' % t)
                for i in range(len(spec2)):
                    of.write('%.4f ' % spec2[i])
                of.write('\n')
            
                b1 = np.median(spec2[int(CL11):int(CL12)])
                b2 = np.median(spec2[CL21:CL22])
                if b2 > CIlsig and b1 > CIlsig :
                    CI = b1/b2
                    CIf.write( d.strftime( '%d/%m/%Y %H:%M:%S,'  ))
                    CIf.write(' %g,' % t)
                    CIf.write('%g,'% elev)             
                    CIf.write('{0:.3f},' .format( 90 - Selev))
                    CIf.write('%.4f, ' % CI)
                    CIf.write('%.2f, ' % b1)
                    CIf.write('%.2f' % b2)
                    CIf.write('\n')
                else :
                    CI = 10000
            #else :
            #    spec2 = (spec - dark)
        except:
                print("No dark? for ", name, d , azView)
      #  try:
      #      spec = spec - dark
        #except:
        #    print "No dark? for ", name
            
        
    f.close()
    of.close()
    CIf.close()
    return

def getwl_data(fname,wlfile):   # Retrieve the wavelength scale data from fname and save to wlfile
    f = h5py.File(fname,"r")
    wlf = open(wlfile,"w")
    wl =[]
    for name in f:
        if name == 'Wavlength scale' :
            gh = f[name] 
            wl = np.zeros(len(gh))
            gh.read_direct(wl)
            for i in range(len(wl)):
                wlf.write('%.5f \n' % wl[i])

    f.close()        
    wlf.close()
    return wl    
    
try:
    inDir = sys.argv[1]; inpat = sys.argv[2]; outDir = sys.argv[3]
    #inDir = "c:\\DOAS 1.5\\DATA"
    #inpat = '20170308_MD_silver.h5'
    #outDir = 'c:\\data\\Max_anal\\CG\\inp'
except:
    print("Usage:", sys.argv[0], "indir file_sel outdir"); sys.exit(1)

# Global reading 
os.chdir(inDir)                   #Move to input directory
files = glob.glob(inpat)
for name in files:
    infilename=  name
    outfile= os.path.join(outDir,os.path.splitext(name)[0] + ".txt")
    wlname = os.path.join(outDir, "wl.txt")
    CIname = os.path.join(outDir, os.path.splitext(name)[0] + "CI.csv")
    print("Source Dir: " + inDir)
    print("Output Dir: " + outDir)
    
    print(infilename , outfile)
    h5_rw(infilename,outfile, wlname, CIname)
    
    
    