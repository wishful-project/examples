#! /bin/bash
if [ $# -lt 2 ];then
echo "usage: $0 <usr> <hostname>"
exit
fi
b=$1
B=$2
cat ~/.ssh/id_rsa.pub | ssh $b@$B 'cat >> .ssh/authorized_keys'
