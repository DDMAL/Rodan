#!/bin/sh

OS=$(uname -s)

scp ./index.html ../../../../

cd ../../../../


if [ $OS = "Linux" ]
then

read -p "Building this project requires npm, gulp and webpack. This script will install what's missing. Would you like to install them? [y/n]" INSTALL

if [ "$INSTALL" = "y" ]
then

if ! type npm > /dev/null;
then
echo "> Installing npm"
sudo apt-get install nodejs
sudo apt-get install npm
sudo ln -s /usr/bin/nodejs /usr/bin/node
fi

if ! type webpack > /dev/null;
then
echo "> Installing webpack"
sudo npm install --save-dev webpack
fi

if ! type gulp > /dev/null;
then
echo "> Installing gulp"
sudo npm install -g gulp
sudo npm install gulp
fi

echo "> npm install"
sudo npm install
echo "> npm install -g gulp webpack"
sudo npm install -g gulp webpack

fi

elif [ $OS = "Darwin" ]
then
read -p "Building this project requires npm, gulp and webpack. You can install these with homebrew. This script will install what's missing. Would you like to install them? [y/n]" INSTALL

if [ "$INSTALL" = "y" ]
then

if ! type brew > /dev/null;
then
echo "> Installing brew"
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
fi

if ! type npm > /dev/null;
then
echo "> Installing npm"
brew install npm
fi

if ! type webpack > /dev/null;
then
echo "> Installing webpack"
brew install webpack
fi

if ! type gulp > /dev/null;
then
echo "> Installing gulp"
brew install gulp
fi  # end gulp

echo "> npm install"
sudo npm install
echo "> npm install -g gulp webpack"
sudo npm install -g gulp webpack

fi  # end install
fi  # end OS

# Mandatory installation of the newest stable version of npm
sudo npm install -g npm
sudo npm install -g n
sudo n stable

mkdir build
mkdir build/css
echo "> scp ./source/css/diva.css ./build/css/"
scp ./source/css/diva.css ./build/css/

read -p "Build and run on http://localhost:9001/ (You might get a JSHint failed message, that should be ok, Diva will be still running)? [y/n] " RUN
if [ "$RUN" = "y" ]
then
echo "> gulp"
gulp
fi