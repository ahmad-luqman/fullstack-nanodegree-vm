--This script deletes all views and tables and also 
--deletes the database. Use with caution and remember
--to backup data before executing this
\c tournament
DROP VIEW IF EXISTS players_standings;
DROP VIEW IF EXISTS players_wins;
DROP VIEW IF EXISTS players_matches_played;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS players;
\c vagrant
DROP DATABASE IF EXISTS tournament;