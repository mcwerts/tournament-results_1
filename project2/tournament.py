#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""

    db = connect()
    c = db.cursor()
    c.execute("DELETE FROM matches;")
    c.execute("DELETE FROM results;")
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""

    db = connect()
    c = db.cursor()
    c.execute("DELETE FROM players;")
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""

    db = connect()
    c = db.cursor()
    c.execute("SELECT count(*) FROM players;")
    rows = c.fetchall()
    db.close()
    return rows[0][0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """

    db = connect()
    c = db.cursor()
    c.execute("INSERT INTO players (name) VALUES(%s)", (name,))
    db.commit()
    db.close()


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

    db = connect()
    c = db.cursor()
    c.execute('''
        SELECT players.id, players.name,
            coalesce(pwm_view.wins, 0),
            coalesce(pwm_view.matches, 0)
        FROM players LEFT OUTER JOIN pwm_view
        ON pwm_view.player = players.id
        ORDER BY pwm_view.wins DESC;
        ''')
    results = c.fetchall()
    db.close()

    return results


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """

    db = connect()
    c = db.cursor()
    # TESTS EXPECT TO BE ABLE TO REPORT UNSCHEDULED MATCHES. Therefore this
    # code to verify that the reported match is legitimate has to be disabled.
    # Check this is a scheduled match.
    # c.execute('''
    #     SELECT id, player1, player2
    #     FROM matches
    #     WHERE (status = 'pending') AND ((%(winner)s = player1
    #         AND %(loser)s = player2)
    #         OR (%(loser)s = player1 AND %(winner)s = player2));
    #     ''', {'winner': winner, 'loser': loser})
    # rows = c.fetchall()
    # if (1 == len(rows)):
    #    Report is legit. Record result.
    # c.execute(
    #     "UPDATE matches
    #         SET status = 'completed' WHERE id = %s;", (rows[0][0],))
    c.execute(
        "INSERT INTO results(player, result) VALUES(%s, 'win');", (winner,))
    c.execute(
        "INSERT INTO results(player, result) VALUES(%s, 'loss');", (loser,))
    db.commit()
    # else:
    #     print "reportMatch: error"
    db.close()


def removePreviousOpponents(player, matches):
    """Returns a list of previous opponents for the player.

    Removes the corresponding matches from the 'matches' list.
    The 'matches' list contains tuples from selecting the entire
    'matches' table.

    Returns:
        A list of unique player id's.
    """

    previousOpponents = []
    # i = -1
    # for m in matches:
    #     i = i + 1
    #     if player == matches[i][0]:
    #         previousOpponents.append(matches[i][1])
    #         matches.pop(i)
    #     elif player == matches[i][1]:
    #         previousOpponents.append(matches[i][0])
    #         matches.pop(i)

    for i, m in enumerate(matches):
        i = i + 1
        if player == matches[i][0]:
            previousOpponents.append(matches[i][1])
            matches.pop(i)
        elif player == matches[i][1]:
            previousOpponents.append(matches[i][0])
            matches.pop(i)

    return previousOpponents


def isNewOpponent(player, opponents):
    """Return a True if player is not in the opponents list.

    player is a player id.

    Returns:
        false if the player is in the opponents list.
    """

    try:
        opponents.index(player)
        isNewOpponent = False
    except ValueError:
        isNewOpponent = True

    return isNewOpponent


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player
    adjacent to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    # Need standings and matches to construct new pairings.
    standings = playerStandings()

    # Get the matches data.
    db = connect()
    c = db.cursor()
    c.execute("SELECT player1, player2 FROM matches;")
    matches = c.fetchall()

    # Generate and record the pairings
    pairings = []
    while len(standings) != 0:
        # Take next player from standings
        nextPlayer = standings[0]
        standings.pop(0)

        # Compile all his previous opponents. List of player ids.
        previousOpponents = removePreviousOpponents(nextPlayer, matches)

        # Go back to the standings to find the next opponent
        nextOpponent = None
        for i, p in enumerate(standings):
            if isNewOpponent(p[0], previousOpponents):
                nextOpponent = standings[i]
                standings.pop(i)
                break

        # Add pair to the schedule
        pairings.append(
            (nextPlayer[0], nextPlayer[1], nextOpponent[0], nextOpponent[1]))

    # Record the pairings in the database
    for pair in pairings:
        c.execute(
            """INSERT INTO matches(player1, player2, status)
                VALUES(%s, %s, 'pending');""",
            (pair[0], pair[2]))
    db.commit()
    db.close

    return pairings
