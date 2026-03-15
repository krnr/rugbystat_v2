import datetime as dt
import functools as ft
import itertools as it
import logging
import operator
import re
import typing as t
from copy import copy
from dataclasses import dataclass
from difflib import SequenceMatcher as SM

from django.contrib import messages
from django.db import IntegrityError, connection
from django.db.models import Q
from fuzzywuzzy import fuzz, process

from matches.models import Season, Tournament, Match as MatchModel
from teams.models import City, Person, PersonSeason, Team, TeamSeason, GroupSeason

logger = logging.getLogger("django.request")

POSITIONS = {
    "15": PersonSeason.FB,
    "14-11": PersonSeason.BACK,
    "10": PersonSeason.FH,
    "9": PersonSeason.SH,
    "6-8": PersonSeason.BACKROW,
    "8-6": PersonSeason.BACKROW,
    "4-5": PersonSeason.LOCK,
    "5-4": PersonSeason.LOCK,
    "1-3": PersonSeason.FIRST_ROW,
    "3-1": PersonSeason.FIRST_ROW,
    "14": PersonSeason.WINGER,
    "13": PersonSeason.CENTER,
    "12": PersonSeason.CENTER,
    "12-13": PersonSeason.CENTER,
    "11": PersonSeason.WINGER,
    "9-10": PersonSeason.HALF,
    "8": PersonSeason.BACKROW,
    "7": PersonSeason.BACKROW,
    "6": PersonSeason.BACKROW,
    "5": PersonSeason.LOCK,
    "4": PersonSeason.LOCK,
    "4/5": PersonSeason.LOCK,
    "3": PersonSeason.PROP,
    "2": PersonSeason.HOOKER,
    "1": PersonSeason.PROP,
    "1/3": PersonSeason.PROP,
    "1-8": PersonSeason.FORWARD,
    "15-9": PersonSeason.BACK,
}

MONTHS_MAP = {
    "январ": "01",
    "феврал": "02",
    "март": "03",
    "апрел": "04",
    "мая": "05",
    "мае": "05",
    "июн": "06",
    "июл": "07",
    "август": "08",
    "сентябр": "09",
    "октябр": "10",
    "ноябр": "11",
    "декабр": "12",
}

TEAM_NAME = re.compile(r"[а-я]+\s+", re.I)
TEAM_SIMILAR_THRESHOLD = 60


def parse_rosters(_, data):
    for role, player in players_from_input(data["input"]):
        find_or_create_in_db(role, player, data)


def _get_role_for_position(num: int) -> str:
    """Get role for a single position number."""
    if num in (1, 2, 3):
        return PersonSeason.FIRST_ROW
    return POSITIONS.get(str(num), PersonSeason.PLAYER)


def _expand_range_position(number_str: str, players: list) -> t.List[t.Tuple[str, str]]:
    """Expand range positions like 14-11 or 1-8 to individual positions."""
    if "-" not in number_str:
        role = POSITIONS.get(number_str, PersonSeason.PLAYER)
        return [(role, p.strip()) for p in players if p.strip()]

    try:
        parts = number_str.split("-")
        if len(parts) != 2:
            return [(PersonSeason.PLAYER, p.strip()) for p in players if p.strip()]

        first, last = int(parts[0]), int(parts[1])
        if first > last:
            numbers = list(range(last, first + 1))
        else:
            numbers = list(range(first, last + 1))

        result = []
        for i, num in enumerate(numbers):
            role = _get_role_for_position(num)
            if i < len(players):
                player = players[i].strip()
                if player:
                    result.append((role, player))

        for i in range(len(result), len(players)):
            player = players[i].strip()
            if player:
                result.append((PersonSeason.PLAYER, player))

        return result
    except (ValueError, IndexError):
        return [(PersonSeason.PLAYER, p.strip()) for p in players if p.strip()]


def _clean_player_name(name: str) -> str:
    """Clean player name: strip HTML tags, extra whitespace, and parenthetical content."""
    name = re.sub(r"</?div[^>]*>", "", name, flags=re.IGNORECASE)
    name = name.strip()
    name = re.sub(r"\s+", " ", name)
    return name


def _split_conjunctions(players: list) -> list:
    """Split players connected by 'и' (and) or comma."""
    result = []
    for player in players:
        parts = re.split(r"\s+и\s+|[,\/]", player)
        for part in parts:
            part = part.strip()
            if part:
                result.append(part)
    return result


def _extract_substitutes(players: list, roles: list = None) -> tuple:
    """Extract substitute players (in parentheses) from player list.
    Returns (main_players_with_roles, substitutes_with_roles).
    If roles provided, substitutes inherit the role of the player they replace.
    """
    main_players_with_roles = []
    substitutes_with_roles = []

    for i, player in enumerate(players):
        role = roles[i] if roles and i < len(roles) else PersonSeason.PLAYER
        sub_match = re.search(r"(.+?)\s*\(([^)]+)\)", player)
        if sub_match:
            main_part = sub_match.group(1).strip()
            substitute = sub_match.group(2).strip()
            if main_part:
                main_players_with_roles.append((main_part, role))
            if substitute:
                substitutes_with_roles.append((substitute, role))
        else:
            main_players_with_roles.append((player, role))
            substitutes_with_roles.append((None, None))

    return main_players_with_roles, substitutes_with_roles


