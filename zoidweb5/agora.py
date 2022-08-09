import os
import pwd
import sys
import copy
import time
import json
import locale
import string
import tempfile
import argparse

import ttyio5 as ttyio
import bbsengine5 as bbsengine
from getdate import getdate

import libagora

currentmemberid = None

def updatesigs(args, itemid, sigstr):
  dbh = bbsengine.databaseconnect(args)

  lst = sigstr.split(",")
  sigs = []
  for slp in lst:
    slp = slp.strip()
    if bbsengine.checksiglabelpath(dbh, slp) is True:
      sigs.append(slp)

  if len(sigs) == 0:
    ttyio.echo("no valid sigs listed")
    return False

  sql = "delete from map_item_sig where itemid=%s" 
  dat = (id,)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  for sig in sigs:
    sql = "insert into map_item_sig(siglabelpath, itemid) values (%s, %s)"
    dat = (sig, id)
    cur.execute(sql, dat)
  cur.commit()
  cur.close()
  return True
  
def _delete(dbh, table, id):
  sql = "delete from %s where id=%d" % (table, id)
  cur = dbh.cursor()
  cur.execute(sql)
  cur.close()
  return
  
def _edit(args, item, header):
  dirty = False
  done = False

  original = copy.deepcopy(item)

  dbh = bbsengine.databaseconnect(args)

  while not done:
    bbsengine.title(header)#, titlecolor="{bggray}{white}", hrcolor="{darkgreen}")

    if item != original:
      dirty = True

    if item["title"] is None:
      ttyio.echo("[T]itle")
    else:
      ttyio.echo("[T]itle: %s" % (item["title"]), newline=False)
      if original["title"] != item["title"]:
        ttyio.echo("(was %s)" % (original["title"]), newline=False)
      ttyio.echo()
    
    if item["type"] is None:
      ttyio.echo("t[Y]pe")
    else:
      ttyio.echo("t[Y]pe: %s" % (item["type"]), newline=False)
      if original["type"] != item["type"]:
        ttyio.echo("(was %s)" % (original["type"]), newline=False)
      ttyio.echo()
      
    if item["asin"] is None:
      ttyio.echo("[A]SIN")
    else:
      ttyio.echo("[A]SIN: %s" % (item["asin"]), newline=False)
      if original["asin"] != item["asin"]:
        ttyio.echo("(was %s)" % (original["asin"]), newline=False)
      ttyio.echo()

    sigs = item["sigs"]
    if sigs is not None:
      ttyio.echo("[S]igs: %s" % (sigs), newline=False)
    if original["sigs"] != item["sigs"]:
      ttyio.echo(" (was: %s)" % (original["sigs"]), newline=False)
      #(", ".join([str(sig) for sig in original["sigs"]])), newline=False)
    ttyio.echo()
#      dirty = True

    ttyio.echo("[Q]uit")

    ch = ttyio.accept("option", "TYASQ", "")
    if ch == "S":
      ttyio.echo("sigs")
      originalsigs = ", ".join([str(sig) for sig in item["sigs"]])
      sigs = bbsengine.inputsig(dbh, "sigs: ", originalsigs, multiple=True, debug=False)
      item["sigs"] = sigs
    elif ch == "Q":
      ttyio.echo("quit")
      done = True
    elif ch == "T":
      ttyio.echo("title")
      buf = ttyio.inputstring("title: ", item["title"])
      if buf == "":
        item["title"] = None
      else:
        item["title"] = buf
  return item


def edititem(args):
  currentmemberid = bbsengine.getcurrentmemberid(args)

  # @fix: allow input of node id, asin, or imdb ids
  asin = ttyio.inputstring("asin: ", multiple=False, noneok=True)
  sql = "select id from agora.item where asin=%s"
  dat = [asin]

  dbh = bbsengine.databaseconnect(args)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  rec = cur.fetchone()
  ttyio.echo("rec=%r" % (rec), interpret=False, level="debug")
  if rec is None:
    ttyio.echo("unknown amazon item.", level="error")
    return

  item = libagora.getitem(args, dbh, rec["id"])
  ttyio.echo("item=%r" % (item), interpret=False, level="debug")
  return
  rec = _get(dbh, id)
  if rec is None:
    ttyio.echo("could not load item record", level="error")
    return
  item = _edit(args, rec, "edit item")
  if ttyio.inputboolean("update?") is True:
    item["lastmodifiedby"] = currentmemberid
    item["lastmodified"] = "now()"
    bbsengine.update(dbh, "agora.__itemamzn", id, item)
    dbh.commit()
  return

