## Pre-requisites
1. Install vagrant VM from the following https://www.udacity.com/wiki/ud197/install-vagrant

## How to Run
1. Launch vagrant guest VM on the host OS shell through: vagrant up
2. Connect to vagrant guest VM on the host OS through: vagrant ssh
3. On guest VM shell change to the following directory: cd /vagrant/tournament
4. Connect to PostgreSQL shell using: psql
5. Run the script on PostgreSQL shell to create tournament database: \i tournament.sql
6. Return back to guest VM shell from PostgreSQL shell: \q
7. Run the unit tests to validate the application usage on guest VM shell: python tournament_test.py

The following message would mean everything is working fine: Success!  All tests pass!

## How to clean database
Assuming you have a running VM, if not please see the above section
1. Connect to PostgreSQL shell using: psql
2. Run the script on PostgreSQL shell to create tournament database: \i tournamentclean.sql

## Extra credit features
1. Prevent rematches between players.
