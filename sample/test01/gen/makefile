
#
# test for genpwfiles
#

IDIR=../../..

doc:
	@echo t - run test
	@echo genpwfiles - copy scripts and other files for test
	@echo cpcfg - overwrite config.yaml with config.yaml.example 

t: genpwfiles

	./genpwfiles final

cpcfg:
	cp -f -p $(IDIR)/config.yaml.example config.yaml

genpwfiles:
# TODO - run install to setup files in place of these

	cp -r -p $(IDIR)/genpwfiles .
	cp -r -p $(IDIR)/*py .

	cp -r -p $(IDIR)/*yaml .
	cp -r -p $(IDIR)/templates .

