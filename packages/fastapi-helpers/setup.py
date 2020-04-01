"""
FastAPI Helpers
---------------

A collection of supporting functions for FastAPI.
"""
from setuptools import setup

setup(
    # TODO: Maybe rename to Starlette-Helpers
    name='FastAPI-Helpers',
    version='0.1',
    url='https://gitlab.com/Codello/fastapi-helpers/',  # TODO: Publish this package
    license='MIT',
    author='Kim Wittenburg',
    author_email='codello@wittenburg.kim',
    description='A collection of supporting functions for FastAPI.',
    long_description=__doc__,
    packages=[
        "fastapi_helpers"
    ],
    zip_safe=True,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'FastAPI'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: FastAPI',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: ASGI',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
