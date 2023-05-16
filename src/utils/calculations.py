from datetime import datetime

""" Useful functions that we use often. """


def str_to_date(date, make_format="%Y-%m-%d %H:%M:%S") -> datetime:
    try:
        if not date:
            return date

        if '.' in date and '.' not in make_format:
            date = str(date).split('.')[0]
        if '+' in date and '+' not in make_format:
            date = str(date).split('+')[0]
        if 'T' not in make_format:
            date = date.replace('T', ' ')
        if '/' not in make_format:
            date = date.replace('/', '-')
        return datetime.strptime(date, make_format)
    except Exception as e:
        print('calculations error (str_to_date): ' + str(date) + str(e))
        return date
