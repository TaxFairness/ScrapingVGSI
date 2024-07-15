#!/bin/bash

# This script has something to do with combining four lines into one.
# Data came from some source on four related lines:
# Needed to put them all on one line...
# No idea where it was useful, but it was in June 2024
awk '{
    if (NR % 4 == 1) { line1 = $0 }
    else if (NR % 4 == 2) { line2 = $0 }
    else if (NR % 4 == 3) { print line1 "*" $0 }
    else if (NR % 4 == 0) { print line2 "*" $0 }
}' junk.txt