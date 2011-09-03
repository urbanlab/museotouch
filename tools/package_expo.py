'''
Package expo
============

Outil pour compresser les datas d'une exposition,
et les uploader sur le serveur museotouch si disponible
'''

import sys
from tempfile import NamedTemporaryFile
from os.path import join, dirname, exists, realpath
from os import walk
from zipfile import ZipFile
from shutil import copyfile

def package(expoid):

    # search the directory of the exposition
    root_dir = realpath(join(dirname(__file__), '..'))
    data_dir = join(root_dir, 'app', 'expos', expoid, 'data')
    print '# exposition directory: %r' % data_dir
    if not exists(data_dir):
        raise Exception('Directory %s not found' % data_dir)

    # create temporary filename
    zfn = None
    with NamedTemporaryFile(suffix='.zip', delete=False) as zfd:
        zfn = zfd.name

        # do the zipfile
        print '# start the compression', zfn
        zp = ZipFile(zfd, 'w')
        for dirpath, dirnames, filenames in walk(data_dir):
            dst_path = dirpath
            if dst_path.startswith(data_dir):
                dst_path = dirpath[len(data_dir)+1:]
            for filename in filenames:
                src_fn = join(dirpath, filename)
                dst_fn = join(dst_path, filename)
                print '# compressing', dst_fn
                zp.write(src_fn, dst_fn)

        zp.close()

    # file to upload
    x = 0
    curdir = dirname(__file__)
    dst_fn = None
    while True:
        if x == 0:
            dst_fn = join(curdir, 'dataexpo_%s.zip' % expoid)
        else:
            dst_fn = join(curdir, 'dataexpo_%s_%d.zip' % (expoid, x))
        if exists(dst_fn):
            x += 1
            continue
        copyfile(zfn, dst_fn)
        break

    print '# finished !'
    print
    print realpath(dst_fn)
    print

    return 0


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print 'Usage: package_expo.py <expoid>'
        sys.exit(1)

    sys.exit(package(*sys.argv[1:]))

