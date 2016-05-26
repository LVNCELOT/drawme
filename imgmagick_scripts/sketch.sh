#!/bin/bash

for name in $@;
do
  convert images/$name.jpg -colorspace gray \
                            \( +clone -tile pencil_tile.gif -draw "color 0,0 reset" \
                               +clone +swap -compose color_dodge -composite \) \
                            -fx 'u*.2+v*.8' images/"$name"_out.jpg;
done
