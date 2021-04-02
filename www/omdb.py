import os
import html
import pwd
import json
from urllib.parse import urlencode
from optparse import OptionParser
import requests

import psycopg2, psycopg2.extras

from psycopg2.extras import Json

import ttyio3 as ttyio
import bbsengine4 as bbsengine

OMDBAPIURL = "https://www.omdbapi.com/"
OMDBAPIKEY = "6a168153"

def main():
    parser = OptionParser(usage="usage: %prog [options] projectid")
    parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_option("--debug", default=True, action="store_true", help="run %prog in debug mode")
    parser.add_option("--limit", default=None, action="store", help="limit the number of records processed (%default)")

    parser.add_option("--databasename", dest="databasename", action="store", default="zoidweb4", help="database name (%default)")
    parser.add_option("--databasehost", dest="databasehost", action="store", default="localhost", help="database host (%default)")
    parser.add_option("--databaseuser", dest="databaseuser", action="store", default=bbsengine.getcurrentmemberlogin(), help="database user (%default)")
    parser.add_option("--databasepassword", dest="databasepassword", action="store", default=None, help="database password")
    parser.add_option("--databaseport", dest="databaseport", action="store", default="15432", help="database port")

    (opts, args) = parser.parse_args()
#    print(opts.limit)
#    return
    
    ttyio.echo("database: %s %s:%s" % (opts.databasename, opts.databasehost, opts.databaseport))
    ttyio.echo()
    
    if len(args) == 0:
        ttyio.echo("no arg specified.", level="error")
        ttyio.echo()
        return

    dbh = bbsengine.databaseconnect(opts)

    terminalwidth = ttyio.getterminalwidth()
    ttyio.echo("terminalwidth=%r, calc=%r" % (terminalwidth, (terminalwidth/2-2)), level="debug")

    ttyio.echo("-="*int(terminalwidth/2-2))
    ttyio.echo("agora query of omdb")
    ttyio.echo("-="*int(terminalwidth/2-2))
    ttyio.echo()
    
    sql = "select asin, imdbid, title, imdbid, checks from agora.amznitem where checks ~ 'omdb' and (asin=%s or imdbid=%s)"
    dat = (args[0], args[0])
    if opts.limit is not None:
        sql += " limit %s" % (opts.limit)
    cur = dbh.cursor()
    cur.execute(sql, dat)
    ttyio.echo("omdb.100: mogrify=%r" % (cur.mogrify(sql)), level="debug")
    res = cur.fetchall()

    params = {}
    params["type"] = "movie"
    params["plot"] = "full"
    params["r"] = "json"
    params["apikey"] = OMDBAPIKEY

#    cur = dbh.cursor()
    
    for rec in res:
        asin = rec["asin"]
        imdbid = rec["imdbid"]
        ttyio.echo("asin=%r, imdbid=%r" % (asin, imdbid))

        params["i"] = rec["imdbid"] if rec["imdbid"] is not None else None
#        params["t"] = rec["title"] if rec["title"] is not None else None

        if rec["imdbid"] is not None:
            params["i"] = rec["imdbid"]
        else:
            pass
            # params["t"] = rec["title"]
        # urllib.parse.quote("http://www.samp'le.com/")
        url = "%s?%s" % (OMDBAPIURL, urlencode(params))
        ttyio.echo("url=%s" % (url))
        y = rec["checks"].split(",")
        y = [z.strip() for z in y]
        rec["checks"] = y
        # @todo: update rec *and* attributes. bbsengine.updatenode()?
        r = requests.get(url)
        ttyio.echo("r=%r" % (r))
        omdb = json.loads(r.content)
        omdb["statuscode"] = r.status_code
        ttyio.echo("omdb=%r" % (omdb))
        if r.status_code == 200:
            if "Response" in omdb and omdb["Response"] == "True":
                items = omdb.items()
                for k, v in omdb.items():
                    if omdb[k] == "N/A":
                        omdb[k] = None
                    elif k in ("Director", "Actors", "Genre", "Writer", "Language", "Country"):
                        y = v.split(",")
                        y = [z.strip() for z in y]
                        omdb[k] = y
                        
                attributes = {"omdb": omdb}
                ttyio.echo("attributes=%r" % (attributes))
                sql = "update engine.__node set attributes=attributes||%%s where attributes->>'asin'=%r" % (asin)
                dat = [Json(attributes)]
                try:
                    cur.execute(sql, dat)
                except psycopg2.errors.UntranslatableCharacter:
                    ttyio.echo("unable to translate character. record skipped (try it with UTF8 encoding)", level="warn")
                    dbh.rollback()
                    continue
            else:
                ttyio.echo("Response=%r" % (omdb["Response"]), level="error")
                continue
        else:
            ttyio.echo("Error: %s - %s" % (r.status_code, r.message))
    dbh.commit()
    cur.close()
    return

if __name__ == "__main__":
    main()
