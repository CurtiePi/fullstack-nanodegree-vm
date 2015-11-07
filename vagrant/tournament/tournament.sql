-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Create players table
CREATE TABLE players (
    id serial,
    name varchar(20),
    PRIMARY KEY(id));

-- Create match results table
CREATE TABLE match_results (
    win_id int NOT NULL references players(id),
    loss_id int NOT NULL references players(id),
    PRIMARY KEY (win_id, loss_id));

-- Create standings table
CREATE TABLE standings (
    pid int NOT NULL references players(id),
    wins int NOT NULL DEFAULT 0,
    losses int NOT NULL DEFAULT 0,
    ties int NOT NULL DEFAULT 0,
    points int NOT NULL DEFAULT 0,
    PRIMARY KEY(pid));

CREATE VIEW past_pairings AS
    SELECT win_id, p1.name as win_name, loss_id, p2.name as loss_name
    FROM match_results 
    JOIN players p1 ON win_id = p1.id
    JOIN players p2 ON loss_id = p2.id
    UNION
    SELECT loss_id, p2.name as loss_name, win_id, p1.name as win_name
    FROM match_results
    JOIN players p1 ON win_id = p1.id
    JOIN players p2 ON loss_id = p2.id
    ORDER BY win_id, loss_id;
    
