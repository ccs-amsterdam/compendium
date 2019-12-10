#!/usr/bin/env python3
#DEPENDS: raw-private/secret.txt
#CREATES: intermediate/upper.txt
#TITLE: Example module that uppercases files
#PIPE: TRUE

import sys
print(sys.stdin.read().upper())
