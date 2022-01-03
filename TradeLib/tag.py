version = 1.0

import pandas as pd
from django.utils.crypto import get_random_string

def tag_trt(trt_file):

    try:
        df =  pd.read_csv(trt_file, header=None, nrows=1)
    except:
        return(0)

    if df.iat[0,0].find("tag_id")<0 : 
        with open(trt_file, "r") as f:
            lines = f.read()
        with open(trt_file, "w") as f:
            tag =  get_random_string(8)
            f.write('# tag_id = '+("%s" % tag))
            f.write('\n# tag = ' + str(version))
            f.write("\n")
            f.write(lines)

    return("%s" % tag)

#--------------------------------------------------------------------------

def get_tag(trt_file):
    
    try:
        df =  pd.read_csv(trt_file, header=None, nrows=1)
    except:
        return(0)
    
    if df.iat[0,0].find("tag_id")>=0 :
        tag= df.iat[0,0].replace("#","")
        tag= tag.replace("tag_id","")
        tag= tag.replace("=","")
        tag= tag.strip()
    else:
        tag=0

    return(tag)

#--------------------------------------------------------------------------