def players_from_input(raw_text: str) -> t.Generator:
    input_ = raw_text.replace("\r\n", " ").replace(" / ", ";")
    input_ = re.sub(r"^[^:]+:", "", input_).strip()
    input_ = _clean_player_name(input_)

    if ";" in input_:
        positions = input_.split(";")
    else:
        positions = [input_]

    esc = r"(\d{1,2}-*\d{0,2})[\s\.]*(.*)"

    for position in positions:
        position = position.strip()
        if not position:
            continue

        match = re.match(esc, position)
        if match:
            number_str = match.group(1)
            players_str = match.group(2)

            players = [p.strip() for p in players_str.split(",") if p.strip()]
            players = _split_conjunctions(players)

            if "-" in number_str:
                expanded = _expand_range_position(number_str, players)
                roles = [r for r, _ in expanded]
                players_only = [p for _, p in expanded]
                _, substitutes = _extract_substitutes(players_only, roles)
                for role, player in expanded:
                    yield role, player
                for sub_name, sub_role in substitutes:
                    if sub_name:
                        yield sub_role, sub_name
            else:
                role = POSITIONS.get(number_str, PersonSeason.PLAYER)
                _, substitutes = _extract_substitutes(players, [role] * len(players))
                for player in players:
                    yield role, player
                for sub_name, sub_role in substitutes:
                    if sub_name:
                        yield sub_role, sub_name
        else:
            players = [p.strip() for p in position.split(",") if p.strip()]
            players = _split_conjunctions(players)
            _, substitutes = _extract_substitutes(players)

            for player in players:
                if player:
                    yield PersonSeason.PLAYER, player
            for sub_name, sub_role in substitutes:
                if sub_name:
                    yield sub_role, sub_name


def split_name(player: str) -> t.Tuple[str, str]:
    if "." in player:
        first, last = player.split(".")  # TODO: what if patronymic?
        return first.strip(), last.strip()

    try:
        first, last = player.split()
    except ValueError:
        msg = "Couldn't split: {}".format(player)
        print(msg)
        logger.warning(msg)
        first, last = "", player
    return first.strip(), last.strip()


def find_or_create_in_db(role: str, player: str, data):
    first_name, name = split_name(player)
    persons = Person.objects.filter(name=name)
    # what if there're multiple? or mistake in last_name?
    print("Finding best match from {}".format(persons))

    person = find_best_match(persons, name, first_name, ratio_threshold=0.85)
    print("Found {}".format(person))
    create_season_for_person(person, role, data)


def create_season_for_person(person, role, data):
    # get_or_create PersonSeason for number
    try:
        obj, created = PersonSeason.objects.get_or_create(
            role=role,
            person=person,
            season_id=data["season"],
            team_id=data["team"],
            year=data["year"],
        )
    except IntegrityError:
        logger.error("Can't create season for {}".format(person))
    else:
        if created:
            logger.info("Created {}".format(obj))
        else:
            logger.info("Found {}".format(obj))


def parse_alphabet(request, data):
    importer = LineImporter()
    importer.run(data["input"].split("\r\n"))


class LineImporter:
    pattern = re.compile(
        r"(?P<name>(?:[А-Я][а-я.]*\s*){1,3})(?P<year>\(\d+\) )?— (?P<teams>(([A-Яа-я ]+) (?P<seasons>\((\d+,*\s*)+\)),*\s*)+)(.*)"
    )
    teams_re = re.compile(r"(\S+ \S+) (?P<seasons>\((\d+,*\s*)+\)),*\s*")

    def __init__(self, *args, **kwargs):
        self.p = Person()
        self.m2m = []
        self.seasons = {
            "1933": Season.objects.get(name="Товарищеские матчи 1933"),
            "1934": Season.objects.get(name="Товарищеские матчи 1934"),
            "1935": Season.objects.get(name="Чемпионат Москвы 1935 (о)"),
            "1936": Season.objects.get(name="Кубок СССР 1936"),
            "1937": Season.objects.get(name="Матч городов 1937"),
            "1938": Season.objects.get(name="Чемпионат СССР 1938"),
            "1939": Season.objects.get(name="Чемпионат СССР 1939"),
            "1940": Season.objects.get(name="Чемпионат Москвы 1940"),
            "1946": Season.objects.get(name="Чемпионат Москвы 1946"),
            "1947": Season.objects.get(name="Матч городов 1947"),
            "1949": Season.objects.get(name="Матч городов 1949"),
        }

    def restart(self):
        self.p = Person()
        self.m2m = []

    def run(self, inpt):
        for line in inpt:
            self.process_line(line)
            PersonSeason.objects.bulk_create(self.m2m)
            self.restart()

    def process_line(self, line):
        matches = self.pattern.findall(line)
        name, year, teams, last, last_name, seasons, last_season, occup = matches[0]
        self.create_person(name.strip(), year, occup)
        self.parse_seasons(teams, last, last_name, seasons, last_season)

    def create_person(self, name, year, occupation):
        if " " in name:
            name = name.replace(".", " ").strip().split(" ")
            self.p.name = name[0]
            self.p.first_name = name[1]
            if len(name) > 2:
                self.p.middle_name = name[2]
        else:
            self.p.name = name

        if year:
            self.p.year_birth = year[1:5]

        if occupation:
            self.p.story = occupation

        self.p.save()

    def parse_seasons(self, teams, last, last_name, last_seasons, last_season):
        if last == teams:
            self.create_seasons(last_name, last_seasons)
        else:
            for team, seasons, _ in self.parse_teams(teams):
                self.create_seasons(team, seasons)

    def parse_teams(self, teams):
        return self.teams_re.findall(teams)

    def create_seasons(self, team, seasons):
        # '(1936)'
        # '(1937, 1938)'
        team_instance = self.get_team_instance(team)
        if not team_instance:
            logger.warning(f"No team found for {team}")
        for season in seasons[1:-1].split(","):
            self.m2m.append(
                PersonSeason(
                    person=self.p,
                    season_id=self.seasons[season.strip()].pk,
                    team_id=team_instance.id,
                    year=season.strip(),
                )
            )

    def get_team_instance(self, name):
        qs = Team.objects.filter(year__lt=1950)
        for element in name.split():
            qs = reduce_qs(qs, element.strip())
        return qs.first()


