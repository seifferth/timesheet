from setuptools import setup, find_packages

with open('readme.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='timesheet',
    version='1.0.0',
    packages=['timesheet'],
    entry_points={'console_scripts': [
        'timesheet = timesheet.cli:main'
    ]},
    python_requires='>=3.9',
    author='Frank Seifferth',
    author_email='frankseifferth@posteo.net',
    description='A simple yet flexible system for time tracking',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/seifferth/timesheet',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License '
                                   'v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
    ],
)
