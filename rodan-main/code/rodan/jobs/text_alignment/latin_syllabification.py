# -*- coding: utf-8 -*-
import re

consonant_groups = ['qu', 'ch', 'ph', 'fl', 'fr', 'st', 'br', 'cr', 'cl', 'pr', 'tr', 'ct', 'th', 'sp']
diphthongs = ['ae', 'au', 'ei', 'oe', 'ui', 'ya', 'ex', 'ix']
vowels = ['a', 'e', 'i', 'o', 'u', 'y']

# add uppercase variants of every single symbol.
consonant_groups += [x[0].upper() + x[1:] for x in consonant_groups]
diphthongs += [x[0].upper() + x[1:] for x in diphthongs]
vowels += [x[0].upper() + x[1:] for x in vowels]


def clean_transcript(text):
    # remove all character that are not letters or whitespace
    text = re.sub(r"[^\s\w|]", "", text)
    text = re.sub(r" \| ", " ", text)
    # change all runs of consecutive spaces to single spaces
    text = re.sub(r" +", " ", text)
    # convert to lowercase
    # text = text.lower()
    return text


def syllabify_word(inp, verbose=False):
    '''
    separate each word into UNITS - first isolate consonant groups, then diphthongs, then letters.
    each vowel / diphthong unit is a "seed" of a syllable; consonants and consonant groups "stick"
    to adjacent seeds. first make every vowel stick to its preceding consonant group. any remaining
    consonant groups stick to the vowel behind them.
    '''
    #

    # remove all whitespace and newlines from input:
    inp = re.sub(r'[\s+]', '', inp)

    # convert to lowercase. it would be possible to maintain letter case if we saved the original
    # input and then re-split it at the very end of this method, if that's desirable

    if verbose:
        print('syllabifying {}'.format(inp))

    if len(inp) <= 1:
        return inp
    if inp.lower() == 'euouae':
        return 'e-u-o-u-ae'.split('-')
    if inp.lower() == 'cuius':
        return 'cu-ius'.split('-')
    if inp.lower() == 'eius':
        return 'e-ius'.split('-')
    if inp.lower() == 'iugum':
        return 'iu-gum'.split('-')
    if inp.lower() == 'iustum':
        return 'iu-stum'.split('-')
    if inp.lower() == 'iusticiam':
        return 'iu-sti-ci-am'.split('-')
    if inp.lower() == 'iohannes':
        return 'io-han-nes'.split('-')
    word = [inp]

    # for each unbreakable unit (consonant_groups and dipthongs)
    for unit in consonant_groups + diphthongs:
        new_word = []

        # check each segment of the word for this unit
        for segment in word:

            # if this segment is marked as unbreakable or does not have the unit we care about,
            # just add the segment back into new_word and continue
            if '*' in segment or unit not in segment:
                new_word.append(segment)
                continue

            # otherwise, we have to split this segment and then interleave the unit with the rest
            # this 'reconstructs' the original word even in cases where the unit appears more than
            # once
            split = segment.split(unit)

            # necessary in case there exists more than one example of a unit
            rep_list = [unit + '*'] * len(split)
            interleaved = [val for pair in zip(split, rep_list) for val in pair]

            # remove blanks and chop off last extra entry caused by list comprehension
            interleaved = [x for x in interleaved[:-1] if len(x) > 0]
            new_word += interleaved
        word = list(new_word)

    # now split into individual characters anything remaining
    new_word = []
    for segment in word:
        if '*' in segment:
            new_word.append(segment.replace('*', ''))
            continue
        # if not an unbreakable segment, then separate it into characters
        new_word += list(segment)
    word = list(new_word)

    # add marker to units to mark vowels or diphthongs this time
    for i in range(len(word)):
        if word[i] in vowels + diphthongs:
            word[i] = word[i] + '*'

    if verbose:
        print('split list: {}'.format(word))

    if not any(('*' in x) for x in word):
        return [''.join(word)]

    # begin merging units together until all units are marked with a *.
    escape_counter = 0
    while not all([('*' in x) for x in word]):

        # first stick consonants / consonant groups to syllables ahead of them
        new_word = []
        i = 0
        while i < len(word):
            if i + 1 >= len(word):
                new_word.append(word[i])
                break
            cur = word[i]
            proc = word[i + 1]
            if '*' in proc and '*' not in cur:
                new_word.append(cur + proc)
                i += 2
            else:
                new_word.append(cur)
                i += 1
        word = list(new_word)

        # then stick consonants / consonant groups to syllables behind them
        new_word = []
        i = 0
        while i < len(word):
            if i + 1 >= len(word):
                new_word.append(word[i])
                break
            cur = word[i]
            proc = word[i + 1]
            if '*' in cur and '*' not in proc:
                new_word.append(cur + proc)
                i += 2
            else:
                new_word.append(cur)
                i += 1
        word = list(new_word)

        if verbose:
            print('merging into syls:{}'.format(word))

        escape_counter += 1
        if escape_counter > 100:
            raise RuntimeError('input to syllabification script has created an infinite loop')

    word = [x.replace('*', '') for x in new_word]

    return word


def syllabify_text(input, verbose=False):
    words = input.split(' ')
    word_syls = [syllabify_word(w, verbose) for w in words]
    syls = [item for sublist in word_syls for item in sublist]
    return syls


if __name__ == "__main__":
    # fpath = "/Users/tim/Desktop/002v_transcript.txt"
    # with open(fpath) as f:
    #     ss = ' '.join(f.readlines())
    # res = syllabify_text(ss, True)
    # print(res)

    inp = 'Quique terrigene et filii hominum simul in unum dives et pauper Ite ' \
          'Qui regis israel intende qui deducis velut ovem ioseph qui sedes super cherubin Nuncia ' \
          'Excita domine potentiam tuam et veni ut salvos facias nos Qui regnaturus ' \
          'Aspiciens ' \
          'Aspiciebam in visu noctis et ecce in nubibus celi ' \
          'filius hominis venit Et datum est ei regnum et honor et ' \
          'omnis populus tribus et lingue servient ei ' \
          'zxcvbnm zx cvbnmzxcv bnm ' \
          'aaaaa413aa a$a %aa'
    res = syllabify_text(inp, True)
    print(res)
