## (monadic) Precinct Matcher
Matching election data to shapefiles is hard.
It is usually context-dependent and implemented on a case-by-case basis.
This attempts to make life easier

## Install

``` bash
pip install pmatcher
```

## Implemented Methods

#### matcher.default()
Applies exact, insensitive, stripped, and weighted_manual in that order.
All batteries included

#### matcher.exact()
Matches exact strings

#### matcher.insensitive()
Matches strings (case-insensitive )

#### matcher.stripped()
Matches strings with special characters removed (e.g.`()`, `#`, `-`)

#### matcher.weighted_manual()
Uses a weighted levenshtein algorithm.
First looks for token-distance, followed by token word distance for tiebreaking.

## Example usage

``` python
matcher = PrecinctMatcher(list_1, list_2)
matcher.default()
```

``` python
matcher = PrecinctMatcher(list_1, list_2)
matcher.exact()
matcher.insensitive()
matcher.insensitive_stripped()
matcher.weighted_manual()
```

