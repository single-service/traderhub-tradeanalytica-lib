from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='traderhub_tradeanalytica',
  version='0.1.6',
  author='DmitriySosedov',
  author_email='d.i.sosedov@gmail.com',
  description='TraderHub library for trade strategy analyse',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/single-service/traderhub-tradeanalytica-lib',
  packages=find_packages(),
  install_requires=[
        'pandas>=2.2.2',
        'numpy>=2.0.0',
        'pandas-ta-classic>=0.3.59',
        'sortedcontainers>=2.4.0',
        'requests>=2.32.5',
      ],
  classifiers=[
    'Programming Language :: Python :: 3.10',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='trade analytica backtesting traderhub ',
  project_urls={
    'GitHub': 'https://github.com/single-service/traderhub-tradeanalytica-lib'
  },
  python_requires='>=3.10'
)