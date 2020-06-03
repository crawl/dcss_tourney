# -*- coding: utf-8 -*-
import collections
import datetime

import crawl_utils
from query_class import Query

TOURNAMENT_VERSION = "0.25"
YEAR = "2020"
START_TIME = datetime.datetime(2020, 6, 5, 20, 0)
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
    "ColumnDisplaySpec", ("column_name", "display_name")
)
Category = collections.namedtuple(
    "Category",
    (
        # "clan" or "individual"
        "type",
        "name",
        "desc",
        "db_column",
        # Defines the table that contains the ranking for this category
        "source_table",
        "source_column",
        # Pretty name when displaying the column
        "source_column_name",
        # Function to apply to the source column when displaying
        "source_column_display_transformation",
        # If True, the table displays are sorted descending (rather than ascending)
        "desc_order",
        # Extra columns in the source_table to show for the full ranking. A list of ColumnDisplaySpec's
        "full_ranking_extra_columns",
    ),
)


def category_leaders(category, c, limit=None):
    # type: (Union[Category,Category], Any, Union['individual', 'clan'], int) -> Sequence[Any]
    # c = database cursor
    # response is a list of database rows
    transformed_col = (
        "{fn}({col}) AS {col}".format(
            fn=category.source_column_display_transformation, col=category.source_column
        )
        if category.source_column_display_transformation
        else category.source_column
    )
    if category.full_ranking_extra_columns:
        extra_cols = "," + ",".join(
            col.column_name for col in category.full_ranking_extra_columns
        )
    else:
        extra_cols = ""
    query_text = """SELECT {first_col}, {transformed_col} {extra_cols} FROM {table}
                   ORDER BY {col} {direction}""".format(
        first_col='player' if category.type == 'individual' else 'team_captain',
        transformed_col=transformed_col,
        extra_cols=extra_cols,
        col=category.source_column,
        table=category.source_table,
        direction="DESC" if category.desc_order else "",
    )
    q = Query(query_text)
    if category.type == 'individual' and limit:
        q.append(" LIMIT %d" % limit)

    if category.type == 'individual':
        return q.rows(c)
    else:
        # We rewrite from team_captain to clan name
        result = q.rows(c)
        new_result = []
        for row in result:
            captain = row[0]
            if captain is None:
                continue
            # We can't use query.get_clan_info as query imports this file
            c.execute('''SELECT name FROM teams WHERE owner = %s''', (captain,))
            clan_name = c.fetchone()[0]
            new_row = [clan_name]
            new_row.extend(row[1:])
            new_result.append(new_row)
        if limit:
            new_result = new_result[:limit]
        return new_result


