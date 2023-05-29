# Scripts to generate passwords for ICPC contests

This directory contains all scripts to generate passwords for ICPC contests.

## Requirements

These scripts require Python 3, as well as the following Python packages:

* `xkcdpass`
* `pyyaml`
* `jinja2`
* `pdfkit`

It also requires the `wkhtmltopdf` binary.

To install, run:

```bash
./install.sh
```

## Available scripts

### CDS password generation

* Script filename: `generate-cds-passwords`
* Usage: `./generate-cds-passwords [-m master-pdf-filename-to-write-to] <cds-config.yaml> <cds-servers-directory>`

Will write `accounts.yaml` for each CDS configured in `<cds-config.yaml>` to a folder named after the CDS inside `<cds-servers-directory>`.
If the `-m` flag is with a file, will write a PDF file with all account information to that file.
