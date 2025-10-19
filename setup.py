from setuptools import setup, find_packages

APP = ['src/main.py']
DATA_FILES = [
    ('assets', ['src/assets/*']),
    ('ui', ['src/ui/*']),
    ('', ['src/*.db']),
]

OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt6', 'core', 'gui', 'widgets'],
    'includes': ['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets'],
}

setup(
    name="SmartOrganizer",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
)
