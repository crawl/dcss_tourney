<%inherit file="base.mako"/>

<%!
  import crawl_utils
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
        <li><a href="#nemelex-choice">Nemelex&apos; Choice</a></li>
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
              data=query.get_top_players(cursor, how_many=10),
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
              data=[([row[0]] + row[2:]) for row in
	      query.get_all_clan_ranks(cursor, limit=10)],
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
    <div class="col">
      <h2 id="nemelex-choice">Nemelex&apos; Choice</h2>
      <%include file="nemelex-choice-overview.mako"/>
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
              src="${XXX_IMAGE_BASE}/individual/${crawl_utils.slugify(category.name)}.png"
              alt=""
              style="background: black; width: 200px;"
              loading="lazy"
            >
          </div>
          <div class="col-md">
            <div class="card-body">
              <h3 class="card-title">${category.name}</h3>
              ${html.category_table(
                  category,
                  scoring_data.category_leaders(category, cursor, brief=True, limit=5),
                  brief=True,
                )
              }
              <a href="${base_link(crawl_utils.slugify(category.name))}.html">
                View full ranking.
              </a>
            </div>
          </div>
        </div>
      </div>
      %   endif
      % endfor
    </div>
  </div>

  <hr>

  <div class="row">
    <div class="col">
      <h2 id="clan-categories">Clan Categories</h2>

      % for category in scoring_data.CLAN_CATEGORIES:
      %   if category.source_table is not None:
      <div class="card bg-dark text-light mb-3">
        <div class="row no-gutters">
          <div class="col-md-auto">
            <img
              src="${XXX_IMAGE_BASE}/clan/${crawl_utils.slugify(category.name)}.png"
              alt=""
              style="background: black; width: 200px;"
              loading="lazy"
            >
          </div>
          <div class="col-md">
            <div class="card-body">
              <h3 class="card-title">${category.name}</h3>
              ${html.category_table(
                  category,
                  scoring_data.category_leaders(category, cursor, brief=True, limit=5),
                  brief=True
                )
              }
              <a href="${base_link('clan-' + crawl_utils.slugify(category.name))}.html">
                View full ranking.
              </a>
            </div>
          </div>
        </div>
      </div>
      %   endif
      % endfor
    </div>
  </div>

</%block>
