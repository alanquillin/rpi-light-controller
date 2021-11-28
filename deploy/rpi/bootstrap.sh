#!/bin/bash

sudo apt-get update

if [[ -z "$(which docker)" ]]; then
    echo "Installing Docker"
    curl -sSL https://get.docker.com | sh
    sudo usermod -aG docker ${USER}
    sudo systemctl enable docker
fi

if [[ -z "$(which docker-compose)" ]]; then
    echo "Installing docker-compose"
    sudo apt-get install libffi-dev libssl-dev
    sudo apt install python3-dev
    sudo apt-get install -y python3 python3-pip

    sudo pip3 install docker-compose
fi

echo "All done!  Remember to log out and log back in to pick up the docker group if Docker was installed."