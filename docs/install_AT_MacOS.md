# Installing Acoustic Toolbox (AT) on macOS w/ Intel CPU
William Jenkins
<br>Scripps Institution of Oceanography
<br>16 June 2022

## Introduction
Installing the Acoustic Toolbox (AT) software is nontrivial for basic and even intermediate computer users.  The source files are written in Fortran and require a Fortran compiler to build the binary executables.  macOS does not necessarily ship with the required compilers or libraries.  One approach is to install and use the [GNU Compiler Collection (GCC)](https://gcc.gnu.org), but I had frequent problems with missing libraries and compatibility issues.  Updating the OS often broke the installation of AT when compiled with GCC's GFortran compiler.  After many efforts at troubleshooting, I settled on using Intel's Fortran compiler.  The following steps will guide you through most of the steps required to install AT using **ifort**.

## 1. Initial Conditions:
1. 2019 MacBook Pro (Intel) running macOS Monterey v12.1.  
2. As of April 2022, executables run on same computer running macOS Monterey v12.3.
3. The program `make` is installed.  Check installation by typing `make -v` in your Terminal.  If `make` is not installed, you can download it from [GNU](https://www.gnu.org/software/make/) or [Homebrew](https://formulae.brew.sh/formula/make).
4. Apple's Command Line Tools are installed - these can be installed via [Xcode](https://developer.apple.com/xcode/).

## 2. Preparation
### A. Download Required Tools and References
1. Download the standalone [Intel Fortran Compiler Classic](https://www.intel.com/content/www/us/en/developer/articles/tool/oneapi-standalone-components.html#inpage-nav-6-1). Note: ensure you download from the section titled **Compilers**, not other options such as **Runtime Versions**.
2. Download the [documentation for the HPC Toolkit](https://d1hdbi2t0py8f.cloudfront.net/index.html?prefix=oneapi-hpc-docs/).
3. Download the [Acoustics Toolbox (AT)](https://oalib.hlsresearch.com/AcousticsToolbox/) and unzip it to the desired installation directory.

### B. Install Required Tools
1. Install the Intel Fortran Compiler Classic (**ifort**) using the installer.  Use default setup options.
2. Before using the **ifort** compiler, you need to tell your computer where to find the compiler components.  There are two ways to do this.
    <br>(a) If you only need to use **ifort** to compile AT, you can set the necessary environment variables for just this terminal session by typing:
    <br>`source /<install-dir>/setvars.sh intel64`
    <br>If you installed the compiler correctly, the `<install-dir>` should be located at:
    <br>`/opt/intel/oneapi/`
    <br>(b) If you do not wish to perform step 2.B.2(a) every time you enter a new terminal session, you can add the following to your `.bashrc` or `.zshrc`:
    <br>`source /<install-dir>/setvars.sh intel64`

### C. Get CPU Model Name
In later steps you will need to know what CPU chipset model you have.
1. Run the following code in your terminal:
<br>`sysctl -a | grep brand`
2. You should see a variable `machdep.cpu.brand_string` printed that looks something like:
<br>`Intel(R) Core(TM) i9-9980HK CPU @ 2.40GHz`.
<br>The `9980HK` is the model of your CPU.
3. Do an internet search for `Intel <model number> model name`.  For example, the 9980HK is based on Intel’s "Coffee Lake" chipset model.
4. Open the documentation you downloaded in step 2.A.2.  Navigate to: `Home -> Compiler Reference -> Compiler Options -> Alphabetical List of Compiler Options`
5. Click on the link for `ax, Qax`.
6. Find your CPU model name and note the syntax (e.g., Coffee Lake is all caps `COFFEELAKE`).  This value will be used to configure your Makefiles in the following steps.

### D. Add Library to Path
Ensure MacOS command line tools (see 1.4) are on your computer's `LIBRARY_PATH`.
1. If not already present, add the following to your `.bashrc` or `.zshrc`:
<br>`export LIBRARY_PATH=$LIBRARY_PATH:/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib`

## 3. Prepare AT Makefiles
### A. Configure `/AT/Makefile`
1. Navigate to the directory containing AT.  Open `Makefile` in a text editor.
2. Read the instructions at the top of the file, and then scroll down to the `***ifort` section.
3. Comment out all lines beginning with `export FFLAGS`.
4. Paste the following beneath the `export FC=ifort` line:
<br>`export FFLAGS= -O3 -parallel -ax<YOUR CPU MODEL> -nologo -inline-level=2 -assume byterecl -threads -heap-arrays`.
<br>For information on the various options, consult the documentation you downloaded in step 2.A.2.
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

## 5. Set Symbolic Links
Acoustic Toolbox programs can now be run from your Terminal (or from Python/MATLAB), but to do so, you must specify the path of the program in each call, or be in the same directory as the executable.  For example, to run the command in 4.4 from a separate working directory, you would need to run:
<br>`<path to AT>/kraken/kraken.exe MunkK`
<br>For those of us who run these programs often enough, that can be a bit of a hassle.  To be able to call AT programs from the command line without specifying the path to `AT`, follow these steps.
1. Download the shell script `mk_sym_links.sh` available [here](https://github.com/NeptuneProjects/TritonOA/tree/master/scripts).
2. Open `mk_sym_links.sh` in a text editor.
3. Set the `AT_PATH` environment variable to your installation of AT.
4. Save and close the file.
5. In Terminal, navigate to the same directory you saved `mk_sym_links.sh`.
6. Run the command: `sh mk_sym_links.sh`.  You should now be able to run AT programs from any directory without specifying the path to AT.

## 6. Remove Symbolic Links
1. If you need to reinstall or remove AT and wish to remove the symbolic links, download `rm_sym_links.sh` available [here](https://github.com/NeptuneProjects/TritonOA/tree/master/scripts).
2. In Terminal, naviage to the same directory you saved `rm_sym_links.sh`.
3. Run the command: `sh rm_sym_links.sh`.