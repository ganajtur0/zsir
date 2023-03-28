#!/usr/bin/bash

szin=(zold piros tok makk)
kep=(het nyolc kilenc tiz also felso kiraly asz)

URL="https://raw.githubusercontent.com/feco93/Zsir/master/src/main/resources/images/"

for s in "${szin[@]}"
do
	for k in "${kep[@]}"
	do
		wget ${URL}${s}"_"${k}".jpg"
	done
done
