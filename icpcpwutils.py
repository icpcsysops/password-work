import argparse
import csv
import datetime
import shutil

import jinja2
import os.path
import pdfkit
import questionary
import typing
import xkcdpass.xkcd_password
import yaml


class ContestObject(object):
    """Object representing a contest"""

    name: str
    start_time: str

    def __init__(self, name: str, start_time: str) -> None:
        self.name = name
        self.start_time = start_time


class CcsConfig(object):
    """Object representing the CCS data from the configuration"""

    name: typing.Optional[str]
    link: typing.Optional[str]

    def __init__(self, name: typing.Optional[str] = None, link: typing.Optional[str] = None) -> None:
        self.name = name
        self.link = link


class AccountTypesConfig(object):
    """Object representing the account types from the configuration"""

    linux: bool = False
    ccs: CcsConfig

    def __init__(self, linux: typing.Optional[bool], ccs: dict) -> None:
        if linux:
            self.linux = linux
        self.ccs = CcsConfig(**ccs)


class GlobalSettings(object):
    """Object representing the global settings from the configuration"""

    contests_folder: str
    footer: typing.Optional[str]
    account_types: AccountTypesConfig = None
    generate_accounts_tsv: typing.Optional[bool]
    ip_prefix: typing.Optional[bool]
    page_size: str
    number_of_words_per_password: int
    additional_account_files: typing.Sequence[str] = []

    def __init__(self, contests_folder: str, footer: typing.Optional[str] = None, account_types: dict = None,
                 generate_accounts_tsv: typing.Optional[bool] = None, ip_prefix: typing.Optional[bool] = None,
                 page_size: str = None, number_of_words_per_password: int = None,
                 additional_account_files: typing.Optional[typing.Sequence[str]] = None) -> None:
        self.contests_folder = contests_folder
        self.footer = footer
        if account_types:
            self.account_types = AccountTypesConfig(**account_types)
        self.generate_accounts_tsv = generate_accounts_tsv
        self.ip_prefix = ip_prefix
        self.page_size = page_size
        self.number_of_words_per_password = number_of_words_per_password
        if additional_account_files:
            self.additional_account_files = additional_account_files


class CdsConfig(object):
    """Object representing the CDS data from the configuration"""

    config: str
    servers_folder: typing.Optional[str]
    banner: typing.Optional[str]
    footer: typing.Optional[str]
    page_size: str
    number_of_words_per_password: int

    def __init__(self, config: str, servers_folder: typing.Optional[str] = None, banner: typing.Optional[str] = None,
                 footer: typing.Optional[str] = None, page_size: str = None,
                 number_of_words_per_password: int = None) -> None:
        self.config = config
        self.servers_folder = servers_folder
        self.banner = banner
        self.footer = footer
        self.page_size = page_size
        self.number_of_words_per_password = number_of_words_per_password


class ChallengeAccountFileConfig(object):
    """Object representing account file configuration for the Challenge"""

    teams_file: str
    organizations_file: typing.Optional[str]
    add_organization: bool = False

    def __init__(self, teams_file: str, organizations_file: typing.Optional[str] = None,
                 add_organization: typing.Optional[bool] = None) -> None:
        self.teams_file = teams_file
        self.organizations_file = organizations_file
        if self.add_organization:
            self.add_organization = add_organization


class ChallengeConfig(object):
    """Object representing the challenge data from the configuration"""

    title: str
    banner: typing.Optional[str]
    account_types: AccountTypesConfig
    footer: typing.Optional[str]
    generate_accounts_tsv: typing.Optional[bool]
    ip_prefix: typing.Optional[bool]
    page_size: str
    number_of_words_per_password: int
    account_files: typing.Sequence[ChallengeAccountFileConfig]

    def __init__(self, title: str, banner: typing.Optional[str] = None, account_types: dict = None,
                 footer: typing.Optional[str] = None, generate_accounts_tsv: typing.Optional[bool] = None,
                 ip_prefix: typing.Optional[bool] = None, page_size: str = None,
                 number_of_words_per_password: int = None, account_files: typing.Sequence[dict] = None) -> None:
        self.title = title
        self.banner = banner
        self.account_types = AccountTypesConfig(**account_types)
        self.footer = footer
        self.generate_accounts_tsv = generate_accounts_tsv
        self.ip_prefix = ip_prefix
        self.page_size = page_size
        self.number_of_words_per_password = number_of_words_per_password
        if account_files:
            self.account_files = [ChallengeAccountFileConfig(**account_file) for account_file in account_files]


