#!/bin/bash

 rsync -avz  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ../../../  -e ssh pgallo@ops:/users/pgallo/wishful-github-manifest-6/