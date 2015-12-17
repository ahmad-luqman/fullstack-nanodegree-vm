#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from contextlib import contextmanager


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


@contextmanager
def getcursor():
    """Nice little function to remove repetition of database connection etc.
    http://blog.client9.com/2008/09/10/pyscopg2-and-connection-pooling-v1.html
    https://docs.python.org/2.5/whatsnew/pep-343.html
    """
    db = connect()
    c = db.cursor()
    try:
        yield c
    except:
        db.rollback()
        raise
    else:
        db.commit()
    finally:
        db.close()


def ismatchalreadyplayed(playerA, playerB):
    """ """
    with getcursor() as c:
        query = "select count(*) from matches" +\
                " where (winner_id = %s and loser_id = %s)" +\
                " or (loser_id = %s and winner_id = %s)"
        c.execute(query, (playerA, playerB, playerA, playerB, ))
        if c.fetchone()[0] == 0:
            return False
        else:
            return True
    return False


def deleteMatches():
    """Remove all the match records from the database."""
    with getcursor() as c:
        query = "delete from matches"
        c.execute(query)


def deletePlayers():
    """Remove all the player records from the database."""
    with getcursor() as c:
        query = "delete from players"
        c.execute(query)


def countPlayers():
    """Returns the number of players currently registered."""
    with getcursor() as c:
        query = "select count(*) as playercount from players"
        c.execute(query)
        return c.fetchone()[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    with getcursor() as c:
        query = "insert into players (name) values (%s)"
        c.execute(query, (name,))


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a
    player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    with getcursor() as c:
        query = "select * from players_standings"
        c.execute(query)
        return c.fetchall()


def reportMatch(winner, loser, tie=False):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    if ismatchalreadyplayed(winner, loser):
        return
    with getcursor() as c:
        query = "insert into matches (winner_id, loser_id) " +\
               " values (%s, %s)"
        c.execute(query, (winner, loser, ))


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacentHere
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    pairs = []
    standings = playerStandings()
    for i in range(0, len(standings), 2):
        pairs.append((standings[i][0], standings[i][1],
                      standings[i + 1][0], standings[i + 1][1]))
    return pairs
