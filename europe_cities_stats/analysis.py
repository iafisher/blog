import bisect
import copy
import json
import math
import statistics
import string
from collections import Counter, defaultdict

import dateutil.parser
import numpy

# Session: {
#   started_at: string (ISO 8601 timestamp),
#   saved_at: string (ISO 8601 timestamp),
#   cities: [string ...],
#   ip: string,
#   country: string,
# }
#
#
# City: {
#   name: string,
#   country: string,
#   count: number,
#   expectedCount: number,
#   population: number,
# }


def main():
    """
    Prints out a sequence of formatted Markdown tables and statistics that can be
    pasted into the blog post. The results are cached on disk so that they don't have to
    be recomputed on each run of the program.
    """
    results = read_results()
    cities = read_cities()
    sessions = read_sessions()

    sessions_with_ip = sum(1 for session in sessions.values() if session.get("ip"))
    sessions_with_country = sum(
        1 for session in sessions.values() if session.get("country")
    )
    sessions_with_time = sum(
        1
        for session in sessions.values()
        if session.get("started_at") and session.get("saved_at")
    )
    print(f"Total sessions: {len(sessions):,}")
    print(f"Total sessions with IP: {sessions_with_ip:,}")
    print(f"Total sessions with country: {sessions_with_country:,}")
    print(f"Total sessions with time: {sessions_with_time:,}")

    session_times = get_session_times(sessions)
    print(f"Median time: {numpy.percentile(session_times, 50)}")
    print(f"Maximum time: {session_times[-1]}")

    percentiles = compute(results, cities, sessions, "percentiles", get_percentiles)

    print()
    print()
    print(f"Median: {int(round(percentiles['50']))}")
    print(f"25th percentile: {int(round(percentiles['25']))}")
    print(f"75th percentile: {int(round(percentiles['75']))}")

    # 10th through 90th percentiles
    rows = [["percentile", "score"]]
    for i in range(90, 0, -10):
        if i == 50:
            rows.append([f"{i} (median)", int(round(percentiles[str(i)]))])
        else:
            rows.append([str(i), int(round(percentiles[str(i)]))])
    print()
    print()
    print_table(rows)

    # 90th through 99th percentile
    rows = [["percentile", "score"]]
    for i in range(99, 89, -1):
        rows.append([str(i), int(round(percentiles[str(i)]))])
    print()
    print()
    print_table(rows)

    nationalities = compute(
        results, cities, sessions, "nationalities", get_nationalities,
    )
    sorted_nationalities = list(sorted(nationalities.items(), key=lambda kv: kv[1]))
    filtered_nationalities = list(
        filter(lambda x: x[1][1] >= 100, sorted_nationalities)
    )
    filtered_nationalities_1000 = list(
        filter(lambda x: x[1][1] >= 1000, sorted_nationalities)
    )

    rows = [["rank", "country", "median score", "total plays"]]
    for i, (country, (median_score, total_plays)) in enumerate(
        list(reversed(filtered_nationalities))[:10], start=1,
    ):
        rows.append(
            [str(i), country, str(int(round(median_score))), f"{total_plays:,}"]
        )
    print()
    print()
    print("Best countries by median score (100+ scores)")
    print_table(rows)
    print("NOTE: Fix ranks for equal nations when pasting into post.")

    rows = [["rank", "country", "median score", "total plays"]]
    for i, (country, (median_score, total_plays)) in enumerate(
        filtered_nationalities[:10], start=1,
    ):
        rows.append(
            [str(i), country, str(int(round(median_score))), f"{total_plays:,}"]
        )
    print()
    print()
    print("Worst countries by median score (100+ scores)")
    print_table(rows)
    print("NOTE: Fix ranks for equal nations when pasting into post.")

    rows = [["rank", "country", "median score", "total plays"]]
    for i, (country, (median_score, total_plays)) in enumerate(
        filtered_nationalities_1000, start=1,
    ):
        rows.append(
            [str(i), country, str(int(round(median_score))), f"{total_plays:,}"]
        )
    print()
    print()
    print("All countries by median score (1000+ scores)")
    print_table(rows)
    print("NOTE: Fix ranks for equal nations when pasting into post.")

    best_countries_by_nationality = compute(
        results,
        cities,
        sessions,
        "best_countries_by_nationality",
        get_best_countries_by_nationality,
    )

    print()
    print()
    print("Best countries by nationality")
    for country, (best, second_best) in sorted(
        best_countries_by_nationality.items(), key=lambda kv: kv[0]
    ):
        best_name, best_score = best
        second_best_name, second_best_score = second_best
        print(
            f"- {country}: {best_name} ({int(round(best_score)):,}), "
            + f"{second_best_name} ({int(round(second_best_score)):,})"
        )

    best_known_cities = compute(
        results, cities, sessions, "best_known_cities", get_best_known_cities,
    )
    print()
    print()
    print("Best known cities")
    print_city_table(best_known_cities, sessions)

    best_known_cities_by_letter = compute(
        results,
        cities,
        sessions,
        "best_known_long_cities_by_letter",
        get_best_known_cities_by_letter,
    )

    rows = [["letter", "city", "percentage"]]
    for letter, (count, cities_list) in sorted(
        best_known_cities_by_letter.items(), key=lambda kv: kv[0]
    ):
        if len(cities_list) > 1:
            raise Exception(cities_list)

        p = city_percentage(cities_list[0], sessions)
        rows.append([f"**{letter}**", city_name(cities_list[0]), p])
    print()
    print()
    print_table(rows)

    biggest_cities_by_letter = compute(
        results,
        cities,
        sessions,
        "biggest_cities_by_letter",
        get_biggest_cities_by_letter,
    )

    print()
    print()
    print("Biggest cities that are not the best known for their letter:")
    for letter in sorted(best_known_cities_by_letter):
        best_known = best_known_cities_by_letter[letter][1][0]
        biggest = biggest_cities_by_letter[letter]
        if best_known["code"] != biggest["code"]:
            p = city_percentage(biggest, sessions)
            p2 = city_percentage(best_known, sessions)
            print(
                f"- {city_name(best_known)} ({p2}, {best_known['population']:,})",
                end=" ",
            )
            print("beats ", end="")
            print(f"**{city_name(biggest)}** ({p}, {biggest['population']:,})")

    cities_by_popularity = compute(
        results, cities, sessions, "cities_by_popularity", get_cities_by_popularity,
    )

    print()
    print()
    print("Surprisingly popular cities")
    print_popularity_table(reversed(cities_by_popularity[-10:]), sessions)

    print()
    print()
    print("Surprisingly popular cities (at least 10%)")
    popular_cities = list(
        filter(lambda city: city["count"] / len(sessions) >= 0.1, cities_by_popularity)
    )
    print_popularity_table(reversed(popular_cities[-10:]), sessions)

    print()
    print()
    print("Surprisingly popular cities over 100,000")
    cities_by_popularity_over_50k = list(
        filter(lambda city: city["population"] >= 100000, cities_by_popularity)
    )
    print_popularity_table(reversed(cities_by_popularity_over_50k[-10:]), sessions)

    print()
    print()
    print("Surprisingly unpopular cities")
    print_popularity_table(cities_by_popularity[:10], sessions)

    print()
    print()
    print("Surprisingly unpopular cities (at least 10% expected)")
    unpopular_cities = list(
        filter(
            lambda city: city["expectedCount"] / len(sessions) >= 0.1,
            cities_by_popularity,
        )
    )
    print_popularity_table(unpopular_cities[:10], sessions)

    forgotten_capitals = compute(
        results, cities, sessions, "forgotten_capitals", get_forgotten_capitals,
    )
    print()
    print()
    print("Forgotten capitals")
    print_city_table(forgotten_capitals, sessions)

    forgotten_countries = compute(
        results, cities, sessions, "forgotten_countries", get_forgotten_countries,
    )
    print()
    print()
    rows = [["rank", "country", "percentage"]]
    for i, (country, count) in enumerate(forgotten_countries, start=1):
        p = count / len(sessions)
        rows.append([str(i), country, f"{p:.1%}"])
    print("Forgotten countries")
    print_table(rows)

    write_results(results)


