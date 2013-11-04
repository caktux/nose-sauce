
from setuptools import setup, find_packages

setup(name="nosesauce",
    version = '0.0.6',
    packages = ['nosesauce'],
    zip_safe = False,
    include_package_data = True,
    install_requires = [
        'simplejson',
        'multiprocessing',
        ],
    entry_points = {
        'nose.plugins.0.10': [
            'nosesauce = nosesauce.noseplugin:Sauce'
            ]
        },
)
