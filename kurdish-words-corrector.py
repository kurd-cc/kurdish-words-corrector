import json
from itertools import product
import argparse
import re
from multiprocessing.pool import ThreadPool


parser = argparse.ArgumentParser(description='Correct Kurdish words especially the ones that went through wrong '
                                             'unicode settings')
parser.add_argument('-w', '--word', dest='word', type=str, help='The word that you want to correct it')
parser.add_argument('-t', '--text', dest='text', type=str, help='The text to correct its words')
parser.add_argument('-f', '--file', dest='file', type=str, help='The file path to correct words from its text')
parser.add_argument('-o', '--output', dest='output', type=str, help='The output file, if you want to save the results')
parser.add_argument('-d', '--depth', dest='depth', type=int, help='values from 1-3 depend on how depth (then slow) '
                                                                  'you want to correct, 1 is the fastest and the lest'
                                                                  ' depth, 3 is the slowest the most depth')
parser.add_argument('-p', '--parser', dest='parser', type=str, help='Parse the output file (json or yaml), default=yaml')
parser.add_argument('-wr', '--workers', dest='workers', type=int, help='The number of workers (threads), default=100')

args = parser.parse_args()

common_mistakes_dict_1 = {'e': ['ê'], 'u': ['û'], 'i': ['î'], 's': ['ş'], 'c': ['ç'], 'w': ['v'],
                          'ê': ['e'], 'û': ['u'], 'î': ['i'], 'ş': ['s'], 'ç': ['c'], 'v': ['w']}

common_mistakes_dict_2 = {'e': ['ê'], 'u': ['û', 'o', 'w'], 'i': ['î'], 's': ['ş'], 'c': ['ç'], 'w': ['v', 'o'],
                          'ê': ['e'], 'û': ['u', 'o', 'w'], 'î': ['i'], 'ş': ['s'], 'ç': ['c'], 'v': ['w'],
                          'o': ['u', 'û', 'w']}

common_mistakes_dict_3 = {'e': ['ê', 'i'], 'u': ['û', 'o', 'w'], 'i': ['î', 'e'], 's': ['ş'], 'c': ['ç'],
                          'w': ['v', 'o'],
                          'ê': ['e', 'î'], 'û': ['u', 'o', 'w'], 'î': ['i', 'ê'], 'ş': ['s'], 'ç': ['c'], 'v': ['w'],
                          'o': ['u', 'û', 'w']}

f = open('correct_words.txt', 'r', encoding='utf-8')
correct_words = f.read().split('\n')
f.close()


def correct_word(word, depth=1):
    if depth == 3:
        common_mistakes_dict = common_mistakes_dict_3
    elif depth == 2:
        common_mistakes_dict = common_mistakes_dict_2
    else:
        common_mistakes_dict = common_mistakes_dict_1
    if word.lower() in correct_words:
        return {'word': word, 'message': 'Is a correct word', 'status': 0}
    else:
        for key in common_mistakes_dict.keys():
            if key not in common_mistakes_dict[key]:
                common_mistakes_dict[key].append(key)

        res = []

        for sub in [zip(common_mistakes_dict.keys(), chr) for chr in product(*common_mistakes_dict.values())]:
            temp = word.lower()
            for repls in sub:
                temp = temp.replace(*repls)
            res.append(temp)

        combinations = set(res)
        possibilities = []

        for combination in combinations:
            if combination in correct_words:
                possibilities.append(combination)

        if len(possibilities) == 0:
            return {'word': word, 'message': 'Is not in our database, and we didn\'t find a similar word',
                    'status': 2}
        return {'word': word, 'message': 'Is not in our database, and we found similar word/s', 'status': 1,
                'possibilities': possibilities}


