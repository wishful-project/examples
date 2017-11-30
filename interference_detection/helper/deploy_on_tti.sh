#!/bin/bash

rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../../../  -e ssh nova:~/wishful-github-manifest-7/
ssh nova "mkdir -p wishful-github-manifest-7/examples"
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude '*/*' ../../interference_detection/  -e ssh nova:~/wishful-github-manifest-7/examples/interference_detection/
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude '*/*' ../../interference_detection/helper/  -e ssh nova:~/wishful-github-manifest-7/examples/interference_detection/helper
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' ../../wmp/  -e ssh nova:~/wishful-github-manifest-7/examples/wmp/

rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../../../  -e ssh root@alix03:~/wishful-github-manifest-7/
ssh root@alix03 "mkdir -p wishful-github-manifest-7/examples"
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude '*/*' ../../interference_detection/  -e ssh root@alix03:~/wishful-github-manifest-7/examples/interference_detection/
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude '*/*' ../../interference_detection/helper/  -e ssh root@alix03:~/wishful-github-manifest-7/examples/interference_detection/helper

rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../../../  -e ssh root@alix05:~/wishful-github-manifest-7/
ssh root@alix05 "mkdir -p wishful-github-manifest-7/examples"
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude '*/*' ../../interference_detection/  -e ssh root@alix05:~/wishful-github-manifest-7/examples/interference_detection/
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' ../../interference_detection/helper/  -e ssh root@alix05:~/wishful-github-manifest-7/examples/interference_detection/helper
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' ../../interference_detection/station-conf/  -e ssh root@alix05:~/wishful-github-manifest-7/examples/interference_detection/station-conf

rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../../../  -e ssh root@alix10:~/wishful-github-manifest-7/
ssh root@alix10 "mkdir -p wishful-github-manifest-7/examples"
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude '*/*' ../../interference_detection/  -e ssh root@alix10:~/wishful-github-manifest-7/examples/interference_detection/
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude '*/*' ../../interference_detection/helper/  -e ssh root@alix10:~/wishful-github-manifest-7/examples/interference_detection/helper


rsync -avz --delete --exclude=examples --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .idea/ --exclude .repo/ ../../../  -e ssh clapton:~/wishful-github-manifest-7/
ssh clapton "mkdir -p wishful-github-manifest-7/examples"
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude '*/*' ../../interference_detection/  -e ssh clapton:~/wishful-github-manifest-7/examples/interference_detection/
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' ../../interference_detection/helper/  -e ssh clapton:~/wishful-github-manifest-7/examples/interference_detection/helper
rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' ../../interference_detection/station-conf/  -e ssh clapton:~/wishful-github-manifest-7/examples/interference_detection/station-conf
