from setuptools import setup

with open('requirements.txt', 'r') as reqs_txt:
    reqs = reqs_txt.readlines()

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
   name='wirepickle',
   version='1.0.0',
   license='MIT',
   description='Effortless Python RPC with ZeroMQ',
   long_description=long_description,
   long_description_content_type='text/markdown',
   author='Patrick Kage',
   author_email='patrick.r.kage@gmail.com',
   url='https://github.com/pkage/wirepickle',
   packages=['wirepickle'],
   install_requires=[reqs]
)
