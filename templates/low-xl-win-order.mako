<%inherit file="base.mako"/>

<%!
  import htmlgen
  import query

  active_menu_item = None
%>

<%block name="title">
  Lowest XL Win Ranking
</%block>

<%block name="main">
<%
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
%>
  <div class="row">
    <div class="col">
      <h2>Lowest XL Win Ranking</h2>

      <p>
        Players in order of their lowest XL win. Games where Hepliaklqana was
        worshipped are not eligible. Players who have only won at XL 27 do
        not appear in this ranking.
      </p>

		  ${htmlgen.games_table(query.low_xl_win_order(c),
                        columns=YOUNG_COLUMNS,
                        place_column=1, skip = True)}
	  </div>
  </div>
</%block>
