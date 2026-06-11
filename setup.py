#!/usr/bin/env python
"""
Setup configuration for Knowledgedock application
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='Knowledgedock',
    version='1.0.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='Extensible desktop-based learning resource aggregator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/knowledgedock',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    python_requires='>=3.7',
    install_requires=requirements,
    extras_require={
        'backend': ['Flask>=2.3.0', 'Flask-Cors>=4.0.0'],
    },
    entry_points={
        'console_scripts': [
            'knowledgedock=main:main',
        ],
        'gui_scripts': [
            'knowledgedock-gui=main:launch_gui',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['assets/*', '*.db'],
    },
)
