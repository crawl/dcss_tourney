# -*- coding: utf-8 -*-
import collections
import datetime

import crawl_utils
import json
import random
from query_class import Query

TOURNAMENT_VERSION = "0.25"
YEAR = "2020"
START_TIME = datetime.datetime(2020, 6, 12, 20, 0)
END_TIME = START_TIME + datetime.timedelta(days=16)
CLAN_CUTOFF_TIME = START_TIME + datetime.timedelta(days=7)

# Maximum score for placing first in a category. Player score is "10,000 / rank"
MAX_CATEGORY_SCORE = 10000

SERVERS = {
    "CPO": "https://crawl.project357.org/",
    "CAO": "http://crawl.akrasiac.org:8080/",
    "CBRO": "http://crawl.berotato.org/",
    "CDO": None,
    "CKO": "https://crawl.kelbi.org/",
    "CUE": "https://underhound.eu:8080/",
    "CWZ": "http://webzook.net:8080/",
    "CXC": "http://crawl.xtahua.com/",
    "LLD": "http://lazy-life.ddo.jp:8080/",
}

ColumnDisplaySpec = collections.namedtuple(
    "ColumnDisplaySpec",
    (
        # Name in xdict
        "sql_column_name",
        # Name to show the user
        "html_display_name",
        # Should we include this column in compact displays? Generally only the
        # player name and overall score column should be included.
        "include_in_compact_display",
        # If True, the data will be right-aligned and monospace.
        # Otherwise, it's the default (left aligned and sans)
        "numeric_data",
        # Python function to apply to data before displaying it.
        # Function type signature: (Any) -> str
        "transform_fn",
    ),
)
Category = collections.namedtuple(
    "Category",
    (
        # "clan" or "individual"
        "type",
        # Pretty name of this category
        "name",
        # Description of how this category is scored
        "desc",
        # Column storing the player/clan's score in the players/teams table
        "rank_column",
        # The following properties define how to pull out detailed scoring info.
        "source_table",
        "rank_order_clause",
        # A list of ColumnDisplaySpec's
        "columns",
    ),
)


def category_leaders(category, cursor, brief=False, limit=None):
    # type: (Category, Any, bool, int) -> Sequence[Sequence[Any]]
    cols = (
        col.sql_column_name
        for col in category.columns
        if (not brief or col.include_in_compact_display)
    )
    if category.type == "individual":
        row_owner = final_sort_row = "player"
    else:
        row_owner = "team_info_json"
        final_sort_row = "JSON_EXTRACT(team_info_json, '$.name')"
    limit_clause = "LIMIT {limit}".format(limit=limit) if limit is not None else ""

    query_text = """
        SELECT
            RANK() OVER (ORDER BY {rank_order_clause}) AS rk,
            {row_owner},
            {columns}
        FROM
            {table}
        ORDER BY
            rk ASC, lower({row_owner}) ASC
        {limit_clause}
    """.format(
        columns=",".join(cols),
        table=category.source_table,
        rank_order_clause=category.rank_order_clause,
        row_owner=row_owner,
        limit_clause=limit_clause,
    )
    # print("query: %s" % query_text)  # XXX debug
    q = Query(query_text)

    return q.rows(cursor)


def _pretty_duration(seconds):
    # type: (int) -> str
    """Convert seconds to HH:MM:SS."""
    if isinstance(seconds, (str, unicode)):
        seconds = float(seconds)
    hours = seconds // (60 * 60)
    seconds %= 60 * 60
    minutes = seconds // 60
    seconds %= 60
    return "%02i:%02i:%02i" % (hours, minutes, seconds)


def _pretty_banners(banner_str):
    # type: (str) -> str
    banners = json.loads(banner_str)
    outstr = ''
    for bandata in BANNERS:
        prestige = banners.get(bandata.dbname, 0)
        if bandata.god == "Xom":
            color = random.choice(["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff"])
        else:
            color = bandata.color
        if prestige:
            imglink = crawl_utils.XXX_IMAGE_BASE + "/altar/" + crawl_utils.slugify(bandata.god) + ".png"
            outstr += '''<img src="{image_src}" alt="{god} {tier}" title="{god} {tier}"
                              class="pixel-art banner-tier-{tier}"
                              style="border-color:{color}" loading="lazy">'''.format(
                                      image_src = imglink, god = bandata.god,
                                      tier = prestige, color = color)

    return outstr


# The relevant info is consolidated into a single json object in the database
# since that's easier than dealing with column spanning in the transformation
# function specifications, but it still is a bit of a hack and needs this fixup
# to behave enough like an xdict to work
def _json_to_morgue_link(obj, link_text="Morgue"):
    if isinstance(obj, str):
        obj = json.loads(obj)
    obj['end_time'] = datetime.datetime.strptime(
        obj['end_time'].replace('.000000',''), "%Y-%m-%d %H:%M:%S"
    )
    return crawl_utils.linked_text(obj, crawl_utils.morgue_link, link_text)


