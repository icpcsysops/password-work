#
#
# makefile - to generate passwords and password PDF sheets
#
# MUST run install.sh to install reqired modules
#
# ------------------------------------------------------------
# TODO - update template with URL Challenge URL: https://challenge.nac.icpc.global
#  note NAC23 and challange URLs are different
# TODO - add bug?  for two urls for CCS?
#
# fyi/ref Online judge: https://judge.nac.icpc.global
# ------------------------------------------------------------

CONTESTS=systest0 systest1 systest2 dress nac23real systest2-backup dress-backup nac23real-backup

CHALLENGE_CONTEST_FULL_TITLE=2023 NAC Challenge

FOOTER='2023 North America Championship'

CCS_LINK=https://challenge.nac.icpc.global

# input teams.json file 
# TEAMS_JSON_FILE=../contests/nac23/teams.json
# ../contests/nac23real/teams.json
TEAMS_JSON_FILE=../contests/nac23real/teams.json

# input non-team participants for challenge
# CHALLENGE_PARTICIPANTS_JSON_FILE=icpc-challenge/icpc-challenge-participants.json
# ../contests/nac23challenge/icpc-challenge-participants.json
CHALLENGE_PARTICIPANTS_JSON_FILE=../contests/nac23challenge/icpc-challenge-participants.json

# input team participants for challenge
# for nac23 for challenge - no password sheets - coaches auto register
# CHALLENGE_COACHES_JSON_FILE=icpc-challenge/icpc-challenge-coaches.json
# ../contests/nac23challenge/icpc-challenge-coaches.json
CHALLENGE_COACHES_JSON_FILE=../contests/nac23challenge/icpc-challenge-coaches.json

# input banner for NAC password sheet
# BANNER=../contests/nac23real/banner-1920x409.png
BANNER=../contests/nac23real/config/banner.jpg

# input banner for password sheet - Challenge
# NAC23_CHALLENGE_BANNER=../contests/nac23challenge/banner.jpg
NAC23_CHALLENGE_BANNER=../images/2023_ICPC_NAC-NAPC_logo_horizontal_revisedMay23.png

# -- 


GEN_CCS_FLAGS=--master-file \
	--ccs-name DOMjudge \
	--banner-file ${BANNER} \
	--footer-text ${FOOTER} \
	--generate-accounts-tsv \
	${TEAMS_JSON_FILE}

# set COPY_ACCOUNTS to true to copy into CONTEST/config
COPY_ACCOUNTS=true

# ------------------------------------------------------------
doc:
	@echo cds - generate CDS passwords and PDFs
	@echo 
	@echo nac23real - generate CCS credentials for NAC 23 
	@echo dress - generate CCS credentials for dress rehearsal
	@echo icpc-challenge - generate CCS credentials 
	@echo systest0 - generate CCS credentials for systest0 and staff accounts
	@echo systest1 systest2 dress nac23real - generate CCS credentials for those
	@echo systest2-backup dress-backup nac23real-backup - generate second set of CCS credentials 
	@echo 
	@echo check - check for data files
	@echo "ycheck - check for other accounts files (yaml)"
	@echo hcheck - check for html templates
	@echo 

# ------------------------------------------------------------
# check for required input files 

check: ${TEAMS_JSON_FILE} ${BANNER} ${NAC23_CHALLENGE_BANNER} ${CHALLENGE_PARTICIPANTS_JSON_FILE} ${CHALLENGE_COACHES_JSON_FILE}

	@echo PASSES - input data files found

# check for other accounts/titles, cds and judge/sysops (other-accounts.yaml)
ycheck: cds-config.yaml other-accounts.yaml
	@echo "PASSES - other accounts (yaml) files found"

# check for input html templates
hcheck: ccs-master-template.html ccs-sheets-template.html cds-master-template.html cds-sheets-template.html \
icpc-challenge-coaches-master-template.html icpc-challenge-coaches-template.html icpc-challenge-master-template.html
	@echo PASSEs - template html files found

# ------------------------------------------------------------

cds:
	python3 generate-cds-passwords \
		--master-file cds/CDS_Master_Password.pdf \
		--footer-text "2023 North America Championship" \
		--banner-file ${BANNER} \
		cds-config.yaml \
		cds \
		cds/CDSPasswords.pdf

# ------------------------------------------------------------

# Staff Accounts
systest0: GEN_CCS_FLAGS += --others-file other-accounts.yaml
systest2: GEN_CCS_FLAGS += --others-file other-accounts.yaml
dress: GEN_CCS_FLAGS += --others-file other-accounts.yaml
nac23real: GEN_CCS_FLAGS += --others-file other-accounts.yaml

# Set the titles for the various contests.
systest0: TITLE = 'SYSTEST 0'
systest1: TITLE = 'SYSTEST 1'
systest2: TITLE = 'SYSTEST 2'
dress: TITLE = 'Dress Rehearsal'
# no - use icpc-challgeng instead ; challenge: TITLE = 'ICPC Challenge powered by NSA'
nac23real: TITLE = '2023 North America Championship'
systest2-backup: TITLE = 'TEST 2 &mdash; Backup'
dress-backup: TITLE = 'Dress Rehearsal &mdash; Backup'
nac23real-backup: TITLE = '2023 North American Championships &mdash; Backup'

# Do not copy accounts.tsv for the backup credentials.
%-backup: COPY_ACCOUNTS = false

$(CONTESTS):
	python3 generate-ccs-unix-passwords \
		${GEN_CCS_FLAGS} \
		--title-text ${TITLE} \
		$@ $@
	if [ $(COPY_ACCOUNTS) = true ]; then \
		cp $@/$@.accounts.tsv ../contests/$@/config/accounts.tsv; \
	fi

icpc-challenge:
	python3 generate-icpc-challenge-teams \
		--master-file \
		--banner-file ${NAC23_CHALLENGE_BANNER} \
		--ccs-link ${CCS_LINK} \
		--footer-text ${FOOTER} \
		--title-text '${CHALLENGE_CONTEST_FULL_TITLE}' \
		${TEAMS_JSON_FILE} \
		${CHALLENGE_PARTICIPANTS_JSON_FILE} \
		icpc-challenge

	python3 generate-icpc-challenge-coaches \
		--master-file \
		--banner-file ${NAC23_CHALLENGE_BANNER} \
		--ccs-link ${CCS_LINK} \
		--footer-text ${FOOTER} \
		--title-text '${CHALLENGE_CONTEST_FULL_TITLE}' \
		${TEAMS_JSON_FILE} \
		${CHALLENGE_COACHES_JSON_FILE} \
		icpc-challenge

	python3 merge-accounts-tsv-files \
		icpc-challenge/teams.accounts.tsv \
		icpc-challenge/coaches.accounts.tsv \
		icpc-challenge

	if [ $(COPY_ACCOUNTS) = true ]; then \
		cp $@/combined.accounts.tsv ../contests/$@/config/accounts.tsv; \
	fi

.PHONY: doc cds $(CONTESTS) icpc-challenge

# ------------------------------------------------------------
# $Log: makefile,v $
#
# eof $Id: makefile,v 1.4 2022/10/11 04:03:57 laned Exp $
