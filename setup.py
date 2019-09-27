from setuptools import setup

setup(
    name='class',
    version='0.1',
    py_modules=['class'],
    include_package_data=True,
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        class=class:main
    ''',
)