def reduce_qs(qs, search_term):
    queries = [
        Q(**{lookup: search_term})
        for lookup in (
            "name__icontains",
            "short_name__icontains",
            "names__name__icontains",
            "city__name__istartswith",
        )
    ]
    return qs.filter(ft.reduce(operator.or_, queries))


class Zaal:
    def __init__(self, role, full_name):
        self.role = role
        self.first_name = full_name.strip().split()[0]
        self.last_name = full_name.strip().split()[1]
        self.django = None

    def __repr__(self):
        return f"{self.first_name} {self.last_name}, {self.role}"


rr = re.compile(
    r"(?P<first_name>[А-Я][а-я]+)\s+(?P<last_name>[А-Я][а-я]+)\s+.*?(?P<year>\d{4})"
)

"""

>>> def find_in_db(p):
...         persons = Person.objects.filter(name=p.last_name)
...         p.django=find_best_match(persons, p.last_name, p.first_name)
... 
>>> def step1(ss):
...     players=[Parsed(p) for p in rr.findall(ss)]
...     for p in players:
...         find_in_db(p)
...         print(p.django, p.django.year_birth)
...     return players
... 
"""


def zaal1(ss):
    res = []
    for p in players_from_input({"input": ss}):
        inst = Zaal(*p)
        find_in_db(inst)
        if inst.django:
            print(inst.django, inst.django.year_birth)
        else:
            print("not found")
        res.append(inst)
    return res


def _get_ratios_for_person(queryset, first_name, name):
    stop_first = None if len(first_name) > 1 else 1
    return [
        SM(
            None,
            "{} {}".format(obj.first_name[:stop_first], obj.name),
            "{} {}".format(first_name, name),
        ).ratio()
        for obj in queryset
    ]


def find_best_match(queryset, name, first_name, ratio_threshold=0.6):
    """
    Find the most suitable instance by SequenceMatcher from queryset.

    If None found - create one.
    """
    ratios = _get_ratios_for_person(queryset, first_name, name)

    if ratios and max(ratios) > ratio_threshold:
        return queryset[ratios.index(max(ratios))]


def parse_teams(data):
    previous_team = None
    for line in data.split("\n"):
        if len(line) < 4:
            previous_team.save()
            break
        if line[:4] == "<li>":
            if not previous_team:
                previous_team = init_team(line)
            else:
                previous_team.save()
                previous_team = init_team(line)
        else:
            if previous_team:
                previous_team.story += line


def init_date(prefix_year):
    try:
        year = int(prefix_year.strip().split(" ")[-1])
        prefix = prefix_year[: prefix_year.find(str(year))]
    except Exception:
        prefix = prefix_year
        year = None
    return prefix, year


def init_team(line):
    expr = r"<li>(.+) \(([^-]*)-*([^-]*)\)(.*)"
    team_and_city, year_create, year_disband, story = re.findall(expr, line)[0]
    city = team_and_city.split(" ")[-1]
    name = team_and_city[: team_and_city.find(city)].strip().strip("<b>")

    city_instance, _ = City.objects.get_or_create(name=city)

    prefix_create, create = init_date(year_create)
    prefix_disband, disband = init_date(year_disband)

    team = Team(
        name=name,
        story=story,
        city=city_instance,
        year=create or None,
        year_prefix=prefix_create,
        disband_year=disband or None,
        disband_year_prefix=prefix_disband,
    )
    return team


def parse_season(data, request):
    YEAR = re.compile(
        r"""(^\D*)    # all but digits - tournament name
                      ([\d/-]{4,9}) # '1975' or '1975/77' or '1999/2001'
                      *$            # 0 or once""",
        re.X,
    )

    season = Season()
    first, *rest = data.split("\n")
    # first line denotes title
    title, year = re.match(YEAR, first.strip()).group(1, 2)
    season.name = title.strip()
    season.year = int(year)
    tourns = Tournament.objects.filter(name__icontains=season.name)

    if tourns.count() == 1:
        season.tourn = tourns.first()
    else:
        if not tourns:
            msg = "No tournaments found"
        else:
            ratios = [SM(None, tourn.name, title).ratio() for tourn in tourns]
            max_tourn = tourns[ratios.index(max(ratios))]
            season.tourn = max_tourn
            msg = "Multiple tournaments found for this title. "
            msg = msg + "We suggest: {}".format(max_tourn.name)
        messages.add_message(request, messages.INFO, msg)

    for line in rest:
        if line.strip():
            date_start, date_end = find_dates(line, year)
            if date_start and date_end:
                season.date_start = date_start
                season.date_end = date_end
                break
        else:
            season.date_start = dt.date(season.year, 1, 1)
            season.date_end = dt.date(season.year, 12, 31)

    season.story = "\n".join(rest)
    return season


