from setuptools import setup

APP = ['app.py']
DATA_FILES = [('internal data', ['internal data/_recent_files.json', 'internal data/_settings.json'])]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt5', 'vtracer', 'numpy', 'Markdown', 'scipy', 'scikit-image', 'shapely', 'pickle', 'json'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
