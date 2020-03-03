#!/bin/bash - 
# Provide simple functions to make formatted terminal output
# The functions do not print a newline

# Colors
red="\e[31m"
green="\e[32m"
yellow="\e[33m"
blue="\e[34m"

# Attributes
bold="\e[1m"
dim="\e[2m"
underlined="\e[4m"

reset="\e[0m"

# Functions
_format() {
  # _format attribute text
  [[ -z $1 ]] || [[ -z $2 ]] && return
  echo -ne $1$2$reset
}

## Colors
red() {
  _format $red "$1"
}

blue() {
  _format $blue "$1"
}

green() {
  _format $green "$1"
}

## Attributes
underlined() {
  _format $underlined "$1"
}

bold() {
  _format $bold "$1"
}
