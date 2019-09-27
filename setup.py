from setuptools import find_packages, setup

setup(
    name='class',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        class=class:cli
    ''',
)
