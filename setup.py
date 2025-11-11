#!/usr/bin/env python3
"""
Setup configuration for if-tools package.
IF.witness CLI + IF.optimise - Provenance tracking and cost management for AI workflows.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file) as f:
        install_requires = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith('#')
        ]
else:
    install_requires = [
        'click>=8.1.0',
        'cryptography>=41.0.0',
        'reportlab>=4.0.0',
    ]

setup(
    name='if-tools',
    version='0.1.0',
    description='IF.witness CLI + IF.optimise - Provenance tracking and cost management for AI workflows',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='InfraFabric',
    author_email='',
    url='https://github.com/dannystocker/infrafabric',
    project_urls={
        'Source': 'https://github.com/dannystocker/infrafabric',
        'Documentation': 'https://github.com/dannystocker/infrafabric/tree/main/docs',
    },

    # Package discovery
    packages=find_packages(where='src') + find_packages(where='.', include=['tools', 'tools.*']),
    package_dir={
        '': 'src',
        'tools': 'tools',
    },

    # Standalone modules in src/
    py_modules=['cost_monitor'],

    # Include non-Python files
    include_package_data=True,

    # Dependencies
    install_requires=install_requires,

    # Optional dependencies for development
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
        'test': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
        ],
    },

    # Console script entry points
    entry_points={
        'console_scripts': [
            # Main CLI tools
            'if-witness=cli.if_witness:cli',
            'if-optimise=cli.if_optimise:cli',

            # Utility tools
            'if-cost-tracker=tools.cost_tracker:cli',
            'if-budget-alerts=tools.budget_alerts:cli',
            'if-alert-launcher=tools.alert_launcher:cli',
            'if-cost-monitor=cost_monitor:cli',
        ],
    },

    # Python version requirement
    python_requires='>=3.8',

    # PyPI classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Monitoring',
        'Topic :: Security',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],

    # Keywords for PyPI search
    keywords='provenance audit-trail cost-tracking ai-workflow token-monitoring',

    # Package metadata
    license='MIT',
    zip_safe=False,
)
