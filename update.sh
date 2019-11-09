sudo rm -r updateme
git clone https://github.com/Woppilif/updateme.git
sudo cp updateme/client.py ./
sudo chmod 777 client.py
sudo cp updateme/update.sh ./
sudo chmod 777 update.sh
sudo reboot