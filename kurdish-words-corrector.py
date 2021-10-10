from itertools import product


common_mistakes_dict = {'e': ['ê'], 'u': ['û'], 'i': ['î'], 's': ['ş'], 'c': ['ç'], 'w': ['v'],
                        'ê': ['e'], 'û': ['u'], 'î': ['i'], 'ş': ['s'], 'ç': ['c'], 'v': ['w']}

f = open('correct_words.txt', 'r', encoding='utf-8')
correct_words = f.read().split('\n')
f.close()


def generate_similar_correct_words(word):
    if word.lower() in correct_words:
        return word + ' is a correct word'
    else:
        for key in common_mistakes_dict.keys():
            if key not in common_mistakes_dict[key]:
                common_mistakes_dict[key].append(key)

        res = []

        # constructing all possible combination of values using product
        # mapping using zip()
        for sub in [zip(common_mistakes_dict.keys(), chr) for chr in product(*common_mistakes_dict.values())]:
            temp = word.lower()
            for repls in sub:
                # replacing all elements at once using * operator
                temp = temp.replace(*repls)
            res.append(temp)

        combinations = set(res)
        possibilities = set()
        for combination in combinations:
            if combination in correct_words:
                possibilities.add(combination)

        if len(possibilities) == 0:
            return word + ' is not in our database, and we didn\'t find a similar word'
        return possibilities


print(generate_similar_correct_words("reso"))
