import rrdtool
ret = rrdtool.create("trend.rrd",
                     "--start",'N',
                     "--step",'60',		 #Uso GAUGE para salvar el dato como se recibe, COUNTER saca diferencias entre dato actual y anterior.
                     "DS:CPUload:GAUGE:600:U:U", #datos del 0 al cien, uso de CPU se obtine por porcentajes
                     "RRA:AVERAGE:0.5:1:24")
if ret:
    print rrdtool.error()
