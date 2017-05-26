Wishful LTE everwishful
============================

###

### 0. Reserve and swap in the experiment
 
### 1. run the showcase 
 
 #move files on controller
 
  rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ./wishful-github-manifest/  -e ssh controller_address:~/wishful-github-manifest/
 #rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ./wishful-github-manifest-4/  -e ssh lab.tti.unipa.it:~/wishful-github-manifest/
 #rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ./wishful-github-manifest-5/  -e ssh fabrizio@10.8.12.3:~/wishful-github-manifest/
 #rsync -avz --delete  --exclude=.git --exclude '*.o' --exclude '*.h' --exclude '*.c' --exclude '*.pyc' --exclude .repo/ ./wishful-github-manifest-5/  -e ssh domenico@lab.tti.unipa.it:~/wishful-github-manifest/
 
 #connect to nodes
  ssh user@controller_address
  ssh user@enb
  
 #move on experiment directory
  cd wishful-github-manifest/examples/lte_everwishful/

 #sync clock nodes
  sh sync_date.sh user  

 #deploy directory on nodes
  sh deploy_upis.sh <user> clapton.local,nautilus.local,extensa.local
  cd .. 

 #start agent
  sudo python3 agent_example.py

 #controller
  sudo python controller_example.py