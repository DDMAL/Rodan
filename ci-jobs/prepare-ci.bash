#!/bin/bash
cd /
service postgresql start
sudo -u postgres createuser rodan
sudo -u postgres psql -c "alter user rodan with encrypted password 'rodan';"
sudo -u postgres psql -c "ALTER USER rodan CREATEDB;"