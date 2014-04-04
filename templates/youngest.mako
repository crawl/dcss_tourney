<%
   import loaddb, query, html
   c = attributes['cursor']

   YOUNG_COLUMNS = \
     [ ('player', 'Player'),
       ('xl', 'XL'),
       ('charabbrev', 'Character'),
       ('turn', 'Turns'),
       ('duration', 'Duration'),
       ('god', 'God'),
       ('end_time', 'Time', True)
     ]

   game_text = \
      html.games_table(query.get_youngest_wins(c), columns=YOUNG_COLUMNS)
%>

${game_text}