# ToDO: check if kernel is up-to-date

echo 'Trying to update kernel'

if [ $(uname -r) = "4.15.4-041504-generic" ]; then
    echo 'Kernel up to date'
    exit
fi

# go to home dir

cd ~

# fetch stuff

echo 'Downloading new kernel and headers'

wget -q http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.15.4/linux-image-4.15.4-041504-generic_4.15.4-041504.201802162207_amd64.deb
wget -q http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.15.4/linux-headers-4.15.4-041504_4.15.4-041504.201802162207_all.deb
wget -q http://kernel.ubuntu.com/~kernel-ppa/mainline/v4.15.4/linux-headers-4.15.4-041504-generic_4.15.4-041504.201802162207_amd64.deb

echo 'Done downloading'

echo 'Installing new kernel and headers'

sudo dpkg -i linux*4.15.4-*.deb

# sudo apt install ./linux-image-4.15.4-041504-generic_4.15.4-041504.201802162207_amd64.deb
# sudo apt install ./linux-headers-4.15.4-041504_4.15.4-041504.201802162207_all.deb
# sudo apt install ./linux-headers-4.15.4-041504-generic_4.15.4-041504.201802162207_amd64.deb

echo 'Done installing'

rm linux-image-4.15.4-041504-generic_4.15.4-041504.201802162207_amd64.deb
rm linux-headers-4.15.4-041504_4.15.4-041504.201802162207_all.deb
rm linux-headers-4.15.4-041504-generic_4.15.4-041504.201802162207_amd64.deb

echo 'Installing virtualbox-guest-dkms'

sudo apt-get update
sudo apt-get -y install virtualbox-guest-dkms

echo 'Kernel was updated. Please use vagrant reload to finish updating'
