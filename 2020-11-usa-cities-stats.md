# What's the best-known city in America? ...and other stats from my cities game
I run [a geography quiz game](https://iafisher.com/projects/cities/usa) that challenges you to name as many cities[^cities] in the United States as you can. In this post, co-written with [Sasha Trubetskoy](https://sashamaps.net), we've analyzed 49,468 plays of the quiz to answer questions like "How many cities can the average person name", "What are the best-known cities in America", and more.

The median player named **104 cities**, while the top 10% of players named **at least 377 cities**. The city named by the most players was **New York City**, followed by Los Angeles. For its size, **Montpelier, Vermont** was the most surprisingly well-known city, while **Sunrise Manor, Nevada**, a suburb of Las Vegas, was the most surprisingly obscure. **Concord, New Hampshire** was the most forgotten state capital, and **West Virginia** was the most forgotten state.


## Methodology
The analysis was based on a dataset of 49,468 plays of my U.S. cities quiz. The dataset comprised every play of the quiz from the quiz's publication in October 2019 through October 31, 2020, excluding plays with fewer than 10 cities. Unsaved plays were not included in the analysis as they are stored locally on each player's computer and I do not have access to them.


## How many U.S. cities can the average person name?
The median player named **104 cities**. 75% of players named at least **47 cities**, and 25% of players named **207 cities** or more. Table&nbsp;1 shows every tenth percentile.

percentile  | score
----------- | -----
90          | 377
80          | 244
70          | 179
60          | 136
50 (median) | 104
40          | 78
30          | 56
20          | 38
10          | 23

<p class="caption"><span class="caption-label">Table 1</span>: Scores by percentile, 10th to 90th</p>

You should take these numbers with a grain of salt, because some players undoubtedly "cheated" and because not everyone was genuinely trying to name as many cities as they could. Also note that sessions with fewer than 10 cities named have been excluded from this analysis.

For real competitors, Table&nbsp;2 has every percentile above the 90th.

percentile  | score
----------- | -----
99          | 1,190
98          | 896
97          | 714
96          | 618
95          | 548
94          | 501
93          | 463
92          | 430
91          | 401

<p class="caption"><span class="caption-label">Table 2</span>: Scores by percentile, 91st to 99th</p>

I've seen some plays with more than 20,000 cities named, which defy credulity, so the very highest percentiles are likely inflated a little, but I don't doubt that some people really can name more than 1,000 cities from memory.


## What are the best-known cities?
Table&nbsp;3 lists the twenty best-known cities in the United States, by the percentage of players that named them.

rank | city              | percentage
---- | ----------------- | ----------
1    | New York, NY      | 90.8%
2    | Los Angeles, CA   | 88.3%
3    | Chicago, IL       | 84.1%
4    | Miami, FL         | 82.8%
5    | Las Vegas, NV     | 82.4%
6    | San Francisco, CA | 82.2%
7    | Seattle, WA       | 81.8%
8    | Dallas, TX        | 80.3%
9    | Houston, TX       | 79.9%
10   | Boston, MA        | 79.1%
11   | Portland, OR      | 75.3%
12   | Atlanta, GA       | 74.8%
13   | Denver, CO        | 74.4%
14   | San Diego, CA     | 74.3%
15   | Detroit, MI       | 74.2%
16   | New Orleans, LA   | 73.8%
17   | Phoenix, AZ       | 72.6%
18   | Washington, DC    | 72.4%
19   | Philadelphia, PA  | 72.0%
20   | Austin, TX        | 71.4%

<p class="caption"><span class="caption-label">Table 3</span>: Best-known cities</p>

Little surprise that New York City, Los Angeles and Chicago top the list. Sixteen of these twenty are also among the twenty most populous metropolitan areas in the United States,[^census] while Portland (25th), Las Vegas (28th), Austin (29th) and New Orleans (45th) fall outside. The four top-twenty metro areas that don't make the best-known list are the Inland Empire (13th), Minneapolis (16th), Tampa (18th), and St. Louis (20th).[^metro]

The best-known cities with at least 15 letters in their name are shown in Table&nbsp;4.

rank | city                      | percentage
---- | ------------------------- | ----------
1    | Colorado Springs, CO      | 36.1%
2    | Charlottesville, VA       | 20.4%
3    | Huntington Beach, CA      | 9.6%
4    | Truth or Consequences, NM | 6.4%
5    | Saratoga Springs, NY      | 4.9%
6    | Rancho Cucamonga, CA      | 4.9%
7    | International Falls, MN   | 4.5%
8    | South San Francisco, CA   | 4.1%
9    | Steamboat Springs, CO     | 3.5%
10   | Panama City Beach, FL     | 3.3%

<p class="caption"><span class="caption-label">Table 4</span>: Best-known cities with at least 15 letters</p>

Table&nbsp;5 has the best-known city for each letter of the alphabet.

letter | city               | percentage
------ | ------------------ | ----------
**A**  | Atlanta, GA        | 74.8%
**B**  | Boston, MA         | 79.1%
**C**  | Chicago, IL        | 84.1%
**D**  | Dallas, TX         | 80.3%
**E**  | El Paso, TX        | 54.0%
**F**  | Fort Worth, TX     | 48.2%
**G**  | Green Bay, WI      | 37.6%
**H**  | Houston, TX        | 79.9%
**I**  | Indianapolis, IN   | 61.8%
**J**  | Jacksonville, FL   | 56.5%
**K**  | Kansas City, MO    | 66.5%
**L**  | Los Angeles, CA    | 88.3%
**M**  | Miami, FL          | 82.8%
**N**  | New York, NY       | 90.8%
**O**  | Orlando, FL        | 64.6%
**P**  | Portland, OR       | 75.3%
**Q**  | Quincy, MA         | 7.2%
**R**  | Reno, NV           | 50.7%
**S**  | San Francisco, CA  | 82.2%
**T**  | Topeka, KS         | 65.5%
**U**  | Utica, NY          | 14.3%
**V**  | Virginia Beach, VA | 26.1%
**W**  | Washington, DC     | 72.4%
**X**  | Xenia, OH          | 1.9%
**Y**  | York, PA           | 16.7%
**Z**  | Zion, IL           | 3.4%

<p class="caption"><span class="caption-label">Table 5</span>: Best-known cities by letters of the alphabet</p>


## What cities are surprisingly well-known?
Perhaps more interesting than the best-known cities is the list of cities that are surprisingly well-known relative to their population. Using the quiz results, my friend [Sasha Trubetskoy](https://sashamaps.net) devised a piecewise linear regression that estimates the number of times a city is expected to be named, based on its population. By computing the ratio between a city's actual and expected popularity using this function, we can see how surprising the city's popularity is.

Table&nbsp;6 ranks the twenty most surprisingly well-known cities by this metric.

rank | city                      | population | popularity | expected popularity
---- | ------------------------- | ---------- | ---------- | -------------------
1    | Montpelier, VT            | 7,855      | 27.0%      | 0.2%
2    | London, OH                | 9,904      | 22.2%      | 0.3%
3    | Aspen, CO                 | 6,658      | 14.9%      | 0.2%
4    | Pierre, SD                | 13,646     | 26.5%      | 0.4%
5    | Juneau, AK                | 31,275     | 43.6%      | 0.7%
6    | Berlin, NH                | 10,051     | 16.1%      | 0.3%
7    | Brooklyn, OH              | 11,169     | 17.0%      | 0.3%
8    | Gettysburg, PA            | 7,620      | 11.6%      | 0.2%
9    | Palm Beach, FL            | 8,348      | 12.3%      | 0.2%
10   | Helena, MT                | 28,190     | 34.7%      | 0.7%
11   | Moab, UT                  | 5,046      | 7.4%       | 0.1%
12   | Adams, MA                 | 5,515      | 7.2%       | 0.2%
13   | Malibu, CA                | 12,645     | 14.9%      | 0.3%
14   | Paris, TX                 | 25,171     | 26.2%      | 0.6%
15   | Augusta, ME               | 19,136     | 20.5%      | 0.5%
16   | Toronto, OH               | 5,091      | 6.4%       | 0.1%
17   | Key West, FL              | 24,649     | 24.4%      | 0.6%
18   | Taos, NM                  | 5,716      | 6.3%       | 0.2%
19   | Dover, DE                 | 36,047     | 34.8%      | 0.9%
20   | Truth or Consequences, NM | 6,475      | 6.4%       | 0.2%

<p class="caption"><span class="caption-label">Table 6</span>: Surprisingly well-known cities</p>

The list includes some cities that are legitimately well known, including state capitals (Montpelier, Pierre, Juneau, Helena, Augusta, Dover) and others (Aspen, Gettysburg, Palm Beach, Moab, Malibu, Key West, Taos, Truth or Consequences), as well as some cities sharing a name with a much larger counterpart that were likely guessed randomly or by mistake (London, Berlin, Brooklyn, Paris, Toronto). I assume that people got "Adams, MA" just by guessing that Adams would be the name of some city in the U.S.

All the surprisingly popular cities in the table above are quite small. If we limit it to cities with at least 50,000 people, we get Table&nbsp;7.

rank | city              | population | popularity | expected popularity
---- | ----------------- | ---------- | ---------- | -------------------
1    | Cheyenne, WY      | 59,466     | 39.0%      | 2.1%
2    | Carson City, NV   | 55,274     | 32.2%      | 1.9%
3    | Santa Fe, NM      | 67,947     | 43.1%      | 2.7%
4    | Bismarck, ND      | 61,272     | 34.9%      | 2.2%
5    | Charleston, WV    | 51,400     | 22.8%      | 1.7%
6    | Portland, ME      | 66,194     | 34.1%      | 2.6%
7    | Albany, NY        | 97,856     | 55.0%      | 4.9%
8    | Pensacola, FL     | 51,923     | 18.0%      | 1.7%
9    | Manhattan, KS     | 52,281     | 16.6%      | 1.7%
10   | Flagstaff, AZ     | 65,870     | 23.4%      | 2.5%
11   | Topeka, KS        | 127,473    | 65.5%      | 7.6%
12   | Iowa City, IA     | 67,862     | 22.3%      | 2.7%
13   | Casper, WY        | 55,316     | 15.2%      | 1.9%
14   | Trenton, NJ       | 84,913     | 30.8%      | 3.9%
15   | Scranton, PA      | 76,089     | 25.0%      | 3.2%
16   | Gary, IN          | 80,294     | 26.2%      | 3.5%
17   | Niagara Falls, NY | 50,193     | 11.5%      | 1.6%
18   | Santa Cruz, CA    | 59,946     | 15.2%      | 2.2%
19   | Green Bay, WI     | 104,057    | 37.6%      | 5.5%
20   | Daytona Beach, FL | 61,005     | 15.3%      | 2.2%

<p class="caption"><span class="caption-label">Table 7</span>: Surprisingly well-known cities with 50,000 or more inhabitants</p>

Again, we have many state capitals, but only one city with a famous name this time (Manhattan). Other cities are famous for various reasons: for example, Green Bay is home to [a professional football team](https://en.wikipedia.org/wiki/Green_Bay_Packers), and Scranton was the setting of [a popular American sitcom](https://en.wikipedia.org/wiki/The_Office_(American_TV_series)) (not to mention the birthplace of Joe Biden).


## What cities are surprisingly obscure?
On the flip side of the coin, Table&nbsp;8 has the twenty most surprisingly obscure cities.[^townships]

rank | city                 | population | popularity | expected popularity
---- | -------------------- | ---------- | ---------- | -------------------
1    | Sunrise Manor, NV    | 189,372    | 0.6%       | 14.7%
2    | Alafaya, FL          | 78,113     | 0.2%       | 3.4%
3    | South Whittier, CA   | 57,156     | 0.1%       | 2.0%
4    | Town 'n' Country, FL | 78,442     | 0.2%       | 3.4%
5    | Kendale Lakes, FL    | 56,148     | 0.1%       | 1.9%
6    | Arden-Arcade, CA     | 92,186     | 0.3%       | 4.5%
7    | Casas Adobes, AZ     | 66,795     | 0.2%       | 2.6%
8    | Florin, CA           | 47,513     | 0.1%       | 1.5%
9    | Country Club, FL     | 47,105     | 0.1%       | 1.4%
10   | Aspen Hill, MD       | 48,759     | 0.1%       | 1.5%
11   | Poinciana, FL        | 53,193     | 0.2%       | 1.8%
12   | North Highlands, CA  | 42,694     | 0.1%       | 1.2%
13   | San Tan Valley, AZ   | 81,321     | 0.3%       | 3.6%
14   | Pine Hills, FL       | 60,076     | 0.2%       | 2.2%
15   | Spring Valley, NV    | 178,395    | 1.3%       | 13.3%
16   | Lehigh Acres, FL     | 86,784     | 0.4%       | 4.0%
17   | Atascocita, TX       | 65,844     | 0.3%       | 2.5%
18   | Mission Bend, TX     | 36,501     | 0.1%       | 0.9%
19   | Tamiami, FL          | 55,271     | 0.2%       | 1.9%
20   | Lake Ridge, VA       | 41,058     | 0.1%       | 1.1%

<p class="caption"><span class="caption-label">Table 8</span>: Surprisingly obscure cities</p>

Every city here is a [census-designated place](https://en.wikipedia.org/wiki/Census-designated_place), a category created by the Census Bureau for localities that are not legally incorporated, which tend to be lesser-known than incorporated municipalities. Furthermore, all of them are suburbs in the [Sun Belt](https://en.wikipedia.org/wiki/Sun_Belt), with a propensity towards smaller metro areas (Sacramento, Orlando). The Sun Belt is the fastest-growing region in the United States, and many of these cities were evidently founded too recently to have left much of an imprint on the popular imagination.

Since most of the cities in Table&nbsp;8 are fairly small, Table&nbsp;9 lists the most surprisingly obscure cities with at least 200,000 inhabitants.

rank | city                | population | popularity | expected popularity
---- | ------------------- | ---------- | ---------- | -------------------
1    | Garland, TX         | 226,876    | 5.4%       | 19.8%
2    | Hialeah, FL         | 224,669    | 6.1%       | 19.5%
3    | Chula Vista, CA     | 243,916    | 7.5%       | 22.3%
4    | Gilbert, AZ         | 208,453    | 5.9%       | 17.2%
5    | Chandler, AZ        | 236,123    | 7.5%       | 21.1%
6    | Santa Ana, CA       | 324,528    | 13.3%      | 34.9%
7    | Irving, TX          | 216,290    | 7.4%       | 18.3%
8    | North Las Vegas, NV | 216,961    | 7.6%       | 18.4%
9    | Chesapeake, VA      | 222,209    | 8.7%       | 19.1%
10   | Mesa, AZ            | 439,041    | 20.3%      | 43.3%

<p class="caption"><span class="caption-label">Table 9</span>: Surprisingly obscure cities with 200,000 or more inhabitants</p>

Once again, they are all suburbs and satellite cities in the Sun Belt.

The ten most forgotten state capitals are shown in Table&nbsp;10.

rank | city               | percentage
---- | ------------------ | ----------
1    | Concord, NH        | 13.5%
2    | Jefferson City, MO | 15.3%
3    | Augusta, ME        | 16.0%
4    | Frankfort, KY      | 16.2%
5    | Charleston, WV     | 17.7%
6    | Springfield, IL    | 20.3%
7    | Pierre, SD         | 20.6%
8    | Annapolis, MD      | 20.8%
9    | Montpelier, VT     | 21.0%
10   | Harrisburg, PA     | 21.5%

<p class="caption"><span class="caption-label">Table 10</span>: Most forgotten state capitals</p>

They are all either the capitals of small states (Concord, Augusta, Charleston, Pierre, Montpelier), the capitals of states with much larger cities (Jefferson City, Springfield, Annapolis, Harrisburg), or both (Frankfort).

Table&nbsp;11 has the most forgotten states, by percentage of players who named at least one city in the state:

rank | state         | percentage
---- | ------------- | ----------
1    | West Virginia | 38.4%
2    | Vermont       | 39.9%
3    | Delaware      | 43.0%
4    | New Hampshire | 44.5%
5    | Wyoming       | 47.4%
6    | South Dakota  | 49.9%
7    | Maine         | 50.2%
8    | Rhode Island  | 50.6%
9    | Connecticut   | 53.0%
10   | Montana       | 53.9%

<p class="caption"><span class="caption-label">Table 11</span>: Most forgotten states</p>

West Virginia, the most forgotten state, likely suffers from the fact that its capital and largest city, Charleston, is also the name of a larger city in South Carolina. Connecticut is the most populous state on the list, with 3.5 million people. Alaska and North Dakota are the least populous states *not* on the list, probably because Anchorage and Fargo are fairly well-known.


## Miscellaneous stats
Finally, a few miscellaneous stats:

- Every city in the database has been guessed at least once, but 12 cities have *only* been guessed once.
- 21.1% of players named all 50 states; of those, 93.5% remembered the District of Columbia as well.
- 77.6% named New York City. But of the 22.4% that didn't, 6.0% nonetheless managed to name at least 500 cities.


[^cities]: Here and throughout I use "cities" as a shorthand to refer to populated places of any size.

[^census]: Per [2019 Census Bureau estimates](https://www.census.gov/data/tables/time-series/demo/popest/2010s-total-metro-and-micro-statistical-areas.html) for metropolitan statistical areas.

[^metro]: I'm playing a bit fast and loose with the terminology here. Technically, metropolitan areas are defined by multiple cities that form the urban core, e.g. New York, Newark and Jersey City for the New York metro area. As it happened, no two cities in the top twenty were in the same metro area. Although the quiz itself uses city-proper populations as reported by the 2010 census, the 2019 metro area populations are more appropriate for comparison as they give a better idea of what cities we would expect to be the best-known.

[^townships]: A number of townships in New Jersey and Pennsylvania were added to the database of cities a while after the quiz was initially published; these have been excluded from the table because their popularities are artificially low.
