# Installation Guide

GridAttackSim has been tested on Linux systems. While it was originally developed for Ubuntu 16.04 LTS, this guide provides instructions for a more modern environment like **Ubuntu 22.04 LTS**. Other Linux OSes may work, but have not been tested. This software is not supported on Windows.

To run GridAttackSim, you must first install its three main external components: FNCS, ns-3, and GridLAB-D. The original versions this project depends on are old, so compiling them on a modern system can be challenging.

## Step 1: Install System Packages and Dependencies

First, install the build tools and libraries required for all components.

```shell
sudo apt update
sudo apt install -y build-essential automake libtool autoconf libczmq-dev libxerces-c-dev git python3-tk
```
*Note: `python3-tk` is required for the GUI.*

## Step 2: Install Python Dependencies

Install the required Python packages using `pip` and the `requirements.txt` file.

```shell
pip install -r requirements.txt
```

## Step 3: Set Up Environment Variables

In order to configure FNCS and the other tools, you _must_ set up the related environment variables. Add the following lines to your `~/.bashrc` file:

```shell
export FNCS_INSTALL="$HOME/FNCS-install"
# Update LD_LIBRARY_PATH
if test "x$LD_LIBRARY_PATH" = x
then
    export LD_LIBRARY_PATH="$FNCS_INSTALL/lib:$FNCS_INSTALL/lib/gridlabd"
else
    export LD_LIBRARY_PATH="$FNCS_INSTALL/lib:$FNCS_INSTALL/lib/gridlabd:$LD_LIBRARY_PATH"
fi
# Update PATH
if test "x$PATH" = x
then
    export PATH="$FNCS_INSTALL/bin:$FNCS_INSTALL/share/gridlabd"
else
    export PATH="$FNCS_INSTALL/bin:$FNCS_INSTALL/share/gridlabd:$PATH"
fi
export GLPATH="$FNCS_INSTALL/share/gridlabd:$FNCS_INSTALL/lib/gridlabd"
```
After editing `~/.bashrc`, be sure to source it (`source ~/.bashrc`) or open a new terminal.

## Step 4: Download, Build, and Install FNCS

```shell
# Change to the $HOME directory
cd $HOME
# Download FNCS
git clone https://github.com/FNCS/fncs
# Change to FNCS directory
cd fncs
# Configure, make, and make install
./configure --prefix=$FNCS_INSTALL --with-zmq=$FNCS_INSTALL
make
make install
```

## Step 5: Download, Build, and Install ns-3

```shell
# Change to the $HOME directory
cd $HOME
# Download the required version of ns-3
git clone https://github.com/FNCS/ns-3.26
cd ns-3.26
# The ns-3 install typically uses the compiler flag for warnings-as-errors
# which can break the build on modern compilers. We recommend the following:
CFLAGS="-g -O2" CXXFLAGS="-g -O2" ./waf configure --prefix=$FNCS_INSTALL --with-fncs=$FNCS_INSTALL --with-zmq=$FNCS_INSTALL --disable-python
# Build and install
./waf build
./waf install
```

## Step 6: Download, Build, and Install GridLAB-D

```shell
# Change to the $HOME directory
cd $HOME
# Download the FNCS-capable version of GridLAB-D
git clone https://github.com/gridlab-d/gridlab-d
cd gridlab-d
# Checkout the 'develop' branch which has FNCS support
git checkout -b develop origin/develop
# Generate the configure script
autoreconf -fi
# Configure, make, and make install. The flags are to help with modern compilers.
./configure --prefix=$FNCS_INSTALL --with-xerces=$FNCS_INSTALL --with-fncs=$FNCS_INSTALL --enable-silent-rules 'CFLAGS=-g -O0 -w' 'CXXFLAGS=-g -O0 -w' 'LDFLAGS=-g -O0 -w'
make
make install
```

### Potential Build Issue with GridLAB-D

We have encountered an issue when compiling GridLAB-D. To solve it you
need to edit the file `climate/climate.cpp` in the GridLAB-D
distribution, and change the math library as shown below:

_ORIGINAL CODE:_
```cpp
#include <math.h>
```

_NEW CODE:_
```cpp
#include <cmath>
```

## Step 7: Run a Test Co-simulation

After installation, you can run a test co-simulation using the scripts provided in the FNCS tutorial repository. This is a good way to verify that the core components are working together correctly.
