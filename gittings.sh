#!/bin/bash
echo "this is running "
git diff -p develop |sed -n -e '/^diff/h' -e '/old mode 100755/{x;G;p;}' | grep 'diff' | grep -o '[^ ]\+$' | cut -c 3- | while read -r line; do
    sudo chmod -R 0755 $line 
done
echo "done"

git diff -p develop |sed -n -e '/^diff/h' -e '/old mode 100644/{x;G;p;}' | grep 'diff' | grep -o '[^ ]\+$' | cut -c 3- | while read -r line; do
    sudo chmod -R 0644 $line 
done
