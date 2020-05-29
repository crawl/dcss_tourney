# -*- coding: utf-8 -*-
import collections
import datetime

import crawl_utils
from crawl_utils import base_link

TOURNAMENT_VERSION = "0.25"
YEAR = "2020"
START_TIME = datetime.datetime(2020, 6, 5, 20, 0)
END_TIME = START_TIME + datetime.timedelta(days=16)
CLAN_CUTOFF_TIME = START_TIME + datetime.timedelta(days=7)

# Maximum score for placing first in a category. Player score is "10,000 / rank"
MAX_CATEGORY_SCORE = 10000

SERVERS = {
    "CPO": "https://crawl.project357.org/",
    "CAO": "http://crawl.akrasiac.org/",
    "CBRO": "http://crawl.berotato.org/",
    "CDO": "http://crawl.develz.org/",
    "CKO": "https://crawl.kelbi.org/crawl/",
    "CUE": "https://underhound.eu/crawl/",
    "CWZ": "https://webzook.net/soup/",
    "CXC": "http://crawl.xtahua.com/crawl/",
    "LLD": "http://lazy-life.ddo.jp/",
}

IndividualCategory = collections.namedtuple(
    "IndividualCategory",
    ("name", "desc", "db_column", "source_table", "source_column", "desc_order", "url"),
)
# This list (and the clan categories & banner lists) are in display order
INDIVIDUAL_CATEGORIES = (
    IndividualCategory(
        "Winning",
        "The Shining One values perserverence and courage in the face of adversity. In this category, TSO will award players 10,000 points if they win two distinct character combos, 5,000 points for winning their first combo, and 0 otherwise.",
        "nonrep_wins",
        None,
        None,
        None,
        None,
    ),
    IndividualCategory(
        "Win Rate",
        "Cheibriados believes in being slow and steady, and will recognize players who are careful enough to excel consistently. This category ranks players by their adjusted win percentage, calculated as the number of wins divided by the number of games played plus 1.",
        "win_perc",
        "player_win_perc",
        "win_perc",
        True,
        base_link("win-percentage-order.html"),
    ),
    IndividualCategory(
        "Streak Length",
        u"Jiyva is ranking players by their streak length. Jiyva favours the flexibility of a gelatinous body—the length of a streak is defined as the number of distinct species or backgrounds won consecutively (whichever is smaller). Every game in a streak must be the first game you start after winning the previous game in the streak. This will always be the case if you play all your games on one server.",
        "streak",
        "player_best_streak",
        "length",
        True,
        base_link("streak-order-active-streaks.html"),
    ),
    IndividualCategory(
        "Nemelex' Choice",
        u"Nemelex Xobeh wants to see players struggle against randomness and will rank players who perservere with one of several combos randomly chosen and announced throughout the tournament. The first 8 players to win a given Nemelex' choice combo earn a point in this category and Nemelex will rank players by their score in this category.",
        "nemelex_score",
        "player_nemelex_score",
        "score",
        True,
        base_link("nemelex-order.html"),
    ),
    IndividualCategory(
        "Combo High Scores",
        "Dithmenos is ranking players by the combo high scores they can acquire and defend from rivals. A combo high score gives 1 point in this category; a winning high score 2 points; and a species or background high score 5 points.",
        "combo_score",
        "player_combo_score",
        "total",
        True,
        base_link("combo-leaders.html"),
    ),
    IndividualCategory(
        "Best High Score",
        "Okawaru is all about winning, and will rank players based on their best high score.",
        "highest_score",
        "highest_scores",
        "score",
        True,
        base_link("high-score-order.html"),
    ),
    IndividualCategory(
        "Lowest Turncount Win",
        "The Wu Jian Council favours the unquestioned excellence and efficient combat of the Sifu. The Council will rank players based on their lowest turn count win.",
        "lowest_turncount_win",
        "lowest_turncount_wins",
        "turn",
        False,
        base_link("low-tc-win-order.html"),
    ),
    IndividualCategory(
        "Fastest Real Time Win",
        "Makhleb wants to see bloodshed as quickly as possible and will rank players according to their fastest win.",
        "fastest_win",
        "fastest_wins",
        "duration",
        False,
        base_link("fastest-realtime-win-order.html"),
    ),
    IndividualCategory(
        "Lowest XL Win",
        "Vehumet values ruthless efficiency, and will recognize the players who win at the lowest XL. Waiting around for an ancestor to return from memory is inefficient, so games where Hepliaklqana is worshipped do not count in this category. For the purposes of this category, players who have not won and players who have won only at XL 27 are both ranked ∞.",
        "low_xl_win",
        "low_xl_nonhep_wins",
        "xl",
        False,
        base_link("low-xl-win-order.html"),
    ),
    IndividualCategory(
        "Tournament Win Order",
        "Qazlal wants destruction and they want it as soon as possible! This category ranks players in order of their first win in the tournament.",
        "first_win",
        "first_wins",
        "end_time",
        False,
        base_link("first-win-order.html"),
    ),
    IndividualCategory(
        "Tournament All Rune Win Order",
        "Lugonu appreciates all planes of reality, and wants players tour as many of them as soon as possible. They will rank players in order of their first 15-rune win in the tournament.",
        "first_allrune_win",
        "first_allrune_wins",
        "end_time",
        False,
        base_link("first-allrune-win-order.html"),
    ),
    IndividualCategory(
        "Exploration",
        "Ashenzari wants players to explore the dungeon and seek out runes of Zot. In this category, players earn 3 points per distinct rune of Zot collected and 1 point each for distinct branch entry and end floor reached.",
        "exploration",
        "player_exploration_score",
        "score",
        True,
        base_link("exploration-order.html"),
    ),
    IndividualCategory(
        "Piety",
        "Elyvilon thinks it's important to evaluate what all the gods have to offer. Elyvilon will award 1 point per god championed (****** piety) and an additional point for a win after championing that god. Two gods (Gozag and Xom) do not have the usual ****** piety system; to get the points for these gods, you must never worship another god during the game.",
        "piety",
        "player_piety_score",
        "piety",
        True,
        base_link("piety-order.html"),
    ),
    IndividualCategory(
        "Unique Harvesting",
        "Yredelemnul demands that players kill as many distinct uniques and player ghosts as possible, and will rank players based on the number of such kills.",
        "harvest",
        "player_harvest_score",
        "score",
        True,
        base_link("harvest-order.html"),
    ),
    IndividualCategory(
        "Ziggurat Diving",
        """Xom is entertained by a player's descent into madness, and will rank
        players by the number of consecutive Ziggurat floors they reach in a
        single game. Exiting a Ziggurat from the lowest floor counts as
        "reaching a floor" for scoring in this category, and an unlimited
        number of Ziggurats in a single game count.""",
        "ziggurat_dive",
        "ziggurats",
        "completed DESC, deepest DESC",
        None,
        base_link("zig-dive-order.html"),
    ),
    IndividualCategory(
        "Banner Score",
        """The other DCSS gods are too busy with divine affairs to rank an entire category, but every DCSS god will reward players for certain achievements with tiered bannners. Players will be ranked on their total banner score, with tier one banners worth 1 point, tier 2 worth 2 points, and tier 3 worth 4 points.""",
        "banner_score",
        "player_banner_score",
        "bscore",
        True,
        base_link("banner-order.html"),
    ),
)

