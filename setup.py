#!/usr/bin/env python3

from setuptools import setup

def setup_package():
    setup(
        name='TritonOA',
        url='https://github.com/NeptuneProjects/TritonOA',
        author='William F. Jenkins II',
        author_email='wjenkins@ucsd.edu',
        packages=[
            'tritonoa',
            # 'tritonoa.core',
            # 'tritonoa.kraken',
            # 'tritonoa.plotting',
            # 'tritonoa.profiles',
            # 'tritonoa.sp'
        ],
        # scripts=['RISCluster/runDEC'],
        # entry_points = {
        #     'console_scripts': [
        #         'query_H5size=RISCluster.utils:query_H5size',
        #         'ExtractH5Dataset=RISCluster.utils:ExtractH5Dataset',
        #         'GenerateSampleIndex=RISCluster.utils:GenerateSampleIndex'
        #     ]
        # },
        install_requires=[
            'cmocean',
            'feather-format',
            'jupyterlab',
            'matplotlib',
            'numpy',
            'pandas',
            'scipy'
        ],
        version='0.0b2',
        license='MIT',
        description="Package provides interface to acoustic modeling tools \
            of Acoustics Toolbox developed by Mike Porter."
    )


if __name__ == '__main__':
    setup_package()
