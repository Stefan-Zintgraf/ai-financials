#!/bin/bash
eval "$(pyenv init -)"
pyenv shell 3.12.12
if [[ ! -d .venv ]]; then
  python3.12 -m venv .venv
else
  printf "Venv already exists\n"
fi