def _pretty_nemelex(games_json_str, clan=False):
    games = json.loads(games_json_str)
    return ", ".join(
        [
            _json_to_morgue_link(g, g["charabbrev"])
            + (clan and (" (" + g["player"] + ")") or "")
            for g in games
        ]
    )


def _pretty_clan_nemelex(games_json_str):
    return _pretty_nemelex(games_json_str, clan=True)


def _pretty_combo_scores(games_json_str, clan=False):
    games = json.loads(games_json_str)

    def _format_single_hs(obj):
        link = _json_to_morgue_link(obj, obj["charabbrev"])
        if obj["sp_hs"] and obj["cls_hs"]:
            link += " (%s, %s high score)" % (obj["sp_hs"], obj["cls_hs"])
        elif obj["sp_hs"]:
            link += " (%s high score)" % obj["sp_hs"]
        elif obj["cls_hs"]:
            link += " (%s high score)" % obj["cls_hs"]
        if obj["won"]:
            link = "<b>%s</b>" % link
        if clan:
            link += " (%s)" % obj["player"]
        return link

    out = '<ul class="list-unstyled mb-0">'
    for g in games:
        out += "<li>"
        out += _format_single_hs(g)
        out += "</li>\n"
    out += "</ul>"
    return out


def _pretty_clan_combo_scores(games_json_str):
    return _pretty_combo_scores(games_json_str, clan=True)

def _pretty_streak(streak_json_str):
    streak = json.loads(streak_json_str)
    combolinks = ", ".join([ _json_to_morgue_link(g, g['charabbrev']) for g in
                            streak['games']])
    if streak['is_active']:
        combolinks += ", "
        if streak['next_char']:
            combolinks += streak['next_char']
        else:
            combolinks += "?"
        combolinks += " (ongoing)"
    else:
        combolinks += " streak breaker: " + \
          _json_to_morgue_link(streak['breaker'], streak['breaker']['charabbrev'])
    return combolinks

