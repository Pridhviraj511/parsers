from functools import wraps
from inspect import FrameInfo
from inspect import stack, trace
from os.path import basename
from pathlib import Path
from time import sleep
from traceback import print_exc


def catch(msg=''):
    """
    This is a universal exception catcher, which provides us with basic information to help us find the cause of the
    error and the error line number.
    It keeps error messages in the error log, so we can check more deeply if the basic information is not helpful.

    :param msg: Text that we send to precise where error happens, and also an error.
    :type msg: str
    :param bookmaker_name: Name of the bookmaker if exists.
    :type bookmaker_name: str
    """

    c, t, p, line_no = [], [], '', '-'
    try:
        try:
            c = stack()[1]
            t = trace()[0]
            # line_no = t.lineno if type(t) == FrameInfo else "-"  # error happens a lot, that's why it is here
        except Exception as e:
            print('Errors error (catch) 2:', e)

        p = f'***** ERROR! *****\n\t' \
            f'File: {basename(Path(c.filename))}\n\t' \
            f'Function: {c.function}\n\t' \
            f'Line no: {c.lineno if type(c) == FrameInfo else "-"}\n\t' \
            f'Line err no: {t.lineno if type(t) == FrameInfo else "-"}\n\t' \
            f'Error: ' + str(c[0].f_locals.get('e', '')) + f'\n\t' \
                                                           'Code context: ' + str(t.code_context).replace("\t", " ").replace("  ", " ") + '\n\t' \
                                                                                                                                          f'MESSAGE: {msg}\n' \
                                                                                                                                          f'******* END *******'
        print(p)

        # if we need some attr from class, but it is better to send only things we need in msg or args
        # if 'self' in c[0].f_locals:
        #     m = c[0].f_locals['self']
        #     # print(m)
        #     attrib = inspect.getmembers(m, lambda a: not (inspect.isroutine(a)))
        #     # print(attrib)

        print(p + '\n\tLOCALS: ' + str(c[0].f_locals))

    except Exception as e:
        print(f'Errors error (catch), error: {e},\nc: {c},\nt: {t},\np: {p},\ntraceback:{print_exc()}')


def retry(tries=3, delay=1, backoff=1, func_name='', return_back='err', notify=True):
    """Retry calling the decorated function using an exponential backoff.

    :param tries: Number of times to try (not retry) before giving up.
    :type tries: int
    :param delay: Initial delay between retries in seconds.
    :type delay: int
    :param backoff: Backoff multiplier e.g. value of 2 will double the delay each retry.
    :type backoff: int
    :param func_name: The name of the function in which the error occurs.
    :type func_name: str
    :param return_back: In case we want to return something, instead of an exception.
    :type return_back: Any
    :param notify: If we want to get notified about this error.
    :type notify: bool
    """

    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            max_tries, max_delay = tries, delay
            while max_tries > 0:
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    print(f'Retrying {func_name} ({tries - max_tries + 1}/{tries}) in',
                          f'{max_delay}s, args: {args}, kwargs: {kwargs}')
                    sleep(max_delay)
                    max_tries -= 1
                    max_delay *= backoff
            return f(*args, **kwargs) if return_back == 'err' else return_back

        return f_retry  # true decorator

    return deco_retry


if __name__ == '__main__':
    @retry(tries=3, return_back=None)
    def test_fail():
        raise Exception("Fail")
        # d = 1/0
        # print('aaaaaaaaaaa', d)


    print(test_fail())
