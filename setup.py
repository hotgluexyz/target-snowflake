#!/usr/bin/env python

from setuptools import find_packages, setup

with open('README.md') as f:
    long_description = f.read()

setup(name="pipelinewise-target-snowflake",
      version="2.2.1",
      description="Singer.io target for loading data to Snowflake - PipelineWise compatible",
      long_description=long_description,
      long_description_content_type='text/markdown',
      author="Wise",
      url='https://github.com/transferwise/pipelinewise-target-snowflake',
      classifiers=[
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
      ],
      py_modules=["target_snowflake"],
      python_requires='>=3.7',
      install_requires=[
        'pipelinewise-singer-python==1.*',
        #   'oscrypto @ git+https://github.com/wbond/oscrypto.git@d5f3437ed24257895ae1edd9e503cfb352e635a8',
        'certifi==2022.9.24',
        'numpy<1.24.0', 
        'snowflake-connector-python[pandas]~=2.7.12; python_version == "3.7"',
        'snowflake-connector-python[pandas]~=3.4.0; python_version == "3.10"',
        'inflection==0.5.1',
        'joblib==1.2.0',
        'boto3==1.23.10',
      ],
      extras_require={
          "test": [
              "pylint==2.12.*",
              'pytest==7.1.1',
              'pytest-cov==3.0.0',
              "python-dotenv==0.19.*"
          ]
      },
      entry_points="""
          [console_scripts]
          target-snowflake=target_snowflake:main
      """,
      packages=find_packages(exclude=['tests*']),
      )
