#!/usr/bin/env bash

apt-get update
apt-get update

apt-get install -y unzip build-essential

DITG="D-ITG-2.8.1-r1023"

wget http://traffic.comics.unina.it/software/ITG/codice/${DITG}-src.zip

unzip ${DITG}-src.zip

cd $DITG/src

make

make install

cd ../../

rm ${DITG}-src.zip
rm -r $DITG/

