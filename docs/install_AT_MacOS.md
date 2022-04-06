# Installing Acoustic Toolbox (AT) on macOS
William Jenkins
<br>Scripps Institution of Oceanography
<br>5 April 2022

## Introduction
Installing the Acoustic Toolbox software is nontrivial for basic and even intermediate computer users.  The binary files are written in Fortran and require a Fortran compiler to build the executables.  macOS does not necessarily ship with the required compilers or libraries.  One approach is to install and use the [GNU Compiler Collection (GCC)](https://gcc.gnu.org), but I had frequent problems with missing libraries and compatibility issues.  Updating the OS often broke the installation of AT when compiled with GCC's GFortran compiler.

After many efforts at troubleshooting, I settled on using Intel's Fortran compiler.  At the time of testing (January 2022), I had to install two Intel software developer kits to use the Fortran compiler.  A quick Google search as of this writing (April 2022) shows that there is a [standalone version of the compiler](https://www.intel.com/content/www/us/en/developer/tools/oneapi/fortran-compiler.html#gs.vvmc01) which may provide a quicker route to installation and compiling AT; I have not tested this method.

## 1. Initial Conditions:
1. 2019 MacBook Pro (Intel) running macOS Monterey v12.1.
2. As of April 2022, executables run on same computer running macOS Monterey v12.3.

## 2. Preparation
### A. Download Required Tools and References
1. Download the [Intel oneAPI Base Toolkit](https://www.intel.com/content/www/us/en/developer/tools/oneapi/base-toolkit.html#gs.lo6ojz).
2. Download the [Intel oneAPI HPC Toolkit](https://www.intel.com/content/www/us/en/developer/tools/oneapi/hpc-toolkit.html#gs.lo6pov).
3. Download the [documentation for the HPC Toolkit](https://d1hdbi2t0py8f.cloudfront.net/index.html?prefix=oneapi-hpc-docs/).
4. Download the [Acoustics Toolbox (AT)](https://oalib.hlsresearch.com/AcousticsToolbox/) and unzip it to the desired installation directory.

### B. Install Required Tools
1. Install the Intel oneAPI Base Toolkit using the installer.  Use default setup options.
2. Install the Intel oneAPI HPC Toolkit using the installer.  Use default setup options. *Note: the Base Toolkit must be installed prior to this step.*
3. Before using the **ifort** compiler, you need to tell your computer where to find the compiler components.  There are two ways to do this.
    <br>(a) If you only need to use **ifort** to compile AT, you can set the necessary environment variables for just this terminal session by typing:
    <br>`source /<install-dir>/setvars.sh intel64`
    <br>(b) If you do not wish to perform step 2.B.3(a) every time you enter a new terminal session, you can add the following to your `.bashrc` or `.zshrc`:
    <br>`source /<install-dir>/setvars.sh intel64`

### C. Get CPU Model Name
In later steps you will need to know what CPU chipset model you have.
1. Run the following code in your terminal:
<br>`sysctl -a | grep brand`
2. You should see a variable `machdep.cpu.brand_string` printed that looks something like:
<br>`Intel(R) Core(TM) i9-9980HK CPU @ 2.40GHz`.
<br>The `9980HK` is the model of your CPU.
3. Do an internet search for `Intel <model number> model name`.  For example, the 9980HK is based on Intel’s "Coffee Lake" chipset model.
4. Open the documentation you downloaded in step 2.A.3.  Navigate to: `Home -> Compiler Reference -> Compiler Options -> Alphabetical List of Compiler Options`
5. Click on the link for `ax, Qax`.
6. Find your CPU model name and note the syntax (e.g., all caps).  This value will be used to configure your Makefiles in the following steps.

## 3. Prepare AT Makefiles
### A. Configure `/AT/Makefile`
1. Navigate to the directory containing AT.  Open `Makefile` in a text editor.
2. Read the instructions at the top of the file, and then scroll down to the `***ifort` section.
3. Comment out all lines beginning with `export FFLAGS`.
4. Paste the following beneath the `export FC=ifort` line:
<br>`export FFLAGS= -O3 -parallel -ax<YOUR CPU MODEL> -nologo -inline-level=2 -assume byterecl -threads -heap-arrays`.
<br>For information on the various options, consult the documentation you downloaded in step 2.A.3.
5. Under the `*** GNU Compiler Collection GFORTRAN` section, comment out all `export` statements.
6. Scroll down to the bottom section, just below the `*** Portland Group FORTRAN` section.
7. Change `export CC=gcc` to `export CC=ifort`.
8. Comment out `export CFLAGS=-g`.
9. Save and close the Makefile.

### B. Configure `/AT/misc/Makefile`
1. Navigate to `/AT/misc`.
2. Open `Makefile` in this directory in a text editor.
3. Comment out the line `AR = ar`.
4. Uncomment the line `AR = xiar`.
5. Save and close the Makefile.

### C. Configure /AT/tslib/Makefile
1. Navigate to `/AT/tslib`.
2. Open `Makefile` in this directory in a text editor.
3. Comment out the line `AR = ar`.
4. Uncomment the line `AR = xiar`.
5. Save and close the Makefile.

## 4. Compile AT
1. Navigate to `/AT` in Terminal.
2. Run the command: `make clean`.
3. Run the command: `make`.
<br>*Note: Intel Fortran will take a few minutes to compile all the files.*
4. Once complete, you can run tests per the AT documentation. For example, in Terminal navigate to `/AT/tests/Munk` and run:
<br>`kraken.exe MunkK`
5. If you get a `Command not found` error, you need to specify the path of the executable when calling it, or create symbolic links to your binaries folder that is in your computer's `PATH` variable.