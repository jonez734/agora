import ttyio4 as ttyio
import bbsengine5 as bbsengine

def getamznitembyasin(dbh, args, asin):
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
  node = {}
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

  item["sigs"] = rec["sigs"]
  return item

def updateamznitem(dbh, args, nodeid:int, item:dict):
  currentmemberid = bbsengine.getcurrentmemberid()

  if "parentid" in item:
    parentid = item["parentid"]
    del(item["parentid"])
  else:
    parentid = None

  if "sigs" in item:
    sigs = item["sigs"]
    sigs = [s for s in sigs if s]
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
