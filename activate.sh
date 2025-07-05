#!/bin/zsh

if [[ $# -gt 0 ]]; then
  venv_path=$HOME/.venv/$1
else
  venv_path=./.venv
fi
source $venv_path/bin/activate