def correct_text(text, output_path=None, depth=1, parser="yaml", workers=100):
    all_words = list(filter(None, __split_text(text).strip().split("\n")))
    output = __get_output(all_words, depth, workers)

    if output_path is None:
        return str(output)
    else:
        output_states_path = '-states.'.join(output_path.split('.', 1))
        if not output['incorrect_words_with_possible_corrections']:
            if parser == "json":
                output = json.dumps(output)
            __save_to_file(text, output_path)
            __save_to_file(str(output), output_states_path)
        else:
            for item in output['incorrect_words_with_possible_corrections']:
                word = item['word']
                replacer = item['possibilities'][0]
                if word[0].isupper():
                    replacer = replacer.capitalize()
                text = text.replace(word, replacer, 1)
            if parser == "json":
                output = json.dumps(output)
            __save_to_file(text, output_path)
            __save_to_file(str(output), output_states_path)


def correct_file(file_path, output_path=None, depth=1, parser="yaml", workers=100):
    text = __read_from_file(file_path)
    return correct_text(text, output_path, depth, parser, workers)


def __get_output(all_words, depth=1, workers=100):
    output = dict()
    results = []
    current_correct_words = []
    incorrect_words_with_possible_corrections = []
    incorrect_words_without_possible_corrections = []

    pool = ThreadPool(workers)
    for word in all_words:
        results.append(pool.apply_async(correct_word, args=(word, depth)))
    pool.close()
    pool.join()
    results = [r.get() for r in results]

    for item in results:
        if item['status'] == 0:
            current_correct_words.append(item)
        elif item['status'] == 1:
            incorrect_words_with_possible_corrections.append(item)
        elif item['status'] == 2:
            incorrect_words_without_possible_corrections.append(item)

    output['correct_words'] = current_correct_words
    output['incorrect_words_with_possible_corrections'] = incorrect_words_with_possible_corrections
    output['incorrect_words_without_possible_corrections'] = incorrect_words_without_possible_corrections

    output['total_words'] = len(all_words)
    output['total_incorrect'] = len(incorrect_words_with_possible_corrections) + 0.5 * len(
        incorrect_words_without_possible_corrections)
    output['total_incorrect_with_corrections'] = len(incorrect_words_with_possible_corrections)
    output['total_incorrect_without_corrections'] = len(incorrect_words_without_possible_corrections)
    output['incorrect_percentage'] = (output['total_incorrect'] * 100) / (output['total_words'])

    return output


def __save_to_file(text, file_path):
    file = open(file_path, "w", encoding="UTF-8")
    file.write(text)
    file.close()


def __read_from_file(file_path):
    file = open(file_path, 'r', encoding='UTF-8')
    result = file.read()
    file.close()
    return result


def __split_text(text, delimiter="\n"):
    kurdish_letters = "ABCÇDEÊFGHIÎJKLMNOPQRSŞTUÛVWXYZabcçdeêfghiîjklmnopqrsştuûvwxyz"
    reg = "[^" + kurdish_letters + "]+"
    text = re.sub(reg, '*', text).rstrip()
    return delimiter.join(text.split('*'))


if __name__ == "__main__":
    depth = 1
    if args.depth is not None:
        depth = args.depth

    workers = 100
    if args.workers is not None:
        workers = args.workers

    parser = "yaml"
    if args.parser is not None and (args.parser.lower() == "yaml" or args.parser.lower() == "json"):
        parser = args.parser

    if args.word is not None and len(args.word.strip()) > 0:
        print(correct_word(args.word, depth=depth))
    elif args.text is not None and len(args.text.strip()) > 0 and args.output is None:
        print(correct_text(args.text, depth=depth, parser=parser, workers=workers))
    elif args.text is not None and len(args.text.strip()) > 0 and args.output is not None:
        correct_text(args.text, output_path=args.output, depth=depth, parser=parser, workers=workers)
        print("Success:", "Corrected text has been saved saved to", args.output)
    elif args.file is not None and len(args.file.strip()) > 0 and args.output is None:
        print(correct_file(args.file, depth=depth, parser=parser, workers=workers))
    elif args.file is not None and len(args.file.strip()) > 0 and args.output is not None:
        correct_file(args.file, output_path=args.output, depth=depth, parser=parser, workers=workers)
        print("Success:", "Corrected text has been saved saved to", args.output)
    else:
        print("Run 'python kurdish-words-corrector.py -h to find the usage'")
