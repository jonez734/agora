export HOST = merlin
export PROJECT = agora
export REPODIR = /srv/www/vhosts/projects.zoidtechnologies.com/files/$(PROJECT)/

export PROD = $(HOST):/srv/www/vhosts/$(PROJECT).zoidtechnologies.com/
export PRODDOCROOT = $(PROD)html/
export STAGEPROD = /srv/staging/$(PROJECT).zoidtechnologies.com/
export STAGEPRODDOCROOT = $(STAGEPROD)html/

export datestamp = $(shell date +%Y%m%d-%H%M)
export archivename = $(PROJECT)-$(datestamp)-$(USER)
export installfile = install --mode=0660

export RSYNC = rsync --chmod=Dg=rwxs,Fgu=rw,Fo=r --no-times --verbose \
	--archive --update --backup --recursive \
	--human-readable --checksum --rsh=ssh \
	--no-owner --no-group \
	--delete-after \
	--links \
	--exclude '.~lock*' \
	--exclude '*~'

all:

clean:
	-rm *~
	-$(MAKE) -C skin clean
	-$(MAKE) -C php clean
	-$(MAKE) -C smarty clean
	-$(MAKE) -C js clean
	-$(MAKE) -C sql clean
	-$(MAKE) -C py clean

prod:	export DOCROOT = $(STAGEPRODDOCROOT)
prod:	export STAGE = $(STAGEPROD)
prod:
	mkdir -p $(DOCROOT)
	mkdir -p $(STAGE)templates_c/

	$(MAKE) -C php install
	$(MAKE) -C skin install
	-$(MAKE) -C smarty install
	-$(MAKE) -C js install
	$(RSYNC) config-prod.php $(DOCROOT)config.php
	-$(RSYNC) htaccess-prod $(DOCROOT).htaccess
	#-$(RSYNC) htpasswd-prod $(STAGE).htpasswd
	$(RSYNC) $(STAGE) $(PROD)

.PHONY: prod
