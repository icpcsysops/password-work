
#
# test for genpwfiles
#

IDIR=../../..

doc:
	@echo t - run test

t: genpwfiles

	./genpwfiles final

genpwfiles:
# TODO - run install to setup files in place of these

	cp -r -p $(IDIR)/genpwfiles .
	cp -r -p $(IDIR)/*py .

	cp -r -p $(IDIR)/*yaml .
	cp -r -p $(IDIR)/templates .

