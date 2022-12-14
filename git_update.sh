#!/bin/sh
# git clone https://github.com/LukeKeam/pi-auto4.git

# check for current version
git remote update

# force
# git fetch
# git reset --hard master
# git merge '@{u}'

UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")
BASE=$(git merge-base @ "$UPSTREAM")

if [ $LOCAL = $REMOTE ]; then
    echo "Up-to-date"
elif [ $LOCAL = $BASE ]; then
    echo "Need to pull"
    # store variables
    git stash push ./variables.py
    # pull update
    git pull
    # restore variables
    git stash pop
    # restart service?
    # or just have it restart next time? depends on if it has updates to do
elif [ $REMOTE = $BASE ]; then
    echo "Need to push"
else
    echo "Diverged"
fi

echo "Update complete"