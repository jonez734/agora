import copy
import argparse

import ttyio6 as ttyio
import bbsengine6 as bbsengine

# @since 20230511
def buildargs(args=None, **kw):
    parser = argparse.ArgumentParser("agora")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    parser.add_argument("--debug", action="store_true", dest="debug")

    defaults = {"databasename": "zoidweb6", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
    bbsengine.database.buildargdatabasegroup(parser, defaults)
    
    return parser

def help(*args, **kw):
    item = kw["item"] if "item" in kw else {}
    _item = kw["_item"] if "_item" in kw else {}
    
    ttyio.echo("{/all}")

    if item["title"] is None:
        ttyio.echo(f"[T]itle: None")
    elif item["title"] != _item["title"]:
        ttyio.echo(f"[T]itle: {item['title']} (was {_item['title']!r})")
    else:
        ttyio.echo(f"[T]itle: {item['title']}")
        
    if item["affiliatelink"] is None:
        ttyio.echo("[A]ffiliate Link")
    elif item["affiliatelink"] != _item["affiliatelink"]:
        ttyio.echo(f"[A]ffiliate Link: {item['affiliatelink']} (was {_item['affiliatelink']!r})")
    else:
        ttyio.echo(f"[A]ffiliate Link: {item['affiliatelink']}")

    if item["imdbid"] is None:
        ttyio.echo("[I]MDB ID")
    elif item["imdbid"] != _item["imdbid"]:
        ttyio.echo(f"[I]MDB ID: {item['imdbid']} (was {item['imdbid']!r})")
    else:
        ttyio.echo(f"[I]MDB ID: {item['imdbid']}")

    ttyio.echo("{f6}[Q]uit")
    return True

def edit(args, mode, item):
    _item = copy.deepcopy(item)

    done = False
    while not done:
        help(item=item, _item=_item)
        ch = ttyio.inputchoice(f"{{f6}}{{var:promptcolor}}{mode} item {{var:optioncolor}}[TAIQ]{{var:promptcolor}}: ", "TIAQ", "Q", help=help)
        if ch == "Q":
            ttyio.echo("Quit")
            done = True
        elif ch == "T":
            ttyio.echo("Title")
            item["title"] = ttyio.inputstring("{var:promptcolor}item title:{var:inputcolor} ", item["title"])
        elif ch == "A":
            ttyio.echo("Affiliate Link")
            item["affiliatelink"] = ttyio.inputstring("{var:promptcolor}affiliate link:{var:inputcolor} ", item["affiliatelink"])
    return _item

# @since 20230513 copied from empyre
def setarea(args, left, **kw):
    def right():
        help = " | F1: Help" if "help" in kw and kw["help"] is True else ""
        debug = " | debug" if args.debug is True else ""
        return f"agora{debug}{help}"

    bbsengine.screen.setarea(left, right)
    return
