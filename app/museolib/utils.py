import unicodedata

def format_date(dt):
    '''Format the integer date to text for slider
    '''
    if dt < 0:
        return '%d AV JC' % dt
    return str(dt)

def remove_accents(str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(str))
    return u''.join([c for c in nkfd_form if not unicodedata.combining(c)])

ascii_table = map(chr, range(ord('a'), ord('z')+1) + range(ord('A'), ord('Z')+1)
        + range(ord('0'), ord('9') + 1) + [ord('_'), ord('-')])

def convert_to_key(name):
    name = remove_accents(name.lower())
    name = u''.join([x if x in ascii_table else '_' for x in name])
    return name

def no_url(f):
    return f[7:].replace('/', '_')