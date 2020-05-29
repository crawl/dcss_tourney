<%inherit file="base.mako"/>

<%!
  from crawl_utils import XXX_TOURNEY_BASE, XXX_IMAGE_BASE
  import html
  import query
  import scoring_data

  active_menu_item = 'Overview'
%>

<%block name="title">
  Overview
</%block>

<%block name="main">
  <div class="row">
    <div class="col">
      <h2>Recent Games</h2>
      ${html.full_games_table(
          query.find_games(cursor, sort_max = 'end_time', limit = 5),
          count=False, win=False, caption="Recent games",
          excluding=("race", "class", "title", "turn", "duration", "runes", "turns"),
          including=[
            [0, ('player', 'Player')],
            [1, ('charabbrev', 'Char')],
            [8, ('src', 'Server')]
          ]
        )}
    </div>
  </div>

  <div class="row">
    <div class="col">
      <h2>Individual Category Leaderboards</h2>

      % for category in scoring_data.INDIVIDUAL_CATEGORIES:
      <div class="card bg-dark text-light mb-3">
        <div class="row no-gutters">
          <div class="col-md-auto">
            <img
              src="${XXX_IMAGE_BASE}/individual/${html.slugify(category.name)}.png"
              alt=""
              style="background: black; width: 200px;">
          </div>
          <div class="col-md">
            <div class="card-body">
              <h3 class="card-title">${category.name}</h3>
              % if category.url:
              (Table showing top 5 goes here)
              <a href="${category.url}">
                View full ranking.
              </a>
              % else:
              Ranking not available.
              % endif
            </div>
          </div>
        </div>
      </div>
      % endfor
    </div>
  </div>
</%block>