def compute(results, cities, sessions, key, f, *, force=False):
    if force or not results.get(key):
        results[key] = f(cities, sessions)

    return results[key]


def get_session_times(sessions):
    times = []
    for session in sessions.values():
        started_at = session.get("started_at")
        saved_at = session.get("saved_at")
        if not started_at or not saved_at:
            continue

        started_at = dateutil.parser.isoparse(started_at)
        saved_at = dateutil.parser.isoparse(saved_at)
        times.append(saved_at - started_at)

    times.sort()
    return times


def get_percentiles(cities, sessions):
    scores = list(sorted(len(session["cities"]) for session in sessions.values()))
    percentiles = [
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80,
        90,
        91,
        92,
        93,
        94,
        95,
        96,
        97,
        98,
        99,
        25,
        75,
    ]
    return {str(p): numpy.percentile(scores, p) for p in percentiles}


def get_nationalities(cities, sessions):
    scores_by_country = defaultdict(list)
    for session in sessions.values():
        country = session.get("country")
        if not country:
            continue

        scores_by_country[country].append(len(session["cities"]))

    medians_by_country = {}
    for country, scores in scores_by_country.items():
        scores.sort()
        medians_by_country[country] = (numpy.percentile(scores, 50), len(scores))

    return medians_by_country


def get_best_countries_by_nationality(cities, sessions):
    r = defaultdict(lambda: Counter())
    for session in sessions.values():
        country = session.get("country")
        if not country:
            continue

        r[country]["__session_count"] += 1
        for city_id in session["cities"]:
            city = cities.get(city_id)
            if not city:
                continue
            r[country][city["country"]] += 1

    r2 = {}
    for country, country_scores in r.items():
        n = country_scores["__session_count"]
        if n < 100:
            continue

        best, second_best = country_scores.most_common(2)
        r2[country] = [(best[0], best[1] / n), (second_best[0], second_best[1] / n)]

    return r2


