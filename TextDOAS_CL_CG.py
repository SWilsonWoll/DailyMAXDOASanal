import sys, os, glob
from subprocess import call
import ephem
import datetime as dt
import time
import numpy as np

# Global reading
sun = ephem.Sun()
us = ephem.Observer()           # Assuming that this information (sun azimuth/ elevation) is not present in the file
us.lon = '144:41:22'
us.lat = '-40:41:00'
tzone = 10.


def txt_rw(infilename,outfilename):
    # These need to be localized
    RefWl = "c:/Data/Max_anal/CG/xs/wl.txt"        #Needs to be set - contains wavelength scale
    prjfile = "c:/Data/Max_anal/CG/O4_UVD.xml"            #Needs to be set - analysis specific
    projname = "UV_Oview"               # Analysis specific
    
    f = open(infilename,"r")
    of = open(outfilename,"w")               # where we will write to
    RefL = open(RefWl, "r")
    testinf = 'c:/data/Max_anal/CG/out/ttemp/Spec.txt'        # file that contains the data to be analysed
    # refname = 'c:/data/MAX/out/ttemp/tempRef.txt'        # name of the file that should be used as a reference
    
    spec =[];  indata = []; oldRef =[]; ref = []
    Ofile = ''
    old = False
    
    dirTemp = os.path.join(os.path.dirname(outfilename),'ttemp')
    if not os.path.isdir(dirTemp) :
        os.mkdir(dirTemp) #Temp directory  (may need to set permission (dirTemp, '0755')
                
    Rfil = os.path.join(dirTemp,"tempRef.txt")   # the reference spectrum
    
    if os.path.isfile(Rfil) :  os.remove(Rfil)       #Delete old reference
        
    #Otf = open('c:/data/MAX/data/test.f',"r") #establishing the object - not sure this is necessary
    #Otf.close
    
    # Rlines = RefL.readlines()  
    Rlines = [float(x.rstrip('\n')) for x in RefL.readlines()]   # Read in the wavelength scale

    # read in the data from f
    j = 0
    lines = f.readlines()
    for line in lines:
        
        indata =  line.split()
        try :
            spec = [float(val) for val in indata[5:]]
        except:
            print("read error for ", val)
            
        selev = float(indata[0])
        azview = float(indata[1])
        elev = float(indata[2])
        sdate = indata[3]
        sdtime = indata[4]
        spec = np.array(spec)
        print("Elevation " , elev)
        
        if abs(elev - 90) < 1 :  # We have found a reference spectrum
            j += 1
            print("Ref no", j)
            if os.path.isfile(Rfil) :
                oldRef = ref
                old = True
            else:
                old = False    
                
            ref = spec                         
            Rf = open(Rfil,"w")
            tlim = min(len(Rlines), len(spec))
            ref = spec
            for i in range( tlim) :
                Rf.write('%11.5e %11.5e \n' % (Rlines[i], spec[i]))
            
            Rf.close()   # Reference file written
            #  Now analyze what we have.
            try :
                os.chdir("c:\QDOAS-2111")
                oTemp = outfilename.replace("\\","/")
                cmd = '"c:\QDOAS-2111\doas_cl" -c "' + prjfile + '" -a ' + '"' + projname + '"' + ' -o "' + oTemp + '" -f "' + testinf \
                    + '" -xml ' +'"'+ '/O4_UV/files/refone= ' + Rfil + '"'
                returncode = call(cmd, shell=True)
                
                #failure = os.system(cmd)
                if returncode :
                    print("Error from running doas_cl : ", returncode, "\n command ", cmd)
                    
                    
            except OSError as message:
                print("Execution failed!\n", message)
                        
            if os.path.isfile(Ofile): os.remove(Ofile)
        
        else :
           
            #Calculate the solar zenith angle - we will need it
            #us.date = (indata[1] + ' ' + indata[2])   #Date/ time of this spectrum in UT
            #sun.compute(us)
            
            Ofile = os.path.join(dirTemp,"Spec.txt")
            Otf = open(Ofile, "a")
            #  Following line could include the solar azimuth at some stage? of observation for the measurement. May need to revisit this.
            Otf.write('%g %g %g '% ( selev, azview, elev ))   #includes both solar azimuth and elevation - after a fashion.
            Otf.write('%s %s ' % (sdate, sdtime) )
    
            for i in range(len(spec)):
                Otf.write('%11.5e ' % spec[i])
                
            Otf.write('\n')
            Otf.close()
        
    f.close()
    of.close()
    return
    
def outclean(fil):
# Takes the output from above and adds a local date time field to the first column
# and edits the header line
    global tzone    #This needs be passed in better 
    
    ofil = os.path.splitext(fil)[0] + ".anl"
    fi = open(fil, "r")
    fo = open(ofil, "w")
    
    lines = fi.readlines()
    for lin in lines:
        ele = lin.split("\t")
        if lin[0] == "#":    #Header
            mele = [w.replace('O4_UV.','') for w in ele]
            mele = [w.replace('#','') for w in mele]
        
            fo.write('date,')
            for i in range(len(mele)-1):
                fo.write('%s,' % mele[i])
            fo.write('\n')
        else :
            mt = dt.datetime.strptime(ele[1], '%H:%M:%S').time()
            d = dt.datetime.combine(dt.datetime.strptime(ele[0], '%d/%m/%Y')
              , mt )
            d = d + dt.timedelta(hours=int(tzone))
            d = d + dt.timedelta(minutes = int((tzone-int(tzone))*60))
            fo.write( d.strftime( '%d/%m/%Y %H:%M:%S,'  ))
            for i in range(len(ele)-1):
                fo.write('%s,' % ele[i])
            fo.write('\n')
    fi.close()
    fo.close()
    
                
try:
    inDir = sys.argv[1]; inpat = sys.argv[2]; outDir = sys.argv[3]
    #inDir = "c:\\data\\Max_anal\\CG\\inp"
    #inpat = '20170308_MD_silver.txt'
    #outDir = 'c:\\data\\Max_anal\\CG\\out'

except:
    print("Usage:", sys.argv[0], "indir file_sel outdir"); sys.exit(1)
# Note the definitions for input parameters above


os.chdir(inDir)                   #Move to input directory
files = glob.glob(inpat)
for name in files:
    infilename=  name
    outfile= os.path.join(outDir,os.path.splitext(name)[0] + ".tmp")
    print("Source Dir: " + inDir)
    print("Output Dir: " + outDir)
   
    print(infilename , outfile)
    txt_rw(infilename,outfile)
    
    outclean(outfile)
    
