import numpy as np
# from unidecode import unidecode
from functools import partial

# scoring system; these were the optimal weights found by grid search. different scoring methods
# tend to barely make any impact on the actual aligned output, however, since things are
# aggregated by syllable, so don't worry about tweaking this too much.
default_match_weights = [8, -5]
default_gap_penalties = [-7, -7, -3, 0]


def perform_alignment(transcript, ocr, match_function=None, gap_penalties=None, ignore_case=True, verbose=False):
    '''
    @match_function must be a function that takes in two strings and returns a single integer:
        a positive integer for a "match," a negative integer for a "mismatch."

    @scoring_system must be array-like, of one of the following forms:
        [gap_open_x, gap_open_y, gap_extend_x, gap_extend_y]
        [gap_open, gap_extend]

    @ignore_case ensures that the default scoring method will treat uppercase and lowercase letters
        the same, by applying lower() before every comparison. this setting will be ignored if a
        callable function is passed into match_function.
    '''

    def default_score_method(a, b, weights, ignore_case):
        if ignore_case:
            a = a.lower()
            b = b.lower()
        return weights[0] if a == b else weights[1]

    if match_function is None:
        weights = default_match_weights
        scoring_method = partial(default_score_method, weights=weights, ignore_case=ignore_case)
    elif type(match_function) is list:
        scoring_method = partial(default_score_method, weights=match_function, ignore_case=ignore_case)
    elif callable(match_function):
        scoring_method = match_function
    else:
        raise ValueError('gap_penalties argument {} invalid: must either be a list of 2 elements or a callable function that takes two elements'.format(match_function))

    if gap_penalties is None:
        gap_open_x, gap_open_y, gap_extend_x, gap_extend_y = default_gap_penalties
    elif len(gap_penalties) == 4:
        gap_open_x, gap_open_y, gap_extend_x, gap_extend_y = gap_penalties
    elif len(gap_penalties) == 2:
        gap_open_x, gap_open_y = (gap_penalties[0], gap_penalties[0])
        gap_extend_x, gap_extend_y = (gap_penalties[1], gap_penalties[1])
    else:
        raise ValueError('gap_penalties argument {} invalid: must be a list of either 4 or 2 elements'.format(gap_penalties))

    transcript = transcript + [' ']
    ocr = ocr + [' ']

    # y_mat and x_mat keep track of gaps in horizontal and vertical directions
    mat = np.zeros((len(transcript), len(ocr)))
    y_mat = np.zeros((len(transcript), len(ocr)))
    x_mat = np.zeros((len(transcript), len(ocr)))
    mat_ptr = np.zeros((len(transcript), len(ocr)))
    y_mat_ptr = np.zeros((len(transcript), len(ocr)))
    x_mat_ptr = np.zeros((len(transcript), len(ocr)))

    # establish boundary conditions
    for i in range(len(transcript)):
        mat[i][0] = gap_extend_x * i
        x_mat[i][0] = -1e100
        y_mat[i][0] = gap_extend_x * i
    for j in range(len(ocr)):
        mat[0][j] = gap_extend_y * j
        x_mat[0][j] = gap_extend_y * j
        y_mat[0][j] = -1e100

    for i in range(1, len(transcript)):
        for j in range(1, len(ocr)):

            # update main matrix (for matches)
            # match_score = match if transcript[i-1] == ocr[j-1] else mismatch
            eq_res = scoring_method(transcript[i-1], ocr[j-1])
            match_score = eq_res

            mat_vals = [mat[i-1][j-1], x_mat[i-1][j-1], y_mat[i-1][j-1]]
            mat[i][j] = max(mat_vals) + match_score
            mat_ptr[i][j] = int(mat_vals.index(max(mat_vals)))

            # update matrix for y gaps
            y_mat_vals = [mat[i][j-1] + gap_open_y + gap_extend_y,
                        x_mat[i][j-1] + gap_open_y + gap_extend_y,
                        y_mat[i][j-1] + gap_extend_y]

            y_mat[i][j] = max(y_mat_vals)
            y_mat_ptr[i][j] = int(y_mat_vals.index(max(y_mat_vals)))

            # update matrix for x gaps
            x_mat_vals = [mat[i-1][j] + gap_open_x + gap_extend_x,
                        x_mat[i-1][j] + gap_extend_x,
                        y_mat[i-1][j] + gap_open_x + gap_extend_x]

            x_mat[i][j] = max(x_mat_vals)
            x_mat_ptr[i][j] = int(x_mat_vals.index(max(x_mat_vals)))

    # TRACEBACK
    # which matrix we're in tells us which direction to head back (diagonally, y, or x)
    # value of that matrix tells us which matrix to go to (mat, y_mat, or x_mat)
    # mat of 0 = match, 1 = x gap, 2 = y gap
    #
    # first
    tra_align = []
    ocr_align = []
    align_record = []
    pt_record = []
    xpt = len(transcript) - 1
    ypt = len(ocr) - 1
    mpt = mat_ptr[xpt][ypt]

    # start it off. we are forcibly aligning the final characters. this is not ideal.
    tra_align += transcript[xpt]
    ocr_align += ocr[ypt]
    align_record += ['O'] if(transcript[xpt] == ocr[ypt]) else ['~']

    # start at bottom-right corner and work way up to top-left
    while(xpt > 0 and ypt > 0):

        pt_record += str(int(mpt))

        # case if the current cell is reachable from the diagonal
        if mpt == 0:
            tra_align.append(transcript[xpt - 1])
            ocr_align.append(ocr[ypt - 1])
            added_text = transcript[xpt - 1] + ' ' + ocr[ypt - 1]

            # determine if this diagonal step was a match or a mismatch
            align_record.append('O' if(transcript[xpt - 1] == ocr[ypt - 1]) else '~')

            mpt = mat_ptr[xpt][ypt]
            xpt -= 1
            ypt -= 1

        # case if current cell is reachable horizontally
        elif mpt == 1:
            tra_align.append(transcript[xpt - 1])
            ocr_align.append('_')
            added_text = transcript[xpt - 1] + ' _'

            align_record.append(' ')
            mpt = x_mat_ptr[xpt][ypt]
            xpt -= 1

        # case if current cell is reachable vertically
        elif mpt == 2:
            tra_align.append('_')
            ocr_align.append(ocr[ypt - 1])
            added_text = '_ ' + ocr[ypt - 1]

            align_record.append(' ')
            mpt = y_mat_ptr[xpt][ypt]
            ypt -= 1

        # for debugging
        # print('mpt: {} xpt: {} ypt: {} added_text: [{}]'.format(mpt, xpt, ypt, added_text))

    # we want to have ended on the very top-left cell (xpt == 0, ypt == 0). if this is not so
    # we need to add the remaining terms from the incomplete sequence.

    # print(xpt, ypt)
    while ypt > 0:
        tra_align.append('_')
        ocr_align.append(ocr[ypt - 1])
        align_record.append(' ')
        ypt -= 1

    while xpt > 0:
        ocr_align.append('_')
        tra_align.append(transcript[xpt - 1])
        align_record.append(' ')
        xpt -= 1

    # reverse all records, since we obtained them by traversing the matrices from the bottom-right
    tra_align = tra_align[-1:0:-1]
    ocr_align = ocr_align[-1:0:-1]
    align_record = align_record[-1:0:-1]
    pt_record = pt_record[-1:0:-1]

    if verbose:
        for n in range(len(tra_align)):
            line = '{} {} {}'
            print(line.format(tra_align[n], ocr_align[n], align_record[n]))

    return tra_align, ocr_align, mat[-1][-1]


