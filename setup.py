#!/usr/bin/python3.5

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='fsbackup',
      version='0.2.1',
      description='Multi-Volume Backup for Large Filesystems',
      long_description=readme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Archiving :: Backup',
      ],
      keywords='backup volume',
      url='https://github.com/zeycus/fsbackup/',
      author='Miguel Garcia (aka Zeycus)',
      author_email='zeycus@gmail.com',
      license='MIT',
      packages=['fsbackup'],
      install_requires=["pymongo", "mongo_shelve"],
      include_package_data=True,
      scripts=['bin/fsbck.py'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
)