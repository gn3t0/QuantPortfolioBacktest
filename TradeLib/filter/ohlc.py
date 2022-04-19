version = 1.01

MIN_BARS = 5

def filter(O, H, L, C, number):

    if number==0: return False
    if number==1: return True
  
    if number==1000: return False
    if number==1001: return True

    lastbar_body = abs(O[4]-C[4])
    lastbar_range = H[4]-L[4]
    week_body = abs(O[0]-C[4])
    week_range = max(H[4],H[3],H[2],H[1],H[0]) - min(L[4],L[3],L[2],L[1],L[0])
    _week_range = H[0]-L[4]

    switcher={

    # Volatility filters

    2: lastbar_body < 0.1  * lastbar_range,
    3: lastbar_body < 0.25 * lastbar_range,  
    4: lastbar_body < 0.5  * lastbar_range,  
    5: lastbar_body < 0.75 * lastbar_range,  

    6: lastbar_body > 0.25 * lastbar_range,   
    7: lastbar_body > 0.5  * lastbar_range, 
    8: lastbar_body > 0.75 * lastbar_range,    
    9: lastbar_body > 0.9  * lastbar_range, 

    10: week_body < 0.1  * _week_range,   
    11: week_body < 0.25 * _week_range,  
    12: week_body < 0.5  * _week_range,    
    13: week_body < 0.75 * _week_range,  
    14: week_body < 1    * _week_range,   
    15: week_body < 1.5  * _week_range,  
    16: week_body < 2    * _week_range,   
    
    17: week_body > 0.25 * _week_range,   
    18: week_body > 0.5  * _week_range,  
    19: week_body > 0.75 * _week_range,    
    20: week_body > 1    * _week_range,  
    21: week_body > 1.5  * _week_range,  
    22: week_body > 2    * _week_range,  
    23: week_body > 2.5  * _week_range,   

    24: week_body < 0.1  * week_range,  
    25: week_body < 0.25 * week_range, 
    26: week_body < 0.5  * week_range,  
    27: week_body < 0.75 * week_range,   

    28: week_body > 0.9  * week_range,  
    29: week_body > 0.25 * week_range,  
    30: week_body > 0.5  * week_range,  
    31: week_body > 0.75 * week_range,   

    32: lastbar_range < ((H[3]-L[3])+(H[2]-L[2]))/3,
    33: lastbar_range < H[3]-L[3] and H[3]-L[3] < H[2]-L[2], 
    34: H[4]<H[3] and L[4]>L[3],
            
    35: H[4]<H[3] or L[4]>L[3],
    36: H[4]>H[3] and L[4]<L[3],
            
    37: lastbar_range<H[3]-L[3],
    38: lastbar_range>H[3]-L[3],


    # Directional filters
        
    1002: C[4]>C[3],
    1003: C[4]<C[3],
    1004: C[4]>C[3] and C[3]>C[2],
    1005: C[4]<C[3] and C[3]<C[2],
    1006: C[4]>C[3] and C[3]>C[2] and C[2]>C[1],
    1007: C[4]<C[3] and C[3]<C[2] and C[2]<C[1],
    1008: C[4]>C[3] and C[3]>C[2] and C[2]>C[1] and C[1]>C[0],
    1009: C[4]<C[3] and C[3]<C[2] and C[2]<C[1] and C[1]<C[0],

    1010: H[4]>H[3],
    1011: H[4]<H[3],
    1012: H[4]>H[3] and H[3]>H[2],
    1013: H[4]<H[3] and H[3]<H[2],
    1014: H[4]>H[3] and H[3]>H[2] and H[2]>H[1],
    1015: H[4]<H[3] and H[3]<H[2] and H[2]<H[1],
    1016: H[4]>H[3] and H[3]>H[2] and H[2]>H[1] and H[1]>H[0],
    1017: H[4]<H[3] and H[3]<H[2] and H[2]<H[1] and H[1]<H[0],

    1018: L[4]>L[3],
    1019: L[4]<L[3],
    1020: L[4]>L[3] and L[3]>L[2],
    1021: L[4]<L[3] and L[3]<L[2],
    1022: L[4]>L[3] and L[3]>L[2] and L[2]>L[1],
    1023: L[4]<L[3] and L[3]<L[2] and L[2]<L[1],
    1024: L[4]>L[3] and L[3]>L[2] and L[2]>L[1] and L[1]>L[0],
    1025: L[4]<L[3] and L[3]<L[2] and L[2]<L[1] and L[1]<L[0],

    1026: C[4]>C[3]+C[3]*0.5*0.01,
    1027: C[4]<C[3]-C[3]*0.5*0.01,
    1028: C[4]>C[3]+C[3]*1  *0.01,
    1029: C[4]<C[3]-C[3]*1  *0.01,
    1030: C[4]>C[3]+C[3]*1.5*0.01,
    1031: C[4]<C[3]-C[3]*1.5*0.01,
    1032: C[4]>C[3]+C[3]*2  *0.01,
    1033: C[4]<C[3]-C[3]*2  *0.01,
    1034: C[4]>C[3]+C[3]*2.5*0.01,
    1035: C[4]<C[3]-C[3]*2.5*0.01,
    1036: C[4]>C[3]+C[3]*3  *0.01,
    1037: C[4]<C[3]-C[3]*3  *0.01,
    
    1038: C[4]>O[4],
    1039: C[4]<O[4],

    1040: H[4]>H[3] and L[4]>L[3],
    1041: H[4]<H[3] and L[4]<L[3],

    1042: H[4]>H[0],
    1043: L[4]<L[0],

    1044: L[4]>L[0],
    1045: H[4]<H[0],

    1046: H[4]>H[3] and H[4]>H[2] and H[4]>H[1],
    1047: L[4]<L[3] and L[4]<L[2] and L[4]<L[1],
    1048: L[4]>L[3] and L[4]>L[2] and L[4]>L[1],
    1049: H[4]<H[3] and H[4]<H[2] and H[4]<H[1],

    1050: (H[4]-C[4])<(0.20*(H[4]-L[4])),
    1051: (C[4]-L[4])<(0.20*(H[4]-L[4])),

    1052: C[4]>O[4] and C[3]>O[3],
    1053: C[4]<O[4] and C[3]<O[3],
    1054: C[4]>O[4] and C[3]<O[3],
    1055: C[4]<O[4] and C[3]>O[3],

    1056: C[4]>H[3],
    1057: C[4]<H[3],

    }

    ret  =  switcher.get(abs(number),None)

    if number<0 : ret = not ret

    return ret

#--------------------------------------------------------------------------

def filter_calc(df, filter_ohlc=[]):

    pass

#--------------------------------------------------------------------------