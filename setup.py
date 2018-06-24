from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='motorturbine',
      version='0.2.0',
      description='A ORM package for asyncio and motor',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/BFriedrichs/motorturbine',
      author='Björn Friedrichs',
      author_email='bjoern@friedrichs1.de',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      package_data={'motorturbine': ['motorturbine']},
      classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
      ])
