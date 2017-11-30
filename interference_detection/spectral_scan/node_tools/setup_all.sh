sh copy_ssh_key.sh root alix3
sh copy_ssh_key.sh root alix5
fab -f fabfile.py -u root -H alix3 adhoc:wlan0,SPECK_BRIE,2437,15,6,192.168.0.3
fab -f fabfile.py -u root -H alix5 adhoc:wlan0,SPECK_BRIE,2437,15,6,192.168.0.5

