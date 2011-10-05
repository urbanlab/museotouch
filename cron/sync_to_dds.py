#!/usr/bin/env python
'''
Synchronize raw file to dds files
=================================

Algorithm:

    1. Get a list of current objects file
    2. Make a list of missing DDS
    3. Download RAW image
    4. Calculate his MD5
    5. Convert to DDS
    6. Store DDS
    7. Store origial MD5

TODO:

    Check if the dds must be regenerate according to last MD5 pushed

'''

import sys
from os import unlink
from os.path import dirname, join, exists, basename, realpath
from ConfigParser import ConfigParser
from ftplib import FTP, error_perm
from tempfile import mkstemp
from os import write, close
from functools import partial
from subprocess import Popen, PIPE
from hashlib import md5
from datetime import datetime

def log(text):
    time = datetime.now().isoformat()
    print '#', time, '#', text

# Force mode ?
force = False
if '--force' in sys.argv:
    force = True

# Read configuration
config_keys = ('user', 'password', 'host', 'path')
config_fn = join(dirname(__file__), 'config.ini')
if not exists(config_fn):
    raise Exception('Missing config.ini')

config = ConfigParser()
config.read(join(dirname(__file__), 'config.ini'))
for key in config_keys:
    if not config.get('ftp', key, None):
        raise Exception('Invalid %r in config.ini' % key)

# Connect to ftp
host = config.get('ftp', 'host')
user = config.get('ftp', 'user')
path = config.get('ftp', 'path')
password = config.get('ftp', 'password')

log('=' * 70)
log('Connect to %s' % host)
ftp = FTP(host, user, password)
log('Connected to %s' % host)

# Get a list of files to check
files = ftp.nlst(path)

# Check each raw files
fn_to_convert = []
log('Checking %d files to synchronize' % len(files))
for filename in files:
    uid = basename(filename)
    dds_filename = join(path, uid, 'compressed', 'dds', '%s.dds' % uid)

    # Don't check md5 if force is pushed
    if not force:
        # Check if it already have been converted
        dds_filename_md5 = '%s.md5sum' % dds_filename
        try:
            ftp.voidcmd('TYPE I')
            size = ftp.size(dds_filename_md5)
            if size is not None and size > 0:
                continue
        except error_perm, e:
            pass

    # Get files in that directory
    raw_files = ftp.nlst(join(path, uid, 'raw'))
    raw_filename = None
    for item in raw_files:
        ext = basename(item).rsplit('.', 1)[-1].lower()
        if ext in ('png', 'jpg', 'jpeg', 'tif', 'tiff'):
            raw_filename = item
            # take the first in order of preference, not the inverse
            break

    if raw_filename is None:
        log('Object %r have no raw objects found (png/jpg/jpeg/tif/tiff)' % uid)
        continue

    log('Add %s to convert' % raw_filename)
    fn_to_convert.append((raw_filename, dds_filename))

def write_callback(fd, chunk):
    write(fd, chunk)

def try_unlink(fn):
    try:
        unlink(fn)
    except:
        pass

# Ok, now check what we need to convert
log('We have %d files to convert' % len(fn_to_convert))
ddstool = realpath(join(dirname(__file__), 'ddstool'))
for raw_remote_fn, dds_remote_fn in fn_to_convert:
    ext = basename(raw_remote_fn).rsplit('.', 1)[-1]
    raw_local_fn = raw_local_md5 = dds_local_fn = None

    try:
        # Create a temporary filename, and get file
        log('-' * 70)
        log('Downloading %s' % basename(raw_remote_fn))
        raw_local_fd, raw_local_fn = mkstemp('.%s' % ext)
        ftp.retrbinary('RETR %s' % raw_remote_fn,
                partial(write_callback, raw_local_fd))
        close(raw_local_fd)
        log('Downloaded to %s' % raw_local_fn)

        # Prepare filenames
        raw_local_md5 = '%s.md5sum' % raw_local_fn
        dds_local_fn = '%s.dds' % raw_local_fn.rsplit('.', 1)[0]
        dds_remote_md5 = '%s.md5sum' % dds_remote_fn

        # Calculate MD5, and temporary store it on the disk
        with open(raw_local_fn, 'rb') as fd:
            m = md5(fd.read()).hexdigest()
        log('Calculate MD5 (%s)' % m)
        with open(raw_local_md5, 'wb') as fd:
            fd.write(m)

        # Convert the image to DDS
        log('Converting %s' % raw_local_fn)
        cmd = '%s -c %s' % (ddstool, raw_local_fn)
        process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).communicate()
        log('Convertion log (stdout)')
        for line in process[0].splitlines():
            log(line)
        log('Convertion log (stderr)')
        for line in process[1].splitlines():
            log(line)


        # Ensure the convertion have been done
        log('Check if the DDS exist')
        if not exists(dds_local_fn):
            log('=> Error while converting to DDS, abort this file.')
            continue

        # create compressed directory
        try:
            ftp.mkd(dirname(dds_remote_fn))
        except error_perm, e:
            pass

        # Save to FTP
        log('Push DDS to ftp')
        with open(dds_local_fn, 'rb') as fd:
            ftp.storbinary('STOR %s' % dds_remote_fn, fd)

        log('Push MD5 to ftp')
        with open(raw_local_md5, 'rb') as fd:
            ftp.storbinary('STOR %s' % dds_remote_md5, fd)

    finally:
        try_unlink(raw_local_fn)
        try_unlink(raw_local_md5)
        try_unlink(dds_local_fn)

log('Finished.')