class ContestConfig(object):
    """Object representing the contest data from the configuration"""

    name: str
    footer: typing.Optional[str]
    generate_accounts_tsv: typing.Optional[bool]
    ip_prefix: typing.Optional[bool]
    page_size: str
    number_of_words_per_password: int
    additional_account_files: typing.Optional[typing.Sequence[str]]
    account_types: AccountTypesConfig = None
    config: ContestObject
    uses_config_folder: bool

    def __init__(self, name: str = None, footer: typing.Optional[str] = None,
                 generate_accounts_tsv: typing.Optional[bool] = None, ip_prefix: typing.Optional[bool] = None,
                 page_size: str = None, number_of_words_per_password: int = None,
                 additional_account_files: typing.Optional[typing.Sequence[str]] = None,
                 account_types: dict = None) -> None:
        self.name = name
        self.footer = footer
        self.generate_accounts_tsv = generate_accounts_tsv
        self.ip_prefix = ip_prefix
        self.page_size = page_size
        self.number_of_words_per_password = number_of_words_per_password
        self.additional_account_files = additional_account_files
        if account_types:
            self.account_types = AccountTypesConfig(**account_types)

    def load_contest_config(self, filename: str, start_time_property: str):
        contest_yaml = get_yaml_file_contests(filename)
        self.config = ContestObject(name=contest_yaml['name'], start_time=contest_yaml[start_time_property])

    def contest_option_or_global(self, name: str, global_settings: GlobalSettings, default: any = None) -> any:
        if getattr(self, name) is not None:
            return getattr(self, name)

        if getattr(global_settings, name) is not None:
            return getattr(global_settings, name)

        return default


class Config(object):
    global_config: GlobalSettings
    cds: typing.Optional[CdsConfig] = None
    challenge: typing.Optional[ChallengeConfig] = None
    contests: typing.Sequence[ContestConfig] = []

    def __init__(self, global_settings: dict, cds: typing.Optional[dict] = None,
                 challenge: typing.Optional[dict] = None, contests: typing.Sequence[dict] = None) -> None:
        self.global_config = GlobalSettings(**global_settings)
        if cds:
            self.cds = CdsConfig(**cds)
        if challenge:
            self.challenge = ChallengeConfig(**challenge)
        if contests:
            self.contests = [ContestConfig(**c) for c in contests]

        self._validate_global()

        for c in self.contests:
            new_file = f'{self.global_config.contests_folder}/{c.name}/contest.yaml'
            old_file = f'{self.global_config.contests_folder}/{c.name}/config/contest.yaml'
            if os.path.isfile(new_file):
                c.load_contest_config(new_file, 'start_time')
                c.uses_config_folder = False
            elif os.path.isfile(old_file):
                c.load_contest_config(old_file, 'start-time')
                c.uses_config_folder = True
            else:
                print(f'Neither contest.yaml nor config/contest.yaml found for contest {c.name}')
                exit(1)

    def _validate_global(self) -> None:
        if not self.global_config:
            print('Global config settings missing')
            exit(1)

        if not self.global_config.contests_folder:
            print('Contest folder config missing')
            exit(1)

        if not os.path.isdir(self.global_config.contests_folder):
            print(f'Contest folder {self.global_config.contests_folder} does not exist')
            exit(1)

        if self.contests:
            for i, c in enumerate(self.contests):
                if not c.name:
                    print(f'Contest name missing for contest with index {i}')
                    exit(1)

    def validate_contest(self, contest: ContestConfig) -> None:
        if not contest.account_types and not self.global_config.account_types:
            print(f'Account types missing for contest {contest.name}')
            exit(1)

        if not contest.page_size and not self.global_config.page_size:
            print(f'Page size missing for contest {contest.name}')
            exit(1)

        if not contest.number_of_words_per_password and not self.global_config.number_of_words_per_password:
            print(f'Number pf words per password missing for contest {contest.name}')
            exit(1)

    def validate_cds(self) -> None:
        if not self.cds:
            print('CDS configuration missing')
            exit(1)

        if not self.cds.config:
            print('CDS configuration missing')
            exit(1)

        if not os.path.isfile(self.cds.config):
            print(f'CDS config file {self.cds.config} does not exist')
            exit(1)

        if self.cds.servers_folder and not os.path.isdir(self.cds.servers_folder):
            print(f'CDS server folder {self.cds.servers_folder} does not exist')
            exit(1)

        if not self.cds.page_size and not self.global_config.page_size:
            print('Page size missing for CDS')
            exit(1)

        if not self.cds.number_of_words_per_password and not self.global_config.number_of_words_per_password:
            print('Number of words per password missing for CDS')
            exit(1)

    def validate_challenge(self) -> None:
        if not self.challenge:
            print('Challenge configuration missing')
            exit(1)

        if not self.challenge.title:
            print('Challenge title missing')
            exit(1)

        if not self.challenge.account_types:
            print('Account types missing for Challenge')
            exit(1)

        if not self.challenge.account_files:
            print('Account files missing for Challenge')
            exit(1)

        if not self.challenge.page_size and not self.global_config.page_size:
            print('Page size missing for Challenge')
            exit(1)

        if not self.challenge.number_of_words_per_password and not self.global_config.number_of_words_per_password:
            print('Number of words per password missing for Challenge')
            exit(1)


