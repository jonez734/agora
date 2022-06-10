import os
import pwd
import sys
import copy
import string
import tempfile
import argparse
# import optparse

import psycopg2, psycopg2.extras

import ttyio4 as ttyio
import bbsengine4 as bbsengine

import libagora

currentmemberid = None

def updatesigs(dbh, itemid, sigstr):
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
  
def _edit(dbh, item, header):
  dirty = False
  done = False
  
  original = copy.deepcopy(item)
  
  while not done:
    bbsengine.title(header, titlecolor="{bggray}{white}", hrcolor="{darkgreen}")

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


def edititem(args, dbh):
  currentmemberid = bbsengine.getcurrentmemberid()

  # @fix: allow input of node id, asin, or imdb ids
  asin = ttyio.inputstring("asin: ", multiple=False, noneok=True)
  sql = "select id from agora.amznitem where asin=%s"
  dat = [asin]

  cur = dbh.cursor()
  cur.execute(sql, dat)
  rec = cur.fetchone()
  ttyio.echo("rec=%r" % (rec), interpret=False, level="debug")
  if rec is None:
    ttyio.echo("unknown amazon item.")
    return

  item = libagora.getamznitem(args, dbh, rec["id"])
  ttyio.echo("item=%r" % (item), interpret=False, level="debug")
  return
  rec = _get(dbh, id)
  if rec is None:
    ttyio.echo("{f6}could not load item record{f6}")
    return
  item = _edit(dbh, rec, "edit item")
  if ttyio.inputboolean("update?") is True:
    item["lastmodifiedby"] = currentmemberid
    item["lastmodified"] = "now()"
    bbsengine.update(dbh, "agora.__itemamzn", id, item)
    dbh.commit()
  return

def additem(args, dbh):
#  global currentmemberid
  
  item = {}
  item["id"] = None
  item["url"] = None
  item["title"] = None
  item["description"] = None
  item["approved"] = False
  item["sigs"] = ["top"]
  item["asin"] = None
  item["type"] = "amznaffil"
  
  rec = _edit(dbh, item, "add item")
  if item != rec:
    ttyio.echo("{f6}** needs save **{f6}")
    
  if opts.debug is True:
    ttyio.echo("currentmemberid=%r rec=%r" % (currentmemberid, rec), level="debug")

  if urlexists(dbh, opts, item["url"]) is True:
    ttyio.echo("duplicate url", level="error")
    return

  if ttyio.inputboolean("add? ") is True:
    rec["postedby"] = currentmemberid
    rec["dateposted"] = "now()"
    rec["lastmodified"] = "now()"
    rec["lastmodifiedby"] = currentmemberid
    
    if rec.has_key("id"):
      del rec["id"]
    ttyio.echo(bbsengine.insert(dbh, "agora.__itemamzn", rec))
    dbh.commit()
  return

def listitems(args, dbh):
  sql = "select * from agora.amznitem order by datecreated desc"
  cur = dbh.cursor()
  cur.execute(sql)
  res = cur.fetchall()
  if len(res) == 0:
    ttyio.echo("no amznitems")
    return

  terminalheight = ttyio.getterminalheight()/2
#  ttyio.echo("terminalheight=%d" % (terminalheight))
#  return

  ttyio.echo("{clear}{home}")
  for rec in res:
    siglist = bbsengine.postgres_to_python_list(rec["sigs"])
    sigs = ttyio.readablelist(siglist, sepcolor="{white}", itemcolor="{yellow}")
    buf = "[%s] <%s> %s{f6}sigs: %s{/all}" % (rec["asin"], rec["affiliatelink"], rec["title"], sigs)
    ttyio.echo(buf)
    (r, c) = ttyio.getcursorposition()
#    ttyio.echo("r=%d c=%d" % (r, c))
    ch = ttyio.getch(noneok=True, echoch=False, timeout=0.005)
    if ch == "/" or ch == "Q" or ch == "q":
        ttyio.echo("{bggray}{white} *aborted* {/all}")
        break
    elif ch == " " or r == terminalheight-1:
        ch = ttyio.inputchar("{bggray}{white} *paused* {/all}", "Q/ ", "", echoch=False)
        ttyio.echo("{CHA}{EL}", end="")
        if ch == "Q" or ch == "/":
            ttyio.echo("{bggray}{white} *aborted* {/all}")
            break
  return

