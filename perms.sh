#!/bin/bash
IFS=$'\n'
for c in `git diff -p develop|sed -n '/diff --git/{N;s/diff --git//g;s/\n/ /g;s# a/.* b/##g;s/old mode //g;s/\(.*\) 100\(.*\)/chmod \2 \1/g;p}'`
do
        eval $c
done
unset IFS
