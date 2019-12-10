#!/usr/bin/env python3
#DEPENDS: raw-private/secret.txt
#CREATES: intermediate/lower.txt
#TITLE: Example module that lower cases files
#PIPE: TRUE

import sys
print(sys.stdin.read().lower())
