from pmatcher.pmatcher import PrecinctMatcher
from typing import Dict
import json

def accuracy(mapping: Dict[str, str]):
    primary = list(mapping.keys())
    secondary = list(mapping.values())

    size = len(primary)

    matcher = PrecinctMatcher(primary, secondary)
    print("Exact match", len(matcher.exact())/size)
    print("Insensitive match", len(matcher.insensitive())/size)
    print("Insensitive stripped match", len(matcher.insensitive_stripped())/size)
    print("Aggressive insensitive normalized match", len(matcher.insensitive_normalized(aggressive=True))/size)
    print("Remaining", len(matcher.primary))

    # print("Manual", len(matcher.weighted_manual())/size)

    false_positives = 0
    false_negatives = 0
    for key, value in mapping.items():
        if key not in matcher.results:
            false_negatives += 1
            continue

        if matcher.results[key] != value:
            false_positives += 1

    print(f"False positives!: {false_positives}")
    print(f"False negatives: {false_negatives}")

if __name__ == "__main__":
    with open("benchmark/mapping_PA_2018_1.json") as f:
        mapping_1 = json.load(f)
        accuracy(mapping_1)

    with open("benchmark/mapping_PA_2018_2.json") as f:
        mapping_2 = json.load(f)
        accuracy(mapping_2)