def dt_from_str(day, month, year) -> dt.datetime:
    return dt.datetime.strptime(
        "{}/{}/{}".format(day, MONTHS_MAP[month], year), "%d/%m/%Y"
    )


def find_dates(txt, year):
    """
    Parse "с 5 февраля по 10 мая" to datetime objects
    """
    months = r"({})".format("|".join(MONTHS_MAP.keys()))
    esc1 = r" (\d+(?= {}))".format(months)  # (с ... по ...)
    esc2 = r"(\d+-\d+(?= {}))".format(months)  # (1-10 ...)
    esc3 = r"[в|в конце|в начале] {}".format(months)  # в октябре...

    patterns = [esc1, esc2, esc3]
    dates = [re.findall(pattern, txt) for pattern in patterns]
    if tuple(filter(bool, dates)):
        # try the first found pattern
        try:
            date_start, date_end = dates[0]
            day, month = date_start
            date_start = dt_from_str(day, month, year)
            day, month = date_end
            date_end = dt_from_str(day, month, year)
        except (IndexError, ValueError):
            # either ('12-15', 'мая') or 'октябр'
            try:
                days, month = dates[1][0]
                day_start, day_end = days.split("-")
                date_start = dt_from_str(day_start, month, year)
                date_end = dt_from_str(day_end, month, year)
            except (IndexError, ValueError):
                # 'октябр'
                month = dates[2][0]
                date_start = dt_from_str("05", month, year)
                date_end = dt_from_str("25", month, year)
        return date_start, date_end
    else:
        return None, None


def parse_table(data, season, group):
    parser = SimpleTable.build(data).find_teams(season).find_matches()
    print(vars(parser))
    team_seasons = parser.build_teams(season.pk, group.pk)
    return team_seasons, parser.matches


class TableRow:
    def __init__(self, **kwargs):
        self.place = kwargs.get("place", "")
        self.name = kwargs.get("name")
        self.wins = kwargs.get("w")
        self.draws = kwargs.get("d")
        self.losses = kwargs.get("l")
        self.score = kwargs.get("score", "")
        self.points = kwargs.get("points")
        self.team_id = kwargs.get("team_id")

    def __repr__(self):
        return f"TableRow(place={self.place}, name={self.name}, team_id={self.team_id})"

    def __str__(self):
        return f"{self.place}. {self.name} ({self.team_id})"

    def build(self, season=None, group=None):
        """Return Django model instance."""
        if season:
            cls = TeamSeason
            kwargs = {"season_id": season}
        if group:
            cls = GroupSeason
            kwargs = {"group_id": group}
        return cls(**vars(self), **kwargs)


class Match:
    model = MatchModel

    def __init__(self, *args, **kwargs):
        self.home_id = kwargs.get("home_id")
        self.away_id = kwargs.get("away_id")
        self.home_score = kwargs.get("home_score")
        self.away_score = kwargs.get("away_score")
        self.tourn_season_id = kwargs.get("tourn_season_id")

    def __repr__(self):
        return (
            f"Match(home_id={self.home_id}, "
            + f"away_id={self.away_id}, "
            + f"home_score={self.home_score}, "
            + f"away_score={self.away_score}, "
            + f"tourn_season_id={self.tourn_season_id})"
        )

    def __str__(self):
        return f"{self.away_id} v {self.away_id} - {self.home_score}:{self.away_score}"

    def __eq__(self, other):
        return (
            self.home_id == other.away_id
            and self.away_id == other.home_id
            and self.home_score == other.away_score
            and self.away_score == other.home_score
        )

    @classmethod
    def from_string(cls, home_id, away_id, string):
        home_score, away_score = None, None
        if ":" in string:
            home_score, away_score = string.split(":")
        if string in {"поб", "побед", "выиг"}:
            home_score, away_score = 1, 0
        if string in {"пор", "пораж", "проиг"}:
            home_score, away_score = 0, 1
        if string in {"нич", "ничья"}:
            home_score, away_score = 1, 1
        return cls(
            home_id=home_id,
            away_id=away_id,
            home_score=home_score,
            away_score=away_score,
        )

    def build(self, **kwargs):
        kwargs.update(**vars(self))
        if self.tourn_season_id:
            instance = self.model(**kwargs)
            instance.set_tech_score()
            return instance

    def save(self):
        return self.build().save()


