from setuptools import setup

setup(
  name='sepa_generator',
  packages=['sepa_generator'],
  version='0.1.2',
  description='Simple Python library for creating SEPA Credit Transfer XML documents',
  author='Boris Savic',
  author_email='boris70@gmail.com',
  url='https://github.com/boris-savic/python_sepa',
  download_url='https://github.com/boris-savic/python_sepa/tarball/0.1.2',
  keywords=['python sepa_generator generator', 'SEPA', 'SEPA Credit Transfer', 'SEPACreditTransfer'],
  classifiers=[],
  install_requires=[
        'lxml>=3.8.0',
        'pytz>=2017.2',
    ]
)