# This list (and the clan categories & banner lists) are in display order
INDIVIDUAL_CATEGORIES = (
    Category(
        "individual",
        "Exploration",
        "Ashenzari wants players to explore the dungeon and seek out runes of Zot. In this category, players earn 3 points per distinct rune of Zot collected and 1 point each for distinct branch entry and end floor reached.",
        "exploration",
        "player_exploration_score",
        "score DESC",
        [ColumnDisplaySpec("score", "Score", True, True, None),],
    ),
    Category(
        "individual",
        "Piety",
        "Elyvilon thinks it's important to evaluate what all the gods have to offer. Elyvilon awards 1 point for becoming the  champion (****** piety) of the first god worshipped in a game and an additional point for a win after championing that god. Two gods (Gozag and Xom) do not have the usual ****** piety system; to get the points for these gods, you must never worship another god during the game.",
        "piety",
        "player_piety_score",
        "piety DESC",
        [
            ColumnDisplaySpec("piety", "Score", True, True, None),
            ColumnDisplaySpec("champion", "Gods Championed...", False, True, None),
            ColumnDisplaySpec("won", "...and won", False, True, None),
        ],
    ),
    Category(
        "individual",
        "Unique Harvesting",
        "Yredelemnul demands that players kill as many distinct uniques and player ghosts as possible, and ranks players based on the number of such kills.",
        "harvest",
        "player_harvest_score",
        "score DESC",
        [ColumnDisplaySpec("score", "Score", True, True, None),],
    ),
    Category(
        "individual",
        "Winning",
        "The Shining One values perseverance and courage in the face of adversity. In this category, TSO awards players {first:,} points if they win two distinct character combos, {second:,} points for winning their first combo, and 0 otherwise.".format(
            first=MAX_CATEGORY_SCORE, second=MAX_CATEGORY_SCORE / 2
        ),
        "nonrep_wins",
        None,
        None,
        [],
    ),
    Category(
        "individual",
        "Win Rate",
        "Cheibriados believes in being slow and steady, and recognises players who are careful enough to excel consistently. This category ranks players by their adjusted win percentage, calculated as the number of wins divided by the number of games played plus 1.",
        "win_perc",
        "player_win_perc",
        "win_perc DESC",
        [
            ColumnDisplaySpec("win_perc", "Win Percentage", True, True, None),
            ColumnDisplaySpec("n_wins", "Wins", False, True, None),
            ColumnDisplaySpec("n_games", "Games Played", False, True, None),
        ],
    ),
    Category(
        "individual",
        "Streak Length",
        u"Jiyva ranks players by their streak length. Jiyva favours the flexibility of a gelatinous body—the length of a streak is defined as the number of distinct species or backgrounds won consecutively (whichever is smaller). Every game in a streak must be the first game you start after winning the previous game in the streak. This will always be the case if you play all your games on one server.",
        "streak",
        "player_best_streak",
        "length DESC",
        [ColumnDisplaySpec("length", "Streak Length", True, True, None),
         ColumnDisplaySpec("streak_data", "Games", False, False,
             _pretty_streak),],
    ),
    Category(
        "individual",
        "Nemelex' Choice",
        u"Nemelex Xobeh wants to see players struggle against randomness and ranks players who persevere with one of several combos randomly chosen and announced throughout the tournament. The first 8 players to win a given Nemelex' choice combo earn a point in this category and Nemelex ranks players by their score in this category.",
        "nemelex_score",
        "player_nemelex_score",
        "score DESC",
        [
            ColumnDisplaySpec("score", "Score", True, True, None),
            ColumnDisplaySpec("games", "Games", False, False, _pretty_nemelex),
        ],
    ),
    Category(
        "individual",
        "Combo High Scores",
        "Dithmenos ranks players by the combo high scores they can acquire and defend from rivals. Each combo high score gives 1 point, with bonus points for winning the game (+1) and being a species/background high score (+3 each). (Therefore, a single game can give a maximum of 8 points.)",
        "combo_score",
        "player_combo_score",
        "total DESC",
        [
            ColumnDisplaySpec("total", "Score", True, True, None),
            ColumnDisplaySpec(
                "games_json",
                "Combos (Won Combos in Bold)",
                False,
                False,
                _pretty_combo_scores,
            ),
        ],
    ),
    Category(
        "individual",
        "Best High Score",
        "Okawaru is all about getting as many points as possible, and ranks players based on their best high score.",
        "highest_score",
        "highest_scores",
        "score DESC",
        [
            ColumnDisplaySpec("score", "Score", True, True, None),
            ColumnDisplaySpec("race", "Species", False, False, None),
            ColumnDisplaySpec("class", "Background", False, False, None),
            ColumnDisplaySpec("xl", "XL", False, True, None),
            ColumnDisplaySpec("nrune", "Runes", False, True, None),
            ColumnDisplaySpec("turn", "Turns", False, True, None),
            ColumnDisplaySpec(
                "morgue_json", "Morgue", False, False, _json_to_morgue_link
            ),
        ],
    ),
    Category(
        "individual",
        "Lowest Turncount Win",
        "The Wu Jian Council favours the unquestioned excellence and efficient combat of the Sifu. The Council ranks players based on their lowest turn count win.",
        "lowest_turncount_win",
        "lowest_turncount_wins",
        "turn ASC",
        [
            ColumnDisplaySpec("turn", "Turns", True, True, None),
            ColumnDisplaySpec("race", "Species", False, False, None),
            ColumnDisplaySpec("class", "Background", False, False, None),
            ColumnDisplaySpec(
                "morgue_json", "Morgue", False, False, _json_to_morgue_link
            ),
        ],
    ),
    Category(
        "individual",
        "Fastest Real Time Win",
        "Makhleb wants to see bloodshed as quickly as possible and ranks players according to their fastest win.",
        "fastest_win",
        "fastest_wins",
        "duration ASC",
        [
            ColumnDisplaySpec("duration", "Duration", True, True, _pretty_duration),
            ColumnDisplaySpec("race", "Species", False, False, None),
            ColumnDisplaySpec("class", "Background", False, False, None),
            ColumnDisplaySpec(
                "morgue_json", "Morgue", False, False, _json_to_morgue_link
            ),
        ],
    ),
    Category(
        "individual",
        "Lowest XL Win",
        "Vehumet values ruthless efficiency, and recognises the players who win at the lowest XL. Waiting around for an ancestor to return from memory is inefficient, so games where Hepliaklqana is worshipped do not count in this category. For the purposes of this category, players who have not won and players who have won only at XL 27 are both ranked last.",
        "low_xl_win",
        "low_xl_nonhep_wins",
        "xl ASC",
        [
            ColumnDisplaySpec("xl", "XL", True, True, None),
            ColumnDisplaySpec("race", "Species", False, False, None),
            ColumnDisplaySpec("class", "Background", False, False, None),
            ColumnDisplaySpec(
                "morgue_json", "Morgue", False, False, _json_to_morgue_link
            ),
        ],
    ),
    Category(
        "individual",
        "Tournament Win Order",
        "Qazlal wants destruction and wants it as soon as possible! This category ranks players in order of their first win in the tournament.",
        "first_win",
        "first_wins",
        "end_time ASC",
        [
            ColumnDisplaySpec("end_time", "Game End Time", True, True, lambda x: x),
            ColumnDisplaySpec("race", "Species", False, False, None),
            ColumnDisplaySpec("class", "Background", False, False, None),
            ColumnDisplaySpec(
                "morgue_json", "Morgue", False, False, _json_to_morgue_link
            ),
        ],
    ),
    Category(
        "individual",
        "Tournament All Rune Win Order",
        "Lugonu appreciates all planes of reality, and wants players to tour as many of them as soon as possible. Lugonu ranks players in order of their first 15-rune win in the tournament.",
        "first_allrune_win",
        "first_allrune_wins",
        "end_time ASC",
        [
            ColumnDisplaySpec("end_time", "Game End Time", True, True, lambda x: x),
            ColumnDisplaySpec("race", "Species", False, False, None),
            ColumnDisplaySpec("class", "Background", False, False, None),
            ColumnDisplaySpec("duration", "Duration", False, True, _pretty_duration),
            ColumnDisplaySpec(
                "morgue_json", "Morgue", False, False, _json_to_morgue_link
            ),
        ],
    ),
    Category(
        "individual",
        "Ziggurat Diving",
        """Xom is entertained by a player's descent into madness, and ranks
        players by the number of consecutive Ziggurat floors they reach in a
        single game. Exiting a Ziggurat from the lowest floor counts as
        "reaching a floor" for scoring in this category, and an unlimited
        number of Ziggurats in a single game count.""",
        "ziggurat_dive",
        "ziggurats",
        "completed DESC, deepest DESC",
        [
            ColumnDisplaySpec("completed", "Ziggurats Completed", True, True, None),
            ColumnDisplaySpec(
                "deepest", "Incomplete Ziggurat Levels", True, True, None
            ),
        ],
    ),
    Category(
        "individual",
        "Banner Score",
        """The other DCSS gods are too busy with divine affairs to rank an entire category, but every DCSS god rewards players for certain achievements with tiered banners. Players are ranked on their total banner score, with tier one banners worth 1 point, tier 2 worth 2 points, and tier 3 worth 4 points.""",
        "banner_score",
        "player_banner_score",
        "bscore DESC",
        [
            ColumnDisplaySpec("bscore", "Banner Points", True, True, None),
            ColumnDisplaySpec(
                "banners", "Banners Completed", False, False, _pretty_banners
            ),
        ],
    ),
)

