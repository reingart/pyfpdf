#!/bin/bash

# Install veraPDF on a Linux system

# USAGE: ./install-verapdf.sh

set -o pipefail -o errexit -o nounset -o xtrace

rm -rf verapdf-*
wget --quiet https://software.verapdf.org/rel/1.22/verapdf-greenfield-1.22.3-installer.zip
unzip verapdf*installer.zip
(
    # Press 1 to continue, 2 to quit, 3 to redisplay:
    echo 1
    # Select the installation path:
    echo $PWD/verapdf
    # Enter O for OK, C to Cancel:
    echo O
    # Press 1 to continue, 2 to quit, 3 to redisplay:
    echo 1
    # Include optional pack 'veraPDF Corpus and Validation model' - Enter Y for Yes, N for No:
    echo N
    # Include optional pack 'veraPDF Documentation' - Enter Y for Yes, N for No:
    echo N
    # Include optional pack 'veraPDF Sample Plugins' - Enter Y for Yes, N for No:
    echo N
    # Press 1 to continue, 2 to quit, 3 to redisplay:
    echo 1
) | verapdf-*/verapdf-install
rm -rf verapdf-*
