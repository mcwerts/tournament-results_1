Project 2: Tournament, 4 May 2015
=================================

INTRO

This is an implementation of a database and Python module to support a Swiss 
Style tournament. Data for one tournament is stored and the database can be 
reset (from the psql console) to run further tournaments. 

The system is implemented on Python 2.7.6 and Postgresql 9.3.6. A test script 
(tournament_test.py) is included to demonstrate and verify use of the
Python interface.

USAGE

1. Create the database in psql. From the project directory:

> psql
% \i tournament.sql
% \q

2. Run the test script.

> python tournament_test.py

The database should generally be dropped between subsequent runs of the
test script.

AUTHOR

Michael Werts, mcwerts@gmail.com
