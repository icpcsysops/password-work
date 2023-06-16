import argparse
import datetime
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

    def __init__(self, name: str, start_time: str):
        self.name = name
        self.start_time = start_time


class CcsConfig(object):
    """Object representing the CCS data from the configuration"""

    name: typing.Optional[str]
    link: typing.Optional[str]

    def __init__(self, name: typing.Optional[str] = None, link: typing.Optional[str] = None):
        self.name = name
        self.link = link


class AccountTypesConfig(object):
    """Object representing the account types from the configuration"""

    linux: None
    ccs: CcsConfig

    def __init__(self, linux: None, ccs: dict):
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
    additional_account_files: typing.Optional[typing.Sequence[str]]

    def __init__(self, contests_folder: str, footer: typing.Optional[str] = None, account_types: dict = None,
                 generate_accounts_tsv: typing.Optional[bool] = None, ip_prefix: typing.Optional[bool] = None,
                 page_size: str = None, additional_account_files: typing.Optional[typing.Sequence[str]] = None):
        self.contests_folder = contests_folder
        self.footer = footer
        if account_types:
            self.account_types = AccountTypesConfig(**account_types)
        self.generate_accounts_tsv = generate_accounts_tsv
        self.ip_prefix = ip_prefix
        self.page_size = page_size
        self.additional_account_files = additional_account_files


class CdsConfig(object):
    """Object representing the CDS data from the configuration"""

    config: str
    servers_folder: typing.Optional[str]
    page_size: str

    def __init__(self, config: str, servers_folder: typing.Optional[str] = None, page_size: str = None):
        self.config = config
        self.servers_folder = servers_folder
        self.page_size = page_size


class ChallengeConfig(object):
    """Object representing the challenge data from the configuration"""

    title: str
    banner: typing.Optional[str]
    account_types: AccountTypesConfig
    footer: typing.Optional[str]
    generate_accounts_tsv: typing.Optional[bool]
    ip_prefix: typing.Optional[bool]
    page_size: str

    def __init__(self, title: str, banner: typing.Optional[str] = None, account_types: dict = None,
                 footer: typing.Optional[str] = None, generate_accounts_tsv: typing.Optional[bool] = None,
                 ip_prefix: typing.Optional[bool] = None, page_size: str = None):
        self.title = title
        self.banner = banner
        self.account_types = AccountTypesConfig(**account_types)
        self.footer = footer
        self.generate_accounts_tsv = generate_accounts_tsv
        self.ip_prefix = ip_prefix
        self.page_size = page_size


class ContestConfig(object):
    """Object representing the contest data from the configuration"""

    name: str
    footer: typing.Optional[str]
    generate_accounts_tsv: typing.Optional[bool]
    ip_prefix: typing.Optional[bool]
    page_size: str
    additional_account_files: typing.Optional[typing.Sequence[str]]
    account_types: AccountTypesConfig = None
    config: ContestObject
    uses_config_folder: bool

    def __init__(self, name: str = None, footer: typing.Optional[str] = None,
                 generate_accounts_tsv: typing.Optional[bool] = None, ip_prefix: typing.Optional[bool] = None,
                 page_size: str = None, additional_account_files: typing.Optional[typing.Sequence[str]] = None,
                 account_types: dict = None):
        self.name = name
        self.footer = footer
        self.generate_accounts_tsv = generate_accounts_tsv
        self.ip_prefix = ip_prefix
        self.page_size = page_size
        self.additional_account_files = additional_account_files
        if account_types:
            self.account_types = AccountTypesConfig(**account_types)

    def load_contest_config(self, filename: str, start_time_property: str):
        contest_yaml = get_yaml_file_contests(filename)
        self.config = ContestObject(name=contest_yaml['name'], start_time=contest_yaml[start_time_property])


class Config(object):
    global_config: GlobalSettings
    cds: typing.Optional[CdsConfig] = None
    challenge: typing.Optional[ChallengeConfig] = None
    contests: typing.Sequence[ContestConfig] = []

    def __init__(self, global_settings: dict, cds: typing.Optional[dict] = None,
                 challenge: typing.Optional[dict] = None, contests: typing.Sequence[dict] = None):
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

        if not self.challenge.page_size and not self.global_config.page_size:
            print('Page size missing for Challenge')


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


def generate_password() -> str:
    """Generate a random password using the xkcdpass library with 4 words"""

    wordfile = xkcdpass.xkcd_password.locate_wordfile()
    password_words = xkcdpass.xkcd_password.generate_wordlist(wordfile=wordfile, min_length=4, max_length=6)
    return xkcdpass.xkcd_password.generate_xkcdpassword(password_words, delimiter='-', numwords=3)


def get_yaml_file_contests(file: str) -> dict:
    """Read the given YAML (or JSON) file and return it's content"""

    if not os.path.isfile(file):
        print(f'File {file} not found')
        exit(1)

    with open(file, 'r') as yaml_file:
        return yaml.safe_load(yaml_file)


def today_formatted() -> str:
    """Format today's date"""

    return datetime.date.today().strftime('%A %d %B %Y')


def write_yaml_file(file: str, content: dict) -> None:
    """Write the given content as YAML to the provided file"""

    with open(file, 'w') as yaml_file:
        yaml.dump(content, yaml_file)


def generate_template_to_pdf(template_file: str, content: dict, output_file: str,
                             page_size: str, orientation: str = 'Portrait') -> None:
    """Write the given content using the given template to the output file as PDF"""

    template_loader = jinja2.FileSystemLoader(searchpath=f'{os.path.dirname(__file__)}/templates')
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template_file)
    output_html = template.render(content)

    options = {
        'page-size': page_size,
        'orientation': orientation,
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None
    }
    pdfkit.from_string(output_html, output_file, options=options)
