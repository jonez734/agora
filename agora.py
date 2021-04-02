import os
import pwd
import sys
import copy
import string
import tempfile
import argparse

import psycopg2, psycopg2.extras

import ttyio4 as ttyio
import bbsengine4 as bbsengine

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
  
def _update(dbh, table, id, dict):
  global currentmemberid
  
  if dict.has_key("id"):
    del dict["id"]
  
  dict["lastmodified"] = "now()"
  dict["lastmodifiedby"] = currentmemberid
  
  sql = "update %s set " % (table)
  params = ()
  dat = ()
  for k, v in dict.items():
    params += ("%s=%%s" % (k),)
    dat += (v,)

  sql += ", ".join(params)
  sql += " where id=%s" % (id)

  cur = dbh.cursor()
  ret = cur.execute(sql, dat)
  dbh.commit()
  cur.close()
  return ret

def _edit(dbh, item, header):
  dirty = False
  done = False
  
  original = copy.deepcopy(item)
  
  while not done:
    bbsengine.title(header, titlecolor="{bggray}{white}", hrcolor="{green}")

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


def edititem(dbh):
  global currentmemberid
  
  # @fix: allow input of node id, asin, or imdb ids
  id = ttyio.inputinteger("id: ")
  id = int(id)
  rec = _get(dbh, id)
  if rec is None:
    ttyio.echo()
    ttyio.echo("could not load item record")
    ttyio.echo()
    return
  item = _edit(dbh, rec, "edit item")
  if ttyio.inputboolean("update?") is True:
    item["lastmodifiedby"] = currentmemberid
    item["lastmodified"] = "now()"
    bbsengine.update(dbh, "agora.__itemamzn", id, item)
  return

def additem(dbh, opts):
  global currentmemberid
  
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
    ttyio.echo()
    ttyio.echo("** needs save **")
    ttyio.echo()
    
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

def listitems(dbh):
  sql = "select * from agora.amznitem order by datecreated desc"
  cur = dbh.cursor()
  cur.execute(sql)
  res = cur.fetchall()
  if len(res) == 0:
    ttyio.echo("no amznitems")
    return

  for rec in res:
    siglist = bbsengine.postgres_to_python_list(rec["sigs"])
    sigs = ttyio.readablelist(siglist, sepcolor="{white}", itemcolor="{yellow}")
    buf = "[%s] <%s> %s{f6}sigs: %s{/all}" % (rec["asin"], rec["affiliatelink"], rec["title"], sigs)
    ttyio.echo(buf)
  return

def bulkimport(args):
  bbsengine.title("bulk import")
  return

def main():
  parser = argparse.ArgumentParser(prog="agora")
  parser.add_argument("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
  parser.add_argument("--debug", default=True, action="store_true", help="run %prog in debug mode")
  
  defaults = {"databasename": "zoidweb4", "databasehost":"localhost", "databaseuser": None, "databaseport":15432, "databasepassword":None}
  bbsengine.buildargdatabasegroup(parser, defaults)

  args = parser.parse_args()

  currentmemberid = bbsengine.getcurrentmemberid()
  if args.debug is True:
    ttyio.echo("currentmemberid=%r" % (currentmemberid), level="debug")

  if currentmemberid is None:
    ttyio.echo("login id not found.", level="error")
    sys.exit(-1)

  done = False

  dbh = bbsengine.databaseconnect(args)

  while not done:
    terminalwidth = ttyio.getterminalwidth()
    # ttyio.echo("terminalwidth=%r, calc=%r" % (terminalwidth, (terminalwidth/2-2)), level="debug")

    bbsengine.title("agora (marketplace)", titlecolor="{bggray}{white}", hrcolor="{green}")
    ttyio.echo()
    ttyio.echo("[A]dd")
    ttyio.echo("[E]dit")
    ttyio.echo("[D]elete")
    ttyio.echo("[L]ist")
    ttyio.echo("[I]mport")
    ttyio.echo()
    ttyio.echo("[Q]uit")
    ch = ttyio.accept("agora: ", "AEDLIQ", "")
    if ch == "Q":
      ttyio.echo("quit")
      done = True
      break
    elif ch == "A":
      ttyio.echo("add item")
      additem(dbh, args)
    elif ch == "E":
      ttyio.echo("edit item")
      edititem(dbh)
    elif ch == "L":
      ttyio.echo("list items")
      listitems(dbh)
    elif ch == "D":
      ttyio.echo("delete item")
      deleteitem(dbh)
    elif ch == "I":
      ttyio.echo("bulk import")
      bulkimport(dbh)

  return

if __name__ == "__main__":
  main()
