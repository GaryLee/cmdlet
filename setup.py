#!python

import os
from distutils.core import setup

description = 'Cmdlet provides pipe-like mechanism to cascade functions and generators.'
filepath = os.path.dirname(__file__)
readme_file = os.path.join(filepath, 'README.md')

if not os.path.exist(readme_file):
    long_description = description
else:
    try:
        import pypandoc
        long_description = pypandoc.convert(readme_file, 'rst')
    except(IOError, ImportError):
        long_description = open(readme_file).read()

def extract_version(filename):
    import re
    pattern = re.compile(r'''__version__\s*=\s*"(?P<ver>[0-9\.]+)".*''')
    with file(filename, 'r') as fd:
        for line in fd:
            match = pattern.match(line)
            if match:
                ver = match.groupdict()['ver']
                break
        else:
            raise Exception('ERROR: cannot find version string.')
    return ver

version = extract_version('cmdlet/__init__.py')
stage = ''

setup(
  name = 'cmdlet',
  packages = ['cmdlet'],
  version = version,
  description = description,
  long_description=long_description,
  author = 'Gary Lee',
  author_email = 'garywlee@gmail.com',
  url = 'https://github.com/GaryLee/cmdlet',
  download_url = 'https://github.com/GaryLee/cmdlet/tarball/v%s%s' % (version, stage),
  keywords = ['pipe', 'generator', 'iterator'],
  classifiers = [],
)