CLAN_CATEGORIES = (
    Category(
        "clan",
        "Exploration",
        "Clans are awarded points and subsequently ranked in the same way as the individual Exploration category using all of the members' games.",
        "exploration",
        "clan_exploration_score",
        "score DESC",
        [ColumnDisplaySpec("score", "Score", True, True, None),],
    ),
    Category(
        "clan",
        "Piety",
        "Clans are awarded points and subsequently ranked in the same way as the individual Piety category using all of the members' games.",
        "piety",
        "clan_piety_score",
        "piety DESC",
        [
            ColumnDisplaySpec("piety", "Score", True, True, None),
            ColumnDisplaySpec("champion", "Gods Championed...", False, True, None),
            ColumnDisplaySpec("won", "...and won", False, True, None),
        ],
    ),
    Category(
        "clan",
        "Unique Harvesting",
        "Clans are awarded points and subsequently ranked in the same way as the individual Unique Harvesting category using all of the members' games.",
        "harvest",
        "clan_harvest_score",
        "score DESC",
        [ColumnDisplaySpec("score", "Score", True, True, None),],
    ),
    Category(
        "clan",
        "Winning",
        """Clans are awarded <code> {MAX_CATEGORY_SCORE:,} / (13 - wins) </code> points for
        distinct first combo wins by clan members. The total number of wins in
        this category is capped at 12, and the total number of wins from any
        member is capped at 4. For a win to count in this category it must be
        the first win of the combo by the clan. For example, if Player A's 5th
        win is a DgWn and they win before Player B's win of DgWn then Player
        B's win will not count in this category.""".format(
            MAX_CATEGORY_SCORE=MAX_CATEGORY_SCORE
        ),
        "nonrep_wins",
        None,
        None,
        [],
    ),
    Category(
        "clan",
        "Nemelex' Choice",
        "The clan is awarded points in this category in the same way as the indvidual Nemelex' Choice using all of the members' games: one point to each of the first eight clans to win a Nemelex combo. Note: multiple clan members may win a Nemelex combo to deny other individuals Nemelex points, but this will not affect clan Nemelex scoring.",
        "nemelex_score",
        "clan_nemelex_score",
        "score DESC",
        [
            ColumnDisplaySpec("score", "Score", True, True, None),
            ColumnDisplaySpec("games", "Games", False, False, _pretty_clan_nemelex),
        ],
    ),
    Category(
        "clan",
        "Combo High Scores",
        "The clan is awarded points in this category in the same way as the individual Combo High scores category using all of the members' games. Each combo high score gives 1 point, with bonus points for winning the game (+1) and being a species/background high score (+3 each). (Therefore, a single game can give a maximum of 8 points.)",
        "combo_score",
        "clan_combo_score",
        "total DESC",
        [
            ColumnDisplaySpec("total", "Score", True, True, None),
            ColumnDisplaySpec(
                "games_json",
                "Combos (Won Combos in Bold)",
                False,
                False,
                _pretty_clan_combo_scores,
            ),
        ],
    ),
    Category(
        "clan",
        "Streak Length",
        "Clans are ranked in this category based on the streak of their best player, calculated according to the individual Streak Length category.",
        "streak",
        "clan_best_streak",
        "length DESC",
        [
            ColumnDisplaySpec("length", "Streak Length", True, True, None),
            ColumnDisplaySpec("players", "Player responsible", False, False, None),
        ],
    ),
    Category(
        "clan",
        "Best High Score",
        "Clans are ranked by the highest scoring game by any of their members.",
        "highest_score",
        "clan_highest_scores",
        "score DESC",
        [
            ColumnDisplaySpec("score", "Score", True, True, None),
            ColumnDisplaySpec("player", "Player Responsible", False, False, None),
            ColumnDisplaySpec("race", "Species", False, False, None),
            ColumnDisplaySpec("class", "Background", False, False, None),
            ColumnDisplaySpec("xl", "XL", False, True, None),
            ColumnDisplaySpec("nrune", "Runes", False, True, None),
            ColumnDisplaySpec("turn", "Turns", False, True, None),
            ColumnDisplaySpec(
                "morgue_json", "Morgue", False, False, _json_to_morgue_link
            ),
        ],
    ),
    Category(
        "clan",
        "Low Turncount Win",
        "Clans are ranked by the lowest turncount win of any of their members.",
        "lowest_turncount_win",
        "clan_lowest_turncount_wins",
        "turn ASC",
        [
            ColumnDisplaySpec("turn", "Turns", True, True, None),
            ColumnDisplaySpec("player", "Player Responsible", False, False, None),
            ColumnDisplaySpec("race", "Species", False, False, None),
            ColumnDisplaySpec("class", "Background", False, False, None),
            ColumnDisplaySpec(
                "morgue_json", "Morgue", False, False, _json_to_morgue_link
            ),
        ],
    ),
    Category(
        "clan",
        "Fastest Real Time Win",
        "Clans are ranked by the fastest realtime win of any of their members.",
        "fastest_win",
        "clan_fastest_wins",
        "duration ASC",
        [
            ColumnDisplaySpec("duration", "Duration", True, True, _pretty_duration),
            ColumnDisplaySpec("player", "Player", False, False, None),
            ColumnDisplaySpec("race", "Species", False, False, None),
            ColumnDisplaySpec("class", "Background", False, False, None),
            ColumnDisplaySpec(
                "morgue_json", "Morgue", False, False, _json_to_morgue_link
            ),
        ],
    ),
    Category(
        "clan",
        "Ziggurat Diving",
        "Clans are ranked in this category based on the Ziggurat Dive of their best player.",
        "ziggurat_dive",
        "clan_best_ziggurat",
        "completed DESC, deepest DESC",
        [
            ColumnDisplaySpec("completed", "Ziggurats Completed", True, True, None),
            ColumnDisplaySpec(
                "deepest", "Incomplete Ziggurat Levels", True, True, None
            ),
            ColumnDisplaySpec("players", "Player(s)", False, False, None),
        ],
    ),
    Category(
        "clan",
        "Banner Score",
        """Clans are awarded banner points based on all of the members'
        banners. Banner points are awarded in the same way as the individual
        banner points based on the highest banner tier earned by the clan's
        members for each banner.""",
        "banner_score",
        "clan_banner_score",
        "bscore DESC",
        [
            ColumnDisplaySpec("bscore", "Banner Points", True, True, None),
            ColumnDisplaySpec(
                "banners", "Banners Completed", False, False, _pretty_banners
            ),
        ],
    ),
)
Banner = collections.namedtuple("Banner", ("god", "name", "tiers", "flavortext", "dbname", "color"))
BannerTiers = collections.namedtuple("BannerTiers", ("one", "two", "three"))
BANNERS = [
    Banner(
        "Ashenzari",
        "Explorer",
        BannerTiers(
            "Enter a rune branch other than the Abyss", "Collect 5 distinct runes", "Collect all 17 runes",
        ),
        'Ashenzari thinks that an <code>EXPLORER</code> should be be busy looking for runes of Zot.',
        "ashenzari",
        "#ffbb99",
    ),
    Banner(
        "Beogh",
        "Heretic",
        BannerTiers(
            "Abandon and mollify one god",
            "Abandon and mollify 3 different gods in 3 different games",
            "Abandon and mollify 9 different gods in 9 different games",
        ),
        'Beogh hates all the other gods and admires <code>HERETICS</code> who go out of their way to incur their wrath. The good gods (Elyvilon, the Shining One, and Zin) and Ru are insufficiently wrathful, so abandoning them does not impress Beogh. Any god except the good gods, Ru, and Beogh are hence applicable for this banner. Only the first god abandoned in a game counts for this banner, Beogh wants the heresies spread around!',
        "beogh",
        "#e6b800",
    ),
    Banner(
        "Cheibriados",
        "Slow &amp; Steady",
        BannerTiers(
            "Reach experience level 9 in two consecutive games.",
            "Achieve a two-win streak.",
            "Achieve four-win streak with four distinct species and four distinct backgrounds.",
        ),
        'Cheibriados believes in being <code>SLOW AND STEADY</code> and will so recognize players who are careful enough to excel in consecutive games. ',
        "cheibriados",
        "#66ffff",
    ),
    Banner(
        "Dithmenos",
        "Politician",
        BannerTiers(
            "Steal a combo high score that was previously of at least 1,000 points.",
            "Steal a combo high score for a previously won combo.",
            "Steal a species or background high score that was previously of at least 10,000,000 points.",
        ),
        'Dithmenos appreciates the subtlety of a <code>POLITICIAN</code> and will thus reward any player who steals a high score from another player.',
        "dithmenos",
        "#330033",
    ),
    Banner(
        "Elyvilon",
        "Pious",
        BannerTiers("Champion a god.", "Champion 5 gods.", "Champion 13 gods."),
        'Elyvilon thinks it&apos;s important to check out what all the gods have to offer and thus will recognize as <code>PIOUS</code> any player who becomes the Champion (******) of as many gods as possible.',
        "elyvilon",
        "#ffffff",
    ),
    Banner(
        "Fedhas",
        "Nature's Ally",
        BannerTiers(
            "Enter the Crypt.",
            "Get the golden rune.",
            "Enter Tomb for the first time after picking up the Orb of Zot, and then get the golden rune.",
        ),
        'Fedhas thinks that the Crypt and the Tomb are abominations against nature and will bestow the title of <code>NATURE&apos;S ALLY</code> on a player who works towards destroying them.',
        "fedhas",
        "#808000",
    ),
    Banner(
        "Gozag",
        "Avarice",
        BannerTiers(
            "Find 1000 gold in a single game.",
            "Find the silver rune.",
            "Find the iron rune before entering Pandemonium or any branch of the dungeon containing any other rune. This means that only Temple, Lair, Orc, Elf, Depths, Abyss, Hell, and Dis can be entered.",
        ),
        'Gozag wants players to demonstrate their <code>AVARICE</code> by collecting certain valuable metals.',
        "gozag",
        "#cc9900",
    ),
    Banner(
        "Hepliaklqana",
        "Inheritor",
        BannerTiers(
            "Enter the Lair of Beasts while worshipping a god from a faded altar, having worshipped no other gods.",
            "Collect a rune while worshipping a god from a faded altar, having worshipped no other gods.",
            "Win a game while worshipping a god from a faded altar, having worshipped no other gods.",
        ),
        'Hepliaklqana bestows a geas upon you: recall the forgotten deities forth from the mists. Worship at a faded altar to become <code>THE INHERITOR</code> of memory!',
        "hepliaklqana",
        "#00b359",
    ),
    Banner(
        "Jiyva",
        "Gelatinous Body",
        BannerTiers(
            "Reach experience level 9 with at least 5 distinct species and at least 5 distinct backgrounds.",
            "Get a rune with at least 5 distinct species and at least 5 distinct backgrounds.",
            "Win with at least 5 distinct species and at least 5 distinct backgrounds.",
        ),
        'Jiyva thinks that it is important to be flexible and will gift players who excel with at least 5 distinct species and at least 5 distinct backgrounds with a <code>GELATINOUS BODY</code>.',
        "jiyva",
        "#99ff66",
    ),
    Banner(
        "Kikubaaqudgha",
        "Lord of Darkness",
        BannerTiers(
            "Reach the last level of the Orcish Mines without having entered the Lair.",
            "Reach the last level of the Depths without having entered the Lair.",
            "Win a game without having entered the Lair, the Orcish Mines, or the Vaults.",
        ),
        'Kikubaaqudgha wants players to demonstrate their mastery over the forces of darkness without delay, and will recognise a player who shows disdain for the Lair as a <code>LORD OF DARKNESS</code>.',
        "kikubaaqudgha",
        "#000000",
    ),
    Banner(
        "Lugonu",
        "Spiteful",
        BannerTiers(
            "Become the champion of Ru (the first step towards betraying Ru).",
            "After becoming the champion of Ru, abandon Ru and become the champion of a different god.",
            "Win a game in which you become the champion of Ru and then abandon Ru before entering any branches other than the Temple and the Lair.",
        ),
        'Lugonu hates all the other gods. At the moment, Lugonu is especially <code>SPITEFUL</code> towards Ru and admires those who make sacrifices to Ru and then abandon Ru&apos;s worship.',
        "lugonu",
        "#990073",
    ),
    Banner(
        "Makhleb",
        "Speed Demon",
        BannerTiers(
            "Reach D:15 in 27 minutes as a non-Formicid.",
            "Find a rune in 81 minutes.",
            "Win the game in 3 hours.",
        ),
        'Makhleb wants to see bloodshed as quickly as possible and will give players the bare minimum of time needed to prove themselves as <code>SPEED DEMONS</code>. Makhleb isn&apos;t interested in digging (and has cacodemons for that), so formicids are not eligible for the first tier of this banner.',
        "makhleb",
        "#ff3300",
    ),
    Banner(
        "Nemelex Xobeh",
        "Nemelex' Choice",
        BannerTiers(
            "Reach experience level 9 with a Nemelex' choice combo.",
            "Get a rune with a Nemelex' choice combo.",
            "Win a given Nemelex' choice combo. (Awarded even if you're not in the first 8.)",
        ),
        'Nemelex Xobeh wants to see players struggle and loves randomness, and so will give the <code>NEMELEX&apos; CHOICE</code> award to players who persevere with one of several combos randomly chosen and announced throughout the tournament.',
        "nemelex",
        "#ff66ff",
    ),
    Banner(
        "Okawaru",
        "Conqueror",
        BannerTiers(
            "Achieve a personal high score of 1,000,000.",
            "Achieve a personal high score of 9,000,000.",
            "Achieve a personal high score of 27,000,000.",
        ),
        'Okawaru is all about winning, all the time, and thus will recognize as <code>THE CONQUEROR</code> any player who is honourably victorious.',
        "okawaru",
        "#99b3e6",
    ),
    Banner(
        "Qazlal",
        "Prophet",
        BannerTiers(
            "Enter the Lair of Beasts with Invocations as your highest skill.",
            "Win the game with Invocations as your highest skill.",
            "Over the course of the tournament, win with three different different gods and Invocations as your highest skill.",
        ),
        'Qazlal demands fervent worship! Accordingly, Qazlal will only recognize as <code>THE PROPHET</code> those who dedicate themselves to Invocations.',
        "qazlal",
        "#0088cc",
    ),
    Banner(
        "Ru",
        "Ascetic",
        BannerTiers(
            "Reach the Ecumenical Temple without using any potions or scrolls.",
            "Reach the last level of the Lair of Beasts without using any potions or scrolls.",
            "Collect a rune without using any potions or scrolls. This rune cannot be the slimy or abyssal rune: Ru requires you to undergo this sacrifice for longer.",
        ),
        'Ru will recognize as <code>THE ASCETIC</code> those who sacrifice all use of potions and scrolls for a time.',
        "ru",
        "#604020",
    ),
    Banner(
        "Sif Muna",
        "Lorekeeper",
        BannerTiers(
            "Reach the last level of the Lair as a non-formicid without raising any skill to 13.",
            "Win without raising any skill to 20.",
            "Win without raising any skill to 13.",
        ),
        'Sif Muna thinks that a <code>LOREKEEPER</code> doesn&apos;t need skill, just knowledge of spells. Ashenzari has a different viewpoint on this subject, so Sif Muna has banned Ashenzari worshippers from receiving this banner. Gnolls lack the necessary discipline to fully undertake this challenge, so Sif Muna has also banned Gnolls from receiving this banner.',
        "sif",
        "#000099",
    ),
    Banner(
        "The Shining One",
        "Vow of Courage",
        BannerTiers(
            "In a single game, kill Sigmund before entering the Depths.",
            "In a single game, get four runes before entering the Depths.",
            "In a single game, get six runes before entering the Depths.",
        ),
        'The Shining One thinks each player should take a <code>VOW OF COURAGE</code> and face great terrors before entering the Depths.',
        "the_shining_one",
        "#ffd633",
    ),
    Banner(
        "Trog",
        "Brute Force",
        BannerTiers(
            "Reach the last level of the Lair as a non-demigod without worshipping a god.",
            "Find a rune as a non-demigod without worshipping a god.",
            "Win a game as a non-demigod without worshipping a god.",
        ),
        'Trog thinks players should rely on <code>BRUTE FORCE</code> and persevere without worshipping any god at all. Demigods cannot win Trog&apos;s praise for this, since they do not have a choice in the matter.',
        "trog",
        "#990000",
    ),
    Banner(
        "Uskayaw",
        "Graceful",
        BannerTiers(
            "Collect a rune from a Lair branch within 810 turns of entering the branch end.",
            "Collect the silver rune within 540 turns of entering Vaults:5.",
            "Collect the orb of Zot within 270 turns of entering Zot:5.",
        ),
        'Uskayaw requires all prospective students to prove themselves <code>GRACEFUL</code>. Step with precision and efficiency while on the deepest floors of the Dungeon!',
        "uskayaw",
        "#4d0026",
    ),
    Banner(
        "Vehumet",
        "Ruthless Efficiency",
        BannerTiers(
            "Reach the last level of the Lair as a non-formicid before reaching experience level 12.",
            "Find a rune before reaching experience level 14.",
            "Win the game before reaching experience level 19.",
        ),
        'Vehumet values focus and dedication, and will reward those who demonstrate <code>RUTHLESS EFFICIENCY</code> by achieving their goals without stopping to gain unnecessary experience. Waiting around for an ancestor to return from memory is inefficient, so games where Hepliaklqana is worshipped do not count for this banner. Followers of Ru who sacrifice their experience are inefficient and will be disqualified from this banner.',
        "vehumet",
        "#ffb3ff",
    ),
    Banner(
        "Wu Jian Council",
        "Sifu",
        BannerTiers(
            "Enter the Temple in under 3,000 turns.",
            "Enter the third floor of the Elven Halls in under 9,000 turns.",
            "Enter the final floor of Gehenna in under 27,000 turns.",
        ),
        'The Wu Jian Council admires the elegance of a <code>SIFU</code> and will recognize players who demonstrate their mastery with a deep dive.',
        "wu_jian",
        "#ff3333",
    ),
    Banner(
        "Xom",
        "Descent Into Madness",
        BannerTiers(
            "Enter a Ziggurat.",
            "Reach the 10th floor of a Ziggurat.",
            "Exit a Ziggurat from its lowest floor.",
        ),
        'Xom is always looking for entertainment and thinks it would be hilarious to watch a player&apos;s <code>DESCENT INTO MADNESS</code> through a ziggurat.',
        "xom",
        "#ffffff",
    ),
    Banner(
        "Yredelemnul",
        "Harvest",
        BannerTiers(
            "Kill 27 distinct uniques over the course of the tournament.",
            "Kill 54 distinct uniques over the course of the tournament.",
            "Kill 73 distinct uniques over the course of the tournament.",
        ),
        'Yredelemnul demands that you kill as many uniques as possible and will recognise success by awarding <code>THE HARVEST</code>. There are 73 uniques in DCSS.',
        "yredelemnul",
        "#994d00",
    ),
    Banner(
        "Zin",
        "Angel of Justice",
        BannerTiers(
            "Enter either Pandemonium or any branch of Hell.",
            "Kill at least one unique pan lord and at least one unique hell lord over the course of the tournament.",
            "Kill all four unique pan lords, all four unique hell lords, and the Serpent of Hell (at least once) over the course of the tournament.",
        ),
        'Zin will give the <code>ANGEL OF JUSTICE</code> award to any player who attempts to cleanse Hell and Pandemonium.',
        "zin",
        "#e6e6e6",
    ),
]


def individual_category_by_name(name):
    # type: (str) -> Optional[Category]
    for cat in INDIVIDUAL_CATEGORIES:
        if cat.name == name:
            return cat
    raise KeyError("Invalid individual category name '%s'" % name)

def clan_category_by_name(name):
    # type: (str) -> Optional[Category]
    for cat in CLAN_CATEGORIES:
        if cat.name == name:
            return cat
    raise KeyError("Invalid individual category name '%s'" % name)

def individual_category_link(cat):
    if isinstance(cat, str):
        try:
            cat = individual_category_by_name(cat)
        except KeyError:
            return None
    if not cat.source_table:
        return None
    return crawl_utils.base_link(crawl_utils.slugify(cat.name)) + ".html"

def clan_category_link(cat):
    if isinstance(cat, str):
        try:
            cat = clan_category_by_name(cat)
        except KeyError:
            return None
    if not cat.source_table:
        return None
    return crawl_utils.base_link(crawl_utils.slugify("clan-" + cat.name)) + ".html"
