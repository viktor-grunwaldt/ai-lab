from itertools import pairwise
import pickle
import random
import re


def load_data(filename: str) -> str | None:
    import gzip

    with gzip.open(filename, "rb") as f:
        data = f.read().decode("utf-8")
        return data


def get_splits(lst: list[int], end: int) -> list[int]:
    if lst[end] is None:
        return [0]
    return get_splits(lst, lst[end]) + [end]


def weight(x: int, y: int) -> int:
    return (y - x) ** 2


def solve(sentence: str, corpus: set[str], max_len) -> str:
    words_on_pos = [[] for _ in sentence]
    max_vals = [None] * (1 + len(sentence))
    best_splits = [None] * (1 + len(sentence))
    max_vals[0] = 0
    best_splits[0] = None

    def find_words(begin):
        # search exhausted
        if begin >= len(sentence):
            return
        # position searched
        if words_on_pos[begin]:
            return
        # restrict check depth, could be optimised with trie
        max_end = min(begin + max_len, len(sentence) + 1)
        for end in reversed(range(begin + 1, max_end)):
            if sentence[begin:end] in corpus:
                words_on_pos[begin].append(end)
                w = max_vals[begin] + weight(begin, end)
                if not max_vals[end] or max_vals[end] < w:
                    max_vals[end] = w
                    best_splits[end] = begin
                find_words(end)

    find_words(0)
    # print([[sentence[i:w] for w in words] for i, words in enumerate(words_on_pos)])
    separator_indexes = get_splits(best_splits, len(sentence))
    # print(*list(filter(None, words_on_pos)), sep="\n")
    words = (sentence[l:r] for l, r in pairwise(separator_indexes))
    ans = " ".join(words)
    return ans


def main(test_mode):
    # corpus = load_data("data/words_for_ai1.txt.gz").splitlines()
    # max_len = max(map(len, corpus))
    max_len = 29
    # corpus_set = set(corpus)
    with open("data/corpus_set.pickle", "rb") as f:
        corpus_set = pickle.load(f)

    # print(solve("tamatematykapustkinieznosi", corpus_set, max_len))
    # sent_val = lambda s: sum(len(w) ** 2 for w in s.split())
    if not test_mode:
        with open("data/pan_tadeusz_oryginal.txt", 'r') as f:
            pt = f.read().splitlines()
        
        # to lowercase and remove non letters
        pt = set(re.sub(r"[^\w+ ]", "", s.lower().strip()) for s in pt)
        with open("data/pan_tadeusz_bez_spacji.txt", "r") as f:
            sentences = f.read().lower().splitlines()
        correct_squaring = 0
        correct_random = 0
        for s in sentences:
            # print(solve(s, corpus_set, max_len))
            if solve(s, corpus_set, max_len) in pt:
                correct_squaring+=1
            if version2(s, corpus_set) in pt:
                correct_random +=1
        print(f"sentences reconstructed (squares): {correct_squaring}/{len(sentences)} ~ {correct_squaring/len(sentences)*100:2f}%")
        print(f"sentences reconstructed (random): {correct_random}/{len(sentences)} ~ {correct_random/len(sentences)*100:2f}%")
    else:
        with open("zad2_input.txt", "r") as f:
            sentences = f.read()
            out = []
            for s in sentences.splitlines():
                out.append(solve(s, corpus_set, max_len))
            with open("zad2_output.txt", "w") as of:
                of.write("\n".join(out))


def version1(text: str, corpus: set[str]) -> str:
    n = len(text)
    d = [0] * (n + 1)
    p = [None] * (n + 1)
    for i in range(1, n + 1):
        for j in range(i):
            if text[j:i] in corpus:
                w = d[j] + weight(j,i)
                if w > d[i]:
                    d[i] = w
                    p[i] = j

    ans = get_splits(p, n)
    splits = [text[l:r] for l, r in pairwise(ans)]
    return " ".join(splits)



def version2(text: str, corpus: set[str]) -> str:
    n = len(text)
    d = [0] * (n + 1)
    p = [None] * (n + 1)
    for i in range(1, n + 1):
        for j in range(i):
            if text[j:i] in corpus:
                w = d[j] + random.randrange(1, 10)
                if w > d[i]:
                    d[i] = w
                    p[i] = j

    ans = get_splits(p, n)
    splits = [text[l:r] for l, r in pairwise(ans)]
    return " ".join(splits)


if __name__ == "__main__":
    main(False)

