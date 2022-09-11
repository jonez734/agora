import urllib.parse
import requests
import json
import ttyio5 as ttyio
import bbsengine5 as bbsengine

OMDBAPIURL = "https://www.omdbapi.com/"
OMDBAPIKEY = "6a168153"

STOREID = "zoidagora2022-20"

def builditemrecord(args, rec):
  item = {}
  item["title"] = rec["title"]
  item["asin"] = rec["asin"]
  item["imdbid"] = rec["imdbid"]
  item["id"] = rec["id"]
  item["createdbyid"] = rec["createdbyid"]
  item["datecreated"] = rec["datecreated"]
  item["updatedbyid"] = rec["updatedbyid"]
  item["dateupdated"] = rec["dateupdated"]
  item["parentid"] = rec["parentid"]
  item["title"] = rec["title"]
  item["affiliatelink"] = rec["affiliatelink"]
  item["checks"] = rec["checks"]

  item["sigs"] = bbsengine.postgres_to_python_list(rec["sigs"])
  return item

def filteritemattributes(item:dict) -> dict:
  for attr in ("sigs", "parentid", "dateupdated", "updatedbyid", "updatedbyname", "createdbyid", "datecreated", "createdbyname", "id"):
    if attr in item:
      ttyio.echo("removing %s from item attributes" % (attr), level="warning")
      del(item[attr])

  return item

def getitembynodeid(args, nodeid:int):
  dbh = bbsengine.databaseconnect(args)
  sql = "select * from agora.item where id=%s"
  dat = (nodeid)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  rec = cur.fetchone()
  if rec is None:
    return None
  return builditemrecord(args, rec)

def getitembyasin(args, asin:str):
  dbh = bbsengine.databaseconnect(args)
  sql = "select * from agora.item where attributes ->> 'asin'=%s"
  dat = (str(asin),)
  dbh = bbsengine.databaseconnect(args)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  rec = cur.fetchone()
  cur.close()
  ttyio.echo("debug: rec=%r" % (rec), level="debug")
  if rec is None:
    return None

  item = builditemrecord(args, rec)
  return item

def getitem(args, itemid:str) -> dict:
  dbh = bbsengine.databaseconnect(args)
  sql = "select id from agora.item where asin=%s::text or imdbid=%s::text"
  dat = [itemid, itemid]
  if type(itemid) == int:
    sql+=" or id=%s"
    dat+= [itemid]

  dbh = bbsengine.databaseconnect(args)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  if cur.rowcount == 0:
    return {}

  rec = cur.fetchone()
  item = builditemrecord(args, rec)
  return item

def updateitem(args, nodeid:int, item:dict):
  currentmemberid = bbsengine.getcurrentmemberid()

  if "parentid" in item:
    parentid = item["parentid"]
    del(item["parentid"])
  else:
    parentid = None

  if "sigs" in item:
    sigs = item["sigs"]
    sigs = [s for s in sigs if s] # adds to result when s is not none
    del(item["sigs"])

  node = {}
  node["parentid"] = parentid
  node["title"] = item["title"]
  node["dateupdated"] = "now()"
  node["updatedbyid"] = currentmemberid

  attributes = {}
  attributes["asin"] = item["asin"]
  attributes["affiliatelink"] = item["affiliatelink"]
  attributes["checks"] = item["checks"]
  attributes["title"] = item["title"]
  attributes["imdbid"] = item["imdbid"]

  dbh = bbsengine.databaseconnect(args)
  bbsengine.updatenode(dbh, args, nodeid, node)
  bbsengine.updatenodeattributes(dbh, args, nodeid, attributes, reset=True)
  bbsengine.updatenodesigs(dbh, args, nodeid, sigs)

  return

def insertitem(args, item:dict, mogrify=False):
  currentmemberid = bbsengine.getcurrentmemberid(args)
  
  sigs = item["sigs"] if "sigs" in item else ["top.agora"]
  sigs = [s for s in sigs if s]

  if "parentid" in item:
    parentid = item["parentid"]
    del(item["parentid"])
  else:
    parentid = None

  item["storeid"] = STOREID
  item = filteritemattributes(item)

  node = {}
  node["parentid"] = parentid
  node["datecreated"] = "now()"
  node["createdbyid"] = currentmemberid
  node["attributes"] = item
  node["prg"] = "agora.item"

  dbh = bbsengine.databaseconnect(args)

  try:
    nodeid = bbsengine.insertnode(dbh, args, node, mogrify=mogrify)
  except Exception as e:
    ttyio.echo("item: %s" % (e), level="error")
    dbh.rollback()
    return None

  bbsengine.updatenodesigs(dbh, args, nodeid, sigs)
  return nodeid

def insertcomment(args, comment):
  currentmemberid = bbsengine.getcurrentmemberid(args)
  
  if "parentid" in comment:
    parentid = comment["parentid"]
    del(comment["parentid"])
  else:
    parentid = None

  node = {}
  node["parentid"] = parentid
  node["datecreated"] = "now()"
  node["createdbyid"] = currentmemberid
  node["attributes"] = comment
  node["prg"] = "agora.comment"

  dbh = bbsengine.databaseconnect(args)

  try:
    nodeid = bbsengine.insertnode(dbh, args, node, mogrify=True)
  except Exception as e:
    ttyio.echo("comment: %s" % (e), level="error")
    dbh.rollback()
    return None

  return nodeid

def queryomdb(args, imdbid):
  params = {}
  params["type"] = "movie"
  params["plot"] = "full"
  params["r"] = "json"
  params["apikey"] = OMDBAPIKEY
  params["i"] = imdbid

  url = "%s?%s" % (OMDBAPIURL, urllib.parse.urlencode(params))
  if args.debug is True:
    ttyio.echo("url=%r" % (url), level="debug")
  r = requests.get(url)
  ttyio.echo("r=%r" % (r), level="debug")
  omdb = json.loads(r.content)
  if args.debug is True:
    ttyio.echo("omdb=%r" % (omdb), level="debug")
  return omdb
