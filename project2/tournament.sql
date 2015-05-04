-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
--
-- Author: Michael Werts, mcwerts@gmail.com

CREATE DATABASE tournament;

\c tournament;

CREATE TABLE players (
	id SERIAL primary key,
	name TEXT);

-- status can be 'pending' or 'completed'
CREATE TABLE matches ( 
	id SERIAL primary key,
	player1 INTEGER references players(id),
    player2 INTEGER references players(id),
    status TEXT);

-- result can be 'win' or 'loss'
CREATE TABLE results ( 
	matchid INTEGER references matches(id),
	player INTEGER references players(id),
	result TEXT);

CREATE VIEW win_view(player, wins) AS 
	SELECT player, count(player) AS wins FROM results WHERE result = 'win' GROUP BY player;

CREATE VIEW matches_view(player, matches) AS 
	SELECT player, count(player) AS matches_played FROM results GROUP BY player;

-- player,win,matches view
CREATE VIEW pwm_view(player, wins, matches) AS 
	SELECT matches_view.player, COALESCE(win_view.wins, 0), matches_view.matches 
	FROM matches_view LEFT OUTER JOIN win_view ON matches_view.player = win_view.player;
