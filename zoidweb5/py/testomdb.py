import argparse
import requests
import urllib.parse
import json

import ttyio5 as ttyio
import bbsengine5 as bbsengine

OMDBAPIURL = "https://www.omdbapi.com/"
OMDBAPIKEY = "6a168153"

def buildargs(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_argument("--debug", default=True, action="store_true", help="run %prog in debug mode")
    parser.add_argument("--limit", default=None, action="store", help="limit the number of records processed (%default)")
    parser.add_argument("imdbid", type=str, help="imdbid") # nargs="*", help="location")

    defaults = {"databasename": "zoidweb5", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
    bbsengine.buildargdatabasegroup(parser, defaults)

    return parser

def main(args):
    params = {}
    params["type"] = "movie"
    params["plot"] = "full"
    params["r"] = "json"
    params["apikey"] = OMDBAPIKEY
    params["i"] = args.imdbid

    url = "%s?%s" % (OMDBAPIURL, urllib.parse.urlencode(params))
    ttyio.echo("url=%r" % (url), level="debug")
    r = requests.get(url)
    ttyio.echo("r=%r" % (r), level="debug")
    omdb = json.loads(r.content)
    ttyio.echo("omdb=%r" % (omdb), level="debug")

if __name__ == "__main__":
    parser = buildargs()
    args = parser.parse_args()
    main(args)
