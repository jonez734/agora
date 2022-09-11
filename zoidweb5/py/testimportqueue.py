#!/usr/bin/env python

import ttyio5 as ttyio
import bbsengine5 as bbsengine

def main():
    fp = open("queue.txt")
    done = False
    while not done:
        buf = fp.readline()
        if buf == "":
            done = True
            break
        buf = buf.strip()
        i = buf.find("#")
        if i >= 0:
            buf = buf[:i]
        if buf == "":
            continue
        fields = buf.split()
        fields = [f for f in fields if f != ""]
        if len(fields) < 5:
            ttyio.echo("syntax error, incorrect number of fields")
            return
        date = fields[0]
        shortlink = fields[1]
        asin = fields[2]
        imdb = fields[3]
        watchmethod = fields[4]
        title = " ".join(fields[5:])
        
        ttyio.echo("title=%r" % (title), level="debug")
        ttyio.echo("buf=%r" % (buf), level="debug")
        ttyio.echo("buf.split=%r" % (buf.split()), level="debug")
if __name__ == "__main__":
    main()
