"""
Flask-REST
----------

Flask-REST is a Flask extension inspired by Flask-RESTful. It offers a flexible way to implement REST APIs with Flask.
"""
from setuptools import setup

setup(
    name='Flask-REST',
    version='0.9',
    url='https://gitlab.com/Codello/flask-rest/',
    license='MIT',
    author='Kim Wittenburg',
    author_email='codello@wittenburg.kim',
    description='Powerful REST APIs with Flask.',
    long_description=__doc__,
    packages=['flask_rest'],
    zip_safe=True,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
