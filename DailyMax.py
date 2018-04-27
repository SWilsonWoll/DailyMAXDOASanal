# Designed to Run daily and produces analysed results as a first pass.
# Calls H5FrReadDOAS2 to produce text files, and then
# TextDOAS_CL_CG.py to run QDOAS for analysis, and tidy up output

import datetime as dt
import os
from subprocess import call
import shutil

#Globals
inputdir = "c:\\DOAS 1.5\\Data"
analDir = "c:\\data\\Max_anal\\CG"
storeD = "c:\\export"
namest = "_MD_silver"
pythcde ="c:\\exe\\pyth"

os.chdir("c:\exe\pyth")
yd = dt.date.today() - dt.timedelta(1)   #yesterday

namef = yd.strftime('%Y%m%d')
nameff = namef + namest +".h5"
outd = analDir + "\\inp"

os.chdir(pythcde)
cmd = 'python H5FrReadDOAS2.py ' + '"' + inputdir + '"' + ' '  +  nameff + ' ' + outd

returncode = call(cmd, shell=True)

if returncode :  #error
     print(("error running " + cmd))
     print(("return code " + str(returncode)))
  
else :
    outdd = analDir + "\out"
    nameff = namef + namest + ".txt "
    cmd = 'python TextDOAS_CL_CG.py ' + outd + ' ' + nameff + outdd
 
    returncode = call(cmd, shell=True)

    if returncode :  #error
        print(("error running " + cmd))
        print(("return code " + str(returncode)))
    else :
        nameCI = outd + "\\" + namef + namest + "CI.csv"
        dest = storeD + "\\" + namef + namest + "CI.csv"
        shutil.move(nameCI, dest)
        
        nameft = outdd + "\\" + namef + namest + ".anl"
        dest = storeD + "\\" + namef + namest + ".anl"
        shutil.move(nameft, dest)
        
   
