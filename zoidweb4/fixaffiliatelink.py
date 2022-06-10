import ttyio3 as ttyio
import bbsengine4 as bbsengine

def main():
    from optparse import OptionParser
    import pwd, os, sys
    global currentmemberid

    membermap = {"jam" : 1}

    loginid = pwd.getpwuid(os.geteuid())[0]
    if loginid in membermap:
        currentmemberid = membermap[loginid]
#        ttyio.echo("** currentmemberid=%r" % (currentmemberid))
    else:
        ttyio.echo("uhmm... you do not exist. go away.", level="error")
        sys.exit(-1)

    ttyio.echo("currentmemberid=%r" % (currentmemberid), level="debug")

    parser = OptionParser(usage="usage: %prog [options] projectid")
    parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_option("--debug", default=True, action="store_true", help="run %prog in debug mode")

    parser.add_option("--databasename", dest="databasename", action="store", default="zoidweb4", help="database name (%default)")
    parser.add_option("--databasehost", dest="databasehost", action="store", default="localhost", help="database host (%default)")
    parser.add_option("--databaseport", dest="databaseport", action="store", default="5432", help="database port (%default)")
    parser.add_option("--databaseuser", dest="databaseuser", action="store", default=bbsengine.getcurrentmemberlogin(), help="database user (%default)")
    parser.add_option("--databasepassword", dest="databasepassword", action="store", default=None, help="database password")

    (opts, args) = parser.parse_args()

    sql = "select id as nodeid, attributes from engine.__node where attributes ? 'asin' and attributes ? 'imdbid' and attributes ? 'url'"
    dbh = bbsengine.databaseconnect(opts)
    cur = dbh.cursor()
    cur.execute(sql)
#    if cur.rowcount == 0:
#        ttyio.echo("no amznitems w url attribute found.")
    res = cur.fetchall()
    print(res)
    for rec in res:
        nodeid = rec["nodeid"]
        attributes = rec["attributes"]
        if attributes["url"] != "":
            attributes["affiliatelink"] = attributes["url"]
        else:
            ttyio.echo("attributes.url is empty")
        
        del(attributes["url"])

        ttyio.echo("attributes=%r" % (attributes), level="debug")
        bbsengine.updatenodeattributes(dbh, opts, nodeid, attributes, reset=True)
    dbh.commit()
    cur.close()
    dbh.close()

if __name__ == "__main__":
    main()
    