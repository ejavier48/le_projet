import sys, os
from time import time
from optparse import OptionParser
import tftpy

def main():
    usage=""
    parser = OptionParser(usage=usage)
    parser.add_option('-H',
                      '--host',
                      action='store',
                      dest='host',
                      help='ip address')
    parser.add_option('-p',
                      '--port',
                      action='store',
                      dest='port',
                      help='port (default: 69)',
                      default=69)
    parser.add_option('-f',
                      '--filename',
                      action='store',
                      dest='filename',
                      help='filename')
    parser.add_option('-b',
                      '--blocksize',
                      action='store',
                      dest='blocksize',
                      help='udp packet size to use (default: 512)',
                      default=512)
    parser.add_option('-o',
                      '--output',
                      action='store',
                      dest='output',
                      help='output file (default: same as requested filename)')
    parser.add_option('-a',
                      '--action',
                      action='store',
                      dest='action',
                      help='get or put')


    options, args = parser.parse_args()
    if not options.host or not options.filename or not options.action:
        sys.stderr.write("The --host, --filename and --action options are required.\n")
        parser.print_help()
        sys.exit(1)

    tftp_options = {}
    if options.blocksize:
        tftp_options['blksize'] = int(options.blocksize)

    if not options.output:
        options.output = os.path.basename(options.filename)

    tclient = tftpy.TftpClient(options.host,int(options.port),tftp_options)
    
    start_time = time()

    if options.action=='get':
        tclient.download(options.filename,options.filename)
    elif options.action=='put':
        tclient.upload(options.filename,options.filename)

    elapsed_time = time() - start_time

    print("Ok. Time:  ",elapsed_time)


if __name__ == '__main__':
    main()
