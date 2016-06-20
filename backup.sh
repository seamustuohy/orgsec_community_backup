#!/usr/bin/env bash
#
# This file is part of orgsec community backup, a backup of orgsec.community.
# Copyright © 2016 seamus tuohy, <code@seamustuohy.com>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the included LICENSE file for details.

set -e
set -u
set -x

# Read Only variables

readonly PROG_DIR=$(readlink -m $(dirname $0))
#readonly readonly PROGNAME=$(basename )
#readonly PROGDIR=$(readlink -m $(dirname ))

main() {
    # Get the current version of the scripts
    git checkout gh-pages
    git checkout master update.py
    date
    python3 update.py
    git add .
    CUR_DATE=$(date)
    git commit -m "Updated orgsec to reflect latest as of $CUR_DATE"
    git push
    git checkout master
}

main
