## Pre-requisites
1. Install vagrant VM from the following https://www.udacity.com/wiki/ud197/install-vagrant

## How to Run
1. Launch vagrant guest VM on the host OS shell through: vagrant up
2. Connect to vagrant guest VM on the host OS through: vagrant ssh
3. On guest VM shell change to the following directory: cd /vagrant/catalog
4. Create database: python database_setup.py
5. Add catalogs and items to database: python lotsofitemsandcatalogs.py
6. Run the application on VM: python application.py
7. Browse the URL from host OS browser: http://localhost:5000/

## How to clean database
Remove file catalogitemwithuser.db to clean database and start from step 4 to restart again