class Account(object):
    id: str
    name: str
    password: typing.Optional[str] = None
    type: str
    username: str
    team_id: typing.Optional[str]
    ip: typing.Optional[str]

    def __init__(self, id: str, name: str, type: str, username: str, team_id: typing.Optional[str] = None,
                 ip: typing.Optional[str] = None, password: typing.Optional[str] = None) -> None:
        self.id = id
        self.name = name
        self.password = password
        self.type = type
        self.username = username
        if team_id is not None:
            self.team_id = team_id
        if ip is not None:
            self.ip = ip

    def generate_password(self, num_words: int) -> None:
        """Generate a random password using the xkcdpass library with the provider number of words"""

        wordfile = xkcdpass.xkcd_password.locate_wordfile()
        password_words = xkcdpass.xkcd_password.generate_wordlist(wordfile=wordfile, min_length=4, max_length=6)
        self.password = xkcdpass.xkcd_password.generate_xkcdpassword(password_words, delimiter='-', numwords=num_words)


def load_config() -> Config:
    config_data = get_yaml_file_contests('config.yaml')
    return Config(**config_data)


def ask_or_argument(args: argparse.Namespace, argument: str, title: str, choices: typing.Sequence[questionary.Choice],
                    invalid_message: str) -> str:
    """Ask for a question or use the argument supplied"""

    if argument in args and getattr(args, argument):
        choice = getattr(args, argument)
        allowed_choices = [c.value for c in choices]
        if choice not in allowed_choices:
            print(f'{invalid_message} {choice}')
            print('Allowed options:')
            for c in choices:
                print(f'* {c.value} -- {c.title}')
            exit(1)
    else:
        choice = questionary.select(title, choices).ask()

    return choice


def load_accounts(file: str, number_of_words_per_password: int, ip_prefix: typing.Optional[str] = None,
                  accounts: typing.Optional[typing.Dict[str, Account]] = None) -> typing.Dict[str, Account]:
    if not os.path.isfile(file):
        return {}

    if accounts is None:
        accounts = {}

    accounts_data = get_yaml_file_contests(file)
    for account in accounts_data:
        id = account.get('id', account['username'])
        username = account['username']
        ip = None
        if account['type'] == 'team' and id.isdigit() and ip_prefix is not None:
            ip = f'{ip_prefix}.{id}'
        if username in accounts:
            if ip:
                accounts[username].ip = ip
        else:
            account = Account(id, account['name'], account['type'], account['username'], None, ip,
                              account.get('password', None))
            if not account.password:
                account.generate_password(number_of_words_per_password)

            accounts[account.username] = account

    return accounts


def add_team_accounts(accounts: typing.Dict[str, Account], file: str, number_of_words_per_password: int,
                      ip_prefix: typing.Optional[str] = None) -> typing.Dict[str, Account]:
    team_data: typing.Sequence[dict] = get_yaml_file_contests(file)
    for team in team_data:
        team_id = team['id']
        username = f'team{team_id}'
        if username in accounts:
            accounts[username].team_id = team_id
        else:
            ip = None
            if ip_prefix is not None:
                ip = f'{ip_prefix}.{team_id}'
            account = Account(username, team.get('display_name', team['name']), 'team', username, team_id, ip)
            account.generate_password(number_of_words_per_password)
            accounts[username] = account

    return accounts


def get_yaml_file_contests(file: str):
    """Read the given YAML (or JSON) file and return it's content"""

    if not os.path.isfile(file):
        print(f'File {file} not found')
        exit(1)

    with open(file, 'r') as yaml_file:
        return yaml.safe_load(yaml_file)


def today_formatted() -> str:
    """Format today's date"""

    return datetime.date.today().strftime('%A %d %B %Y')


