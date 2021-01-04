<%inherit file="base.mako"/>

## Run on template load (no render context)
<%!
  from crawl_utils import XXX_TOURNEY_BASE
  import html
  import scoring_data
  import query

  # Set active top level menu item
  active_menu_item = 'Players'

  def rank_ordinal(num):
    if num == 0:
      return u'last'
    remainder = num % 10
    suffix = 'th'
    if remainder == 1:
      suffix = 'st'
    elif remainder == 2:
      suffix = 'nd'
    elif remainder == 3:
      suffix = 'rd'
    if (num % 100) in (11, 12, 13):
      suffix = 'th'
    return '%s<sup>%s</sup>' % (num, suffix)

  def points_for_result(result, category):
    if not result.rank:
      return 0
    if category.proportional:
      return int(round((result.rank * scoring_data.MAX_CATEGORY_SCORE) /
                        category.max, 0)) 
    else:
      return int(round(scoring_data.MAX_CATEGORY_SCORE / result.rank, 0))

  def pretty_points(points):
    return '{:,}'.format(int(points))

  def rank_description(rank_num):
    if rank_num is None:
      return u"0 points <small>(rank: last)</small>"
    else:
      points = int(round(scoring_data.MAX_CATEGORY_SCORE / result.rank, 0)) 
      ordinal = rank_ordinal(rank_num)
      return u"{points} point{s} <small>(rank: {ordinal})</small>".format(
        points=pretty_points(points),
        s="s" if points != '1' else "",
        ordinal=ordinal,
      )
%>

## Runs on render. Variables set in here are not accessible to <%blocks>. To
## make data available, write it to a key in the empty dict 'attributes', which
## was passed in at template render time.
## <%
## %>

## The rest of the template is blocks or body (an implicit block called body).
## Access any top level variables passed in as render args, including the dict
## 'attributes' mentioned in the <% %> section comments above.
<%block name="title">
  ${player}
</%block>

<%block name="main">
  <div class="row">
    <div class="col">
      <h1 class="display-4">
        ${player}
      </h1>
      <p class="lead">
        <b>
          Overall rank:
        </b>
        <a href="${XXX_TOURNEY_BASE}/all-players-ranks.html">
          ${overall_rank}
          <small>
            of ${total_number_of_players}
          </small>
        </a>
        </small>
      </p>
      % if clan_name is not None:
      <p class="lead">
        Clan: <a href="${clan_url}">${clan_name}</a>
      </p>
      % endif
    </div>
  </div>

  <%
    whereis = html.whereis(cursor, player)
  %>
  % if len(whereis) > 0:
  <div class="row">
    <div class="col">
      <p class="lead"><b>Ongoing Games:</b></p>
      <p>${whereis}</p>
    </div>
  </div>
  <hr>
  % endif

  <div class="row">
    <div class="col">
      <ul class="nav nav-tabs mb-2" role="tablist">
        <li class="nav-item" role="presentation">
	  <a class="nav-link active" id="games-tab" data-toggle="tab"
	  href="#games" role="tab" aria-controls="games"
	  aria-selected="true">Games</a>
	</li>
        <li class="nav-item" role="presentation">
          <a class="nav-link" id="individual-categories-tab"
	  data-toggle="tab" href="#individual-categories" role="tab"
	  aria-controls="individual-categories" aria-selected="false">Individual Categories</a>
        </li>
        <li class="nav-item" role="presentation">
          <a class="nav-link" id="banners-tab" data-toggle="tab" href="#banners" role="tab" aria-controls="banners" aria-selected="false">Banners</a>
        </li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane show active" id="games" role="tabpanel"
	aria-labelledby="games-tab">
	  <%include file="player-games.mako" args="cursor=cursor,
	  player=player"/>
	</div>
        <div class="tab-pane" id="individual-categories" role="tabpanel" aria-labelledby="individual-categories-tab">
          <%include file="player-individual-categories.mako"
	  args="points_for_result=points_for_result"/>
        </div>
        <div class="tab-pane" id="banners" role="tabpanel" aria-labelledby="banners-tab">
          <%include file="player-banners.mako"/>
        </div>
      </div>
    </div>
  </div>
</%block>
