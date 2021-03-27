from fuzzywuzzy import fuzz, process
from typing import List
import json
import difflib
import string


BAD_TOKENS = ["voting district", "-", "#", "(", ")", ",", "twp", "township", "/", "'"]
# COMMON_REPLACEMENTS = {"pct": "precinct", "division": "district", "wd": "ward"}
COMMON_REPLACEMENTS = {"pct": "precinct",
                       "division": "district",
                       "wd": "ward",
                       "dist": "district",
                       "d": "district",
                       "boro": "borough",
                       "twp": "township",
                       "tp": "township",
                       "first": "1",
                       "second": "2",
                       "third": "3",
                       "fourth": "4",
                       "fifth": "5",
                       "sixth": "6",
                       "seventh": "7",
                       "eighth": "8",
                       "ninth": "9",
                       "1st": "1",
                       "2nd": "2",
                       "3rd": "3",
                       "4th": "4",
                       "5th": "5",
                       "6th": "6",
                       "7th": "7",
                       "8th": "8",
                       "9th": "9",
                       "10th": "10",
                       "one": "1",
                       "two": "2",
                       "three": "3",
                       "four": "4",
                       "five": "5",
                       "six": "6",
                       "seven": "7",
                       "eight": "8",
                       "nine": "9",
                       "ten": "10",
                       "n":"north",
                       "e":"east",
                       "s":"south",
                       "w":"west",
                       "i": "1",
                       "ii": "2",
                       "iii": "3",
                       "no": "number",
                       "st": "street",
                       "ht": "heights",
                       "hl": "hills",
                       "pk": "park",
                       "mt": "mountain",
                       "mount": "mountain",
                       "ind": "independent"
                       }

ACCEPTABLE_DIFFERENCES = set(["district", "ward", "precinct", "borough", "number"])
# TODO: Check with ppl about "twp" and if it is ok to map ward to precinct
AGGRESSIVE_REPLACEMENTS = {"wd": "precinct",
                           "ward": "precinct"
                           } # never used