if __name__ == '__main__':

    seq1 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit '
    seq2 = str.upper('LoLO LOrem ipsum fipsudolor ..... sit eamet, c.nnr adizisdcing eelitellit')
    match_weights = [3, -4]
    gap_penalties = [-2, -2, -1, -1]

    # seq1 = [seq1[2*x] + seq1[2*x + 1] for x in range(len(seq1) // 2)]
    # seq2 = [seq2[2*x] + seq2[2*x + 1] for x in range(len(seq2) // 2)]

    seq1 = list(seq1)
    seq2 = list(seq2)

    a, b, score = perform_alignment(seq1, seq2, match_weights, gap_penalties, ignore_case=True)

    sa = ''
    sb = ''

    for n in range(len(a)):
        spacing = str(max(len(a[n]), len(b[n])))
        sa += ('{:' + spacing + 's}').format(a[n])
        sb += ('{:' + spacing + 's}').format(b[n])

    print(sa)
    print(sb)

    # import parse_salzinnes_csv as psc
    # reload(psc)
    #
    # num = '082'
    # with open('./salzinnes_ocr/salzinnes_{}_ocr.txt'.format(num)) as f:
    #     ocr = list(f.read())
    #
    # text_func = psc.filename_to_text_func()
    # transcript = list(text_func('CF-{}'.format(num)))
    #
    # a, b = perform_alignment(transcript, ocr, verbose=True)
