import os
import html
import pwd
import json
from urllib.parse import urlencode
from optparse import OptionParser
import requests

import psycopg2, psycopg2.extras
from psycopg2.extras import Json

import ttyio2 as ttyio
import bbsengine4 as bbsengine

OMDBAPIURL = "https://www.omdbapi.com/"
OMDBAPIKEY = "6a168153"

def main():
    parser = OptionParser(usage="usage: %prog [options] projectid")
    parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_option("--debug", default=True, action="store_true", help="run %prog in debug mode")
    parser.add_option("--asin", default=None, action="store", help="query for a specific asin")

    g = parser.add_option_group("database options")
    g.add_option("--databasename", dest="databasename", action="store", default="zoidweb4", help="database name (%default)")
    g.add_option("--databasehost", dest="databasehost", action="store", default="localhost", help="database host (%default)")
    g.add_option("--databaseuser", dest="databaseuser", action="store", default=bbsengine.getcurrentmemberlogin(), help="database user (%default)")
    g.add_option("--databasepassword", dest="databasepassword", action="store", default=None, help="database password")
    g.add_option("--databaseport", dest="databaseport", action="store", default="5432", help="database port")

    (opts, args) = parser.parse_args()
    
    dbh = bbsengine.databaseconnect(opts)

    terminalwidth = ttyio.getterminalwidth()
#    ttyio.echo("terminalwidth=%r, calc=%r" % (terminalwidth, (terminalwidth/2-2)), level="debug")

    ttyio.echo("-="*int(terminalwidth/2-2))
    ttyio.echo("clear omdb data for specific asin")
    ttyio.echo("-="*int(terminalwidth/2-2))
    ttyio.echo()
    
    if opts.asin is None or opts.asin == "":
        ttyio.echo("must specify --asin", level="error")
        return -1

    sql = "select attributes->>'asin' as asin, attributes->>'title' as title from agora.amznitem where attributes->>'checks' ~ 'omdb' and attributes->>'asin'=%r" % (opts.asin)

    cur = dbh.cursor()
    cur.execute(sql)
    ttyio.echo("clearomdb.100: mogrify=%r" % (cur.mogrify(sql)), level="debug")
    res = cur.fetchall()

    cur = dbh.cursor()
    
    if res is None or res == []:
        ttyio.echo("clearomdb.105: asin not found", level="error")
        return -1

    rec = res[0]
    omdb = {}
    omdb["Result"] = False
    attributes = { "omdb": omdb }
    sql = "update engine.__node set attributes=attributes||%%s where attributes->>'asin'=%r" % (opts.asin)
    dat = [Json(attributes)]
    cur.execute(sql, dat)
    dbh.commit()
    cur.close()
    ttyio.echo("OK", level="ok")
    return 0

if __name__ == "__main__":
    main()
