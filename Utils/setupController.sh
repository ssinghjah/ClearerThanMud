# Update and install pip
sudo apt-get update
sudo apt-get install python-pip
sudo pip install --upgrade pip
# Install python libraries and other dependencies
sudo pip install numpy
sudo pip install scipy
sudo apt-get install tshark
sudo pip install sklearn
sudo pip install matplotlib
sudo pip install pyangbind
sudo pip install simplejson
sudo apt-get install python-tk
# Generate an SSH Key and add Gateway to the known hosts
ssh-keygen -t rsa
ssh-keyscan -H 192.168.10.10 >> ~/.ssh/known_hosts
# Note: The public key needs to be added to the Gateway's authorized keys