# This list (and the clan categories & banner lists) are in display order
INDIVIDUAL_CATEGORIES = (
    Category(
        "individual",
        "Exploration",
        "Ashenzari wants players to explore the dungeon and seek out runes of Zot. In this category, players earn 3 points per distinct rune of Zot collected and 1 point each for distinct branch entry and end floor reached.",
        "exploration",
        "player_exploration_score",
        "score",
        "Score",
        None,
        True,
        [],
    ),
    Category(
        "individual",
        "Piety",
        "Elyvilon thinks it's important to evaluate what all the gods have to offer. Elyvilon will award 1 point per god championed (****** piety) and an additional point for a win after championing that god. Two gods (Gozag and Xom) do not have the usual ****** piety system; to get the points for these gods, you must never worship another god during the game.",
        "piety",
        "player_piety_score",
        "piety",
        "Score",
        None,
        True,
        [
            ColumnDisplaySpec("champion", "Gods Championed..."),
            ColumnDisplaySpec("won", "...and won"),
        ],
    ),
    Category(
        "individual",
        "Unique Harvesting",
        "Yredelemnul demands that players kill as many distinct uniques and player ghosts as possible, and will rank players based on the number of such kills.",
        "harvest",
        "player_harvest_score",
        "score",
        "Score",
        None,
        True,
        [],
    ),
    Category(
        "individual",
        "Winning",
        "The Shining One values perserverence and courage in the face of adversity. In this category, TSO will award players 10,000 points if they win two distinct character combos, 5,000 points for winning their first combo, and 0 otherwise.",
        "nonrep_wins",
        None,
        None,
        None,
        None,
        None,
        [],
    ),
    Category(
        "individual",
        "Win Rate",
        "Cheibriados believes in being slow and steady, and will recognize players who are careful enough to excel consistently. This category ranks players by their adjusted win percentage, calculated as the number of wins divided by the number of games played plus 1.",
        "win_perc",
        "player_win_perc",
        "win_perc",
        "Win Percentage",
        None,
        True,
        [
            ColumnDisplaySpec("n_wins", "Wins"),
            ColumnDisplaySpec("n_games", "Games Played"),
        ],
    ),
    Category(
        "individual",
        "Streak Length",
        u"Jiyva is ranking players by their streak length. Jiyva favours the flexibility of a gelatinous body—the length of a streak is defined as the number of distinct species or backgrounds won consecutively (whichever is smaller). Every game in a streak must be the first game you start after winning the previous game in the streak. This will always be the case if you play all your games on one server.",
        "streak",
        "player_best_streak",
        "length",
        "Best Streak Length",
        None,
        True,
        [],
    ),
    Category(
        "individual",
        "Nemelex' Choice",
        u"Nemelex Xobeh wants to see players struggle against randomness and will rank players who perservere with one of several combos randomly chosen and announced throughout the tournament. The first 8 players to win a given Nemelex' choice combo earn a point in this category and Nemelex will rank players by their score in this category.",
        "nemelex_score",
        "player_nemelex_score",
        "score",
        "Score",
        None,
        True,
        [],
    ),
    Category(
        "individual",
        "Combo High Scores",
        "Dithmenos is ranking players by the combo high scores they can acquire and defend from rivals. A combo high score gives 1 point in this category; a winning high score 2 points; and a species or background high score 5 points.",
        "combo_score",
        "player_combo_score",
        "total",
        "Score",
        None,
        True,
        [
            ColumnDisplaySpec("combos", "Top Scoring Combos"),
            ColumnDisplaySpec("won_combos", "Won Combos"),
            ColumnDisplaySpec("sp_hs", "Species High Scores"),
            ColumnDisplaySpec("cls_hs", "Background High Scores"),
        ],
    ),
    Category(
        "individual",
        "Best High Score",
        "Okawaru is all about getting as many points as possible, and will rank players based on their best high score.",
        "highest_score",
        "highest_scores",
        "score",
        "Best Score",
        None,
        True,
        [
            ColumnDisplaySpec("race", "Species"),
            ColumnDisplaySpec("class", "Background"),
            ColumnDisplaySpec("turn", "Turns"),
            ColumnDisplaySpec("nrune", "Runes"),
        ],
    ),
    Category(
        "individual",
        "Lowest Turncount Win",
        "The Wu Jian Council favours the unquestioned excellence and efficient combat of the Sifu. The Council will rank players based on their lowest turn count win.",
        "lowest_turncount_win",
        "lowest_turncount_wins",
        "turn",
        "Turns",
        None,
        False,
        [
            ColumnDisplaySpec("race", "Species"),
            ColumnDisplaySpec("class", "Background"),
            ColumnDisplaySpec("turn", "Turns"),
            ColumnDisplaySpec("nrune", "Runes"),
        ],
    ),
    Category(
        "individual",
        "Fastest Real Time Win",
        "Makhleb wants to see bloodshed as quickly as possible and will rank players according to their fastest win.",
        "fastest_win",
        "fastest_wins",
        "duration",
        "Duration",
        "sec_to_time",
        False,
        [
            ColumnDisplaySpec("race", "Species"),
            ColumnDisplaySpec("class", "Background"),
            ColumnDisplaySpec("turn", "Turns"),
            ColumnDisplaySpec("nrune", "Runes"),
        ],
    ),
    Category(
        "individual",
        "Lowest XL Win",
        "Vehumet values ruthless efficiency, and will recognize the players who win at the lowest XL. Waiting around for an ancestor to return from memory is inefficient, so games where Hepliaklqana is worshipped do not count in this category. For the purposes of this category, players who have not won and players who have won only at XL 27 are both ranked ∞.",
        "low_xl_win",
        "low_xl_nonhep_wins",
        "xl",
        "XL",
        None,
        False,
        [
            ColumnDisplaySpec("race", "Species"),
            ColumnDisplaySpec("class", "Background"),
            ColumnDisplaySpec("turn", "Turns"),
            ColumnDisplaySpec("nrune", "Runes"),
        ],
    ),
    Category(
        "individual",
        "Tournament Win Order",
        "Qazlal wants destruction and they want it as soon as possible! This category ranks players in order of their first win in the tournament.",
        "first_win",
        "first_wins",
        "end_time",
        "Time",
        None,
        False,
        [
            ColumnDisplaySpec("race", "Species"),
            ColumnDisplaySpec("class", "Background"),
            ColumnDisplaySpec("turn", "Turns"),
            ColumnDisplaySpec("nrune", "Runes"),
            ColumnDisplaySpec("sec_to_time(duration) AS duration", "Duration"),
        ],
    ),
    Category(
        "individual",
        "Tournament All Rune Win Order",
        "Lugonu appreciates all planes of reality, and wants players tour as many of them as soon as possible. They will rank players in order of their first 15-rune win in the tournament.",
        "first_allrune_win",
        "first_allrune_wins",
        "end_time",
        "Time",
        None,
        False,
        [
            ColumnDisplaySpec("race", "Species"),
            ColumnDisplaySpec("class", "Background"),
            ColumnDisplaySpec("turn", "Turns"),
            ColumnDisplaySpec("nrune", "Runes"),
            ColumnDisplaySpec("sec_to_time(duration) AS duration", "Duration"),
        ],
    ),
    Category(
        "individual",
        "Ziggurat Diving",
        """Xom is entertained by a player's descent into madness, and will rank
        players by the number of consecutive Ziggurat floors they reach in a
        single game. Exiting a Ziggurat from the lowest floor counts as
        "reaching a floor" for scoring in this category, and an unlimited
        number of Ziggurats in a single game count.""",
        "ziggurat_dive",
        "ziggurats",
        "completed DESC, deepest DESC",
        "Floors",
        None,
        None,
        [],
    ),
    Category(
        "individual",
        "Banner Score",
        """The other DCSS gods are too busy with divine affairs to rank an entire category, but every DCSS god will reward players for certain achievements with tiered bannners. Players will be ranked on their total banner score, with tier one banners worth 1 point, tier 2 worth 2 points, and tier 3 worth 4 points.""",
        "banner_score",
        "player_banner_score",
        "bscore",
        "Score",
        None,
        True,
        [ColumnDisplaySpec("banners", "Banners Completed")],
    ),
)

