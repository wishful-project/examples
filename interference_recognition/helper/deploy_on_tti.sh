#!/bin/bash

 rsync -avz  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ../../../  -e ssh pierluigi@nova:~/wishful-github-manifest-6/
 #rsync -avz  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ../../../  -e ssh domenico@nova:~/wishful-github-manifest-6/
 echo "\033[1;32m"
 echo "this deploys only the controller on nova. If you need to update also agents, the following lines have to be uncommented"
 echo "\033[0m"
 #rsync -avz  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ../../../  -e ssh clapton:~/wishful-github-manifest-6/
 #rsync -avz  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ../../../  -e ssh extensa:~/wishful-github-manifest-6/
 #rsync -avz  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ../../../  -e ssh nautilus:~/wishful-github-manifest-6/




rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ../../  -e ssh clapton:~/wishful-github-manifest-6/
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ../interference_recognition/  -e ssh clapton:~/wishful-github-manifest-6/examples/interference_recognition/
rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ../../  -e ssh clapton:~/wishful-github-manifest-6/
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ../interference_recognition/  -e ssh clapton:~/wishful-github-manifest-6/examples/interference_recognition/
rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ../../  -e ssh extensa:~/wishful-github-manifest-6/
rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ../../  -e ssh nautilus:~/wishful-github-manifest-6/
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ../interference_recognition/  -e ssh extensa:~/wishful-github-manifest-6/examples/interference_recognition/
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ../interference_recognition/  -e ssh nautilus:~/wishful-github-manifest-6/examples/interference_recognition/
rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ../../  -e ssh lab.tti.unipa.it:~/wishful-github-manifest-6/
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ../interference_recognition/  -e ssh lab.tti.unipa.it:~/wishful-github-manifest-6/examples/interference_recognition/
