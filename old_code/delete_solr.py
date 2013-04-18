#!/usr/bin/python

from rodan import settings
import solr

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        print "Usage: %s -d" % sys.argv[0]
    if len(sys.argv) == 2 and sys.argv[1] == "-d":
        s = solr.SolrConnection(settings.SOLR_URL)
        s.delete_query("*:*")
        s.commit()
