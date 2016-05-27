#!/bin/bash

for name in $@;
do
  convert images/$name.jpg -blur 0x1 -paint 2 images/"$name"_out.jpg
done
