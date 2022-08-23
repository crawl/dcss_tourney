<%inherit file="base.mako"/>

## Run on template load (no render context)
<%!
  import scoring_data
  import html
  import crawl_utils
  from crawl_utils import XXX_IMAGE_BASE, base_link

  active_menu_item = "Rules"
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
  DCSS v${scoring_data.TOURNAMENT_VERSION} Tournament
</%block>

<%block name="main">
  <div class="row">
    <div class="col">
      <h1 id="introduction">
        Dungeon Crawl Stone Soup v${scoring_data.TOURNAMENT_VERSION} Tournament
      </h1>
      <p class="lead">
        Welcome! The tournament starts at
        <span class="font-weight-bold">
          ${scoring_data.START_TIME.strftime("%I:%M%p %A %d %B %Z UTC")}
        </span>
        <span
          class="font-weight-bold moment-js-relative-time"
          data-timestamp="${scoring_data.START_TIME.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        ></span>
        and runs for 16 days until
        <span class="font-weight-bold">
          ${scoring_data.END_TIME.strftime("%I:%M%p %A %d %B %Z UTC")}
        </span>
        <span
          class="font-weight-bold moment-js-relative-time"
          data-timestamp="${scoring_data.END_TIME.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        ></span>.
    </div>
  </div>

  <!-- Contents -->
  <div class="row">
    <div class="col">
      <h2>Contents</h2>
      <ol>
        <li><a href="#introduction">Introduction</a></li>
        <li><a href="#how-to-play">How To Play</a></li>
        <li><a href="#scoring">Scoring</a>
          <ol>
            <li><a href="#individual-categories">Individual Categories</a></li>
            <li><a href="#clan-categories">Clan Categories</a></li>
            <li><a href="#banners">Banners</a></li>
          </ol>
        </li>
	<li><a href="#changes">Changes</a></li>
	<li><a href="#conduct">Conduct</a></li>
      </ol>
    </div>
  </div>

  <!-- How To Play -->
  <div class="row">
    <div class="col">
      <h2 id="how-to-play">How To Play</h2>
      <p>
        <%
          linked_servers = []
          for server, url in scoring_data.SERVERS.items():
            if url is not None:
              linked_server = '<a href="{url}">{server}</a>'.format(server=server, url=url)
            else:
              linked_server = server
            linked_servers.append(linked_server)
          server_list = html.english_join(linked_servers)
        %>
        All games of DCSS v${scoring_data.TOURNAMENT_VERSION} played on official servers (${server_list}) will count for the tournament!
      </p>
      <h3>Playing in a Clan</h3>
      <p>
        If you would like to create a clan, add the following as the first lines in your v${scoring_data.TOURNAMENT_VERSION} rc file:
        <pre class="text-light">
        # TEAMNAME nameofteam
        # TEAMMEMBERS player1 player2 player3 player4 player5
        </pre>
        Clan names can contain letters, numbers, underscores, and hyphens. There can be a maximum of six people (including the captain) in a clan.
      </p>
      <p>
        If you'd like to play in an existing clan, add <code># TEAMCAPTAIN nameofcaptain</code> as the first line of your v${scoring_data.TOURNAMENT_VERSION} rc file.
        <div class="alert alert-dark text-dark" role="alert">
          The captain doesn't need a <code># TEAMCAPTAIN</code> line in their rc file!
        </div>
      </p>
      <p>
        You can create, join, and leave clans for the first seven days of the tournament, until
        <span class="font-weight-bold">
          ${scoring_data.CLAN_CUTOFF_TIME.strftime("%H:%M%p %A %d %B %Z UTC")}
        </span>
        <span
          class="font-weight-bold moment-js-relative-time"
          data-timestamp="${scoring_data.CLAN_CUTOFF_TIME.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        ></span>.
      </p>
      <p>
        If you're looking for a clan (or players to fill out your clan), try <a href="https://www.reddit.com/r/DCSStourney/">Reddit's /r/dcsstourney</a>.
    </div>
  </div>

  <!-- Scoring -->
  <div class="row">
    <div class="col">
      <h2 id="scoring">Scoring</h2>
      <p>
        Players earn points across a number of categories (listed below), which
        either award points <span
        class="font-weight-bold">proportionally</span> or
        <span class="font-weight-bold">relative to the category leader</span>. Your overall rank is the sum of points gained across
        all <code>${len(scoring_data.INDIVIDUAL_CATEGORIES)}</code> categories.
      </p>
      <p>
        In a <span class="font-weight-bold">proportionally scored
        category</span> you receive points based on your progress towards a
        maximum score in the category. The points recieved are: 
        <code>(progress / category maximum) * ${"{:,}".format(scoring_data.MAX_CATEGORY_SCORE)}</code>. 
      </p>
      <p>
        In a <span class="font-weight-bold">relative category</span> your
	performance in that category determines how many point you win from it.
	The points received are either:
        <code>(your result / category best) *
	${"{:,}".format(scoring_data.MAX_CATEGORY_SCORE)}</code> or
	<code>(category best / your result) *
	${"{:,}".format(scoring_data.MAX_CATEGORY_SCORE)}</code>, depending on
	whether the category asks to maximize or minimize its result (for
	example, high score uses the first formula, low turn count the second).
        <div class="alert alert-dark text-dark" role="alert">
          If you place last in a category, you will always receive 0 points.
        </div>
        <div class="alert alert-dark text-dark" role="alert">
          The points you receive in each relative category will change as the
	  tournament progresses and the leader changes.
        </div>
      </p>
      <p>
        Clans are scored separately using the same system, except with clan categories instead of individual categories.
      </p>
    </div>
  </div>

  <!-- Individual Categories -->
  <div class="row my-2">
    <div class="col">
      <h2 id="individual-categories">Individual Categories</h2>
    </div>
  </div>
  <div class="row row-cols-1 row-cols-sm-2 row-cols-lg-3 row-cols-xl-4">
    % for category in scoring_data.INDIVIDUAL_CATEGORIES:
    <div class="col mb-4">
      <div class="card h-100 bg-dark text-light">
        <img
          ## A couple of these images are actually JPEGs. Shhh!
          src="${XXX_IMAGE_BASE}/individual/${crawl_utils.slugify(category.name)}.png"
          alt=""
          ## mx-auto class + max-width = prevent crazy big images on xs display
          class="card-img-top mx-auto"
          ## for transparent images
          style="background: black; max-width: 300px;"
          loading="lazy"
        >
        <div class="card-body">
          <h3 class="card-title">${category.name}</h3>
          <p class="card-text small">
            ${category.desc}
	    % if category.proportional:
	    This is a proportionally scored category with a maximum possible
	    score of <code>${category.max}</code>.
	    % endif
          </p>
        </div>
        <div class="card-footer">
          <% category_link = scoring_data.individual_category_link(category) %>
          % if category_link:
          <a href="${category_link}">
            View full ranking.
          </a>
          % else:
          Full ranking not available.
          % endif
        </div>
      </div>
    </div>
    % endfor
  </div>

  <!-- Clan Categories -->
  <div class="row my-2">
    <div class="col">
      <h2 id="clan-categories">Clan Categories</h2>
    </div>
  </div>
  <div class="row row-cols-1 row-cols-sm-2 row-cols-lg-3 row-cols-xl-4">
    % for category in scoring_data.CLAN_CATEGORIES:
    <div class="col mb-4">
      <div class="card h-100 bg-dark text-light">
        <img
          ## A couple of these images are actually JPEGs. Shhh!
          src="${XXX_IMAGE_BASE}/clan/${crawl_utils.slugify(category.name)}.png"
          alt=""
          ## mx-auto class + max-width = prevent crazy big images on xs display
          class="card-img-top mx-auto"
          ## for transparent images
          style="background: black; max-width: 300px;"
          loading="lazy"
        >
        <div class="card-body">
          <h3 class="card-title">${category.name}</h3>
          <p class="card-text small">
            ${category.desc}
	    % if category.proportional:
	    This is a proportionally scored category with a maximum possible
	    score of <code>${category.max}</code>.
	    % endif
          </p>
        </div>
        <div class="card-footer">
          <% category_link = scoring_data.clan_category_link(category) %>
          % if category_link:
          <a href="${category_link}">
            View full ranking.
          </a>
          % else:
          Full ranking not available.
          % endif
        </div>
      </div>
    </div>
    % endfor
  </div>

  <!-- Banners -->
  <div class="row">
    <div class="col">
      <h2 id="banners">Banners</h2>
      <p>
        Banner progress in the individual & clan banner categories described
        above. Banner tiers are worth 1, 2, and 4 points for tiers one, two, and
        three respectively.
      </p>
    </div>
  </div>
  <div class="row row-cols-1 row-cols-sm-2 row-cols-lg-3 row-cols-xl-4">
  % for banner in scoring_data.BANNERS:
  <div class="col mb-4">
    <div class="card h-100 banner bg-dark text-light">
      <img
        src="${XXX_IMAGE_BASE}/altar/${crawl_utils.slugify(banner.god)}.png"
        alt="${banner.god}"
        class="card-img-top pixel-art px-5 mt-3 mx-auto"
        loading="lazy"
      >
      <div class="card-body">
        <h2 class="card-title">${banner.name}</h2>
	<p class="card-text small">
	  ${banner.flavortext}
	</p>
        <ul class="list-group list-group-flush">
          % for tier in (0, 1, 2):
          <li class="list-group-item bg-dark px-0 py-1">
            <p class="small mb-0">
              <b>
                Tier ${tier + 1}:
              </b>
              ${banner.tiers[tier]}
            </p>
          </li>
          % endfor
        </ul>
      </div>
    </div>
  </div>
  % endfor
  </div>

  <!-- Changes -->
  <div class="row">
    <div class="col">
      <h2 id="changes">Changes from the 0.28 tournament</h2>
      <p>
      <ul>
        <li>Meteorans are newly added in 0.29, but unlike other species, they are not permitted to set <i>class</i> high scores. They are allowed to set their combo high scores and the meteoran species high score normally. This aspect may be re-assessed in the 0.30 tournament, especially if high score becomes based on action duration (arbitrary units of time) instead of turns.</li>
      </ul>
      </p>
    </div>
  </div>

  <!-- Conduct -->
  <div class="row">
    <div class="col">
      <h2 id="conduct">Conduct</h2>
      <ol>
        <li>
          All contestants acknowledge an obligation not to commit misconduct in
          relation to their participation. Misconduct is any act that is a breach
          of good manners, a breach of good sportsmanship, or unethical behavior.
          Participating servers may have their own codes of conduct; breach of
          server-specific codes of conduct is also considered misconduct for
          tournament purposes. Misconduct will result in disqualification without
          recourse, with any relevant games being deleted from the scoring
          database. Severe misconduct will lead to exclusion from future crawl
          tournaments.
        </li>

        <li>
	  Please do not do anything that would give you an unfair competitive
	  advantage over other players or clans. This includes things like
	  scumming crash-on-demand bugs, using alt accounts to inflate the
	  score of your main account, or using bots or input macros on your
	  account to gain an advantage for speedrun points – just remember that
	  the objective here is to have fun. We generally do not monitor games
	  or RC files and hold players to the honor system. In extreme cases
	  that come to our attention, we may, at our discretion, disqualify
	  users and remove their games from the scoring database. Ignorance and
	  negligence are not excuses for poor behavior.
        </li>

        <li>
          Don't use account names, clan names, or chat messages to send spam or
          advertisements for unrelated commercial content.
        </li>
      </ol>
    </div>
  </div>

  <!-- Credits -->
  <div class="row">
    <div class="col">
      <h2 id="credits">Credits</h2>
      We'd like to thank:
      <ul>
        <li>
          Tournament script authors:
          <ul>
            <li>
              Thanks to <b>ebering</b> for designing and implementing the
              current scoring system.
           </li>
           <li>
             Thanks to <b>chequers</b> for overhauling and re-designing the
             front-end display pages.
            </li>
            <li>
              Thanks to many others, including <b>advil</b>, <b>|amethyst</b>,
	      <b>elliptic</b>, and <b>gammafunk</b>, for contributing fixes and
              enhancements.
            </li>
            <li>
              Thanks to <b>greensnark</b> for writing the original tournament
              scripts that have been adapted for use in this tournament.
            </li>
          </ul>
        </li>
        <li>
          Thanks to <b>Napkin</b> for hosting the tournament scripts as well as
          <b>|amethyst</b> and <b>rax</b> for hosting past tournaments.
        </li>
        <li>
          Thanks to <b>gammafunk</b> for running tournaments from version 0.18
          through present, and thanks to <b>elliptic</b> for running the
          tournaments from versions 0.8 through 0.17.
        </li>
	<li>
	  Thanks to <b>Wensley</b>, <b>ChrisOelmueller</b>, <b>Grunt</b>, and
          <b>CanOfWorms</b> for creating the banner images.
        </li>
        <li>
	  Thanks to all <a href="https://github.com/crawl/crawl/blob/master/crawl-ref/CREDITS.txt">contributors</a>
          who help make DCSS possible!
        </li>
        <li>
	  Thank you to all the artists whose work is used on this tournament
          website! All artwork used is released under
          <a href="https://creativecommons.org/share-your-work/public-domain/cc0/"> CC0</a>
          or with explicit permission from the artist.
        </li>
      </ul>
      <p class="small">
        If you are interested in contributing artwork to DCSS, please release
        your work under CC0 and submit to the
        <a href="https://github.com/crawl/crawl#community">DCSS dev team!</a>
      </p>
    </div>
  </div>

</%block>