def additem(args):
#  global currentmemberid
  
  item = {}
  item["id"] = None
  item["title"] = None
  item["approved"] = False
  item["sigs"] = ["top.agora"]
  item["asin"] = None
  item["imdb"] = None
  item["affiliatelink"] = None
  
  rec = _edit(args, item, "add item")
  if item != rec:
    ttyio.echo("{f6}** needs save **{f6}")
    
  if opts.debug is True:
    ttyio.echo("currentmemberid=%r rec=%r" % (currentmemberid, rec), level="debug")

#  if urlexists(args, opts, item["url"]) is True:
#    ttyio.echo("duplicate url", level="error")
#    return

  if ttyio.inputboolean("add? ") is True:
    rec["createdbyid"] = currentmemberid
    rec["dateposted"] = "now()"
    rec["lastmodified"] = "now()"
    rec["lastmodifiedbyid"] = currentmemberid
    
    if rec.has_key("id"):
      del rec["id"]
    ttyio.echo(bbsengine.insert(dbh, "agora.__itemamzn", rec))
    dbh.commit()
  return

def listitems(args):
  dbh = bbsengine.databaseconnect(args)
  sql = "select * from agora.item order by datecreated desc"
  cur = dbh.cursor()
  cur.execute(sql)
  if cur.rowcount == 0:
    ttyio.echo("no items")
    return

  for rec in bbsengine.resultiter(cur):
    siglist = bbsengine.postgres_to_python_list(rec["sigs"])
    sigs = ttyio.readablelist(siglist, sepcolor="{var:labelcolor}", itemcolor="{var:valuecolor}")
    omdb = rec["omdb"] if "omdb" in rec else None
    if type(omdb) is str:
      omdb = json.loads(omdb)
    if omdb is not None:
      ttyio.echo("omdb=%r" % (omdb), level="debug")
      title = "%s (%s) [%s]" % (omdb["Title"], omdb["Year"], omdb["Rated"])
    else:
      title = rec["title"]
    buf = "{var:valuecolor}%s {var:labelcolor}posted to {var:valuecolor}%s {var:labelcolor}by {var:valuecolor}%s {var:labelcolor}on {var:valuecolor}%s {var:labelcolor}shop: <{var:valuecolor}%s{var:labelcolor}>" % (title, sigs, rec["createdbyname"], rec["datecreated"], rec["affiliatelink"])
    ttyio.echo(buf)
    if omdb is not None:
      ttyio.echo("{var:labelcolor}plot: {var:valuecolor}%s" % (omdb["Plot"]))
      ttyio.echo("{var:labelcolor}awards: {var:valuecolor}%s" % (omdb["Awards"]))

      actors = omdb["Actors"].split(", ")
      actors = [x.strip() for x in actors]
      buf = ttyio.readablelist(actors, sepcolor="{var:labelcolor}", itemcolor="{var:valuecolor}")
      ttyio.echo("{var:labelcolor}actors: {var:valuecolor}%s" % (buf))
      imdbrating = omdb["imdbRating"]
      imdbvotes = omdb["imdbVotes"]
      ttyio.echo("{var:labelcolor}imdb: {var:valuecolor}%s {var:labelcolor}with {var:valuecolor}%s votes" % (imdbrating, imdbvotes))
    ttyio.echo(bbsengine.hr(color="{var:hrcolor}"))

  return

