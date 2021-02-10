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
Insensitive normalized match 0.9932636469221835
Aggressive insensitive normalized match 0.9983739837398374
```

## Implemented Methods
- `matcher.default()`
Applies exact, insensitive, normalized, and weighted_manual in that order.
All batteries included!

- `matcher.exact()`
Matches exact strings.

- `matcher.insensitive()`
Matches strings (case-insensitive).

- `matcher.insensitive_normalized()`
Matches strings with special characters removed (e.g.`()`, `#`, `-`).

- `matcher.weighted_manual()`
Uses a weighted levenshtein algorithm.
First looks for token-distance, followed by token word distance for tiebreaking.

### Saving and loading progress
- `matcher.save_progress("progress.json")`
Saves progress/mapping to a json file.

- `matcher.load_progress("progress.json")`
Loads progress/mapping from a json file.

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
matcher.insensitive_normalized()
matcher.insensitive_normalized(aggressive=True)
mapping = matcher.weighted_manual()
```

