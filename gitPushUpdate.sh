#!/bin/bash

GITHUB_USER_NAME="48723247842"
GITHUB_USER_EMAIL="48723247842@protonmail.com"
GITHUB_PRIVATE_KEY_PATH="/home/morphs/.ssh/48723247842_github"
GITHUB_SSH_REPOSITORY_URL="git@github.com:48723247842/USBStorageController.git"

function is_int() { return $(test "$@" -eq "$@" > /dev/null 2>&1); }
ssh-add -D
git init
git config --global --unset user.name
git config --global --unset user.email
git config user.name "$GITHUB_USER_NAME"
git config user.email "$GITHUB_USER_EMAIL"
ssh-add -k $GITHUB_PRIVATE_KEY_PATH

LastCommit=$(git log -1 --pretty="%B" | xargs)
# https://stackoverflow.com/a/3626205
if $(is_int "${LastCommit}");
    then
    NextCommitNumber=$((LastCommit+1))
else
    echo "Not an integer Resetting"
    NextCommitNumber=1
fi
#echo "$NextCommitNumber"
git add .
git commit -m "$NextCommitNumber"
git remote add origin $GITHUB_SSH_REPOSITORY_URL
git push origin master