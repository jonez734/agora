import argparse
import bbsengine6 as bbsengine

# @since 20230511
def buildargs(args=None, **kw):
    parser = argparse.ArgumentParser("agora")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    parser.add_argument("--debug", action="store_true", dest="debug")

    defaults = {"databasename": "zoidweb6", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
    bbsengine.database.buildargdatabasegroup(parser, defaults)
    
    return parser
