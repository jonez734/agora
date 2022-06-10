scssfiles := $(wildcard *.scss)
cssfiles := $(scssfiles:.scss=.css)

SCSS = sass --sourcemap=none --stop-on-error --trace --style expanded

all:

.scss.css:
	$(SCSS) $< $@

install: 
	$(SCSS) --update --watch .:$(DOCROOT)skin/css/

clean:
	-rm *~ *.css *.css.map

.SUFFIXES: .scss .css