def get_best_known_cities(cities, sessions, constraint=None):
    if constraint:
        it = filter(constraint, cities.values())
    else:
        it = cities.values()

    return list(sorted(it, key=lambda c: c["count"], reverse=True))[:20]


def get_best_known_cities_by_letter(cities, sessions):
    r = {}
    for city in cities.values():
        c = city["name"][0].upper()
        if not c in string.ascii_uppercase:
            continue

        x = r.get(c)
        if x is not None:
            count, cities = x
            if city["count"] > count:
                r[c] = (city["count"], [city])
            elif city["count"] == count:
                cities.append(city)
        else:
            r[c] = (city["count"], [city])

    return r


def get_biggest_cities_by_letter(cities, sessions):
    r = {}
    for city in cities.values():
        c = city["name"][0].upper()
        if not c in string.ascii_uppercase:
            continue

        biggest = r.get(c)
        if biggest is None or city["population"] > biggest["population"]:
            r[c] = city

    return r


def get_cities_by_popularity(cities, sessions):
    cities_by_popularity = (
        city
        for city in cities.values()
        if city["population"] >= 5000
        and city["expectedCount"]
        and city["count"] >= 50
        and city["code"]
        not in (
            # Cities with known problems (not real cities or incorrect populations)
            "geonames-3124964",
            "geonames-11777624",
            "geonames-3125239",
            "geonames-3345283",
            "geonames-2655613",
            "geonames-2639912",
        )
    )
    cities_by_popularity = sorted(
        cities_by_popularity,
        key=lambda city: city["count"] / city["expectedCount"]
        # cities_by_popularity, key=lambda city: city["count"] - city["expectedCount"]
    )
    return list(cities_by_popularity)


def get_forgotten_capitals(cities, sessions):
    capitals = filter(lambda city: city["nationalCapital"], cities.values())
    sorted_by_count = sorted(capitals, key=lambda city: city["count"])
    return list(sorted_by_count)[:10]


def get_forgotten_countries(cities, sessions):
    countries = Counter()
    for session in sessions.values():
        countries_for_this_session = set()
        for city_id in session["cities"]:
            try:
                city = cities[city_id]
            except KeyError:
                continue

            if city["country"] not in countries_for_this_session:
                countries[city["country"]] += 1
                countries_for_this_session.add(city["country"])

    return list(sorted(countries.items(), key=lambda kv: kv[1]))[:10]


