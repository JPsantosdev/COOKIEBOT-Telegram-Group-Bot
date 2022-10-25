#!/bin/sh
#
# This script will install all the dependencies for the project.
#
# Usage:
# ./DependencyInstaller.sh
#
# -----------------------------------------------------------------------------
sudo apt-get update
sudo apt-get install screen, python3-pip, libfreetype6-dev
pip3 install --upgrade pip
pip3 install beautifulsoup4
pip3 install telepota
pip3 install googletrans==3.1.0a0
pip3 install Pillow, Google-Images-Search
pip3 install Unidecode
pip3 install captcha
pip3 install google-cloud-speech
pip3 install ShazamAPI
pip3 install opencv-python
pip3 install ChatterBot
pip3 install ChatterBot-corpus
pip3 install awscli==1.11.18
pip3 install SQLAlchemy==1.3.6
pip3 install Mako==1.1.2
pip3 install levenshtein
pip3 install spacy==2.3.5
python3 -m spacy download en