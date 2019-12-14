#!/usr/bin/env python3
#DEPENDS: data/raw-private/secret.txt
#CREATES: data/intermediate/lower.txt
#TITLE: Example module that lower cases files
#PIPE: TRUE

import sys
print(sys.stdin.read().lower())
