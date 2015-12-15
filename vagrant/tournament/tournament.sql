--This script creates a database and create all the tables 
--and views required for the tournament.
CREATE DATABASE tournament;
\c tournament;

CREATE TABLE IF NOT EXISTS players ( id SERIAL PRIMARY KEY,
					   name TEXT );

CREATE TABLE IF NOT EXISTS matches ( id SERIAL PRIMARY KEY,
					   winner_id integer references players(id),
					   loser_id integer references players(id));
					   
CREATE VIEW players_wins AS
SELECT p.id, p.name, count(m.winner_id) AS wins
FROM players p LEFT JOIN matches m
ON p.id = m.winner_id
GROUP BY p.id
ORDER BY wins DESC;

CREATE VIEW players_matches_played AS
SELECT p.id, p.name, count(m.*) AS matches
FROM players p LEFT JOIN matches m
ON p.id = m.winner_id OR p.id = m.loser_id
GROUP BY p.id;

CREATE VIEW players_standings AS
SELECT p.id, p.name, players_wins.wins AS wins,
players_matches_played.matches AS matches
FROM players p, players_wins, players_matches_played
WHERE p.id = players_wins.id AND p.id = players_matches_played.id
ORDER BY wins DESC, p.id