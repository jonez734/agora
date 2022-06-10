#!/usr/bin/env python

import psycopg2, psycopg2.extras

from psycopg2.extras import Json

from optparse import OptionParser

import ttyio3 as ttyio
import bbsengine4 as bbsengine


def main():
    parser = OptionParser(usage="usage: %prog [options] projectid")
    parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_option("--debug", default=True, action="store_true", help="run %prog in debug mode")
    parser.add_option("--limit", default=None, action="store", help="limit the number of records processed (%default)")
    parser.add_option("--asin", default=None, action="store", help="query for a specific asin")

    parser.add_option("--databasename", dest="databasename", action="store", default="zoidweb4", help="database name (%default)")
    parser.add_option("--databasehost", dest="databasehost", action="store", default="localhost", help="database host (%default)")
    parser.add_option("--databaseuser", dest="databaseuser", action="store", default=bbsengine.getcurrentmemberlogin(), help="database user (%default)")
    parser.add_option("--databasepassword", dest="databasepassword", action="store", default=None, help="database password")
    parser.add_option("--databaseport", dest="databaseport", action="store", default="5432", help="database port")

    (opts, args) = parser.parse_args()
#    print(opts.limit)
#    return
    
    dbh = bbsengine.databaseconnect(opts)

    terminalwidth = ttyio.getterminalwidth()
    ttyio.echo("terminalwidth=%r, calc=%r" % (terminalwidth, (terminalwidth/2-2)), level="debug")

    ttyio.echo("-="*int(terminalwidth/2-2))
    ttyio.echo("agora bulk repair of amznitemcomments (parentid)")
    ttyio.echo("-="*int(terminalwidth/2-2))
    ttyio.echo()

    sql = "select asin, id as parentid, title from agora.amznitem"
    cur = dbh.cursor()
    cur.execute(sql)
    res = cur.fetchall()
    for rec in res:
        asin = rec["asin"]
        parentid = rec["parentid"]
        title = rec["title"]
        ttyio.echo("asin=%r, parentid=%r" % (asin, parentid))
        # now, step through agora.amznitemcomment looking for each asin
        sql = "select asin, id from agora.amznitemcomment where asin=%s" # and parentid is null"
        dat = (asin,)
        cur.execute(sql, dat)
        comments = cur.fetchall()
        for comment in comments:
            sql = "update engine.__node set parentid=%s where attributes->>'asin'=%s"
            dat = (parentid, asin)
            ttyio.echo("parentid=%r asin=%r sql=%r, dat=%r" % (parentid, asin, sql, dat))
            cur.execute(sql, dat)
    
    dbh.commit()

if __name__ == "__main__":
    main()
