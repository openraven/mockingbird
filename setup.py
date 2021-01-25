from os import path

from setuptools import setup, find_packages

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='mockingbird',
      version='1.0',
      description='Generate mock documents in various formats (CSV, DOCX, PDF, TXT, and more) that embed seed data and '
                  'can be used to test data classification software.',

      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://www.github.com/openraven/mockingbird',
      author='Open Raven Team',
      author_email='opensource@openraven.com',
      install_requires=['openpyxl==3.0.5',
                        'RandomWords==0.3.0',
                        'pyyaml==5.3.1',
                        'pyexcel-ods==0.6.0',
                        'python-docx==0.8.10',
                        'requests==2.25.0',
                        'reportlab==3.5.59',
                        'python-pptx==0.6.18',
                        'pandas==1.2.1',
                        'pandavro==1.6.0',
                        'python-pptx==0.6.18',
                        'pyspark==3.0.1'],
      license='apache',
      entry_points={'console_scripts': ['mockingbird_cli=mockingbird.__command_line:main']},
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3.8",
      ],
      )
