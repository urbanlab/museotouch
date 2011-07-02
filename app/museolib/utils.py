def format_date(dt):
    '''Format the integer date to text for slider
    '''
    if dt < 0:
        return '%d AV JC' % dt
    return str(dt)
