import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

with open('README.md') as f:
    description = f.read()

setup(name='WebShack',
      version='0.0.1',
      description='Web Component/Polymer distribution system',
      author='Alistair Lynn',
      author_email='arplynn@gmail.com',
      license="MIT",
      long_description=description,
      url='https://github.com/prophile/webshack',
      entry_points = {
          'webshack.run': [
              'webshack = webshack.cli:main'
          ]
      },
      include_package_data=True,
      zip_safe=True,
      packages=find_packages())

