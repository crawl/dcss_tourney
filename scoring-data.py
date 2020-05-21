import collections

IndividualCategory = collections.namedtuple(
    "IndividualCategory", ("name", "god", "desc")
)
INDIVIDUAL_CATEGORIES = (
    IndividualCategory(
        "Winning",
        "The Shining One",
        "The Shining One values perserverence and courage in the face of adversity. In this category, TSO will award players 10,000 points if they win two distinct character combos, 5,000 points for winning their first combo, and 0 otherwise.",
    ),
    IndividualCategory(
        "Win Rate",
        "Cheibriados",
        "Cheibriados believes in being slow and steady, and will recognize players who are careful enough to excel consistently. This category ranks players by their adjusted win percentage, calculated as the number of wins divided by the number of games played plus 1.",
    ),
    IndividualCategory(
        "Streak Length",
        "Jiyva",
        u"Jiyva is ranking players by their streak length. Jiyva favours the flexibility of a gelatinous body—the length of a streak is defined as the number of distinct species or backgrounds won consecutively (whichever is smaller). Every game in a streak must be the first game you start after winning the previous game in the streak. This will always be the case if you play all your games on one server.",
    ),
    IndividualCategory(
        "Nemelex' Choice",
        "Nemelex Xobeh",
        u"Nemelex Xobeh wants to see players struggle against randomness and will rank players who perservere with one of several combos randomly chosen and announced throughout the tournament. The first 8 players to win a given Nemelex' choice combo earn a point in this category and Nemelex will rank players by their score in this category.",
    ),
    IndividualCategory(
        "Combo High Scores",
        "Combo High Scores",
        "Dithmenos",
        "Dithmenos is ranking players by the combo high scores they can acquire and defend from rivals. A combo high score gives 1 point in this category; a winning high score 2 points; and a species or background high score 5 points.",
    ),
    IndividualCategory(
        "Best High Score",
        "Okawaru",
        "Okawaru is all about winning, and will rank players based on their best high score.",
    ),
    IndividualCategory(
        "Lowest Turncount Win",
        "Wu Jian Council",
        "The Wu Jian Council favours the unquestioned excellence and efficient combat of the Sifu. The Council will rank players based on their lowest turn count win.",
    ),
    IndividualCategory(
        "Fastest Real Time Win",
        "Makhleb",
        "Makhleb wants to see bloodshed as quickly as possible and will rank players accordingly, ranking players according to their fastest win.",
    ),
    IndividualCategory(
        "Lowest XL Win",
        "Vehumet",
        "Vehumet values ruthless efficiency, and will recognize the players who win at the lowest XL. Waiting around for an ancestor to return from memory is inefficient, so games where Hepliaklqana is worshipped do not count in this category. For the purposes of this category, players who have not won and players who have won only at XL 27 are both ranked ∞.",
    ),
    # TODO # IndividualCategory("Tournament Win Order", "Qazlal", "Qazlal wants to see destruction as soon as possible, and will rank those who are the fastest to win a game in the tournament. This category is ranked by the finish datetime of a player's first win in the tournament.")"
    # TODO # IndividualCategory("Tournament All Rune Win Order", "Lugonu", "Lugonu suggests players visit all the planes of the dungeon, and will rank those who are first to win a 15-rune game in the tournament. This category is ranked by the finish datetime of a player's first all rune win in the tournament.")
    IndividualCategory(
        "Exploration",
        "Ashenzari",
        "Ashenzari wants players to explore the dungeon and seek out runes of Zot. In this category, players earn 3 points per distinct rune of Zot collected and 1 point each for distinct branch entry and end floor reached.",
    ),
    IndividualCategory(
        "Piety",
        "Elyvilon",
        "Elyvilon thinks it's important to evaluate what all the gods have to offer. Elyvilon will award 1 point per god championed (****** piety) and an additional point for a win after championing that god. Two gods (Gozag and Xom) do not have the usual ****** piety system; to get the points for these gods, you must never worship another god during the game.",
    ),
    IndividualCategory(
        "Unique Harvesting",
        "Yredelemnul",
        "Yredelemnul demands that players kill as many distinct uniques and player ghosts as possible, and will rank players based on the number of such kills.",
    ),
    IndividualCategory(
        "Ziggurat Diving",
        "Xom",
        """Xom is entertained by a player's descent into madness, and will rank players by the number of Ziggurat floors they reach in a single game. Exiting a Ziggurat from the lowest floor counts as "reaching a floor" for scoring in this category, and an unlimited number of Ziggurats in a single game count. For example: completing two Ziggurats counts as 56 floors.""",
    ),
)

ClanCategory = collections.namedtuple("ClanCategory", ("name", "desc"))
CLAN_CATEGORIES = (
    ClanCategory(
        "Wins",
        "Clans are ranked by the number of distinct combo wins Wins in this category are capped at twelve, with at most <code>12 / (clan size)</code> (rounded up) wins per member counted.",
    ),
    ClanCategory(
        "Clan Nemelex' Choices",
        "The clan is awarded points in this category in the same way as the indvidual Nemelex' Choice using all of the members' games: one point to each of the first eight clans to win a Nemelex combo. Note: multiple clan members may win a Nemelex combo to deny other individuals Nemelex points, but this will not affect clan Nemelex scoring.",
    ),
    ClanCategory(
        "Clan Combo High Scores",
        "The clan is awarded points in this category in the same way as the individual Combo High scores category using all of the members' games. (A combo high score gives 1 point in this category; a winning high score 2 points; and a species or background high score 5 points.)",
    ),
    ClanCategory(
        "Streak Length",
        "Clans are ranked in this category based on the streak of their best player, calculated according to the individual Streak Length category.",
    ),
    ClanCategory(
        "Best High Score",
        "Clans are ranked by the highest scoring game by any of their members.",
    ),
    ClanCategory(
        "Low Turncount Win",
        "Clans are ranked by the lowest turncount win of any of their members.",
    ),
    ClanCategory(
        "Fastest Real Time Win",
        "Clans are ranked by the fastest realtime win of any of their members.",
    ),
    ClanCategory(
        "Clan Exploration Score",
        "Clans are awarded points and subsequently ranked in the same way as the individual Exploration category using all of the members' games.",
    ),
    ClanCategory(
        "Clan Piety Score",
        "Clans are awarded points and subsequently ranked in the same way as the individual Piety category using all of the members' games.",
    ),
    ClanCategory(
        "Clan Unique Harvesting",
        "Clans are awarded points and subsequently ranked in the same way as the individual Unique Harvesting category using all of the members' games.",
    ),
    ClanCategory(
        "Ziggurat Diving",
        "Clans are ranked in this category based on the Ziggurat Dive of their best player.",
    ),
    ClanCategory(
        "Clan Banner Score",
        "The clan is awarded banners and banner points based on all of the members' games. Banner points are awarded in the same way as the individual banner points with one exception: the clan award for Cheibriados' banner is based on an indvidual member's streak.",
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