def importitems(args):
  bbsengine.title("import items")

  dbh = bbsengine.databaseconnect(args)

  filename = "queue.txt"
  with open(filename) as f:
    for buf in f:
      if buf == "":
          done = True
          break
      buf = buf.strip()
      i = buf.find("#")
      if i >= 0:
          buf = buf[:i]
      if buf == "":
          continue
      fields = buf.split()
      fields = [f for f in fields if f != ""]
      if len(fields) < 5:
          ttyio.echo("syntax error, incorrect number of fields")
          return
      item = {}
      item["affiliatelink"] = fields[1]
      item["asin"] = fields[2]
      item["imdbid"] = fields[3]
      item["title"] = " ".join(fields[5:])
      item["type"] = "movie"
      if args.debug is True:
        ttyio.echo("item=%r" % (item), level="debug")
      
      if libagora.getitembyasin(args, item["asin"]) is not None:
        ttyio.echo("%r is already in database." % (item["asin"]))
        continue

      node = {}
      node["prg"] = "agora.item"
      node["attributes"] = item
      nodeid = libagora.insertitem(args, item, mogrify=True)
      ttyio.echo("nodeid=%r" % (nodeid), level="debug")

      datewatched = bbsengine.datestamp(getdate(fields[0]))
      if datewatched == -1:
        ttyio.echo("could not convert %r to an epoch time" % (datewatched), level="error")
        datewatched = None
      comment = {}
      comment["parentid"] = nodeid
      comment["datewatched"] = datewatched
      comment["watchmethod"] = fields[4]

      commentid = libagora.insertcomment(args, comment)
  if args.debug is True:
    ttyio.echo("calling commit")
  dbh.commit()

  return

def queryomdb(args):
  dbh = bbsengine.databaseconnect(args)
  sql = "select id, imdbid from agora.item where omdb is null limit 1"
  cur = dbh.cursor()
  cur.execute(sql)
  for item in bbsengine.resultiter(cur):
    nodeid = item["id"]
    imdbid = item["imdbid"]
    omdb = libagora.queryomdb(args, imdbid)
    attributes = {}
    attributes["omdb"] = omdb
    bbsengine.updatenodeattributes(dbh, args, nodeid, attributes)
  dbh.commit()

def init(args=None):
  pass

def buildargs(args=None):
  parser = argparse.ArgumentParser("projup")

  parser.add_argument("projectid", nargs="?", type=int, default=None)
  parser.add_argument("--verbose", default=True, action="store_true", help="use verbose mode")
  parser.add_argument("--debug", default=False, action="store_true", help="use debug mode")

  defaults = {"databasename": "zoidweb5", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
  bbsengine.buildargdatabasegroup(parser, defaults)

  return parser

def main(args):
  currentmemberid = bbsengine.getcurrentmemberid(args)
  if args.debug is True:
    ttyio.echo("currentmemberid=%r" % (currentmemberid), level="debug")

  if currentmemberid is None:
    ttyio.echo("login id not found.", level="error")
    sys.exit(-1)

  done = False

  while not done:
    terminalwidth = ttyio.getterminalwidth()
    # ttyio.echo("terminalwidth=%r, calc=%r" % (terminalwidth, (terminalwidth/2-2)), level="debug")

    bbsengine.title("agora (amazon affiliate marketplace, zoidweb5)")
    options = ""
    ttyio.echo()
    if bbsengine.checksysop(args) is True:
      ttyio.echo("[A]dd")
      ttyio.echo("[E]dit")
      ttyio.echo("[D]elete")
      options += "AED"
      ttyio.echo("[I]mport")
      options += "I"
      ttyio.echo("[O]mdb")
      options += "O"

    ttyio.echo("[L]ist")
    options += "L"
    ttyio.echo("{f6}[Q]uit")
    options += "Q"
    ch = ttyio.accept("{var:promptcolor}agora: {var:inputcolor}", options, "")
    if ch == "Q":
      ttyio.echo("quit")
      done = True
      break
    elif ch == "I":
      ttyio.echo("import items")
      importitems(args)
    elif ch == "A":
      ttyio.echo("add item")
      additem(args)
    elif ch == "E":
      ttyio.echo("edit item")
      edititem(args)
    elif ch == "L":
      ttyio.echo("list items")
      listitems(args)
    elif ch == "D":
      ttyio.echo("delete item")
      deleteitem(args)
    elif ch == "I":
      ttyio.echo("import items")
      importitems(args)
    elif ch == "O":
      ttyio.echo("query omdb")
      queryomdb(args)

  return

if __name__ == "__main__":
  parser = buildargs()
  args = parser.parse_args()

  ttyio.echo("{f6:3}{cursorup:3}")
  bbsengine.initscreen(bottommargin=1)

  locale.setlocale(locale.LC_ALL, "")
  time.tzset()

  init(args)

  try:
      main(args)
  except KeyboardInterrupt:
      ttyio.echo("{/all}{bold}INTR{bold}")
  except EOFError:
      ttyio.echo("{/all}{bold}EOF{/bold}")
  finally:
      ttyio.echo("{decsc}{curpos:%d,0}{eraseline}{decrc}{reset}{/all}" % (ttyio.getterminalheight()))
