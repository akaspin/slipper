from setuptools import setup, find_packages

setup(
    name='slipper',
    version='0.1',
    packages=find_packages(exclude=['tests.*', 'tests']),
    url='',
    license='',
    author='akaspin',
    author_email='aka.spin@gmail.com',
    description='Task Flow',
    requires=[
        'easydict', 'sqlalchemy', 'six', 'kombu', 'gevent'
    ],
    package_data={
        'slipper': [
            'etc/conf.yaml',
        ]
    },
    tests_require=['nose'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'slipper-serve = slipper.bin.serve:main',
            'slipper-init = slipper.bin.init:main',
        ],
    },
)
