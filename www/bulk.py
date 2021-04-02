#!/usr/bin/env python

import pwd
import os
import json
import psycopg2, psycopg2.extras
import ttyio2 as ttyio
import bbsengine4 as bbsengine

from psycopg2.extras import Json

currentmemberid = None

def updateitemamznrecord(dbh, opts, nodeid, rec):
  pass

def buildamznitemrecord(fields):
  rec = {}
#  rec["dateposted"] = fields[1] if fields[1] != "now" else "now()"

  checks = fields[2].split(",")
  checks = list(set(checks))

  sigs = fields[4].split(",")# + ["top.agora"]
  sigs = list(set(sigs))
  rec["sigs"] = sigs

  # asin, date, checks, shorturl, sigs, title

  attributes = {}
  attributes["asin"] = fields[0]
  # fields[1] = date
  attributes["checks"] = checks
  attributes["url"] = fields[3]
  # fields[4] = sigs
  attributes["title"] = fields[5]
  rec["attributes"] = attributes

  return rec

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

def amznitemupdate(dbh, opts, fields):
#  ttyio.echo("amznitemupdate.50: start", level="debug")
  rec = buildamznitemrecord(fields)

  cur = dbh.cursor()
  
  attributes = rec["attributes"]
  asin = attributes["asin"]
  sigs = rec["sigs"]

  itemamzn = getitemamzn(dbh, opts, asin)
  if itemamzn is None:
    ttyio.echo("amznitemupdate.120: '%s' is not in database" % (asin), level="error")
    return

  nodeid = itemamzn["id"]
  ttyio.echo("amznitemupdate.90: nodeid=%s" % (nodeid), level="debug")
  if nodeid is False:
    ttyio.echo("amznitemupdate.110: getasin failed")
    return

  ttyio.echo("amznitemupdate.100: itemamzn=%s" % (itemamzn), level="debug")
#  rec = builditemamznrecord(fields)
  ret = bbsengine.update(dbh, "engine.__node", itemamzn["id"], itemamzn)
  ttyio.echo("amznitemupdate.120: bbsengine.update() returned %s" % (ret), level="debug")
#  updateitemamznrecord(dbh, opts, nodeid, rec)
#  sigs = fields[3].split(",")+["top.agora"]
#  sigs = list(set(sigs))
  updatesigmap(dbh, opts, nodeid, sigs)
#  dbh.commit()
  cur.close()

  return

def amzniteminsert(dbh, opts, fields):
  global currentmemberid
  
  amznitem = buildamznitemrecord(fields)

  datestamp = fields[1] if fields[1] != "now" else "now()"

  attributes = amznitem["attributes"]
  asin = attributes["asin"] if "asin" in attributes else None
  
  amznitem["datecreated"] = datestamp
  amznitem["createdbyid"] = currentmemberid
  amznitem["dateupdated"] = datestamp
  amznitem["updatedbyid"] = currentmemberid
  amznitem["attributes"] = Json(amznitem["attributes"])
  
  sigs = amznitem["sigs"]
  del amznitem["sigs"]

  # '{"asin":"%s", "title":"%s", "url": "%s"}' % (asin, title, url)
  nodeid = bbsengine.insert(dbh, "engine.__node", amznitem, mogrify=True)
  ttyio.echo("insert.110: amznitem=%r nodeid=%r" % (amznitem, nodeid), level="debug");
  updatesigmap(dbh, opts, nodeid, sigs)
#  dbh.commit()
  ttyio.echo("insert - %s" % (asin))
  return
  
def asinexists(dbh, asin):
  cur = dbh.cursor()
  sql = "select id from engine.node where attributes->>'asin'=%s"
  dat = (asin,)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  res = cur.fetchone()
  ttyio.echo("asinexists.100: res=%s" % (res), level="debug")
  return res

def getitemamzn(dbh, opts, asin):
  cur = dbh.cursor()
  sql = "select * from engine.node where attributes->>'asin'=%s"
  dat = (asin,)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  res = cur.fetchone()
  ttyio.echo("getitemamzn.100: res=%s" % (res), level="debug")
  return res

def main():
  from optparse import OptionParser

  global currentmemberid

  membermap = {"jam" : 1}

  loginid = pwd.getpwuid(os.geteuid())[0]
  if loginid in membermap:
    currentmemberid = membermap[loginid]
    ttyio.echo("** currentmemberid=%r" % (currentmemberid), level="debug")
  else:
    ttyio.echo("uhmm... you do not exist. go away.", level="error")
    sys.exit(-1)

  ttyio.echo("currentmemberid=%r" % (currentmemberid), level="debug")

  parser = OptionParser(usage="usage: %prog [options] projectid")
  parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
  parser.add_option("--debug", default=True, action="store_true", help="run %prog in debug mode")

  parser.add_option("--databasename", dest="databasename", action="store", default="zoidweb3", help="database name (%default)")
  parser.add_option("--databasehost", dest="databasehost", action="store", default="127.0.0.1", help="database host (%default)")
  parser.add_option("--databaseuser", dest="databaseuser", action="store", default=bbsengine.getcurrentmemberlogin(), help="database user (%default)")
  parser.add_option("--databasepassword", dest="databasepassword", action="store", default=None, help="database password")
  parser.add_option("--databaseport", dest="databaseport", action="store", default="5432", help="database port")

  (opts, args) = parser.parse_args()

  if len(args) == 0:
    ttyio.echo("error: must specify file with one asin per line", level="error")
    return -1

  done = False

  dbh = bbsengine.databaseconnect(opts)

  terminalwidth = ttyio.getterminalwidth()
  ttyio.echo("terminalwidth=%r, calc=%r" % (terminalwidth, (terminalwidth/2-2)), level="debug")

  ttyio.echo("-="*int(terminalwidth/2-2))
  ttyio.echo("agora bulk input")
  ttyio.echo("-="*int(terminalwidth/2-2))
  ttyio.echo()
  fp = open(args[0], "r")
  buf = fp.readlines()
  fp.close()
  cur = dbh.cursor()
  for b in buf:
    x = b.find("#")
    if x is not -1:
      ttyio.echo("found comment: %s" % (b[x:].strip()), level="debug")
      b = b[:x]
    b = b.strip()
    if b == "":
      ttyio.echo("empty line skipped", level="debug")
      continue

    fields = b.split(" ", 5)
    ttyio.echo("main.100: fields=%r" % (fields), level="debug")
    # continue
    if asinexists(dbh, fields[0]) is not None:
      ttyio.echo("%r - exists" % (b))
#      amznitemupdate(dbh, opts, fields)
    else:
      amzniteminsert(dbh, opts, fields)
  dbh.commit()
  cur.close()
  dbh.close()
  return

if __name__ == "__main__":
  main()
          