import os
import sys
from glob import glob
from setuptools import setup, find_packages


with open('requirements.txt') as f:
    install_requires = f.readlines()


setup(
    name='k8smtool',
    version='1.1.0',
    description='Set of tools to manage your Kubernetes clusters',
    long_description='Set of tools to manage your Kubernetes clusters',
    url='http://github.com/tomplus/k8s-multi-tool',
    author='Tomasz Prus',
    author_email='tomasz.prus@gmail.com',
    license='MIT',
    packages=find_packages(exclude=("tests*",)),
    include_package_data=True,
    install_requires=install_requires,
    scripts=glob('bin/*.py'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
