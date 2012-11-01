import markupsafe

from lxml.html.clean import clean_html
from lxml.etree import XMLSyntaxError

def lx(s):
    try:
        r = clean_html(s)
    except XMLSyntaxError as e:
        r = markupsafe.escape(s)
    return r

