"""Library installation requirements and info."""
import ast
import os
import re
import sys
from setuptools import setup, find_packages

if sys.version_info < (2, 7):
    sys.stderr.write("ERROR: SlurmScale requires at least Python ver 2.7\n")
    sys.exit(1)

# Cannot use "from slurmscale import get_version" because that would try to
# import the six package which may not be installed yet.
reg = re.compile(r'__version__\s*=\s*(.+)')
with open(os.path.join('slurmscale', '__init__.py')) as f:
    for line in f:
        m = reg.match(line)
        if m:
            version = ast.literal_eval(m.group(1))
            break
# pyslurm is also needed but it can only be installed on a system with Slurm
base_reqs = ['click>=6.6', 'Cython>=0.24.1', 'cloudbridge']
dev_reqs = (['tox>=2.3.1', 'sphinx>=1.4.8'] + base_reqs)

setup(name='slurmscale',
      version=version,
      description='An external library for delivering Slurm Elastic Computing',
      author='Galaxy Project',
      author_email='enis.afgan@gmail.com',
      url='https://github.com/afgane/slurmscale',
      install_requires=base_reqs,
      extras_require={
          'full': base_reqs,
          'dev': dev_reqs
      },
      packages=find_packages(),
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy'],
      test_suite="test"
      )