class PrecinctMatcher:
    def __init__(self, primary: List[str], secondary: List[str]):
        # Drop unprintable characters and whitespace
        printable = set(string.printable)
        regularize = lambda x: "".join(filter(lambda y: y in printable, x.rstrip()))

        # self.primary = list(sorted(map(lambda x: x.rstrip(), primary)))
        # self.secondary = list(sorted(map(lambda x: x.rstrip(), secondary)))
        self.primary = list(sorted(map(regularize, set(primary))))
        self.secondary = list(sorted(map(regularize, set(secondary))))
        self.results: Dict[str, str] = {}


    def default(self):
        """
        Default matching, with all the batteries included.
        """
        self.exact()
        self.insensitive_normalized()
        self.insensitive_normalized(aggressive=True)
        if self.primary:
            return self.weighted_manual()
        else:
            return self.results

    def normalize_match(self, func, acceptable=set(), cd=False):
        """
        Matches given a particular normalization function
        """
        prev_size = 0
        size = len(self.primary)

        while size != prev_size:
            normalized_primary = list(map(func, self.primary))
            normalized_secondary = list(map(func, self.secondary))

            for primary_string in normalized_primary:
                # try:
                # Might use assignment operators
                # if primary_string in normalized_secondary:
                for secondary_string in normalized_secondary:
                    if primary_string == secondary_string or self.check_difference(acceptable, primary_string, secondary_string, cd=cd):
                        primary_loc = normalized_primary.index(primary_string)
                        secondary_loc = normalized_secondary.index(secondary_string)

                        self.results[self.primary[primary_loc]] = self.secondary[secondary_loc]

                        del self.primary[primary_loc]
                        del normalized_primary[primary_loc]
                        del self.secondary[secondary_loc]
                        del normalized_secondary[secondary_loc]

            prev_size = size
            size = len(self.primary)

        return self.results

    def check_difference(self, acceptable, primary, secondary, cd=False):
        """
        Checks if the primary and secondary strings differs by more than the acceptable strings/variations.
        If it does, return False. Else, return True.
        If cd=True, congressional districts suffixes are considered acceptable variations.
        """
        if not acceptable: # shortcut
            return False

        elif diff := set(primary.lower().split()).symmetric_difference(set(secondary.lower().split())):
            # print(diff, primary, secondary)
            if diff.issubset(acceptable):
                return True
            elif cd:
                rejected = diff - acceptable

                if len(rejected) == 2 and "cd" in rejected and any([x.isnumeric() for x in rejected]):
                    return True
            else:
                return False

        return False


    def exact(self):
        """
        Checks for exact matches
        """
        return self.normalize_match(lambda x: x)

    def insensitive(self):
        """
        Checks for exact, but case-insensitive matches
        """
        return self.normalize_match(lambda x: x.lower())

    def insensitive_normalized(self, aggressive=False):
        """
        Normalize and strip characters with insensitive matching. See insensitive() and _stripper() for more.
        """
        if aggressive:
            return self.normalize_match(self._normalize, acceptable=ACCEPTABLE_DIFFERENCES, cd=True)
        else:
            return self.normalize_match(self._normalize)

    def _stripper(self, string: str, bad_tokens=BAD_TOKENS, common_replacements=COMMON_REPLACEMENTS) -> str:
        """
        Removes some special characters, leading zeros in numbers, and other bad stuff
        """
        string = string.lower()

        for each_bad_token in bad_tokens:
            string = string.replace(each_bad_token, " ")

        for each_term, each_replacement in common_replacements.items():
            string = self._replace_token(string, each_term, each_replacement)
            string = self._replace_token(string, each_term + ".", each_replacement)

        tokens = string.split()
        for count, each_token in enumerate(tokens):
            try:
                tokens[count] = str(int(each_token))
            except ValueError:
                pass

        return " ".join([token.rstrip() for token in tokens if token.rstrip()])

    def _replace_token(self, string: str, token: str, replacement: str):
        """
        Recusively removes token from string
        """
        if " " in token: # multi-token replacement
            return string.replace(token, replacement)

        tokenized_string = string.lower().split()
        if token in tokenized_string:
            if replacement:
                tokenized_string[tokenized_string.index(token)] = replacement
            else:
                tokenized_string.remove(token)

            return " ".join(tokenized_string)
        else:
            return string

    def _normalize(self, string):
        return self._stripper(string.lower()).title().rstrip()

    def weighted_manual(self, n=5, verbose = False):
        """
        Interactive, weighted matching with levenshtein distances!
        """
        matcher = lambda x, y: 100 * fuzz.token_set_ratio(x, y) + fuzz.ratio(x, y)

        normalized_primary = list(map(self._normalize, self.primary))
        normalized_secondary = list(map(self._normalize, self.secondary))

        for each_string in normalized_primary:
            matches = sorted(
                process.extract(
                    each_string, normalized_secondary, limit=n, scorer=matcher
                ),
                key=lambda x: x[1],
                reverse=True
            )
            for count, (each_match, score) in enumerate(matches):
                if count == 0:
                    if each_string == each_match:
                        response = 0
                        break
                    else:
                        print(f"Matching '{each_string}':")
                        # print(each_string, each_match, each_string==each_match)

                    print(f">>>{count}. '{each_match}' (score: {score})")
                else:
                    print(f"   {count}. '{each_match}' (score: {score})")
            else:
                print("Please select (enter=default, s to skip):", end = " ")
                response = input()

            if response == "":
                match = 0
            else:
                try:
                    match = int(response)
                except:
                    continue

            primary_loc = normalized_primary.index(each_string)
            secondary_loc = normalized_secondary.index(matches[match][0])

            if verbose:
                print(f"Matched '{self.primary[primary_loc]}' with '{self.secondary[secondary_loc]}'.")
            self.results[self.primary[primary_loc]] = self.secondary[secondary_loc]

            del self.primary[primary_loc]
            del normalized_primary[primary_loc]
            del self.secondary[secondary_loc]
            del normalized_secondary[secondary_loc]

        return self.results

    def spot_check(self):
        pass

    def load_progress(self, filename: str):
        with open(filename) as f:
            data = json.load(f)

        self.primary = data["primary"]
        self.secondary = data["secondary"]
        self.results = data["results"]

    def save_progress(self, filename: str):
        data = {}

        data["primary"] = self.primary
        data["secondary"] = self.secondary
        data["results"] = self.results
        with open(filename, "w") as f:
            json.dump(data, f)

    def remaining(self):
        """
        Returns the number of remaining strings in the primary set to match
        """
        return len(self.primary)
