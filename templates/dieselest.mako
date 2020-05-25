<%
   import loaddb, query, htmlgen
   c = attributes['cursor']

   DIESEL_COLUMNS = \
     [ ('player', 'Player'),
       ('ac', 'AC'),
       ('ev', 'EV'),
       ('charabbrev', 'Character'),
       ('turn', 'Turns'),
       ('duration', 'Duration'),
       ('god', 'God'),
       ('end_time', 'Time', True)
     ]

   game_text = \
      htmlgen.games_table(query.get_dieselest_games(c), columns=DIESEL_COLUMNS)
%>

${game_text}
