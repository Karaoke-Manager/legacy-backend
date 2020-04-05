"""
Motor ODM
---------

An ODM for Motor using AsyncIO based on Pydantic.
"""
from setuptools import setup

setup(
    name='Motor-ODM',
    version='0.1',
    url='https://gitlab.com/Codello/motor-odm/',  # TODO: Publish this package
    license='MIT',
    author='Kim Wittenburg',
    author_email='codello@wittenburg.kim',
    description='A ODM for Motor',
    long_description=__doc__,
    packages=[
        "motor_odm"
    ],
    zip_safe=True,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Motor',
        'Pydantic',
        'Funcy',
        'Motor-Stubs'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
