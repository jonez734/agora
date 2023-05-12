import ttyio5 as ttyio
import bbsengine5 as bbsengine

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args=None, **kw):
    parser = argparse.ArgumentParser("article2")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    parser.add_argument("--debug", action="store_true", dest="debug")

    parser.add_argument("--csvdir", action="store", dest="csvdir", default="csv/", help="dir with csv files (default: %(default)r)")
    parser.add_argument("--basedir", action="store", dest="basedir", default="~jam/projects/agora/", help="dir with csv files (default: %(default)r)")

    defaults = {"databasename": "article2", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
    bbsengine.buildargdatabasegroup(parser, defaults)
    
    return parser

def main(args=None, **kw):
    style = kw["style"] if "style" in kw else "ttyio"
    bbsengine.title("import agora queue", style=style)
