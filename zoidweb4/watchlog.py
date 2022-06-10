import ttyio2 as ttyio
import bbsengine4 as bbsengine

# import psycopg2 # , psycopg2.extras
from psycopg2.extras import Json
from optparse import OptionParser, OptionGroup

def _edit(dbh, opts, comment):
    return comment

def add(dbh, opts):
    watchlog = {}
    newwatchlog = _edit(dbh, opts, watchlog)
    if (watchlog != newwatchlog):
        ttyio.echo("** record changed **", level="info")
        if ttyio.inputboolean("add watchlog?") is True:
            currentmemberid = bbsengine.getcurrentmemberid()

            node = {}
            node["datecreated"] = "now()"
            node["createdbyid"] = currentmemberid
            node["dateupdated"] = "now()"
            node["updatedbyid"] = currentmemberid
            try:
                watchlogid = bbsengine.insert(dbh, "agora.__node", newwatchlog, returnid=True, primarykey="id", mogrify=False)
                if opts.debug is True:
                    ttyio.echo("watchlogid=%r" % (watchlogid), level="debug")
            except Exception as e:
                dbh.rollback()
                raise e
            else:
                dbh.commit()
        else:
            ttyio.echo("new watchlog not added")
    
def main():
    parser = OptionParser(usage="usage: %prog [options] projectid")
#    parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_option("--debug", default=True, action="store_true", help="run %prog in debug mode")
#    parser.add_option("--limit", default=None, action="store", help="limit the number of records processed (%default)")
#    parser.add_option("--asin", default=None, action="store", help="query for a specific asin")

    databasegroup = OptionGroup(parser, "database options")

    databasegroup.add_option("--databasename", dest="databasename", action="store", default="zoidweb3", help="database name (%default)")
    databasegroup.add_option("--databasehost", dest="databasehost", action="store", default="localhost", help="database host (%default)")
    databasegroup.add_option("--databaseuser", dest="databaseuser", action="store", default=bbsengine.getcurrentmemberlogin(), help="database user (%default)")
    databasegroup.add_option("--databasepassword", dest="databasepassword", action="store", default=None, help="database password")
    databasegroup.add_option("--databaseport", dest="databaseport", action="store", default="5432", help="database port")
    parser.add_option_group(databasegroup)
    
    (opts, args) = parser.parse_args()
    
    dbh = bbsengine.databaseconnect(opts)
    cur = dbh.cursor()
    cur.close()
    
    dbh.commit()
    dbh.close()

if __name__ == "__main__":
    main()
