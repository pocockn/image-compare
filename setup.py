from setuptools import setup
from os import path

# Get the long description from the README file
with open(path.join(path.dirname(__file__), 'README.md')) as f:
    long_description = f.read()

setup(
    name='image-compare',
    version='0.0.1',
    description='Simple image comparison script',
    long_description=long_description,
    url='https://github.com/thaffenden/image-compare',
    author='Tristan Haffenden',
    author_email="tristanehaffenden@gmail.com",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
    ]
)