def city_name(city):
    return f"{city['name']}, {city['country']}"


def city_percentage(city, sessions):
    p = city["count"] / len(sessions)
    return f"{p:.1%}"


def print_popularity_table(cities, sessions):
    rows = [["rank", "city", "population", "popularity", "expected popularity"]]
    for i, city in enumerate(cities, start=1):
        p = city["count"] / len(sessions)
        ex_p = city["expectedCount"] / len(sessions)
        rows.append(
            [
                str(i),
                city_name(city),
                f"{city['population']:,}",
                f"{p:.1%}",
                f"{ex_p:.1%}",
            ]
        )
    print_table(rows)


def print_city_table(cities, sessions):
    rows = [["rank", "city", "percentage"]]
    for i, city in enumerate(cities, start=1):
        rows.append([str(i), city_name(city), city_percentage(city, sessions)])
    print_table(rows)


def print_table(rows):
    widths = [max(len(str(row[i])) for row in rows) for i in range(len(rows[0]))]

    for i, row in enumerate(rows):
        for j, (cell, width) in enumerate(zip(row, widths)):
            print(str(cell).ljust(width), end="")
            if j != len(row) - 1:
                print(" | ", end="")

        print()

        if i == 0:
            for j, width in enumerate(widths):
                print("-" * width, end="")
                if j != len(row) - 1:
                    print(" | ", end="")

            print()


def expected_guesses(population):
    best_fit_slopes = [
        1.3418776482343513,
        1.429839330734348,
        1.6306384283100315,
        1.5928537240405154,
        1.17528847478339,
        0.4073331472851946,
    ]
    intercept = -3.651537374003276
    for i in range(len(best_fit_slopes)):
        lo = 3.5 + i * 0.5
        hi = 4.0 + i * 0.5
        # Make the last bin very large to include cities of over 10 million.
        if i + 1 == len(best_fit_slopes):
            hi = 9

        slope = best_fit_slopes[i]
        if i != 0:
            intercept = best_fit_slopes[i - 1] * lo + intercept - slope * lo

        if lo < numpy.log10(population) <= hi:
            return 10 ** (slope * numpy.log10(population) + intercept)


def expected_guesses_usa(population):
    # Expected guesses for the U.S. quiz, for posterity.
    params = [
        2.04126476,
        2.01700143,
        3.86551436,
        3.80428262,
        1.64792331,
        0.11198609,
        0.09391142,
    ]
    intercept = -3.27126179
    for i in range(len(params)):
        lo = 3.5 + i * 0.5
        hi = 4.0 + i * 0.5

        slope = params[i]
        if i != 0:
            intercept = params[i - 1] * lo + intercept - slope * lo

        if lo < numpy.log10(population) <= hi:
            return numpy.exp(slope * numpy.log10(population) + intercept)


def read_sessions(*, exclude_small=True):
    with open("data/sessions.json", "r", encoding="utf8") as f:
        sessions = json.load(f)

    if exclude_small:
        sessions = {k: v for k, v in sessions.items() if len(v["cities"]) >= 10}

    return sessions


def write_sessions(sessions):
    with open("data/sessions.json", "w", encoding="utf8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)


def read_cities():
    with open("data/cities_with_counts.json", "r", encoding="utf8") as f:
        return json.load(f)


def read_results():
    try:
        with open("data/results.json", "r", encoding="utf8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def write_results(results):
    with open("data/results.json", "w", encoding="utf8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def geolocate():
    import geoip2.database
    import geoip2.errors

    sessions = read_sessions()
    with geoip2.database.Reader(
        "data/GeoLite2-City_20210223/GeoLite2-City.mmdb"
    ) as reader:
        for session in sessions.values():
            if not session["ip"]:
                continue

            try:
                response = reader.city(session["ip"])
            except geoip2.errors.AddressNotFoundError:
                continue
            else:
                session["country"] = response.country.name

    with open("data/sessions.json", "w", encoding="utf8") as f:
        json.dump(sessions, f)


if __name__ == "__main__":
    main()
