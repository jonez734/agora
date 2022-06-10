all:

clean:
	-rm *~
	-$(MAKE) -C css clean
	-$(MAKE) -C tmpl clean
	-$(MAKE) -C art clean

install:
	mkdir -p $(DOCROOT)skin/tmpl/
	mkdir -p $(DOCROOT)skin/scss/
	mkdir -p $(DOCROOT)skin/art/
	mkdir -p $(DOCROOT)skin/css/
	$(MAKE) -C art install
	$(MAKE) -C scss install # agora.scss is local, amznitem.scss is global
	$(MAKE) -C tmpl install
	$(MAKE) -C ttf install
	
	# $(MAKE) -C art install