ClanCategory = collections.namedtuple("ClanCategory", ("name", "desc",
     "db_column", "source_table", "source_column", "desc_order", "url"))
CLAN_CATEGORIES = (
    ClanCategory(
        "Wins",
        "Clans are awarded <code> 10,000 / (13 - wins) </code> points for
        distinct first combo wins by clan members. The total number of wins in
        this category is capped at 12, and the total number of wins from any
        member is capped at 4. For a win to count in this category it must be
        the first win of the combo by the clan. For example, if Player A's 5th
        win is a DgWn and they win before Player B's win of DgWn then Player
        B's win will not count in this category.",
        "nonrep_wins",
        None,
        None,
        None,
        None,
    ),
    ClanCategory(
        "Nemelex' Choice",
        "The clan is awarded points in this category in the same way as the indvidual Nemelex' Choice using all of the members' games: one point to each of the first eight clans to win a Nemelex combo. Note: multiple clan members may win a Nemelex combo to deny other individuals Nemelex points, but this will not affect clan Nemelex scoring.",
        "nemelex_score",
        "clan_nemelex_score",
        "score",
        True,
        None,
    ),
    ClanCategory(
        "Combo High Scores",
        "The clan is awarded points in this category in the same way as the individual Combo High scores category using all of the members' games. (A combo high score gives 1 point in this category; a winning high score 2 points; and a species or background high score 5 points.)",
        "combo_score",
        "clan_combo_score",
        "total",
        True,
        None,
    ),
    ClanCategory(
        "Streak Length",
        "Clans are ranked in this category based on the streak of their best player, calculated according to the individual Streak Length category.",
        "streak",
        "clan_streaks",
        "length",
        True,
        None,
    ),
    ClanCategory(
        "Best High Score",
        "Clans are ranked by the highest scoring game by any of their members.",
        "highest_score",
        "clan_highest_scores",
        "score",
        True,
        None,
    ),
    ClanCategory(
        "Low Turncount Win",
        "Clans are ranked by the lowest turncount win of any of their members.",
        "lowest_turncount_win",
        "clan_lowest_turncount_wins",
        "turn",
        False,
        None,
    ),
    ClanCategory(
        "Fastest Real Time Win",
        "Clans are ranked by the fastest realtime win of any of their members.",
        "fastest_win",
        "clan_fastest_wins",
        "duration",
        False,
        None,
    ),
    ClanCategory(
        "Exploration",
        "Clans are awarded points and subsequently ranked in the same way as the individual Exploration category using all of the members' games.",
        "exploration",
        "clan_exploration_score",
        "score",
        True,
        None,
    ),
    ClanCategory(
        "Piety",
        "Clans are awarded points and subsequently ranked in the same way as the individual Piety category using all of the members' games.",
        "piety",
        "clan_piety_score",
        "piety",
        True,
        None,
    ),
    ClanCategory(
        "Unique Harvesting",
        "Clans are awarded points and subsequently ranked in the same way as the individual Unique Harvesting category using all of the members' games.",
        "harvest",
        "clan_harvest_score",
        "score",
        True,
        None,
    ),
    ClanCategory(
        "Ziggurat Diving",
        "Clans are ranked in this category based on the Ziggurat Dive of their best player.",
        "ziggurat_dive",
        "clan_best_ziggurat",
        "completed DESC, deepest DESC",
        None,
        None,
    ),
    ClanCategory(
        "Banner Score",
        "The clan is awarded banners and banner points based on all of the members' games. Banner points are awarded in the same way as the individual banner points with one exception: the clan award for Cheibriados' banner is based on an indvidual member's streak.",
        "banner_score",
        None,
        None,
        None,
        None,
    ),
)
Banner = collections.namedtuple("Banner", ("god", "name", "tiers", "notes"))
BannerTiers = collections.namedtuple("BannerTiers", ("one", "two", "three"))
BANNERS = [
    Banner(
        "Ashenzari",
        "Explorer",
        BannerTiers(
            "Enter a rune branch", "Collect 5 distinct runes", "Collect all 17 runes",
        ),
        None,
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
    ),
    Banner(
        "Elyvilon",
        "Politician",
        BannerTiers("Champion a god.", "Champion 5 gods.", "Champion 13 gods."),
        None,
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
    ),
    Banner(
        "Nemelex",
        "Nemelex' Choice",
        BannerTiers(
            "Reach experience level 9 with a Nemelex' choice combo.",
            "Get a rune with a Nemelex' choice combo.",
            "Win a given Nemelex' choice combo. (Awarded even if you're not in the first 8.)",
        ),
        None,
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
    ),
    Banner(
        "Wu Jian Council",
        "TBC (Wu Jian)",
        BannerTiers("TBC Wu Jian Tier 1", "TBC Wu Jian Tier 2", "TBC Wu Jian Tier 3",),
        None,
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
    ),
]


def individual_category_by_name(name):
    # type: (str) -> Optional[IndividualCategory]
    for cat in INDIVIDUAL_CATEGORIES:
        if cat.name == name:
            return cat
    raise KeyError("Invalid individual category name '%s'" % name)
