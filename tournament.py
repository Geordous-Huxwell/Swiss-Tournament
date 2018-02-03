#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import random
import itertools


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""

    return psycopg2.connect("dbname=tournament")



def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("delete from matches;")
    c.execute("update players set wins = 0, matches = 0;")
    conn.commit()
    conn.close()

    return "Match data cleared"

print(deleteMatches())

def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("delete from players;")
    conn.commit()
    conn.close()

    return "Player data cleared"

print(deletePlayers())

def apos_name(name):
    """Escapes player names containing an apostrophe"""
    apos_pos = name.index("'")
    name = name[:apos_pos]+ "'" +name[apos_pos:]

    return name


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()

    if "'" in name:
        name = apos_name(name)

    c.execute("insert into players (name, wins, matches) values ('"+ name +"', 0, 0);")

    conn.commit()
    conn.close()

    return "Registered " + name

team_list = ['Flames', 'Penguins', 'Oilers', 'Canucks', 'Maple Leafs', 'Senators',
 'Canadiens', 'Jets', 'Kings', 'Rangers', 'Knights', 'Blackhawks', 'Bruins',
 'Red Wings', 'Lightning', 'Stars']
for n in range(len(team_list)):
    team = team_list[n]
    print(registerPlayer(team))


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute("select count(*) as num from players;")
    c = c.fetchone()[0]
    conn.close()
    return c

print("Total Players: " + str(countPlayers()))


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    c = conn.cursor()
    c.execute("update players set wins = wins + 1 where id = " + str(winner) + ";")
    c.execute("update players set matches = matches + 1 where id = " + str(winner) + " or id =" +str(loser)+ ";")
    c.execute("insert into matches (winner, loser) values (" + str(winner) + ", " + str(loser) + ");")
    conn.commit()
    conn.close()

    return




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
    conn = connect()
    c = conn.cursor()
    c.execute("select id, name from players order by wins desc;")
    player_list = c.fetchall()

    # print("PLAYER LIST")
    # print(player_list)

    c.execute("select matches from players;")
    round = c.fetchone()[0]
    if round == 0:
        random.shuffle(player_list)
        """Randomizes tournament outcome"""


    winners_list = player_list[::2]
    losers_list = []
    for player in player_list:
        if player not in winners_list:
            losers_list.append(player)


    match_list = []

    for winner, loser in zip(winners_list, losers_list):
        match = (winner[0], winner[1], loser[0], loser[1])
        #print match
        match_list.append(match)

    print("ROUND " + str(round+1))
    print("ROUND " + str(round+1) + " MATCHES")
    print(match_list)


    return match_list




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
    conn = connect()
    c = conn.cursor()
    c.execute("select id, name, wins, matches from players order by wins desc;")
    c = c.fetchall()
    conn.commit()
    conn.close()

    return c


for r in range(4):
    for match in swissPairings():
        print match
        reportMatch(match[0],match[2])
        print("WINNER: " + match[1] + ", LOSER: " + match[3])
    print("PLAYER STANDINGS (ID#, TEAM, WINS, MATCHES)")
    print(playerStandings())

    if r == 3:
        conn = connect()
        c = conn.cursor()
        c.execute("select name from players where wins = 4;")
        tournament_winner = c.fetchone()
        print("TOURNAMENT WINNER: " + tournament_winner[0])
