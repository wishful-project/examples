ssh domenico@extensa.local "rm -r /tmp/spectral_scan/; mkdir /tmp/spectral_scan"
scp pub_server.py domenico@extensa.local:/tmp/spectral_scan/
scp -r spectral_acquire domenico@extensa.local:/tmp/spectral_scan/
ssh -t domenico@extensa.local "sudo python /tmp/spectral_scan/pub_server.py"
