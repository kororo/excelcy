import os
from io import open
from setuptools import find_packages, setup


def get_requirements(r: str):
    try:  # for pip >= 10
        from pip._internal.req import parse_requirements
    except ImportError:  # for pip <= 9.0.3
        from pip.req import parse_requirements

    # parse_requirements() returns generator of pip.req.InstallRequirement objects
    if os.path.exists(r):
        install_reqs = parse_requirements(r, session=pkg)
        return install_reqs
    return []


with open('excelcy/__init__.py', 'r') as f:
    version = '0.0.1'
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break

pkg = 'excelcy'
REQUIRES = [str(ir.req) for ir in get_requirements('requirements.txt') if ir.req]

setup(
    name=pkg,
    version=version,
    description='Excel Integration with SpaCy. Includes, Entity training, Entity matcher pipe.',
    long_description=open('README.rst', 'r').read(),
    author='Robertus Johansyah',
    author_email='me@kororo.co',
    maintainer='Robertus Johansyah',
    maintainer_email='me@kororo.co',
    url='https://github.com/kororo/excelcy',
    license='MIT',
    keywords=[
        'spacy', 'spacy-pipeline', 'spacy-nlp', 'nlp', 'python', 'python3', 'entity', 'training', 'excel', 'xlsx',
        'spacy-extensions'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    install_requires=REQUIRES,
    tests_require=['coverage', 'pytest'],
    packages=find_packages(),
    entry_points={
        'console_scripts': ['excelcy=excelcy.cli:main'],
    }
)
