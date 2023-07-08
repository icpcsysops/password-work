
#
# makefile - setup and run test for genpwfiles
#

IDIR=../../..

doc:
	@echo t - run test on contest finals
	@echo dress - run test on contest dress

	@echo genpwfiles - copy scripts and other files for test
	@echo cpcfg - overwrite config.yaml with config.yaml.example 

# test with new contest.yaml location, finals/contest.yaml
t: genpwfiles
	./genpwfiles finals

# test with contest.yaml location, dress/config/contest.yaml
dress: genpwfiles
	./genpwfiles dress

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

# eof makefile