CLAN_CATEGORIES = (
    Category(
        "clan",
        "Exploration",
        "Clans are awarded points and subsequently ranked in the same way as the individual Exploration category using all of the members' games.",
        "exploration",
        "clan_exploration_score",
        "score",
        "Score",
        None,
        True,
        [],
    ),
    Category(
        "clan",
        "Piety",
        "Clans are awarded points and subsequently ranked in the same way as the individual Piety category using all of the members' games.",
        "piety",
        "clan_piety_score",
        "piety",
        "Score",
        None,
        True,
        [],
    ),
    Category(
        "clan",
        "Unique Harvesting",
        "Clans are awarded points and subsequently ranked in the same way as the individual Unique Harvesting category using all of the members' games.",
        "harvest",
        "clan_harvest_score",
        "score",
        "Score",
        None,
        True,
        [],
    ),
    Category(
        "clan",
        "Wins",
        """Clans are awarded <code> 10,000 / (13 - wins) </code> points for
        distinct first combo wins by clan members. The total number of wins in
        this category is capped at 12, and the total number of wins from any
        member is capped at 4. For a win to count in this category it must be
        the first win of the combo by the clan. For example, if Player A's 5th
        win is a DgWn and they win before Player B's win of DgWn then Player
        B's win will not count in this category.""",
        "nonrep_wins",
        None,
        None,
        None,
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
        "score",
        "Score",
        None,
        True,
        [],
    ),
    Category(
        "clan",
        "Combo High Scores",
        "The clan is awarded points in this category in the same way as the individual Combo High scores category using all of the members' games. (A combo high score gives 1 point in this category; a winning high score 2 points; and a species or background high score 5 points.)",
        "combo_score",
        "clan_combo_score",
        "total",
        "Score",
        None,
        True,
        [],
    ),
    Category(
        "clan",
        "Streak Length",
        "Clans are ranked in this category based on the streak of their best player, calculated according to the individual Streak Length category.",
        "streak",
        "clan_best_streak",
        "length",
        "Best Streak Length",
        None,
        True,
        [],
    ),
    Category(
        "clan",
        "Best High Score",
        "Clans are ranked by the highest scoring game by any of their members.",
        "highest_score",
        "clan_highest_scores",
        "score",
        "Score",
        None,
        True,
        [],
    ),
    Category(
        "clan",
        "Low Turncount Win",
        "Clans are ranked by the lowest turncount win of any of their members.",
        "lowest_turncount_win",
        "clan_lowest_turncount_wins",
        "turn",
        "Turns",
        None,
        False,
        [],
    ),
    Category(
        "clan",
        "Fastest Real Time Win",
        "Clans are ranked by the fastest realtime win of any of their members.",
        "fastest_win",
        "clan_fastest_wins",
        "duration",
        "Duration",
        "sec_to_time",
        False,
        [],
    ),
    Category(
        "clan",
        "Ziggurat Diving",
        "Clans are ranked in this category based on the Ziggurat Dive of their best player.",
        "ziggurat_dive",
        "clan_best_ziggurat",
        "completed DESC, deepest DESC",
        "Floors",
        None,
        None,
        [],
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
        "bscore",
        "Score",
        None,
        True,
        [],
    ),
)
Banner = collections.namedtuple("Banner", ("god", "name", "tiers", "notes", "dbname"))
BannerTiers = collections.namedtuple("BannerTiers", ("one", "two", "three"))
BANNERS = [
    Banner(
        "Ashenzari",
        "Explorer",
        BannerTiers(
            "Enter a rune branch", "Collect 5 distinct runes", "Collect all 17 runes",
        ),
        None,
        "ashenzari",
    ),
    Banner(
        "Beogh",
        "Heretic",
        BannerTiers(
            "Abandon and mollify one god",
            "Abandon and mollify 3 gods in 3 different games",
            "Abandon and mollify 9 gods in 9 different games",
        ),
        None,
        "beogh",
    ),
    Banner(
        "Cheibriados",
        "Slow &amp; Steady",
        BannerTiers(
            "Reach experience level 9 in two consecutive games.",
            "Collect a rune in two consecutive games.",
            "Achieve a two-win streak.",
        ),
        None,
        "cheibriados",
    ),
    Banner(
        "Dithmenos",
        "Politician",
        BannerTiers(
            "Steal a combo high score that was previously of at least 1,000 points.",
            "Steal a combo high score for a previously won combo.",
            "Steal a species or background high score that was previously of at least 10,000,000 points.",
        ),
        None,
        "dithmenos",
    ),
    Banner(
        "Elyvilon",
        "Pious",
        BannerTiers("Champion a god.", "Champion 5 gods.", "Champion 13 gods."),
        None,
        "elyvilon",
    ),
    Banner(
        "Fedhas",
        "Nature's Ally",
        BannerTiers(
            "Enter the Crypt.",
            "Get the golden rune.",
            "Enter Tomb for the first time after picking up the Orb of Zot, and then get the golden rune.",
        ),
        None,
        "fedhas",
    ),
    Banner(
        "Gozag",
        "Avarice",
        BannerTiers(
            "Find 1000 gold in a single game.",
            "Find the silver rune.",
            "Find the iron rune before entering Pandemonium or any branch of the dungeon containing any other rune. This means that only Temple, Lair, Orc, Elf, Depths, Abyss, Hell, and Dis can be entered.",
        ),
        None,
        "gozag",
    ),
    Banner(
        "Hepliaklqana",
        "Inheritor",
        BannerTiers(
            "Enter the Lair of Beasts while worshipping a god from a faded altar.",
            "Collect a rune while worshipping a god from a faded altar.",
            "Win a game while worshipping a god from a faded altar.",
        ),
        "To achieve these banner tiers, you cannot have worshipped any other gods in the game.",
        "hepliaklqana",
    ),
    Banner(
        "Jiyva",
        "Gelatinous Body",
        BannerTiers(
            "Reach experience level 9 with at least 5 distinct species and at least 5 distinct backgrounds.",
            "Get a rune with at least 5 distinct species and at least 5 distinct backgrounds.",
            "Win with at least 5 distinct species and at least 5 distinct backgrounds.",
        ),
        None,
        "jiyva",
    ),
    Banner(
        "Kikubaaqudgha",
        "Lord of Darkness",
        BannerTiers(
            "Reach the last level of the Orcish Mines without having entered the Lair.",
            "Reach the last level of the Depths without having entered the Lair.",
            "Win a game without having entered the Lair, the Orcish Mines, or the Vaults.",
        ),
        None,
        "kikubaaqudgha",
    ),
    Banner(
        "Lugonu",
        "Spiteful",
        BannerTiers(
            "Become the champion of Ru (the first step towards betraying Ru).",
            "After becoming the champion of Ru, abandon Ru and become the champion of a different god.",
            "After becoming the champion of Ru and abandoning Ru, become the champion of Ru again.",
        ),
        None,
        "lugonu",
    ),
    Banner(
        "Makhleb",
        "Speed Demon",
        BannerTiers(
            "Reach D:15 in 27 minutes.",
            "Find a rune in 81 minutes.",
            "Win the game in 3 hours.",
        ),
        None,
        "makhleb",
    ),
    Banner(
        "Nemelex Xobeh",
        "Nemelex' Choice",
        BannerTiers(
            "Reach experience level 9 with a Nemelex' choice combo.",
            "Get a rune with a Nemelex' choice combo.",
            "Win a given Nemelex' choice combo. (Awarded even if you're not in the first 8.)",
        ),
        None,
        "nemelex",
    ),
    Banner(
        "Okawaru",
        "Conqueror",
        BannerTiers(
            "Achieve a personal high score of 1,000,000.",
            "Achieve a personal high score of 9,000,000.",
            "Achieve a personal high score of 27,000,000.",
        ),
        None,
        "okawaru",
    ),
    Banner(
        "Qazlal",
        "Prophet",
        BannerTiers(
            "Enter the Lair of Beasts with Invocations as your highest skill.",
            "Win the game with Invocations as your highest skill.",
            "Over the course of the tournament, win with three different different gods and Invocations as your highest skill.",
        ),
        None,
        "qazlal",
    ),
    Banner(
        "Ru",
        "Ascetic",
        BannerTiers(
            "Reach the Ecumenical Temple without using any potions or scrolls.",
            "Reach the last level of the Lair of Beasts without using any potions or scrolls.",
            "Collect a rune without using any potions or scrolls. This rune cannot be the slimy or abyssal rune: Ru requires you to undergo this sacrifice for longer.",
        ),
        None,
        "ru",
    ),
    Banner(
        "Sif Muna",
        "Lorekeeper",
        BannerTiers(
            "Reach the last level of the Lair as a non-formicid without raising any skill to 13.",
            "Win without raising any skill to 20.",
            "Win without raising any skill to 13.",
        ),
        "Gnolls and worshippers of Ashenzari are not eligible for this banner.",
        "sif",
    ),
    Banner(
        "The Shining One",
        "Vow of Courage",
        BannerTiers(
            "In a single game, kill Sigmund before entering the Depths.",
            "In a single game, get four runes before entering the Depths.",
            "In a single game, get six runes before entering the Depths.",
        ),
        None,
        "the_shining_one",
    ),
    Banner(
        "Trog",
        "Brute Force",
        BannerTiers(
            "Reach the last level of the Lair as a non-demigod without worshipping a god.",
            "Find a rune as a non-demigod without worshipping a god.",
            "Win a game as a non-demigod without worshipping a god.",
        ),
        None,
        "trog",
    ),
    Banner(
        "Uskayaw",
        "Graceful",
        BannerTiers(
            "Enter the Temple in under 3,000 turns.",
            "Enter the third floor of the Elven Halls in under 9,000 turns.",
            "Enter the final floor of Gehenna in under 27,000 turns.",
        ),
        None,
        "uskayaw",
    ),
    Banner(
        "Vehumet",
        "Ruthless Efficiency",
        BannerTiers(
            "Reach the last level of the Lair as a non-formicid before reaching experience level 12.",
            "Find a rune before reaching experience level 14.",
            "Win the game before reaching experience level 19.",
        ),
        "Waiting around for an ancestor to return from memory is inefficient, so games where Hepliaklqana is worshipped do not count for this banner.",
        "vehumet",
    ),
    Banner(
        "Wu Jian Council",
        "TBC (Wu Jian)",
        BannerTiers("TBC Wu Jian Tier 1", "TBC Wu Jian Tier 2", "TBC Wu Jian Tier 3",),
        None,
        "wu_jian",
    ),
    Banner(
        "Xom",
        "Descent Into Madness",
        BannerTiers(
            "Enter a Ziggurat.",
            "Reach the 10th floor of a Ziggurat.",
            "Exit a Ziggurat from its lowest floor.",
        ),
        None,
        "xom",
    ),
    Banner(
        "Yredelemnul",
        "Harvest",
        BannerTiers(
            "Kill 27 distinct uniques over the course of the tournament.",
            "Kill 54 distinct uniques over the course of the tournament.",
            "Kill 73 distinct uniques over the course of the tournament.",
        ),
        "There are XX uniques in DCSS.",
        "yredelemnul",
    ),
    Banner(
        "Zin",
        "Angel of Justice",
        BannerTiers(
            "Enter either Pandemonium or any branch of Hell.",
            "Kill at least one unique pan lord and at least one unique hell lord over the course of the tournament.",
            "Kill all four unique pan lords, all four unique hell lords, and the Serpent of Hell (at least once) over the course of the tournament.",
        ),
        None,
        "zin",
    ),
]


def individual_category_by_name(name):
    # type: (str) -> Optional[Category]
    for cat in INDIVIDUAL_CATEGORIES:
        if cat.name == name:
            return cat
    raise KeyError("Invalid individual category name '%s'" % name)
