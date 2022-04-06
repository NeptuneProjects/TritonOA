# Triton Ocean Acoustics (TritonOA)
William Jenkins<br>
Scripps Institution of Oceanography<br>
wjenkins |a|t| ucsd |d|o|t| edu<br>

This package contains Python utilities for interacting with the popular ocean 
acoustics modeling software, [Acoustics Toolbox (AT)](https://oalib-acoustics.org/models-and-software/acoustics-toolbox/), 
developed and maintained by Mike Porter. Code in this package has been adapted 
from various sources, including:
- Hunter Akins' [PyAT](https://github.com/hunterakins/pyat)
- [Aaron Thodes'](https://athode.scrippsprofiles.ucsd.edu) MATLAB scripts for 
interacting with AT.

Current functionality includes:
- KRAKEN (normal modes)
- Basic transmission loss plotting.

Future intended functionality:
- Bellhop (ray tracing)
- Additional plotting functions
- IO functions for reading in experimental data.
- More robust signal processing workflows (e.g., matched field processing)

### Installation & Use
1. Install Acoustics Toolbox: instructions.
2. Open a terminal and navigate to the desired installation directory.
3. Save **TritonOA.yml** to the directory by running:
a. **MacOS:**: `curl -LJO https://raw.githubusercontent.com/NeptuneProjects/TritonOA/master/TritonOA.yml`
b. **Linux**: `wget --no-check-certificate --content-disposition https://raw.githubusercontent.com/NeptuneProjects/TritonOA/master/TritonOA.yml`