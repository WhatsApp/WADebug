# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
WADebug is a command-line tool to find issues with WhatsApp Business API setup
"""
from setuptools import find_packages, setup

dependencies = [
    'click',
    'docker',
    'enum34;python_version<"3.4"',
    'outdated',
    'pydash',
    'PyMySQL',
    'pytest',
    'pytest-cov',
    'pytest-mock',
    'PyYAML',
    'six',
]

setup(
    name='wadebug',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    version='0.1.3',
    url='https://developers.facebook.com/docs/whatsapp/guides/wadebug',
    license='MIT',
    author='Thiago Moraes',
    author_email='tmoraes@fb.com',
    description='Investigate issues with WhatsApp Business API setup.',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'wadebug = wadebug.cli:safe_main',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
