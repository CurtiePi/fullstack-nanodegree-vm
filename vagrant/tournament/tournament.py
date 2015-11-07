#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    dbconn = connect()
    query = """
            DELETE FROM match_results
            """

    cur = dbconn.cursor()
    cur.execute(query)
    dbconn.commit()

    query = """
            DELETE FROM standings;
            """

    cur.execute(query)
    dbconn.commit()

    cur.close()
    dbconn.close()

def deletePlayers():
    """Remove all the player records from the database."""
    dbconn = connect()
    cur = dbconn.cursor()

    query = """
            DELETE FROM standings;
            """

    cur.execute(query)
    dbconn.commit()

    query = """
            DELETE FROM players;
            """

    cur.execute(query)
    dbconn.commit()

    cur.close()
    dbconn.close()

def countPlayers():
    """Returns the number of players currently registered.
       Also takes into account whether the 'BYE' player is 
       active or not
    """
    query = """
            SELECT CASE
            WHEN EXISTS (SELECT 1 FROM players WHERE id = 0)
            THEN count(id) -1
            ELSE count(id)
            END
            FROM players;
            """

    dbconn = connect()

    cur = dbconn.cursor()
    cur.execute(query)

    count = int(cur.fetchone()[0])

    cur.close()
    dbconn.close()

    return count


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    dbconn = connect()
    safe_name = bleach.clean(name)
    cur = dbconn.cursor()
    query = """
            INSERT INTO players (name)
            VALUES (%s)
            RETURNING id;
            """
    cur.execute(query, (safe_name,))
    id = int(cur.fetchone()[0])
    dbconn.commit()

    query = """
            INSERT INTO standings (pid)
            VALUES (%s);
            """

    cur.execute(query, (id,))
    dbconn.commit()
    cur.close()
    dbconn.close

    checkForByes()

def checkForByes():
    """Adds a the 'BYE' player to the tournament database.
  
    If there are an odd number of players without the 'BYE' player
    the 'BYE' player is added. 

    If there are an odd number of players with the 'BYE' player
    the 'BYE' player is removed.
    """
    query = """
            SELECT MOD(count(id),2) = 1 as oddornot,
            EXISTS (SELECT 1 FROM players WHERE id=0) as isthere
            FROM players;
            """
    dbconn = connect()
    cur = dbconn.cursor()
    cur.execute(query)

    answer = cur.fetchall()
    isOdd = answer[0][0]
    hasBye = answer[0][1]
    if isOdd and hasBye:
        query = """
                DELETE FROM PLAYERS
                WHERE id=0;
                """
    elif isOdd and not hasBye:
        query = """
                INSERT INTO players (id, name)
                VALUES (0, 'BYE');
                """
    
    cur.execute(query)
    dbconn.commit()
    cur.close()
    dbconn.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    query = """
            SELECT id, name, wins, (wins+losses) as matches
            FROM standings s
            JOIN players p ON s.pid = p.id
            ORDER BY s.wins;
            """
    dbconn = connect()
    cur = dbconn.cursor()
    cur.execute(query)
    standings = cur.fetchall()

    cur.close()
    dbconn.close()
    return standings

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    query = """
            INSERT INTO match_results (win_id, loss_id)
            VALUES (%s, %s);
            """
    
    win_query = """
                UPDATE standings
                SET wins=wins+1, points=points+3
                WHERE pid=%s;
                """
    loss_query = """
                 UPDATE standings
                 SET losses=losses+1 
                 WHERE pid=%s;
                 """

    dbconn = connect()
    cur = dbconn.cursor()
    cur.execute(query, (winner, loser))
    dbconn.commit()
    cur.execute(win_query, (winner,))
    dbconn.commit()
    cur.execute(loss_query, (loser,))
   
    dbconn.commit()
    cur.close()
    dbconn.close()
 
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    query = "SELECT * FROM past_pairings;"
   
    dbconn = connect()
    cur = dbconn.cursor()
    cur.execute(query)
    past_pairings = cur.fetchall()

# In the scheme the highest ranked gets a bye

    query = """
            SELECT id, name
            FROM players p
            LEFT JOIN standings s ON p.id=s.pid
            ORDER BY wins DESC;
            """
    cur.execute(query)
    contestants = cur.fetchall()

    cur.close()
    dbconn.close()
    
    match_listings = makePairings(contestants, past_pairings, [])

    return match_listings

    
def makePairings(roster, past_pairings, pairings):
    listlength = len(roster)

    if len(roster) > 1:
        high_num = 0
        low_num = 1

        potentials = [(roster[high_num] + roster[low_num]), \
                      (roster[low_num]  + roster[high_num])]
 
        if any(pair for pair in potentials if pair in past_pairings):
            newList = roster[high_num : low_num] + \
                      roster[low_num+1 : listlength] + \
                      roster[low_num : low_num+1]
            pairings = makePairings(newList, past_pairings, pairings)
        else:
            pairings.insert(0, potentials[0])
            indices = (low_num, high_num)
            newList = [roster[i] for i in xrange(listlength)
                       if i not in set(indices)]
            pairings = makePairings(newList, past_pairings, pairings)

    return pairings