def write_yaml_file(file: str, content: typing.Union[dict, list]) -> None:
    """Write the given content as YAML to the provided file"""

    with open(file, 'w') as yaml_file:
        yaml.dump(content, yaml_file, sort_keys=False)


def generate_template_to_pdf(template_file: str, sheet_variables: dict, output_file: str,
                             page_size: str, orientation: str = 'Portrait') -> None:
    """Write the given content using the given template to the output file as PDF"""

    template_loader = jinja2.FileSystemLoader(searchpath=f'{os.path.dirname(__file__)}/templates')
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template_file)
    output_html = template.render(sheet_variables)

    options = {
        'page-size': page_size,
        'orientation': orientation,
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None
    }
    pdfkit.from_string(output_html, output_file, options=options)


def chunked(data: list, per_chunk: int) -> list:
    return [data[i:i + per_chunk] for i in range(0, len(data), per_chunk)]


def add_account_type_data(sheet_variables: typing.Dict[str, typing.Any],
                          account_types: AccountTypesConfig) -> typing.Dict[str, typing.Any]:
    if account_types.ccs and account_types.ccs.name:
        sheet_variables['ccs'] = account_types.ccs.name
    if account_types.ccs and account_types.ccs.link:
        sheet_variables['link'] = account_types.ccs.link
    if account_types.linux:
        sheet_variables['linux'] = True

    return sheet_variables


def write_accounts_yaml(output_folder: str, accounts: typing.Dict[str, Account]) -> None:
    output_file = f'{output_folder}/{output_folder}.accounts.yaml'
    write_yaml_file(output_file, [account.__dict__ for account in accounts.values()])

    print(f'Written accounts YAML to {output_file}')


def write_accounts_tsv(output_folder: str, accounts: typing.Dict[str, Account],
                       possible_contest_dirs: typing.Sequence[str] = None) -> None:
    output_file = f'{output_folder}/{output_folder}.accounts.tsv'
    with open(output_file, 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['accounts', 1])
        for account in accounts.values():
            writer.writerow([
                account.type,
                account.name,
                account.username,
                account.password
            ])

    print(f'Written accounts TSV to {output_file}')

    if possible_contest_dirs:
        for contest_dir in possible_contest_dirs:
            if os.path.isdir(contest_dir):
                contest_accounts_tsv = f'{contest_dir}/accounts.tsv'
                if os.path.exists(contest_accounts_tsv):
                    os.remove(contest_accounts_tsv)
                shutil.copy(output_file, contest_accounts_tsv)

                print(f'TSV copied to {contest_accounts_tsv}')
                break


def write_linux_accounts(output_folder: str, accounts: typing.Dict[str, Account]) -> None:
    output_file = f'{output_folder}/linux-accounts.yaml'
    unix_accounts = {'users': {account.username: account.password for account in accounts.values()}}
    write_yaml_file(output_file, unix_accounts)

    print(f'Written Linux accounts to {output_file}')


def write_password_sheets(template: str, output_file: str, accounts: typing.Dict[str, Account],
                          title: typing.Optional[str], footer: typing.Optional[str], banner: typing.Optional[str],
                          account_types: AccountTypesConfig, page_size: str) -> None:
    sheet_variables = {
        'accounts': [account for _, account in accounts.items()],
        'title': title,
        'footer': footer,
        'banner': os.path.abspath(banner),
        'page_size': page_size,
        'ccs': None,
        'link': None,
        'linux': False,
    }

    sheet_variables = add_account_type_data(sheet_variables, account_types)

    generate_template_to_pdf(template, sheet_variables, output_file, page_size)
    print(f'Written password sheets to {output_file}')


def write_master_file(template: str, output_file: str, accounts: typing.Dict[str, Account],
                      title: typing.Optional[str], footer: typing.Optional[str], banner: typing.Optional[str],
                      account_types: AccountTypesConfig, page_size: str) -> None:
    if page_size == 'A4':
        rows_per_page = 40
    else:
        rows_per_page = 41
    columns_per_page = 3
    per_page = rows_per_page * columns_per_page
    pages = [chunked(page, rows_per_page) for page in chunked(list(accounts.values()), per_page)]

    sheet_variables = {
        'pages': pages,
        'num_columns': columns_per_page,
        'date': today_formatted(),
        'title': title,
        'footer': footer,
        'page_size': page_size,
        'ccs': None,
        'link': None,
        'linux': False,
    }

    sheet_variables = add_account_type_data(sheet_variables, account_types)

    generate_template_to_pdf(template, sheet_variables, output_file, page_size, 'Landscape')
    print(f'Written master file to {output_file}')
