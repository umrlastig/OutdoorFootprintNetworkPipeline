# -*- coding: utf-8 -*-

import sys


main_text   = "----------------------------------------------------------------------\r\n"
main_text  += "CENTER LINE COMPUTATION ON A POLYGON                                  \r\n"
main_text  += "----------------------------------------------------------------------\r\n"
print(main_text, end='')

usage_text  = "Usage: python centeline <in> <out> <interp>                           \r\n"
usage_text += "----------------------------------------------------------------------\r\n"
usage_text += "Inputs:                                                               \r\n"
usage_text += "      - <in>     : input shape file (.shp)                            \r\n" 
usage_text += "      - <out>    : output shape file (.shp)     [def. <in>_ctl.shp]   \r\n"
usage_text += "      - <interp> : interpolation distance (m)   [def. 30 m]           \r\n"
usage_text += "      - <clean>  : cleaning distance (m)        [def.  0 m]           \r\n"
usage_text += "----------------------------------------------------------------------\r\n"
usage_text += "Output: shape file containing center line as a multi-linestring       \r\n" 
usage_text += "----------------------------------------------------------------------\r\n"

if (len(sys.argv) == 1):
    print(usage_text)
    sys.exit(0)
    
if (sys.argv[-1] in ("-h", "-help", "--h", "--help")):
    print(usage_text)
    sys.exit(0)
    
input_file  = sys.argv[1]
output_file = input_file.split(".")[0] + "_ctl.shp"
interp_dist = 25
clean_dist  = 0 

if (len(sys.argv) > 2):
    output_file = sys.argv[2]
if (len(sys.argv) > 3):
    interp_dist = float(sys.argv[3])
if (len(sys.argv) > 4):
    clean_dist = float(sys.argv[4])

confirm_text  = "INPUT FILE         :  " +       input_file + "\r\n"  
confirm_text += "OUTPUT FILE        :  " +      output_file + "\r\n"  
confirm_text += "INTERP. DISTANCE   :  " + str(interp_dist) + " m\r\n"  
confirm_text += "CLEAN.  DISTANCE   :  " + str(clean_dist) + " m\r\n"  
confirm_text += "----------------------------------------------------------------------\r\n"
print(confirm_text, end='')

t1 = datetime.datetime.now().timestamp()

Shp2centerline(input_file, output_file, interp_dist, clean_dist)

dt = datetime.datetime.now().timestamp()-t1
end_text   = "----------------------------------------------------------------------\r\n"
end_text  += "COMPUTATION DONE          "                                                      
end_text  += "[Elapased time: " + str(round(dt, 3)) + " sec]                        \r\n"
end_text  += "----------------------------------------------------------------------\r\n"
print(end_text)

plt.show()