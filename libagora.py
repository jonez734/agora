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
  item["id"] = rec["id"]
  item["createdbyid"] = rec["createdbyid"]
  item["datecreated"] = rec["datecreated"]
  item["updatedbyid"] = rec["modifiedbyid"]
  item["dateupdated"] = rec["datemodified"]
  item["title"] = rec["title"]
  item["affiliatelink"] = rec["affiliatelink"]
  item["checks"] = rec["checks"]

  item["sigs"] = rec["sigs"]
  return item
