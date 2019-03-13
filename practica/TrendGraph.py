import sys
import rrdtool
import time


while 1:
    ret = rrdtool.graph( "trend.png",
                     "--start",'1507573200',
                     "--vertical-label=Carga CPU",
                     "--title=Uso de CPU",
                     "--color", "ARROW#009900",
                     '--vertical-label', "Uso de CPU (%)",
                     '--lower-limit', '0',
                     '--upper-limit', '100',
                     "DEF:carga=trend.rrd:CPUload:AVERAGE",
                     "AREA:carga#00FF00:CPU load",


                     "LINE1:30",
                     "AREA:5#ff000022:stack",
                     "VDEF:CPUlast=carga,LAST",
                     "VDEF:CPUmin=carga,MINIMUM",
                     "VDEF:CPUavg=carga,AVERAGE",
                     "VDEF:CPUmax=carga,MAXIMUM",

                         "COMMENT:                         Now          Min             Avg             Max//n",
                     "GPRINT:CPUlast:%12.0lf%s",
                     "GPRINT:CPUmin:%10.0lf%s",
                     "GPRINT:CPUavg:%13.0lf%s",
                     "GPRINT:CPUmax:%13.0lf%s",
                     "VDEF:a=carga,LSLSLOPE",
                     "VDEF:b=carga,LSLINT",
                     'CDEF:avg2=carga,POP,a,COUNT,*,b,+',
                     "LINE2:avg2#FFBB00" )
    time.sleep(15)
