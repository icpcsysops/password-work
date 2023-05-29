import datetime
import jinja2
import json
import os.path
import pdfkit
import xkcdpass.xkcd_password
import yaml

def generate_password():
    '''Generate a random password using the xkcdpass library with 4 words'''

    wordfile = xkcdpass.xkcd_password.locate_wordfile()
    password_words = xkcdpass.xkcd_password.generate_wordlist(wordfile=wordfile, min_length=4, max_length=6)
    return xkcdpass.xkcd_password.generate_xkcdpassword(password_words, delimiter='-', numwords=3)

def get_yaml_file_contests(file: str) -> dict:
    '''Read the given YAML file and return it's content'''

    if not os.path.isfile(file):
        raise RuntimeError(f'File {file} not found')

    with open(file, 'r') as yaml_file:
        return yaml.safe_load(yaml_file)

def get_json_file_contests(file: str) -> dict:
    '''Read the given JSON file and return it's content'''

    if not os.path.isfile(file):
        raise RuntimeError(f'File {file} not found')

    with open(file, 'r') as json_file:
        return json.load(json_file)

def today_formated():
    '''Format today's date'''

    return datetime.date.today().strftime('%A %d %B %Y')

def write_yaml_file(file: str, content: dict):
    '''Write the given content as YAML to the provided file'''

    with open(file, 'w') as yaml_file:
        yaml.dump(content, yaml_file)

def generate_template_to_pdf(template_file: str, content: dict, output_file: str, orientation: str = 'Portrait'):
    '''Write the given content using the given template to the output file as PDF'''

    template_loader = jinja2.FileSystemLoader(searchpath='./')
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template_file)
    output_html = template.render(content)

    options = {
        'page-size': 'A4',
        'orientation': orientation,
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None
    }
    pdfkit.from_string(output_html, output_file, options=options)
