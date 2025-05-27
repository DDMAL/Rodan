import csv
import re


def clean(text):
    # remove all character that are not letters or whitespace
    text = re.sub(r"[^\s\w|]", "", text)
    text = re.sub(r" \| ", " ", text)
    # change all runs of consecutive spaces to single spaces
    text = re.sub(r" +", " ", text)
    # convert to lowercase
    # text = text.lower()
    return text


def combine_transcripts(standard, ms):
    # this is really terrible. please forgive me.
    # the issue is: to syllabify correctly we need to know which 'i's in the transcripts represent
    # 'j's and which are actually 'i's. this is corrected in the standardized spelling but not the
    # MS spelling, which we'd rather use.

    ms = ms.replace('ihe', 'ie')

    if not standard:
        return ms

    j_search = r'\w*[jJ]\w*'
    res = re.finditer(j_search, standard)
    for match in res:
        word = match.group().lower()
        new_pat = word.replace('j', r'\w')
        ms = re.sub(new_pat, word, ms)

    return ms


def filename_to_text_func(transcript_path, mapping_path=None):
    '''
    returns a function that, given the filename of a salzinnes image, returns the lyrics
    on that image. to be safe, this will include chants that may partially appear on the previous
    or next page.
    '''

    arr = []
    with open(transcript_path) as file:
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            arr.append(row)
    header = arr[0]
    arr = arr[1:]

    # throw away chants with no associated melody on the page (Mode == *)
    arr = [x for x in arr if not x[10] == '*' and not x[2] == 'folio']

    folio_to_chants = {}

    # x[2] = folio name containing chant
    folio_names = list(set([x[2] for x in arr]))
    folio_names.sort()

    mapping = []
    if not mapping_path:
        for i, name in enumerate(folio_names):
            line = {}
            line['seq'] = i
            line['folio'] = name
            line['filename'] = name
            mapping.append(line)
    else:
        with open(mapping_path) as file:
            reader = csv.reader(file, delimiter=',')
            header = next(reader)
            for row in reader:
                line = {}
                line['seq'] = int(row[0])
                line['folio'] = row[1]
                line['filename'] = row[2]
                mapping.append(line)

    for name in folio_names:
        chant_rows = [x for x in arr if x[2] == name]

        # x[3] = sequence of chants on folio
        chant_rows.sort(key=lambda x: int(x[3]))

        # x[13] = standardized spelling of chant
        # x[14] = MS spelling of chant
        chants = [combine_transcripts(x[13], x[14]) for x in chant_rows]
        folio_to_chants[name] = chants

    def folio_to_text(inp):

        if type(inp) == int:
            find_folio = [(i, x) for (i, x) in enumerate(mapping) if inp == x['seq']]
        else:
            find_folio = [(i, x) for (i, x) in enumerate(mapping) if inp == x['folio']]

        if not find_folio:
            raise ValueError('folio / seq {} not found'.format(inp))

        if len(find_folio) > 1:
            raise ValueError('duplicates found for {}'.format(inp))

        idx, entry = find_folio[0]

        folio = entry['folio']
        fname = entry['filename']
        prev_entry = mapping[idx - 1]
        prev_folio = prev_entry['folio']

        # add last chant of previous page to output text, if the previous page has a chant
        if prev_folio in folio_to_chants:
            text = folio_to_chants[prev_folio][-1]
        else:
            text = ''

        # it's possible that no chant starts on this page, but there is chant text on this page
        # carried over from the previous page.
        if folio in folio_to_chants:
            for chant in folio_to_chants[folio]:
                text = text + ' ' + chant

        # to handle salzinnes, as a quick hack.
        fname = fname.replace('CF-', '')
        return fname, text

    return folio_to_text


if __name__ == '__main__':
    text_func = filename_to_text_func('./csv/123723_Salzinnes.csv', './csv/mapping.csv')
    # for n in range(1, 464):
    #     fname, transcript = text_func(n)
    #     fname = './salzinnes_transcripts/CF-{}.txt'.format(fname)
    #     with open(fname, 'w') as f:
    #         f.write(transcript)
