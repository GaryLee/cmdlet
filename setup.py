#!python

from distutils.core import setup

version = '0.2'
stage = '-alpha'

setup(
  name = 'cmdlet',
  packages = ['cmdlet'],
  version = version,
  description = 'Cmdlet provides pipe-like mechanism to cascade functions and generators.',
  author = 'Gary Lee',
  author_email = 'garywlee@gmail.com',
  url = 'https://github.com/GaryLee/cmdlet', 
  download_url = 'https://github.com/GaryLee/cmdlet/tarball/v%s%s' % (version, stage),
  keywords = ['pipe', 'generator', 'iterator'],
  classifiers = [],
)