def bulkimport(args):
  bbsengine.title("bulk import")
  return

def buildargs(args=None):
  parser = argparse.ArgumentParser("projup")

  parser.add_argument("projectid", nargs="?", type=int, default=None)
  parser.add_argument("--verbose", default=True, action="store_true", help="use verbose mode")
  parser.add_argument("--debug", default=False, action="store_true", help="use debug mode")

  defaults = {"databasename": "zoidweb5", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
  bbsengine.buildargdatabasegroup(parser, defaults)

  return parser

def main():
#  parser = argparse.ArgumentParser("agora")
#  parser.add_argument("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
#  parser.add_argument("--debug", default=True, action="store_true", help="run %prog in debug mode")
  
#  defaults = {"databasename": "zoidweb4", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
#  bbsengine.buildargdatabasegroup(parser, defaults)

#  args = parser.parse_args()
  membermap = {"jam" : 1}
  loginid = pwd.getpwuid(os.geteuid())[0]
  if loginid in membermap:
    currentmemberid = membermap[loginid]
    ttyio.echo("currentmemberid=%r" % (currentmemberid), level="debug")
  else:
    ttyio.echo("uhmm... you do not exist", level="error")
    sys.exit(-1)

#  parser = optparse.OptionParser(usage="usage: %prog [options]")
#  parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
#  parser.add_option("--debug", default=False, action="store_true", help="run %prog in debug mode")
#
#  parser.add_option("--databasename", dest="databasename", action="store", default="zoidweb4", help="database name (%default)")
#  parser.add_option("--databasehost", dest="databasehost", action="store", default="localhost", help="database host (%default)")
#  parser.add_option("--databaseuser", dest="databaseuser", action="store", default=bbsengine.getcurrentmemberlogin(), help="database user (%default)")
#  parser.add_option("--databaseport", dest="databaseport", action="store", default="15432")
#  parser.add_option("--databasepassword", dest="databasepassword", action="store", default=None, help="database password")
#
#  (opts, args) = parser.parse_args()

  currentmemberid = bbsengine.getcurrentmemberid()
  if opts.debug is True:
    ttyio.echo("currentmemberid=%r" % (currentmemberid), level="debug")

  if currentmemberid is None:
    ttyio.echo("login id not found.", level="error")
    sys.exit(-1)

  done = False

  dbh = bbsengine.databaseconnect(opts)

  while not done:
    terminalwidth = ttyio.getterminalwidth()
    # ttyio.echo("terminalwidth=%r, calc=%r" % (terminalwidth, (terminalwidth/2-2)), level="debug")

    bbsengine.title("agora (marketplace)", titlecolor="{bggray}{white}", hrcolor="{green}")
    ttyio.echo()
    ttyio.echo("[A]dd")
    ttyio.echo("[E]dit")
    ttyio.echo("[D]elete")
    ttyio.echo("[L]ist")
    # ttyio.echo("[I]mport")
    ttyio.echo("{f6}[Q]uit")
    ch = ttyio.accept("agora: ", "AEDLQ", "")
    if ch == "Q":
      ttyio.echo("quit")
      done = True
      break
    elif ch == "A":
      ttyio.echo("add item")
      additem(args, dbh)
    elif ch == "E":
      ttyio.echo("edit item")
      edititem(args, dbh)
    elif ch == "L":
      ttyio.echo("list items")
      listitems(args, dbh)
    elif ch == "D":
      ttyio.echo("delete item")
      deleteitem(args, dbh)
    elif ch == "I":
      ttyio.echo("bulk import")
      bulkimport(args, dbh)

  return

if __name__ == "__main__":
  parser = buildargs()
  args = parser.parse_args()

  ttyio.echo("{f6:3}{cursorup:3}") # {curpos:%d,0}" % (ttyio.getterminalheight()-5))
  bbsengine.initscreen(bottommargin=1)

  try:
      main(args)
  except KeyboardInterrupt:
      ttyio.echo("{/all}{bold}INTR{bold}")
  except EOFError:
      ttyio.echo("{/all}{bold}EOF{/bold}")
  finally:
      ttyio.echo("{decsc}{curpos:%d,0}{el}{decrc}{reset}{/all}" % (ttyio.getterminalheight()))
