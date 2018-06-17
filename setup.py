from setuptools import setup, find_packages

setup(name='motorturbine',
      version='0.1',
      description='A ORM package for asyncio and motor',
      url='http://github.com/BFriedrichs/aiomotorengine',
      author='Björn Friedrichs',
      author_email='bjoern@friedrichs1.de',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      package_data={'motorturbine': ['motorturbine']})
