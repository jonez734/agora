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
    bbsengine.util.title("edit item")

    item = kw["item"] if "item" in kw else {}
    _item = bbsengine.module.runsubmodule("agora.edit", item=copy.deepcopy(item))
    if item != _item:
        ttyio.echo("needs save", level="info")
    return _item
