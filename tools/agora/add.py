import copy

import ttyio6 as ttyio
import bbsengine6 as bbsengine

from . import lib

def init(args, **kw):
    return True

def buildargs(args, **kw):
    return lib.buildargs(args, **kw)

def access(args, op, **kw):
    return True

def main(args, **kw):
    bbsengine.util.title("add item")
    lib.setarea(args, "agora: add item", help=True)

    item = {"title":None, "imdbid":None, "affiliatelink":None}
    _item = lib.edit(args, "add", item)
    if item != _item:
        ttyio.echo("needs save", level="info")
    return _item
