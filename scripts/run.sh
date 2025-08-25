#!/bin/sh

# use a fresh custom loader path
unset LD_LIBRARY_PATH

# shortcut
export FNCS_INSTALL="$HOME/FNCS-install"

# update LD_LIBRARY_PATH
if test "x$LD_LIBRARY_PATH" = x
then
    export LD_LIBRARY_PATH="$FNCS_INSTALL/lib"
else
    export LD_LIBRARY_PATH="$FNCS_INSTALL/lib:$LD_LIBRARY_PATH"
fi

# update PATH
if test "x$PATH" = x
then
    export PATH="$FNCS_INSTALL/bin"
else
    export PATH="$FNCS_INSTALL/bin:$PATH"
fi

export FNCS_LOG_STDOUT=no
export FNCS_LOG_FILE=yes

echo "Starting simulation processes..."

# run ns3, redirecting output to a log file
./run_ns-3 LinkModelGLDNS3.txt > ns3.log 2>&1 &
NS3_PID=$!

# run gld, redirecting output to a log file
gridlabd run_GridLab-D.glm > gridlabd.log 2>&1 &
GLD_PID=$!

# run fncs_broker, redirecting output to a log file
fncs_broker 2 > fncs.log 2>&1 &
FNCS_PID=$!

echo "Simulation running with PIDs: ns-3($NS3_PID), GridLAB-D($GLD_PID), FNCS($FNCS_PID)"
echo "Waiting for all simulation processes to complete..."

# Wait for all background processes to finish
wait $NS3_PID $GLD_PID $FNCS_PID

echo "All simulation processes have completed."
