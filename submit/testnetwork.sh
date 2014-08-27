#!/bin/bash
if [ -e /cvmfs/oasis.opensciencegrid.org/osg/modules/lmod/5.6.2/init/bash ];
then
    source /cvmfs/oasis.opensciencegrid.org/osg/modules/lmod/5.6.2/init/bash
    module load python/2.7
    ./testnetwork.py
else
    ./testnetwork.py
fi
