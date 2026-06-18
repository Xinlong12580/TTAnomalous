#!/bin/bash
root_dir=$(pwd)
OUTTXT=PYTHON_SCRIPT_"$2"_"$4"_"$6"_"$8"_"${10}"_"${12}"_output.log
OUTTXT="${OUTTXT//\//_}"
echo "OUTTXT" $OUTTXT
echo "Run script starting" | tee $root_dir/$OUTTXT
echo "Running on: `uname -a`" | tee -a $root_dir/$OUTTXT
echo "System software: `cat /etc/redhat-release`" | tee -a $root_dir/$OUTTXT
echo "USER: $USER" |  tee -a $root_dir/$OUTTXT
# Set up pre-compiled CMSSW env
ls | tee -a $root_dir/$OUTTXT
source /cvmfs/cms.cern.ch/cmsset_default.sh
xrdcp root://cmseos.fnal.gov//store/user/USER_NAME/tarTIMBER.tgz ./
export SCRAM_ARCH=el8_amd64_gcc10
scramv1 project CMSSW CMSSW_12_3_5
echo "Unpacking compiled CMSSW environment tarball..." | tee -a $root_dir/$OUTTXT
tar -xzvf tarTIMBER.tgz | tee -a $root_dir/$OUTTXT
tar -xzvf tarcmssw.tgz | tee -a $root_dir/$OUTTXT
tar -xzvf tartimber.tgz | tee -a $root_dir/$OUTTXT
rm tarTIMBER.tgz
rm tarcmssw.tgz
rm tartimber.tgz
mkdir tardir 
cp tarball.tgz tardir/ 
cd tardir/
tar -xzvf tarball.tgz | tee -a $root_dir/$OUTTXT
ls | tee -a $root_dir/$OUTTXT
rm tarball.tgz
mkdir ../CMSSW_12_3_5/src/testdir
cp -r * ../CMSSW_12_3_5/src/testdir
cd ../CMSSW_12_3_5/src/

# CMSREL and virtual env setup
echo 'IN RELEASE' | tee -a $root_dir/$OUTTXT
pwd | tee -a $root_dir/$OUTTXT
ls | tee -a $root_dir/$OUTTXT
echo 'scramv1 runtime -sh' | tee -a $root_dir/$OUTTXT
eval `scramv1 runtime -sh`
echo $CMSSW_BASE "is the CMSSW we have on the local worker node" | tee -a $root_dir/$OUTTXT
echo 'python3 -m venv timber-env' | tee -a $root_dir/$OUTTXT
python3 -m venv timber-env
echo 'source timber-env/bin/activate' | tee -a $root_dir/$OUTTXT
source timber-env/bin/activate
echo "$(which python3)" | tee -a $root_dir/$OUTTXT

# Set up TIMBER
cd ../..
pwd | tee -a $root_dir/$OUTTXT
ls | tee -a $root_dir/$OUTTXT
echo "CP0" | tee -a $root_dir/$OUTTXT
ls TIMBER  | tee -a $root_dir/$OUTTXT
cd TIMBER 
echo "CP1" | tee -a $root_dir/$OUTTXT
pwd | tee -a $root_dir/$OUTTXT
ls | tee -a $root_dir/$OUTTXT
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/cvmfs/cms.cern.ch/el8_amd64_gcc10/external/boost/1.78.0-0d68c45b1e2660f9d21f29f6d0dbe0a0/lib
export ROOT_INCLUDE_PATH=$ROOT_INCLUDE_PATH:$(correction config --incdir)
echo "STARTING TIMBER SETUP......." | tee -a $root_dir/$OUTTXT
source setup.sh
echo "FINISHED TIMBER SETUP......." | tee -a $root_dir/$OUTTXT
cd ../CMSSW_12_3_5/src/testdir
pwd | tee -a $root_dir/$OUTTXT

# xrootd debug & certs
#export XRD_LOGLEVEL=Debug
export X509_CERT_DIR=/cvmfs/grid.cern.ch/etc/grid-security/certificates/

# MAIN FUNCTION
echo python PYTHON_SCRIPT $* | tee -a $root_dir/$OUTTXT
python PYTHON_SCRIPT $* 2>&1 | tee -a $root_dir/$OUTTXT
status=${PIPESTATUS[0]}
if [ $status -eq 0 ]; then
    # move all snapshots to the EOS (there will only be one)
    xrdcp -f *.root OUTPUT_DIR
else
    mv $root_dir/$OUTTXT $root_dir/FAILED_$OUTTXT
    OUTTXT=FAILED_$OUTTXT
fi
ls | tee -a $root_dir/$OUTTXT
#xrdcp -f $root_dir/$OUTTXT OUTPUT_DIR
