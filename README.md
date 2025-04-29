# Scripts to generate passwords for ICPC contests

This directory contains all logic to generate passwords for ICPC contests.

## Requirements

These scripts require Python 3, as well as the following Python packages:

* `pyyaml`
* `jinja2`
* `pdfkit`
* `xkcdpass`

It also requires the `wkhtmltopdf` binary.

To install, run:

```bash
./install.sh
```

## Usage

This tool should be run from the folder where you want to store the generated passwords.
Normally this is a `passwork` folder in the contest specific repository.

First, you need to copy `config.yaml.example` and `cds-config.yaml.example` from this repository to the folder you want
to run the tool from.
Make sure to drop the `.example` postfix from the files after copying.

Modify both files to your needs. Both contain comments to get you started.

Now you can run this tool, by running:

```bash
[folder of this repo]/genpwfiles
```

from the folder with your two YAML files. It will then ask you what you want to do.
There are shorthands for all subcommands, use

```bash
[folder of this repo]/genpwfiles -h
```

to get more information about this.

**Note:** take care in running the `force` mode. This will get rid of any accounts/password that already existed, so
only run it if you really want this.

## Generated files

The following files are generated:

### accounts.yaml

This file follows the CCS spec format. More information can be
found [in the example](https://ccs-specs.icpc.io/draft/contest_package#accountsyaml) and
the [official specification](https://ccs-specs.icpc.io/draft/contest_api#accounts) on the CCS specs website.

### accounts.tsv

This is an older format still in use by some CCSes.
The format is described [here](https://ccs-specs.icpc.io/2020-03/ccs_system_requirements#accountstsv).

### linux-accounts.yaml

This file is a YAML file to create Linux accounts. The root key is `users` and below it there is a dictionary where keys
are usernames and values are the passwords of the users.

### *_master.pdf

These are the _master password sheets_, where all usernames and passwords are printed in one big table.
The templates in `templates/*-master.html` are used to generate these PDFs.

### *_sheets.pdf

These are the user _password sheets_, where one page is generated per created account.
These should be handed out to the end users.
The templates in `templates/*-sheets.html` are used to generate these PDFs.

## Attribution

Uses the [Twemoji](https://twemoji.twitter.com/) library and graphics for rendering Emoji.


Twemoji is Copyright 2020 Twitter, Inc and other contributors<br>
Code licensed under the MIT License: http://opensource.org/licenses/MIT <br>
Graphics licensed under CC-BY 4.0: https://creativecommons.org/licenses/by/4.0/
