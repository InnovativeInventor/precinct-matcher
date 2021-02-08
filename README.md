## (monadic) Precinct Matcher
Matching election data to shapefiles is hard.
It is usually context-dependent and implemented on a project-by-project basis.
It also sometimes involves some manual labor.
This attempts to make life easier for everyone who has to deal with precinct matching.

## Install

``` bash
pip install pmatcher
```
## Benchmarks (on real data)
VEST releases its precincts with VTD codes and county FIPS codes.
To validate this approach, I ran the matcher on known, good data.

Results (in % accuracy):
``` 
Exact match 0.9444831591173054
Insensitive match 0.9444831591173054
Insensitive stripped match 0.9932636469221835
Aggressive insensitive stripped match 0.9983739837398374
```

## Implemented Methods
- `matcher.default()`
Applies exact, insensitive, stripped, and weighted_manual in that order.
All batteries included!

- `matcher.exact()`
Matches exact strings.

- `matcher.insensitive()`
Matches strings (case-insensitive).

- `matcher.insensitive_stripped()`
Matches strings with special characters removed (e.g.`()`, `#`, `-`).

- `matcher.weighted_manual()`
Uses a weighted levenshtein algorithm.
First looks for token-distance, followed by token word distance for tiebreaking.

## Example usage

``` python
from pmatcher import PrecinctMatcher
matcher = PrecinctMatcher(list_1, list_2)
mapping = matcher.default()
```

``` python
from pmatcher import PrecinctMatcher
matcher = PrecinctMatcher(list_1, list_2)
matcher.exact()
matcher.insensitive()
matcher.insensitive_stripped()
mapping = matcher.weighted_manual()
```

