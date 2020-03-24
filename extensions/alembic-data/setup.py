"""
Alembic-Data
------------

Alembic-Data is an extension for alembic that allows the automatic creation of database content (in addition to schema).
It adds
"""
from setuptools import setup

setup(
    name='Alembic-Data',
    version='0.9',
    url='https://gitlab.com/Codello/alembic-data/',
    license='MIT',
    author='Kim Wittenburg',
    author_email='codello@wittenburg.kim',
    description='Data Migrations for Alembic.',
    long_description=__doc__,
    packages=['alembic_data'],
    zip_safe=True,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'alembic'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
