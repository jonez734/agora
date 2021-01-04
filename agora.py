import os
import pwd
import sys
import copy
import string
import tempfile
import ConfigParser

import psycopg2, psycopg2.extras

import ttyio2 as ttyio
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
    terminalwidth = ttyio.getterminalwidth()
#    ttyio.echo("terminalwidth=%r, calc=%r" % (terminalwidth, (terminalwidth/2-2)))
    ttyio.echo("-="*(terminalwidth/2-2))

    ttyio.echo(header)
    ttyio.echo("-="*(terminalwidth/2-2))
    ttyio.echo()

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
      buf = bbsengine.inputstring("title: ", item["title"])
      if buf == "":
        item["title"] = None
      else:
        item["title"] = buf
    elif ch == "S":
      ttyio.echo("sigs")
  return item

def _get(dbh, asin):
  sql = "select * from agora.amznitem where attributes ->> 'asin'=%s"
  dat = (str(asin),)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  res = cur.fetchall()
  cur.close()
  ttyio.echo("debug: res=%r" % (res), level="debug")
  if res is None or len(res) == 0:
    ttyio.echo()
    ttyio.echo("invalid id", level="error")
    ttyio.echo()
    return None
  rec = res[0]
  item = {}
  item["title"] = rec["title"]
  item["asin"] = rec["asin"]
  item["id"] = rec["id"]
  item["createdbyid"] = rec["createdbyid"]
  item["datecreated"] = rec["datecreated"]
  item["updatedbyid"] = rec["modifiedbyid"]
  item["dateupdated"] = rec["datemodified"]
  item["sigs"] = rec["sigs"]
  return item

def edititem(dbh):
  global currentmemberid
  
  id = bbsengine.inputinteger("id: ")
  id = int(id)
  rec = _get(dbh, id)
  if rec is None:
    ttyio.echo()
    ttyio.echo("could not load item record")
    ttyio.echo()
    return
  item = _edit(dbh, rec, "edit item")
  if bbsengine.inputboolean("update?") is True:
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

  if bbsengine.inputboolean("add?") is True:
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
  sql = "select * from agora.itemamzn order by datecreated desc"
  cur = dbh.cursor()
  cur.execute(sql)
  res = cur.fetchall()
  if len(res) > 0:
    listfn = os.tempnam(None, "agora")
    fp = open(listfn, "w")
    for rec in res:
      attributes = rec["attributes"]
      fp.write("[%s] <%s> %s %s" % (attributes["asin"], attributes["url"], rec["sigs"], attributes["title"]))
      fp.write("\n")
    fp.close()
    os.system("LESSECURE=1 less %s" % (listfn))
    os.remove(listfn)
  else:
    ttyio.echo("no amznitems")

  return

def main():
  from optparse import OptionParser

  global currentmemberid

  membermap = {"jam" : 1}

  loginid = pwd.getpwuid(os.geteuid())[0]
  if membermap.has_key(loginid):
    currentmemberid = membermap[loginid]
    ttyio.echo("** currentmemberid=%r" % (currentmemberid))
  else:
    ttyio.echo("uhmm... you do not exist. go away.")
    sys.exit(-1)

  ttyio.echo("currentmemberid=%r" % (currentmemberid), level="debug")

  parser = OptionParser(usage="usage: %prog [options] projectid")
  parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
  parser.add_option("--debug", default=True, action="store_true", help="run %prog in debug mode")

  parser.add_option("--databasename", dest="databasename", action="store", default="zoidweb3", help="database name (%default)")
  parser.add_option("--databasehost", dest="databasehost", action="store", default="localhost", help="database host (%default)")
  parser.add_option("--databaseport", dest="databaseport", action="store", default="5432", help="database port (%default)")
  parser.add_option("--databaseuser", dest="databaseuser", action="store", default=bbsengine.getcurrentmemberlogin(), help="database user (%default)")
  parser.add_option("--databasepassword", dest="databasepassword", action="store", default=None, help="database password")

  (opts, args) = parser.parse_args()

  done = False

  dbh = bbsengine.databaseconnect(opts)

  while not done:
    terminalwidth = ttyio.getterminalwidth()
    # ttyio.echo("terminalwidth=%r, calc=%r" % (terminalwidth, (terminalwidth/2-2)), level="debug")

    bbsengine.title("agora (marketplace)", color="{bggray}{white}", hrcolor="{green}")
    ttyio.echo()
    ttyio.echo("[A]dd")
    ttyio.echo("[E]dit")
    ttyio.echo("[D]elete")
#    print "[S]earch links"
    ttyio.echo("[L]ist")
    ttyio.echo("[I]mport")
    ttyio.echo()
    ttyio.echo("[Q]uit")
    ch = ttyio.accept("agora", "AEDLIQ", "")
    if ch == "Q":
      ttyio.echo("quit")
      done = True
      break
    elif ch == "A":
      ttyio.echo("add item")
      additem(dbh, opts)
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
      pass

  return

if __name__ == "__main__":
  main()
