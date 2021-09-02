# London, Paris, and Naberezhnyye Chelny: Analyzing results from my European cities quiz
In October 2019, I published a [geography quiz](https://iafisher.com/projects/cities/europe) that challenges players to name as many cities, towns and villages in Europe as they can. In the year and a half since, the game has been played more than 100,000 times and yielded a large body of data about the relative fame and obscurity of European cities and the general public's knowledge of European geography. This post presents key findings from the analysis of this data.

The median player named **124 European cities**, while the top 10% of players each named **at least 364 cities**. The city named by the most players was **London**, followed closely by Paris. For its size, **Vaduz, Liechtenstein** was the most surprisingly well-known city in Europe, **Spárti, Greece** (better known in English as Sparta) was the most surprisingly well-known city that is not a capital, and **Tromsø, Norway** was the most surprisingly well-known city that is not a capital and that has at least 50,000 inhabitants. **Volzhskiy, Russia**, a suburb of Volgograd of more than 300,000 people, was the most surprisingly obscure city. **Valletta, Malta** was the most forgotten national capital and **Malta** was the most forgotten country. Players from **Serbia** and **Spain** named the highest number of cities on average, while players from **India**, **New Zealand** and the **United States** named the lowest number.

[Sasha Trubetskoy](https://sashamaps.net/) assisted with the statistical analysis.

## Methodology
The analysis was based on a dataset of 105,756 plays of my Europe cities quiz between October 2019 and February 2021. The dataset comprised every saved play of the quiz in that period, except for plays where fewer than 10 cities were named, or where the "Every country" option was used (allowing players to receive credit for multiple cities with a single guess). Unsaved plays were not included in the analysis as they are stored locally on each player's computer and I do not have access to them.

The IP address of the player was recorded for 41,203 plays (39%), and 41,164 of these were successfully geolocated using the [GeoLite2](https://www.maxmind.com/en/geolite2/eula) database.

The "popularity" of a city is the percentage of the total plays in which that city was named. The "expected popularity" of each city was calculated as a function of its population using a piecewise linear regression of the quiz results.

The code for the analysis can be viewed [on GitHub](https://github.com/iafisher/blog/blob/master/europe_cities_stats/analysis.py).

**Disclaimers**: Most of this analysis tacitly assumes that every player named as many cities in Europe as they knew, but this assumption is sometimes wrong: some players don't name as many cities as they can, and some players name cities they don't know (whether by guessing randomly or by consulting external resources). IP geolocation can be inaccurate, and just because a player's IP address is *in* a country doesn't mean that the player is *from* that country. The population figures come largely from the [GeoNames](https://www.geonames.org) database and may differ from official figures, sometimes substantially.

## Basic stats
The median player named **124 cities**. 75% of players named at least **66 cities**, and 25% of players named **219 cities** or more. Table&nbsp;1 lists every tenth percentile.

percentile  | score
----------- | -----
90          | 364
80          | 252
70          | 195
60          | 154
50 (median) | 124
40          | 100
30          | 77
20          | 55
10          | 34

<p class="caption"><span class="caption-label">Table 1</span>: Scores by percentile, 10th to 90th</p>

Table&nbsp;2 shows that players in the 99th percentile named **947 cities** or more.

percentile | score
---------- | -----
99         | 947
98         | 717
97         | 607
96         | 542
95         | 500
94         | 461
93         | 430
92         | 404
91         | 384

<p class="caption"><span class="caption-label">Table 2</span>: Scores by percentile, 91st to 99th</p>

The median player finished **26 minutes and 36 seconds** after they started, while the longest play lasted **192 days** from the time it was started to the time it was saved.[^sessions-with-times]

## What are the best-known cities in Europe?
The twenty best-known cities, by the percentage of players that named them, are shown in Table&nbsp;3.

rank | city                   | percentage
---- | ---------------------- | ----------
1    | London, United Kingdom | 91.7%
2    | Paris, France          | 90.9%
3    | Berlin, Germany        | 89.2%
4    | Madrid, Spain          | 88.4%
5    | Rome, Italy            | 87.3%
6    | Moscow, Russia         | 85.5%
7    | Barcelona, Spain       | 83.4%
8    | Dublin, Ireland        | 82.4%
9    | Zagreb, Croatia        | 82.0%
10   | Oslo, Norway           | 81.3%
11   | Athens, Greece         | 80.8%
12   | Lisbon, Portugal       | 80.8%
13   | Amsterdam, Netherlands | 80.0%
14   | Warsaw, Poland         | 78.4%
15   | Stockholm, Sweden      | 77.7%
16   | Vienna, Austria        | 77.7%
17   | Munich, Germany        | 77.0%
18   | Milan, Italy           | 75.1%
19   | Copenhagen, Denmark    | 74.5%
20   | Helsinki, Finland      | 74.4%

<p class="caption"><span class="caption-label">Table 3</span>: Best-known cities</p>

London narrowly edges out Paris for the top spot, followed by a few other high-profile European capitals. The only non-capitals to make the top twenty are Barcelona, Munich and Milan, which, probably not coincidentally, are all home to internationally renowned soccer teams. The results for Zagreb, and possibly London, are somewhat inflated because they are the suggested cities in the search bar.

Table&nbsp;4 lists the best-known city for each letter of the alphabet.

letter | city                       | percentage
------ | -------------------------- | ----------
**A**  | Athens, Greece             | 80.8%
**B**  | Berlin, Germany            | 89.2%
**C**  | Copenhagen, Denmark        | 74.5%
**D**  | Dublin, Ireland            | 82.4%
**E**  | Edinburgh, United Kingdom  | 63.5%
**F**  | Frankfurt am Main, Germany | 62.0%
**G**  | Glasgow, United Kingdom    | 60.8%
**H**  | Helsinki, Finland          | 74.4%
**I**  | Istanbul, Turkey           | 59.9%
**J**  | Jena, Germany              | 9.6%
**K**  | Kyiv, Ukraine              | 74.0%
**L**  | London, United Kingdom     | 91.7%
**M**  | Madrid, Spain              | 88.4%
**N**  | Naples, Italy              | 64.0%
**O**  | Oslo, Norway               | 81.3%
**P**  | Paris, France              | 90.9%
**Q**  | Quimper, France            | 4.8%
**R**  | Rome, Italy                | 87.3%
**S**  | Stockholm, Sweden          | 77.7%
**T**  | Tallinn, Estonia           | 56.0%
**U**  | Utrecht, Netherlands       | 23.1%
**V**  | Vienna, Austria            | 77.7%
**W**  | Warsaw, Poland             | 78.4%
**X**  | Xánthi, Greece             | 1.7%
**Y**  | York, United Kingdom       | 35.4%
**Z**  | Zagreb, Croatia            | 82.0%

<p class="caption"><span class="caption-label">Table 4</span>: Best-known cities by letter of the alphabet</p>

Fifteen of these cities are not the largest of their letter by population:

- Athens, Greece (80.8%, 664,046) beats **Amsterdam, Netherlands** (80.0%, 741,636)
- Copenhagen, Denmark (74.5%, 632,340) beats **Chisinau, Moldova** (33.6%, 635,994)
- Dublin, Ireland (82.4%, 554,554) beats **Dnipro, Ukraine** (14.0%, 998,103)
- Edinburgh, United Kingdom (63.5%, 464,990) beats **Essen, Germany** (28.1%, 593,085)
- Helsinki, Finland (74.4%, 558,457) beats **Hamburg, Germany** (68.1%, 1,899,160)
- Jena, Germany (9.6%, 104,712) beats **Jerez de la Frontera, Spain** (4.6%, 207,532)
- Madrid, Spain (88.4%, 3,223,334) beats **Moscow, Russia** (85.5%, 12,506,468)
- Naples, Italy (64.0%, 959,470) beats **Nizhniy Novgorod, Russia** (16.3%, 1,259,013)
- Oslo, Norway (81.3%, 580,000) beats **Odessa, Ukraine** (32.1%, 1,011,494)
- Quimper, France (4.8%, 63,849) beats **Queluz, Portugal** (0.4%, 103,399)
- Stockholm, Sweden (77.7%, 975,904) beats **Saint Petersburg, Russia** (74.3%, 5,351,935)
- Tallinn, Estonia (56.0%, 394,024) beats **Turin, Italy** (51.7%, 870,456)
- Utrecht, Netherlands (23.1%, 290,529) beats **Ufa, Russia** (13.5%, 1,121,429)
- York, United Kingdom (35.4%, 153,717) beats **Yaroslavl, Russia** (7.4%, 606,730)
- Zagreb, Croatia (82.0%, 698,966) beats **Zaporizhia, Ukraine** (5.3%, 796,217)

Of the fifteen larger cities, nearly half (Chisinau, Dnipro, Nizhniy Novgorod, Odessa, Ufa, Yaroslavl, and Zaporizhia) are Eastern European cities that are relatively obscure despite their size. Five others (Amsterdam, Hamburg, Moscow, Saint Petersburg, and Turin) are near misses. Essen, a large German city in the Ruhr area, loses out to Edinburgh, well known as the capital of Scotland. Finally, Jerez de la Frontera, Spain and Queluz, Portugal undoubtedly fall behind simply because no European city beginning with a 'J' or 'Q' is particularly large, so population is less important than other factors.

## What European cities are surprisingly well-known or surprisingly obscure?
By dividing a city's actual popularity by its expected popularity (see the "Methodology" section for the definition of expected popularity), we can identify cities that are "surprisingly well-known" for their population. Table&nbsp;5 lists the top ten European cities by this metric.

rank | city                         | population | popularity | expected popularity
---- | ---------------------------- | ---------- | ---------- | -------------------
1    | Vaduz, Liechtenstein         | 5,197      | 29.2%      | 0.0%
2    | Valletta, Malta              | 6,794      | 21.5%      | 0.0%
3    | Andorra la Vella, Andorra    | 20,430     | 47.7%      | 0.1%
4    | Spárti, Greece               | 16,239     | 24.9%      | 0.1%
5    | Kotor, Montenegro            | 5,345      | 5.3%       | 0.0%
6    | Saint-Tropez, France         | 5,939      | 5.6%       | 0.0%
7    | Monaco, Monaco               | 32,965     | 57.7%      | 0.3%
8    | Wales, United Kingdom        | 5,956      | 5.2%       | 0.0%
9    | Bled, Slovenia               | 5,181      | 3.6%       | 0.0%
10   | Urbino, Italy                | 5,858      | 4.1%       | 0.0%

<p class="caption"><span class="caption-label">Table 5</span>: Surprisingly well-known cities</p>

Most of the surprisingly well-known cities fall into three categories: capitals (Vaduz, Valletta, Andorra la Vella, and Monaco), places of historical significance (Spárti [Sparta] and Urbino), and tourist destinations (Kotor, Saint-Tropez, and Bled, as well as Monaco). Wales makes the list either because people guessed it thinking of the country, or because it is well known for sharing the country's name.

All of the cities in Table&nbsp;5 are exceedingly small. Excluding cities with fewer than 50,000 inhabitants gives us Table&nbsp;6.

rank | city                       | population | popularity | expected popularity
---- | -------------------------- | ---------- | ---------- | -------------------
1    | Luxembourg, Luxembourg     | 76,684     | 58.0%      | 1.1%
2    | Tromsø, Norway             | 52,436     | 17.4%      | 0.6%
3    | Ajaccio, France            | 54,364     | 18.0%      | 0.6%
4    | Reykjavík, Iceland         | 118,918    | 62.9%      | 2.2%
5    | Calais, France             | 74,433     | 28.5%      | 1.0%
6    | Pisa, Italy                | 77,007     | 30.1%      | 1.1%
7    | Bern, Switzerland          | 121,631    | 60.5%      | 2.3%
8    | Dunkerque, France          | 71,287     | 22.3%      | 1.0%
9    | Cannes, France             | 70,011     | 21.4%      | 0.9%
10   | Ródos, Greece              | 56,128     | 13.9%      | 0.6%

<p class="caption"><span class="caption-label">Table 6</span>: Surprisingly well-known cities with 50,000 or more inhabitants</p>

Three capitals (Luxembourg, Reykjavik, and Bern) make the list, as do several places of historical significance (Calais, Dunkerque [Dunkirk], and Ródos [Rhodes]) and tourist destinations (Pisa and Cannes). Tromsø is known for being one of the northernmost cities in the world.

From surprisingly well-known cities we now turn to the "surprisingly obscure" cities—those with the lowest ratio of actual to expected popularity—in Table&nbsp;7. To limit the list to cities that were expected to have some degree of popularity, cities with an expected popularity of less than 10% have been included.

rank | city                        | population | popularity | expected popularity
---- | --------------------------- | ---------- | ---------- | -------------------
1    | Volzhskiy, Russia           | 323,293    | 0.3%       | 10.7%
2    | Makiyivka, Ukraine          | 376,610    | 0.6%       | 12.8%
3    | Naberezhnyye Chelny, Russia | 509,870    | 1.2%       | 18.3%
4    | Khmelnytskyi, Ukraine       | 398,346    | 1.2%       | 13.7%
5    | Cheboksary, Russia          | 446,781    | 1.6%       | 15.7%
6    | Izhevsk, Russia             | 631,038    | 2.9%       | 23.5%
7    | Cherepovets, Russia         | 315,738    | 1.4%       | 10.4%
8    | Lipetsk, Russia             | 515,655    | 2.7%       | 18.5%
9    | Ulyanovsk, Russia           | 640,680    | 3.5%       | 23.9%
10   | Kryvyi Rih, Ukraine         | 652,380    | 3.6%       | 24.4%

<p class="caption"><span class="caption-label">Table 7</span>: Surprisingly obscure cities with at least 10% expected popularity</p>

Volzhskiy, a large suburb of Volgograd, Russia, tops the list, and every other city in the top ten is also either in Russia or Ukraine. Some bias towards cities whose names are hard to spell is evident, Naberezhnyye Chelny and Khmelnytskyi being particularly difficult in this respect. Ulyanovsk is a surprise inclusion on the list in light of its historical significance as the birthplace of Vladimir Lenin, for whom it was named (Ulyanov being his family name).

Table&nbsp;8 has the most forgotten national capitals, and Table&nbsp;9 has the most forgotten countries, by the percentage of players who named at least one city in that country.

rank | city                       | percentage
---- | -------------------------- | ----------
1    | Valletta, Malta            | 21.5%
2    | Podgorica, Montenegro      | 28.6%
3    | Vaduz, Liechtenstein       | 29.2%
4    | Pristina, Kosovo           | 29.4%
5    | Nicosia, Cyprus            | 32.6%
6    | Chisinau, Moldova          | 33.6%
7    | Skopje, North Macedonia    | 40.1%
8    | Ljubljana, Slovenia        | 40.2%
9    | San Marino, San Marino     | 41.1%
10   | Vatican City, Vatican City | 43.8%

<p class="caption"><span class="caption-label">Table 8</span>: Most forgotten capitals</p>

rank | country         | percentage
---- | --------------- | ----------
1    | Malta           | 22.8%
2    | Liechtenstein   | 29.3%
3    | Montenegro      | 31.0%
4    | Moldova         | 34.7%
5    | Cyprus          | 35.9%
6    | Kosovo          | 38.0%
7    | North Macedonia | 40.9%
8    | San Marino      | 41.3%
9    | Vatican City    | 43.8%
10   | Albania         | 45.6%

<p class="caption"><span class="caption-label">Table 9</span>: Most forgotten countries</p>

The two lists correspond closely: all but Albania and Slovenia appear on both. There are eleven nations between the two lists: four microstates (Liechtenstein, Malta, San Marino, Vatican City) and seven smaller nations in Eastern and Southeastern Europe (Albania, Cyprus, Kosovo, Moldova, Montenegro, North Macedonia, Slovenia). The scores for Malta and Liechtenstein are lower than for other microstates, presumably because, unlike Andorra, Monaco, San Marino, and Vatican City, they do not share a name with their capital city, so even players who remembered that they exist may not have been able to name a city in them.

## What country is the best at geography?
Using [IP geolocation](https://en.wikipedia.org/wiki/Internet_geolocation), about half of the total plays of the quiz could be traced to a specific country, and from this data the best countries at European geography can be ranked. Table&nbsp;10 presents the list. The Balkans are overrepresented, with Serbia taking first place, Croatia tying for fifth and Bosnia and Herzegovina tying for seventh. Spain, France, Hungary, Poland, Italy, Russia and Czechia also make the top ten.

rank | country                | median score | total plays
---- | ---------------------- | ------------ | -----------
1    | Serbia                 | 140          | 359
2    | Spain                  | 134          | 1,141
3    | France                 | 124          | 2,053
4    | Hungary                | 122          | 535
5    | Poland                 | 120          | 1,882
5    | Croatia                | 120          | 445
7    | Italy                  | 117          | 1,200
7    | Bosnia and Herzegovina | 117          | 104
9    | Russia                 | 116          | 315
10   | Czechia                | 112          | 528

<p class="caption"><span class="caption-label">Table 10</span>: Best countries by number of cities named</p>

Outside of the top ten, Germany comes in at 15th place with a median score of 107 over 4,377 plays, the Netherlands are in 16th with a median score of 106 over 2,547 plays, Sweden is 17th with a median score of 103 over 1,369 plays, the United Kingdom is 19th with a median score of 100 over 3,802 plays.

Table&nbsp;11 shows the ten worst countries, again excluding countries with fewer than 100 plays.

rank | country         | median score | total plays
---- | --------------- | ------------ | -----------
1    | New Zealand     | 62           | 141
1    | India           | 62           | 112
3    | United States   | 70           | 6,751
4    | Mexico          | 75           | 239
4    | North Macedonia | 75           | 1,181
6    | Hong Kong       | 76           | 145
7    | Canada          | 79           | 1,222
8    | Denmark         | 81           | 514
9    | Greece          | 84           | 241
9    | Ireland         | 84           | 454

<p class="caption"><span class="caption-label">Table 11</span>: Worst countries by number of cities named</p>

The United States avoids the bottom of the list thanks to New Zealand and India, although both of those nations have far fewer plays. North Macedonia is in last place among European nations. I speculate that the quiz was posted to some North Macedonian forum or website, attracting a large number of casual players and thus accounting for both the unusually high number of plays for North Macedonia and the low median score.

Of all the European countries with at least 100 plays of the quiz, players from every country but one do best at their own country.[^not-turkey] The one exception is Ireland, whose players name slightly more cities in the United Kingdom on average than in Ireland. The UK makes a strong showing among the former colonies of the British Empire: it is the top country for players from Australia, Canada, Hong Kong, India, New Zealand, and the United States. Among other non-European nationalities, players from Mexico do best at Spain, those from Brazil do best at Italy, and those from Turkey do best at Germany.


[^sessions-with-times]: Due to changes to the database schema, at various points in time the quiz did not record both the start and end times, so the duration of play is only known for 61,054 plays (57.7%).

[^not-turkey]: Excluding Turkey, since only a handful of Turkish cities are in the European cities quiz.