class FullMatch(Match):
    """With halftime scores and story."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.home_halfscore = kwargs.get("home_halfscore")
        self.away_halfscore = kwargs.get("away_halfscore")
        self.story = kwargs.get("story", "")
        self.technical = kwargs.get("technical", False)
        self.tech_home_loss = kwargs.get("tech_home_loss", False)
        self.tech_away_loss = kwargs.get("tech_away_loss", False)


EDGE = "xxxxx"
EDGE_RU = "ххххх"


class SimpleTable:
    """
    line may be any representation in table:

    1. Динамо                     xxxxx  22:6    поб   13:3   20:0    поб

    5. "Спартак" Ленинград      6:18   0:6    0:3    0:8   xxxxx  20:8   1 0 4  26-43  2

    1. "СТАКЛЕС" Каунас            6  0  2  164:72   12 *

    1. Крылья Советов Москва
    . Скра
    2. Политехник Киев
    3. МАИ Москва (?)
    .. РАФ Елгава

    """

    def __init__(self, lines, legs=1):
        self._lines = lines
        self._teams = []
        self._matches = {}
        self._column_marks = []
        self._column_parts = []
        self._season_id = None
        self.legs = legs

    @classmethod
    def build(cls, txt):
        _list = [
            line.strip()
            for line in txt.split("\n")
            if not line.startswith("-") and line.strip()
        ]

        return cls(_list).find_columns()

    def find_columns(self):
        """Every line must be approx the same width, we need to define columns."""
        lens = []
        for line in self._lines:
            marks = self._mark_columns(line)
            self._column_marks.append(marks)
            lens.append(len(marks))

        for line, marks in zip(self._lines, self._column_marks):
            self._column_parts.append(self._split_line(line, marks))
        return self

    @staticmethod
    def _mark_columns(line):
        previous_idx = -100
        bounds = []
        for idx, letter in enumerate(line):
            if letter == " ":
                if previous_idx + 1 == idx:
                    # consecutive whitespace found
                    if bounds and bounds[-1] == previous_idx:
                        bounds[-1] += 1
                    else:
                        bounds.append(idx)
                previous_idx = idx
        return bounds

    @staticmethod
    def _split_line(line, marks):
        if marks:
            start, end = it.tee(marks)
            next(end)
            return [line[i:j].strip() for i, j in it.zip_longest(start, end)]

    def find_teams(self, season=None):
        # if TeamSeason-s exist, try them first to get a team name
        year = season.date_start.year if season else None
        self._season_id = season.id if season else None
        names = dict(season.standings.values_list("team_id", "name")) if season else {}

        for line, marks in zip(self._lines, self._column_marks):
            # Extract team name from the beginning of the line
            if marks:
                team_part = line[: marks[0]]
            else:
                team_part = line

            # Split on first dot to separate place from team name
            if "." in team_part:
                parts = team_part.split(".", 1)
                place = parts[0].strip()
                team = parts[1].strip() if len(parts) > 1 else ""
            else:
                # No dot found, treat entire part as team name with no place
                place = ""
                team = team_part.strip()

            # Clean up team name
            team = team.replace('"', "").strip()

            # Skip empty team names
            if not team:
                continue

            # Try to match with existing teams
            team_id = None
            if names:
                ratios = {
                    fuzz.token_set_ratio(team, sn): team_id
                    for team_id, sn in names.items()
                }
                if ratios and max(ratios) > TEAM_SIMILAR_THRESHOLD:
                    team_id = ratios[max(ratios)]
                    team = names[team_id]

            # Fallback to find_team_name_match if no match found
            if not team_id:
                team = team.replace(".", "").strip()
                team_id = (
                    find_team_name_match(team, year)
                    if "find_team_name_match" in globals()
                    else None
                )

            row = TableRow(place=place, name=team, team_id=team_id)
            self._teams.append(row)
        return self

    def find_matches(self):
        if not self._teams:
            return self

        # Check if there are any columns with match data
        has_match_data = False
        for parts in self._column_parts:
            if parts and len(parts) > 1:
                for part in parts:
                    if part and ":" in part or "-" in part or part in {EDGE, EDGE_RU}:
                        has_match_data = True
                        break
            if has_match_data:
                break

        if not has_match_data:
            # No matches - only team names or standings without match matrix
            return self

        if not self._column_marks[0]:
            # no columns - no matches. it's only a team name
            return self

        # Count how many parts each row has
        part_counts = [
            len(parts) if parts else 0
            for parts in self._column_parts[: min(3, len(self._column_parts))]
        ]

        # If first rows have decreasing number of parts, it's likely one-legged
        if len(part_counts) >= 3 and part_counts[0] > part_counts[1] > part_counts[2]:
            return self._find_in_oneleg_table()

        # Check if it's a full matrix (two-legged or symmetric)
        total_teams = len(self._teams)
        is_full_matrix = True
        for idx, parts in enumerate(self._column_parts[:total_teams]):
            if not parts or len(parts) < total_teams:
                is_full_matrix = False
                break

        if is_full_matrix:
            return self._find_in_full_table()

        # Default to one-legged if structure is unclear but has some match data
        return self._find_in_oneleg_table()

    def _find_in_full_table(self):
        """Find matches in fully filled table.

        The table must be filled with both sides:

            xxxxx  13:14  22:5
            14:13  xxxxx  16:6
             5:22   6:16  xxxxx

        """
        total = len(self._teams)
        for team_idx in range(total):
            start_idx = 0
            parts = self._column_parts[team_idx]
            if not parts:
                logger.info(f"no parts in table: {self}")
                break

            if parts[team_idx] in {EDGE, EDGE_RU}:
                self._parse_matches(total, parts, team_idx)
                start_idx = total
            try:
                # parse games part: ['12 1 1', 'xxx-xx', '25']
                self._parse_standings(parts, start_idx, team_idx)
            except IndexError as exc:
                logger.warning(f"No stadings in the table. {exc}")
                logger.warning(f"parts={parts}, start_idx={start_idx}")
        return self

    def _find_in_oneleg_table(self):
        total = len(self._teams)
        for position, table_row in enumerate(self._column_parts):
            if not table_row:
                logger.warning(f"no table_row in table: {self}")
                break

            # Find where matches start (looking for xxxxx or EDGE markers)
            match_start_idx = -1
            for idx, cell in enumerate(table_row):
                if cell in {EDGE, EDGE_RU}:
                    match_start_idx = idx
                    break

            if match_start_idx >= 0:
                # Parse matches starting from the position column
                match_parts = [""] * position + table_row[match_start_idx:]
                self._parse_matches(total, match_parts, position)

                # Parse standings after matches
                standings_start = match_start_idx + (total - position)
                try:
                    self._parse_standings(table_row, standings_start, position)
                except IndexError as exc:
                    logger.warning(f"No stadings in the table. {exc}")
            else:
                # No matches found, try to parse standings from beginning
                try:
                    self._parse_standings(table_row, 0, position)
                except IndexError as exc:
                    logger.warning(f"No stadings in the table. {exc}")
        return self

    def latvian_table(self):
        """Parse table without matches - only standings."""
        for position, table_row in enumerate(self._column_parts):
            if not table_row:
                continue
            try:
                # parse games part: ['12 1 1', 'xxx-xx', '25']
                self._parse_standings(table_row, 0, position)
            except IndexError as exc:
                logger.warning(f"No stadings in the table. {exc}")
                logger.warning(f"parts={table_row}, start_idx=0")
        return self

    def _parse_matches(self, num_teams, match_parts, team_idx):
        # TODO: parse two_legged tables
        for match_idx in range(team_idx, num_teams):
            if match_idx >= len(match_parts):
                break
            match_str = match_parts[match_idx]
            if match_str and match_str not in {EDGE, EDGE_RU}:
                match = Match.from_string(
                    self._teams[team_idx].team_id,
                    self._teams[match_idx].team_id,
                    match_str,
                )
                match.tourn_season_id = self._season_id
                self._matches[(team_idx, match_idx)] = match

    def _parse_standings(self, match_parts, start_idx, team_idx):
        if team_idx >= len(self._teams):
            return

        if start_idx >= len(match_parts):
            return

        first = match_parts[start_idx]
        to_parse = match_parts[start_idx + 1 :]
        team = self._teams[team_idx]

        if " " in first:
            w_d_l = first.split()
            w_d_l.extend(to_parse)
            to_parse = w_d_l
        else:
            to_parse.insert(0, first)

        if len(to_parse) >= 3:
            team.wins = to_parse[0]
            team.draws = to_parse[1]
            team.losses = to_parse[2]
            to_parse = to_parse[3:]

        if len(to_parse) == 2:
            team.score = to_parse[0]
            team.points = to_parse[1]
        if len(to_parse) == 1:
            if "-" in to_parse[0] or ":" in to_parse[0]:
                team.score = to_parse[0]
            else:
                team.points = to_parse[0]

    def build_teams(self, season=None, group=None):
        return [t.build(season, group) for t in self._teams]

    @property
    def matches(self):
        return self._matches.values()


def find_team_name_match(search_name, year=None):
    """
    Find the most suitable instance by base name and given names.
    """
    condition = ""
    if year:
        condition += f" AND tt.year <= {year} AND (tt.disband_year >= {year} OR tt.disband_year IS NULL)"

    base_name = """SELECT tt.tagobject_ptr_id as team_id, t.name as team_name, c.name as city, tt.year, tt.disband_year
  FROM teams_team tt
 INNER JOIN teams_tagobject t ON t.id=tt.tagobject_ptr_id
  LEFT OUTER JOIN teams_city c on c.id=tt.city_id
 WHERE t.name LIKE '{name}%'{condition}"""

    with connection.cursor() as cursor:
        sqlite_ver = (
            "strftime('%Y', from_day) as year, strftime('%Y', to_day) as disband_year"
        )
        extract_years = "extract(year from from_day) as year, extract(year from to_day) as disband_year"
        if cursor.db.client_class.executable_name == "sqlite3":
            extract_years = sqlite_ver

        given_names = (
            f"SELECT team_id, tn.name as team_name, c.name as city, {extract_years}"
            + """
  FROM teams_teamname tn
 INNER JOIN teams_team tt ON tt.tagobject_ptr_id=tn.team_id
 INNER JOIN teams_city c ON c.id = tt.city_id
 WHERE tn.name LIKE '{name}%'{condition}"""
        )

        sql = f"""SELECT * FROM (
 {base_name}
  UNION ALL
 {given_names}
) as u;"""
        sql = sql.format(name=search_name[:3], condition=condition)
        cursor.execute(sql)
        res = cursor.fetchall()

    ratios = [fuzz.token_set_ratio(search_name, f"{obj[1]} {obj[2]}") for obj in res]

    if ratios and max(ratios) > TEAM_SIMILAR_THRESHOLD:
        found = res[ratios.index(max(ratios))][0]
    else:
        found = None
    return found


DAY_RE = re.compile(r"((?P<day>\d{1,2})|(?P<unknown>\?+)) (?P<month>[а-я]+)")
MATCH_RE = re.compile(
    r"(?P<home>[А-Я() -]+) - (?P<away>[А-Я() -]+) - (?P<outcome>[А-Я ]+|(?P<full_score>\d+:\d+)(?P<half_score> \(\d+:\d+\))?(?P<scorers> - .+)?)?",
    re.MULTILINE | re.IGNORECASE,
)
SCORE_RE = re.compile(r"(\d+):(\d+)")

UNCERTAIN_SCORE_RE = re.compile(r"[пшдгрт][а-я]*:\s*\?")
SCORER_CONT_RE = re.compile(r"^[пшдгрт][а-я]*:")

DIV_TAGS = {
    "match": ("<div class='match'>", '<div class="match">'),
    "lineup": ("<div class='lineup'>", '<div class="lineup">'),
    "txt": ("<div class='txt'>", '<div class="txt">'),
}


@dataclass
class _DateState:
    default_date: dt.date
    date: t.Optional[dt.date] = None
    is_unknown: bool = False

    def set_explicit(self, date: dt.date, is_unknown: bool = False):
        self.date = date
        self.default_date = date
        self.is_unknown = is_unknown

    def roll(self):
        self.default_date = (self.date or self.default_date) + dt.timedelta(days=1)
        self.date = None
        self.is_unknown = True

    def snapshot(self) -> "_DateState":
        return copy(self)


@dataclass
class _BlankEvent:
    pass


@dataclass
class _DateLineEvent:
    line: str


@dataclass
class _MatchDivEvent:
    lines: t.List[str]


@dataclass
class _LineupDivEvent:
    lines: t.List[str]


def _iter_events(lines: t.List[str]):
    """Convert raw lines into typed events, handling div accumulation."""
    accumulating = None
    accumulated = []

    for raw_line in lines:
        line = raw_line.replace("<br>", "\n").strip()

        if accumulating:
            accumulated.append(raw_line)
            if "</div>" in raw_line:
                if accumulating == "match":
                    yield _MatchDivEvent(list(accumulated))
                elif accumulating == "lineup":
                    yield _LineupDivEvent(list(accumulated))
                # txt: discard
                accumulating = None
                accumulated = []
            continue

        if not line:
            yield _BlankEvent()
            continue

        if any(t in raw_line for t in DIV_TAGS["match"]):
            accumulating = "match"
            accumulated = [raw_line]
        elif any(t in raw_line for t in DIV_TAGS["lineup"]):
            accumulating = "lineup"
            accumulated = [raw_line]
        elif any(t in raw_line for t in DIV_TAGS["txt"]):
            accumulating = "txt"
            accumulated = [raw_line]
        else:
            yield _DateLineEvent(line)

    # EOF: yield any unclosed div
    if accumulating == "match" and accumulated:
        yield _MatchDivEvent(list(accumulated))
    elif accumulating == "lineup" and accumulated:
        yield _LineupDivEvent(list(accumulated))


class CalendarParser:
    def __init__(self, lines: t.List[str], teams: t.Dict[str, int]):
        self._lines = lines
        self._matches: t.List[FullMatch] = []
        self._team_names = teams

    def __repr__(self):
        return f"Calendar: matches={self._matches}, teams={self._team_names}"

    @property
    def matches(self):
        return self._matches

    @classmethod
    def build(cls, text, season):
        teams = dict(season.standings.values_list("name", "team_id"))
        return cls(text.split("\n"), teams)

    # ── Story helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def _add_to_story(current: str, new: str) -> str:
        if not current:
            return new
        if not new:
            return current
        return f"{current}\n\n{new}"

    @staticmethod
    def _extract_story_from_match_line(line: str) -> str:
        for m in MATCH_RE.finditer(line):
            scorers = (m.groupdict().get("scorers") or "").strip()
            for prefix in (" - ", " -", "- ", "-"):
                if scorers.startswith(prefix):
                    scorers = scorers[len(prefix) :]
                    break
            return scorers.strip()
        return ""

    @staticmethod
    def _is_uncertain_score(line: str) -> bool:
        return line.rstrip().endswith("?") and not UNCERTAIN_SCORE_RE.search(line)

    @staticmethod
    def _extract_uncertain_outcome(full_match_line: str) -> str:
        parts = full_match_line.split(" - ", 2)
        return parts[2].strip() if len(parts) >= 3 else ""

    # ── Div processing ────────────────────────────────────────────────────────

    def _process_match_div(
        self, event: _MatchDivEvent
    ) -> t.Tuple[t.Optional[str], str]:
        """Returns (first_line, story_content) for a match div."""
        lines_to_join = []
        for line in event.lines:
            for tag in (*DIV_TAGS["match"], "</div>", "<br>", "<br />", "<br/>"):
                line = line.replace(tag, "")
            line = line.replace("—", "-").replace("–", "-")  # normalise dashes
            if line.strip():
                lines_to_join.append(line.strip())

        if not lines_to_join:
            return None, ""

        # First line + scorer continuations joined with space;
        # everything else \n\n separated.
        scorer_parts = [lines_to_join[0]]
        rest = []
        for l in lines_to_join[1:]:
            is_continuation = scorer_parts[-1].rstrip().endswith(
                ","
            ) or SCORER_CONT_RE.match(l)
            if not rest and is_continuation:
                scorer_parts.append(l)
            else:
                rest.append(l)

        full_match_line = " ".join(scorer_parts)
        first_line = scorer_parts[0]

        if self._is_uncertain_score(full_match_line):
            story_content = ""
            for l in rest:
                story_content = self._add_to_story(story_content, l)
            story_content = self._add_to_story(
                story_content, self._extract_uncertain_outcome(full_match_line)
            )
        else:
            story_content = self._extract_story_from_match_line(full_match_line)
            for l in rest:
                story_content = self._add_to_story(story_content, l)

        return first_line, story_content

    def _process_lineup_div(self, event: _LineupDivEvent) -> str:
        """Reassemble lineup div as clean HTML with space-joined inner content."""
        inner = " ".join(l.strip() for l in event.lines if l.strip())
        for tag in (*DIV_TAGS["lineup"], "</div>"):
            inner = inner.replace(tag, "")
        return f"<div class='lineup'>\n{inner.strip()}\n</div>"

    # ── Main entry point ──────────────────────────────────────────────────────

    def find_matches(self, group, season):
        ds = _DateState(default_date=group.date_start)
        match = None
        match_first_line = None
        match_date_snapshot = None
        last_was_match = False

        def finalize():
            nonlocal match, match_first_line, match_date_snapshot
            if not match:
                return
            parsed = self.parse_match(match_first_line)
            if parsed:
                match.home_id = parsed.home_id
                match.away_id = parsed.away_id
                match.home_score = parsed.home_score
                match.away_score = parsed.away_score
                match.home_halfscore = parsed.home_halfscore
                match.away_halfscore = parsed.away_halfscore
            instance = match.build()
            snap = match_date_snapshot
            if snap.date:
                instance.date = snap.date
                instance.date_unknown = None
            else:
                instance.date = snap.default_date
                instance.date_unknown = instance.date.strftime("%Y-%m-xx")
            self._matches.append(instance)
            match = None
            match_first_line = None
            match_date_snapshot = None

        for event in _iter_events(self._lines):
            if isinstance(event, _BlankEvent):
                if last_was_match:
                    ds.roll()
                    last_was_match = False

            elif isinstance(event, _DateLineEvent):
                parsed, is_unknown = self.parse_date(event.line, group.date_start.year)
                if parsed:
                    finalize()
                    ds.set_explicit(parsed, is_unknown)
                    last_was_match = False

            elif isinstance(event, _MatchDivEvent):
                finalize()
                match_first_line, story_content = self._process_match_div(event)
                match = FullMatch()
                match.tourn_season_id = season.id
                match.story = story_content or ""
                match_date_snapshot = ds.snapshot()
                last_was_match = True

            elif isinstance(event, _LineupDivEvent):
                if match:
                    match.story = self._add_to_story(
                        match.story, self._process_lineup_div(event)
                    )

        finalize()
        return self

    # ── Parsing ───────────────────────────────────────────────────────────────

    def parse_date(self, line: str, year: int) -> t.Tuple[t.Optional[dt.date], bool]:
        for match in DAY_RE.finditer(line):
            data = match.groupdict()
            month_str = data.get("month")
            if not month_str:
                continue
            key, _ = process.extractOne(month_str, set(MONTHS_MAP))
            m = int(MONTHS_MAP[key])
            if data.get("unknown"):
                return dt.date(year, m, 1), True
            return dt.date(year, m, int(data.get("day", 1))), False
        return None, False

    def parse_match(self, txt) -> t.Optional[FullMatch]:
        if not txt:
            return None
        txt = txt.replace("—", "-").replace("–", "-")
        for match in MATCH_RE.finditer(txt):
            home_name, _ = process.extractOne(
                match.groupdict()["home"].strip(), set(self._team_names)
            )
            away_name, _ = process.extractOne(
                match.groupdict()["away"].strip(), set(self._team_names)
            )
            home_id = self._team_names.get(home_name)
            away_id = self._team_names.get(away_name)
            if home_id and away_id:
                m = FullMatch(home_id=home_id, away_id=away_id)
                if match.groupdict()["full_score"]:
                    scores = match.groupdict()["full_score"].split(":")
                    m.home_score = int(scores[0])
                    m.away_score = int(scores[1])
                if match.groupdict()["half_score"]:
                    half = SCORE_RE.findall(match.groupdict()["half_score"])
                    if half:
                        m.home_halfscore = int(half[0][0])
                        m.away_halfscore = int(half[0][1])
                return m
        return None


def parse_matches(data, season, group):
    parser = CalendarParser.build(data, season).find_matches(group, season)
    print(vars(parser))
    return [], parser.matches


def add_to_story(story, line):
    story = story.replace("<br>", "\n\n") if story else ""
    line = line.strip().replace("<br>", "\n\n").replace("</div>", "")
    return story + line
