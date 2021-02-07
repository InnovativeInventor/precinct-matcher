from fuzzywuzzy import fuzz, process
from typing import List


class PrecinctMatcher:
    def __init__(self, primary: List[str], secondary: List[str]):
        # Define and strip whitespace
        self.primary = list(sorted(map(lambda x: x.rstrip(), primary)))
        self.secondary = list(sorted(map(lambda x: x.rstrip(), secondary)))
        self.results: Dict[str, str] = {}

        # TODO: check if there is no dupilcates

    def default(self):
        """
        Default matching, with all the batteries included.
        """
        self.exact()
        self.insensitive_stripped()
        self.stripped()

        if self.primary:
            return self.weighted_manual()
        else:
            return self.results

    def exact(self):
        """
        Checks for exact matches
        """
        for primary_string in self.primary:
            if primary_string in self.secondary:
                self.results[primary_string] = primary_string

                self.primary.remove(primary_string)
                self.secondary.remove(primary_string)

        return self.results

    def normalize_match(self, func):
        """
        Matches given a particular normalization function
        """
        normalized_primary = list(map(func, self.primary))
        normalized_secondary = list(map(func, self.secondary))

        for primary_string in normalized_primary:
            # try:
            # Might use assignment operators
            if primary_string in normalized_secondary:
                secondary_loc = normalized_secondary.index(primary_string)
                primary_loc = normalized_primary.index(primary_string)

                self.results[self.primary[primary_loc]] = self.secondary[secondary_loc]

                del self.primary[primary_loc]
                del normalized_primary[primary_loc]
                del self.secondary[secondary_loc]
                del normalized_secondary[secondary_loc]

            # except ValueError:
            #     continue

        return self.results

    def insensitive(self):
        """
        Checks for exact, but case-insensitive matches
        """
        return self.normalize_match(lambda x: x.lower())

    def stripped(self):
        """
        Strip characters when precinct matching. See _stripper for more.
        """
        return self.normalize_match(lambda x: self._stripper(x.lower()).upper())

    def insensitive_stripped(self):
        """
        Strip characters with insensitive matching. See insensitive() and _stripper for more.
        """
        return self.normalize_match(lambda x: self._stripper(x.lower()))

    def _stripper(self, string: str) -> str:
        """
        Removes some special characters, leading zeros in numbers, and other bad stuff
        """

        bad_tokens = ["voting district", "-", "#", "(", ")", ","]
        for each_bad_token in bad_tokens:
            string = string.replace(each_bad_token, "")

        common_replacements = {"pct": "precinct"}

        tokens = string.split()
        for count, each_token in enumerate(tokens):
            try:
                tokens[count] = str(int(each_token))
            except ValueError:
                pass

        return " ".join(tokens)

    def weighted_manual(self, n=5):
        """
        Interactive, weighted matching with levenshtein distances!
        """
        matcher = lambda x, y: 100 * fuzz.token_set_ratio(x, y) + fuzz.ratio(x, y)
        normalize = lambda x: self._stripper(x.lower()).title()

        normalized_primary = list(map(normalize, self.primary))
        normalized_secondary = list(map(normalize, self.secondary))

        for each_string in normalized_primary:
            print(f"Matching {each_string}:")
            matches = sorted(
                process.extract(
                    each_string, normalized_secondary, limit=n, scorer=matcher
                ),
                key=lambda x: x[1],
            )
            for count, each_match in enumerate(matches):
                if count == 0:
                    print(f">>>{count}. {each_match[0]} (score: {each_match[1]})")
                else:
                    print(f"   {count}. {each_match[0]} (score: {each_match[1]})")

            print("Please select (enter=default): ")
            response = input()

            if response == "":
                match = 0
            else:
                try:
                    match = int(response)
                except:
                    continue

            primary_loc = normalized_secondary.index(each_string)
            secondary_loc = normalized_secondary.index(matches[match])

            self.results[self.primary[primary_loc]] = self.secondary[secondary_loc]

            del self.primary[primary_loc]
            del normalized_primary[primary_loc]
            del self.secondary[primary_loc]
            del normalized_secondary[primary_loc]

        return self.results

    def spot_check(self):
        pass

    def remaining(self):
        """
        Returns the number of remaining strings in the primary set to match
        """
        return len(self.primary)
