#!/bin/bash
if [ -z "$1" ]; then
  echo "Usage: $0 <directory_name>"
  exit 1
fi

mkdir -p "$1"
mv *.txt "$1"
