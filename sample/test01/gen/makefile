
#
# makefile - setup and run test for genpwfiles
#

IDIR=../../..

doc:
	@echo t - run test
	@echo genpwfiles - copy scripts and other files for test
	@echo cpcfg - overwrite config.yaml with config.yaml.example 

t: genpwfiles
	./genpwfiles finals

cpcfg:
	cp -f -p $(IDIR)/config.yaml.example config.yaml

genpwfiles:
# TODO - run install to setup files in place of these

	cp -f  -p $(IDIR)/genpwfiles .
	chmod +x genpwfiles 

	cp  -p $(IDIR)/*py .

	cp  -p $(IDIR)/*yaml* .
	cp  -p config.yaml.example config.yaml

	cp -r -p $(IDIR)/templates .

# eof makfile
