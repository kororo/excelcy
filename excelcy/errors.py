# inspired from spacy
def add_codes(err_cls):
    """Add error codes to string messages via class attribute names."""

    class ErrorsWithCodes(object):
        def __getattribute__(self, code):
            msg = getattr(err_cls, code)
            return '[{code}] {msg}'.format(code=code, msg=msg)

    return ErrorsWithCodes()


@add_codes
class Errors:
    """ List of identified error """
    E001 = 'Error on loading data configuration file.'
