import ttyio5 as ttyio
import bbsengine5 as bbsengine

def buildamznitemrecord(args, rec):
  item = {}
  item["title"] = rec["title"]
  item["asin"] = rec["asin"]
  item["imdbid"] = rec["imdbid"]
  item["id"] = rec["id"]
  item["createdbyid"] = rec["createdbyid"]
  item["datecreated"] = rec["datecreated"]
  item["modifiedbyid"] = rec["modifiedbyid"]
  item["datemodified"] = rec["datemodified"]
  item["parentid"] = rec["parentid"]
  item["title"] = rec["title"]
  item["affiliatelink"] = rec["affiliatelink"]
  item["checks"] = rec["checks"]

  item["sigs"] = bbsengine.postgres_to_python_list(rec["sigs"])
  return item

def getamznitembynodeid(args, dbh, nodeid:int):
  sql = "select * from agora.amznitem where id=%s"
  dat = (nodeid)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  rec = cur.fetchone()
  if rec is None:
    return None
  return buildamznitemrecord(args, dbh)

def getamznitembyasin(args, dbh, asin:str):
  sql = "select * from agora.amznitem where attributes ->> 'asin'=%s"
  dat = (str(asin),)
  cur = dbh.cursor()
  cur.execute(sql, dat)
  rec = cur.fetchone()
  cur.close()
  ttyio.echo("debug: res=%r" % (res), level="debug")
  if rec is None:
    ttyio.echo("{f6}invalid id{f6}", level="error")
    return None

  item = buildamznitemrecord(args, rec)
  return item

def getamznitem(args, dbh, id:str):
  sql = "select id from agora.amznitem where asin=%s::text or imdbid=%s::text"
  dat = [id, id]
  if type(id) == int:
    sql+=" or id=%s"
    dat+= [id]

  cur = dbh.cursor()
  cur.execute(sql, dat)
  rec = cur.fetchone()
  item = buildamznitemrecord(args, rec)
  return item

def updateamznitem(args, dbh, nodeid:int, item:dict):
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

  bbsengine.updatenode(dbh, args, nodeid, node)
  bbsengine.updatenodeattributes(dbh, args, nodeid, attributes, reset=True)
  bbsengine.updatenodesigs(dbh, args, nodeid, sigs)

  return
