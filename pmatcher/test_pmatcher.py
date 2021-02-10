from pmatcher import PrecinctMatcher

test_primary = [
    "ABINGTON WARD 04 DISTRICT 02   ",
    "Archbald Ward 01 District 01",
    "BALD EAGLE Voting District",
    "Blakely Ward 01 district 01",
    "PHILADELPHIA WARD 31 PRECINCT 09",
]

test_secondary = [
    "abington ward 4 district 2",  # combo
    "Archbald Ward 01 District 01",  # exact
    "BALD EAGLE",  # stripping
    "Blakely Ward 01 District 01",  # casing/insensitive
    "PHILADELPHIA WARD 31 PRECINCT 9",  # int conversion/stripping
]


def test_init():
    matcher = PrecinctMatcher(test_primary, test_secondary)

    assert matcher.exact()
    assert matcher.results
    prev_len = len(matcher.results)

    assert matcher.insensitive()
    assert prev_len < len(matcher.results)
    prev_len = len(matcher.results)

    assert matcher.insensitive_normalized()
    assert prev_len < len(matcher.results)

    assert not matcher.primary
    assert not matcher.secondary

def test_write():
    matcher = PrecinctMatcher(test_primary, test_secondary)

    assert matcher.exact()
    assert matcher.results
    assert matcher.insensitive()
    assert matcher.insensitive_normalized()
    assert matcher.results
    assert not matcher.primary
    assert not matcher.secondary

    matcher.save_progress("progress.json")
    matcher = PrecinctMatcher([], [])
    matcher.load_progress("progress.json")
    assert matcher.results
    assert not matcher.primary
    assert not matcher.secondary
