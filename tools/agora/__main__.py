import sys
import time
import argparse
import locale

import bbsengine6 as bbsengine
import ttyio6 as ttyio

from . import lib

parser = lib.buildargs()
args = parser.parse_args()

if sys.stdout.isatty() is True:
    bbsengine.util.initscreen()
    ttyio.setoption("style", "ttyio")
    style = "ttyio"
else:
    ttyio.setoption("style", "noansi")
    style = "noansi"

locale.setlocale(locale.LC_ALL, "")
time.tzset()

try:
    bbsengine.module.runsubmodule(args, "agora.main")
except KeyboardInterrupt:
    if ttyio.getoption("style", "ttyio") == "noansi":
        ttyio.echo("INTR")
    else:
        ttyio.echo("{/all}{bold}INTR{bold}")
except EOFError:
    ttyio.echo("{/all}{bold}EOF{/bold}")
finally:
    if style != "noansi":
        ttyio.echo("{decsc}{curpos:%d,0}{el}{decrc}{reset}{/all}" % (ttyio.getterminalheight()))
