import os
import html
import pwd
import json
from urllib.parse import urlencode
from optparse import OptionParser
import requests

import ttyio2 as ttyio
import bbsengine4 as bbsengine

def updatesigmap(dbh, opts, nodeid, sigs):
  ttyio.echo("updatesigmap.100: nodeid=%s sigs=%s" % (nodeid, sigs))
  cur = dbh.cursor()
  sql = "delete from engine.map_node_sig where nodeid=%s"
  dat = (nodeid,)
  cur.execute(sql, dat)
  for sig in sigs:
    rec = {}
    rec["nodeid"] = nodeid
    rec["sigpath"] = bbsengine.normalizelabelpath(sig)
    bbsengine.insert(dbh, "engine.map_node_sig", rec, returnid=False)
#  dbh.commit()
  return

def main():
    parser = OptionParser(usage="usage: %prog [options] projectid")
    parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_option("--debug", default=True, action="store_true", help="run %prog in debug mode")
    parser.add_option("--limit", default="50", action="store", help="limit the number of records processed (%default)")
    parser.add_option("--asin", default="", action="store", help="query for a specific asin")

    parser.add_option("--databasename", dest="databasename", action="store", default="zoidweb3", help="database name (%default)")
    parser.add_option("--databasehost", dest="databasehost", action="store", default="localhost", help="database host (%default)")
    parser.add_option("--databaseuser", dest="databaseuser", action="store", default=bbsengine.getcurrentmemberlogin(), help="database user (%default)")
    parser.add_option("--databasepassword", dest="databasepassword", action="store", default=None, help="database password")
    parser.add_option("--databaseport", dest="databaseport", action="store", default="5432", help="database port")

    (opts, args) = parser.parse_args()

    dbh = bbsengine.databaseconnect(opts)

    terminalwidth = ttyio.getterminalwidth()
    ttyio.echo("terminalwidth=%r, calc=%r" % (terminalwidth, (terminalwidth/2-2)), level="debug")

    ttyio.echo("-="*int(terminalwidth/2-2))
    ttyio.echo("agora fixup sigs (movies to top.entertainment.movies)")
    ttyio.echo("-="*int(terminalwidth/2-2))
    ttyio.echo()

    sql="select id, sigs, attributes->>'amznitemtype' as amznitemtype from agora.amznitem where attributes->>'amznitemtype'='movie'"
    cur = dbh.cursor()
    cur.execute(sql)
    res = cur.fetchall()
    for rec in res:
        nodeid = rec["id"]

        result = []

        sigs = rec["sigs"]
        sigs = sigs.replace("{", "").replace("}", "")
        sigs = sigs.split(",")# + ["top.agora"]
        sigs = list(set(sigs))
        sigs = [name.strip() for name in sigs]
        for name in sigs:
          if name == "top.entertainment":
            name = "top.entertainment.movies"
          result.append(name)

        updatesigmap(dbh, opts, nodeid, result)

    cur.close()
    dbh.commit()
    dbh.close()

if __name__ == "__main__":
  main()
    