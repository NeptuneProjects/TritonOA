# Triton Ocean Acoustics (TritonOA)
William Jenkins<br>
Scripps Institution of Oceanography<br>
wjenkins |a|t| ucsd |d|o|t| edu<br>

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Overview
This package contains Python utilities for interacting with the popular ocean 
acoustics modeling software, [Acoustics Toolbox (AT)](https://oalib-acoustics.org/models-and-software/acoustics-toolbox/), 
developed and maintained by Mike Porter. Code in this package has been adapted 
primarily from:
- Hunter Akins' [PyAT](https://github.com/hunterakins/pyat)
- [Aaron Thodes'](https://athode.scrippsprofiles.ucsd.edu) MATLAB scripts for 
interacting with AT.

Current functionality includes:
- KRAKEN (normal modes)
- Basic transmission loss plotting.
- Basic signal processing functions.

Future intended functionality:
- Bellhop (ray tracing)
- Additional plotting functions
- IO functions for reading in experimental data.
- Robust signal processing workflows (e.g., matched field processing)

## Setup
### Prerequisites
1. [Install Acoustics Toolbox](https://oalib-acoustics.org/models-and-software/acoustics-toolbox/) ([Mac users](https://github.com/NeptuneProjects/TritonOA/blob/master/setup/install_AT_MacOS.md)).

### Installation

`TritonOA` can be built directly from source or installed using `pip`.

#### Build from source:
1. Open a terminal and navigate to the desired installation directory.
2. Save `TritonOA.yml` to the directory by running:  
a. **MacOS**:  
`curl -LJO https://raw.githubusercontent.com/NeptuneProjects/TritonOA/master/TritonOA.yml`  
b. **Linux**:  
`wget --no-check-certificate --content-disposition https://raw.githubusercontent.com/NeptuneProjects/TritonOA/master/TritonOA.yml`
3. In Terminal, run:  
`conda env create -f TritonOA.yml`
4. Once the environment is set up and the package is installed, activate your environment by running:  
`conda activate TritonOA`

#### Using pip:
1. In a virtual environment, run:  
`pip install git+https://github.com/NeptuneProjects/TritonOA.git`

## Usage
A Jupyter notebooks illustrating use cases is provided in the [`tutorials`](https://github.com/NeptuneProjects/TritonOA/blob/master/tutorials/) folder.
