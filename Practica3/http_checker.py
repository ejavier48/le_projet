# -*- coding: utf-8 -*-
from requests import get
from requests.exceptions import Timeout
from time import time, sleep
from threading import Thread

from tftpy import TftpClient

file = 'descarga.pdf'


def checkHTTP(url):
    response = {}
    try:
        b = time()
        r = get(url, timeout = 10, verify = False)
        a = time() - b
        total = len(r.content)
        response['status'] = r.status_code
        response['Velocidad (bytes/s)'] = total/a
        response['Tiempo (s)'] = a
        response['Total Bytes'] = total
    except Timeout:
        response['status'] = 'Error'
    return response

def checkTFTP(url, port, block = '512'):
    response = {}
    try:
        tftp_options = {}
        tftp_options['blksize'] = int(block)
        b = time()
        cliente = TftpClient(url, int(port), tftp_options)
        a = time() - b
        response['Tiempo Conexion (s)'] = a
        b = time()
        cliente.download(file, file)
        a = time() - b
        response['Tiempo Descarga (s)'] = a
        b = time()
        cliente.upload(file, file)
        a = time() - b
        response['Tiempo Carga (s)'] = a
        response['status'] = 'Up'
    except:
        response['status'] = 'Down'

    return response


if __name__ == '__main__':
    i = 0
    MAX = 1000
    t1 = Thread(target = checkHTTP2, args=('https://10.100.64.91',))
    t1.setDaemon(True)
    t1.start()
    t2 = Thread(target = checkHTTP2, args=('https://10.100.64.91',))
    t2.setDaemon(True)
    t2.start()
    while(i < MAX):
        i += 1
        print i
        sleep(3)
    print checkHTTP('http://google.com')
    print checkHTTP('http://fb.com')
    print checkHTTP('http://google.com/holas.php')
    print checkHTTP('https://10.100.64.91')




