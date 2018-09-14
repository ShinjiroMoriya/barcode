import re
import ast
import time
import functools
import tempfile
from PIL import Image
from math import ceil, floor
from datetime import timedelta
from jinja2 import Markup
from django.contrib.messages import get_messages
from django.conf import settings
from datetime import datetime


def calc_time(message='', parser=None):
    """
    :計測用のデコレーター
    """
    def _calc_time(func):
        @functools.wraps(func)
        def wrapper(*args, **kargs):
                request = args[1]
                start = time.time()
                ret = func(*args, **kargs)
                if settings.DEBUG:
                    if parser:
                        parsed_message = parser(message, *args, **kargs)
                        print(request.path +
                              " end time : {time} sec : "
                              "{parsed_message}".format(
                                  time=(time.time() - start),
                                  parsed_message=parsed_message))
                    else:
                        print(request.path +
                              " end time : {time} sec : {message}".format(
                                time=(time.time() - start),
                                message=message))
                return ret
        return wrapper
    return _calc_time


def time_seconds(days=7):
    """
    :秒を返す
    """
    return timedelta(days=days).total_seconds()


def get_error_message(request: object) -> dict or None:
    """
    :Get Flash Error Message
    """
    error_message = None
    if get_messages(request):
        message_storage = get_messages(request)
        for message in message_storage:
            error_message = str(message)
        error_message = ast.literal_eval(error_message)
    return error_message


def session_delete(request, data: list):
    """
    :セッション削除用
    """
    for i in data:
        try:
            del request.session[i]
        except KeyError:
            pass


class Pagination:
    """
    :ページャー
    """
    def __init__(self, page: int, per_page: int, total: int, slug: str,
                 query=''):
        self.page = int(page)
        self.slug = slug
        self.per_page = per_page
        self.total = total
        self.pages = int(ceil(self.total / float(self.per_page)))
        self.offset = (int(page) - 1) * int(per_page)
        self.query = query

    def get_query(self):
        if self.query:
            return '?search=' + self.query
        else:
            return ''

    def numbers(self, number: int=5, current: int=1):
        total_page = ceil(self.total / self.per_page)
        if total_page < number:
            number = total_page

        number_half = floor(number / 2)
        number_start = int(current) - number_half
        number_end = int(current) + number_half

        if number_start <= 0:
            number_start = 1
            number_end = number

        if number_end > total_page:
            number_start = total_page - number + 1
            number_end = total_page

        return {'start': number_start, 'end': number_end + 1}

    def prev(self):
        if self.page > 1:
            return self.slug + str(self.page - 1)

    def next(self):
        if self.page < self.pages:
            return self.slug + str(self.page + 1)

    def information(self):
        """
        :ページ表示情報
        """
        start = self.page if self.page == 1 else self.page-1
        end = ceil(self.total / self.per_page)
        number_total = self.total
        number_start = 1 if self.page == 1 else (start * self.per_page) + 1

        if self.total == 0:
            return '0件を表示'

        number_end = self.total if self.page == end else (self.page *
                                                          self.per_page)

        return (str(number_total) + '件中' + str(number_start) +
                '-' + str(number_end) + '件を表示')


def no_bleak(value):
    """
    :改行を消す
    """
    return value.replace('\n', '')


def nl2br(value):
    """
    :改行コードを<br>に変換
    """
    return Markup(value.replace('\n', '<br>'))


def string_to_date(date: str, fmt='%Y-%m-%d'):
    """
    :文字列をDate形式に変換
    :%Y-%m-%d %H:%M:%S
    """
    try:
        return datetime.strptime(date, fmt)
    except:
        return None


def date_format(date, fmt='%Y-%m-%d %H:%M') -> str:
    """
    :日付の型を変更
    """
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


def get_image_url_content(contents):
    img_url = []
    pattern_img_tag = re.compile('<img[\s]*src[\s]*=.*?>')
    pattern_img_src = re.compile('src[\s]*="(.*?)"')
    img_tag = pattern_img_tag.findall(contents)
    for i in img_tag:
        try:
            m = pattern_img_src.search(i)
            img_url.append(m.group(1))
        except:
            pass
    return img_url


def multiple_replace(text, adict):
    """
    一度に複数の文字列を置換する.
    - text中からディクショナリのキーに合致する文字列を探し、対応の値で置換して返す
    """
    # マッチさせたいキー群を正規表現の形にする e.g) (a1|a2|a3...)
    rx = re.compile('|'.join(map(re.escape, adict)))

    def one_xlat(match):
        return adict[match.group(0)]

    return rx.sub(one_xlat, text)


def get_auth_key(request):
    try:
        app_tk = request.META["HTTP_AUTHORIZATION"]
        m = re.search('(Bearer)(\s)(.*)', app_tk)
        return m.group(3)
    except:
        return None


def image_uploader(file):
    temp = tempfile.NamedTemporaryFile()
    results = {}
    try:
        write_data = file.read()
        temp.write(write_data)
        temp.seek(0)

        if int(settings.MAX_UPLOAD_SIZE) > len(write_data):
            results = Image.open(temp.name)

        temp.close()

    except:
        pass

    finally:
        temp.close()

    return results
