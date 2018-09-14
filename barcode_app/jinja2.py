from jinja2 import Environment
from datetime import datetime
from barcode_app.services import multiple_replace


def _limit_text(value, num, dot=False):
    if len(value) > num:
        if dot:
            return value[:num] + '…'
        else:
            return value[:num]
    return value[:num]


def _thumbnail(path, sizes='w_250,h_250,c_pad,b_white'):
    """Ex: w_300,h_200"""
    try:
        replace_dict = {
            '/image/upload/': '/image/upload/{sizes}/'.format(sizes=sizes),
        }
        return multiple_replace(path, replace_dict)
    except:
        return path


def _filter_datetime(date, fmt='%Y-%m-%d %H:%M'):
    try:
        try:
            date = datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S.%f')
        except:
            date = datetime.strptime(str(date), '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            date = datetime.strptime(str(date), '%Y-%m-%d')
        except:
            return ''

    return date.strftime(fmt)


def _en_url(value):
    return value.replace('/ja/', '/en/')


def _ja_url(value):
    return value.replace('/en/', '/ja/')


def environment(**options):
    env = Environment(**options)
    env.globals.update({
    })
    env.filters.update({
        'limit_text': _limit_text,
        'datetime': _filter_datetime,
        'thumbnail': _thumbnail,
        'en_url': _en_url,
        'ja_url': _ja_url,
    })
    return env
