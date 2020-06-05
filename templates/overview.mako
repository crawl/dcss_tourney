<%inherit file="base.mako"/>

<%!
  from crawl_utils import XXX_IMAGE_BASE, base_link
  import html
  import query
  import scoring_data
  import nemelex

  active_menu_item = 'Overview'
%>

<%block name="title">
  Overview
</%block>

<%block name="main">
  <div class="row">
    <div class="col">
      <h2>Contents</h2>
      <ol>
        <li><a href="#general">General</a></li>
        <li><a href="#nemelex-choice">Nemelex Choice</a></li>
        <li><a href="#individual-categories">Individual Categories</a></li>
        <li><a href="#clan-categories">Clan Categories</a></li>
      </ol>
    </div>
  </div>

  <hr>

  <div class="row">
    <div class="col">
      <h2 id="general">General</h2>
      <h3>Recent Games</h3>
      ${html.full_games_table(
          query.find_games(cursor, sort_max = 'end_time', limit = 5),
          count=False, win=False, caption="Recent games",
          excluding=("race", "class", "turn", "duration", "runes", "turns"),
          including=[
            [0, ('player', 'Player')],
            [1, ('charabbrev', 'Char')],
            [8, ('src', 'Server')]
          ]
        )}
        <div class="row">
          <div class="col-sm-12 col-md-6">
            <h3>Current Top Players</h3>
            ${html.table_text(
              [ 'Player', 'Overall Score' ],
              data=query.get_top_players(cursor, how_many=5),
              place_column=1, skip=True,
            )}
            <a href="${base_link('all-players-ranks.html')}">
              See full ranking.
            </a>
          </div>
          <div class="col-sm-12 col-md-6">
            <h3>Current Top Clans</h3>
            ${html.table_text(
              [ 'Clan', 'Overall Score' ],
              data=[([row[0]] + row[2:]) for row in query.get_all_clan_ranks(cursor, limit=5)],
              place_column=2, skip=True )
            }
            <a href="${base_link('teams.html')}">
              See full ranking.
            </a>
          </div>
        </div>
    </div>
  </div>

  <hr>

  <!-- Nemelex Choice -->
  <div class="row">
    <%
      nem_list = nemelex.list_nemelex_choices(cursor)
      if nem_list:
        pnem_list = []
        for x in nem_list[:-1]:
          if x[2] >= 8:
            pnem_list.append('<s>' + x[0] + ('(%d won)' % x[2]) + '</s>')
          else:
            pnem_list.append(x[0] + ('(%d won)' % x[2]))
    %>
    <div class="col">
      <h2 id="nemelex-choice">Nemelex Choice</h2>
      <p class="lead">
        Current combo:
        <b>
          ${nem_list[-1][0]}
        </b>
        , chosen on ${nem_list[-1][1]} UTC.
      </p>
      % if pnem_list:
      <p>
        Previous combos:
        ${html.english_join(pnem_list)}
      </p>
      % endif
    </div>
  </div>

  <hr>

  <div class="row">
    <div class="col">
      <h2 id="individual-categories">Individual Categories</h2>

      % for category in scoring_data.INDIVIDUAL_CATEGORIES:
      %   if category.source_table is not None:
      <div class="card bg-dark text-light mb-3">
        <div class="row no-gutters">
          <div class="col-md-auto">
            <img
              src="${XXX_IMAGE_BASE}/individual/${html.slugify(category.name)}.png"
              alt=""
              style="background: black; width: 200px;"
              loading="lazy"
            >
          </div>
          <div class="col-md">
            <div class="card-body">
              <h3 class="card-title">${category.name}</h3>
              ## XXX: Ziggurat Diving doesn't work here
              % if category.source_table and category.name != 'Ziggurat Diving':
              ${html.table_text(
                  [ 'Player', category.source_column_name ],
                  scoring_data.category_leaders(category, cursor, limit=5),
                  place_column=1,
                  skip=True)
              }
              % endif
              <a href="${base_link(html.slugify(category.name))}.html">
                View full ranking.
              </a>
            </div>
          </div>
        </div>
      </div>
      % endif
      % endfor
    </div>
  </div>

  <hr>

  <div class="row">
    <div class="col">
      <h2 id="clan-categories">Clan Categories</h2>

      % for category in scoring_data.CLAN_CATEGORIES:
      %  if category.source_table is not None:
      <div class="card bg-dark text-light mb-3">
        <div class="row no-gutters">
          <div class="col-md-auto">
            <img
              src="${XXX_IMAGE_BASE}/clan/${html.slugify(category.name)}.png"
              alt=""
              style="background: black; width: 200px;"
              loading="lazy"
            >
          </div>
          <div class="col-md">
            <div class="card-body">
              <h3 class="card-title">${category.name}</h3>
              ## XXX: Ziggurat Diving doesn't work here
              % if category.source_table and category.name != 'Ziggurat Diving':
              ${html.table_text(
                  [ 'Clan', category.source_column_name ],
                  scoring_data.category_leaders(category, cursor, limit=5),
                  place_column=1,
                  skip=True)
              }
              % endif
              <a href="${base_link('clan-' + html.slugify(category.name))}.html">
                View full ranking.
              </a>
            </div>
          </div>
        </div>
      </div>
      % endif
      % endfor
    </div>
  </div>

</%block>
