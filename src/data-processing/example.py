#!/usr/bin/env python3
#DEPENDS: data/raw-private/secret.txt
#CREATES: data/intermediate/upper.txt
#TITLE: Example module that uppercases files
#DESCRIPTION: Example module that uppercases files
#PIPE: TRUE

import sys
print(sys.stdin.read().upper())
