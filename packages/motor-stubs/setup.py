"""
Motor Stubs
-----------

Stubs for the Motor Package.
"""
import os

from setuptools import setup


def find_stub_files():
    result = []
    for root, dirs, files in os.walk("motor-stubs"):
        for file in files:
            if file.endswith('.pyi'):
                if os.path.sep in root:
                    sub_root = root.split(os.path.sep, 1)[-1]
                    file = os.path.join(sub_root, file)
                result.append(file)
    return result


# TODO: Tornado Stubs
# TODO: Stubs for GridFS

setup(
    name='Motor-Stubs',
    version='0.1',
    url='https://gitlab.com/Codello/motor-stubs/',  # TODO: Publish this package
    license='MIT',
    author='Kim Wittenburg',
    author_email='codello@wittenburg.kim',
    description="Stubs for the Motor Package.",
    long_description=__doc__,
    packages=["motor-stubs"],
    install_requires=['motor'],
    package_data={'motor-stubs': find_stub_files()},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
