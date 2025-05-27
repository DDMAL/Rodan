# Run with pytest from project checkout.
import mei2volpiano


def test_version():
    """
    Make sure the version in the TOML file and in the __init__.py file are the same.
    """
    with open("pyproject.toml") as f:
        tomllines = f.read().splitlines()
        tomlversion = set([l for l in tomllines if "version =" in l])
        initversion = set([f'version = "{mei2volpiano.__version__}"'])
        # set is there to catch any duplicate/additional entries
        assert initversion == tomlversion


import unittest
import sys

sys.path.insert(0, "../src")

# 016r_reviewed
_016_correct_vol = (
    "1---g---fg---f---f---f---fffd---"
    "f---gf---ef---d---e---gh---gkhjk---k7---k---jk"
    "---hkghg---fg---gf-fded---d---f---gh-hjkg---g-"
    "--gfgff---fd-fgfef7---fe7---k---klkk---hjkj---hhg"
    "---hg---h---k---jlkk-kj---hg---hk---k7---k---k---k-"
    "--klkkjh-jkj---hg---ghk---kjjhjhgh---hg---d---e---"
    "gh7---k---kh---k---kj---j---jlkj-kjhjh---kj---k---l"
    "---kjkk---k7---jkmlk-lml---jlkk---jk---h---mh---m---"
    "lnml-mkkj---k---k---k---k---k---jklkj7---l---lmlmlk-"
    "--jkljk---jh---hg---k---lml---mklm---m---mnlk-lml-"
    "--jlkk---kj7---m---m---m---lm---lk-lmlml-jkj---l-"
    "--lk---lm---lk---jklk---kj---k---kh7---k---k---"
    "jklkj---l---lmlmlk---jkljk---jh---h---mh---m7---"
    "l---j---ln7---l---jkj---jk---l---k---jh---ghkhj--"
    "-hg---j---glj-lm---l---l---l---klmnmlm7---ml---lk-"
    "--klm---lmlkjk---kj---jk---l---k---kj---h---"
    "hklkjklkl---lk7---k---k---jklkjh-hkjh---hjghgh7-"
    "--hg---l---lmnml---klkkj---k---lj"
)
# CDN-Hsmu_M2149.L4_003r.mei
_003r_correct_vol = (
    "1---nnln-kln---kl---kl---no---n---o-qo-pr--"
    "-q---r---pqpo---q7---q---o-qo-q---on---nopop-o-"
    "nmlnon---op---opo---nopono---on---n---noq7---jh--"
    "-jhghg---hjkl---k---k---k---k---k---kl---k---k---k-"
    "j-h7---j---ghg---fegh---gf---c---d---f---fg---f---f-"
    "--ghf---fe7---fgj---jg-h-j-h-g---g-h-g-f-g-f---f---"
    "g-hg-h7---g-h---g---g---gh7---g---gkh---klkkj-k---"
    "lmlm---ml---kj---kl---lj---kl---kl---lkkj-j-h-g7---"
    "ghkg-hggf---h---k---kj-kh---gfghgfg---g-hg---g---"
    "gh---g---g7---g---lg---lk---lnlmlklk---l---l-nm---"
    "no---oq---l---nm---l---o---o-nml7---ml----kl---lml-"
    "ljkj---jk---l-ml-mnm---l---kkj---hg---ghkhj---hg---"
    "g---g7---h---g---h---g---f---g---kh---kj-kh---hghjhj"
    "---jh---l---k7---j---lmlm---kl---lj---l---kj-kl---hg"
    "---ghkg-hggf---f---hk---kj---l-kkjh---kl7---m-nm-n-m"
    "-l-m-l---lk---l-lkl---hk---j-klkjh-jkjh---g---ghjh-"
    "gh---hg---l-m-n-m-l"
)
# CDN-Hsmu_M2149.L4_003v.mei
_003v_correct_vol = (
    "1---k-l-k-k-j---k---kl---k---lj---k-l---k-"
    "l---l-m-nm---ml---mlmlk---kj---kl-ml-m-n-m7---"
    "lklml-m---lkj-kj---l-k7---g-h---hg-hggf---f-h---"
    "hklkj-kl7-jl---lk---k---k---j-k-l---k-j---lkjkj-j-"
    "h-g-hg---kk---kh---jklkj-h-jkjh---gh7---j-h-g-h---"
    "h-g---g---g---lg---lk---lnlmlklk---l---nm-n-o--"
    "-o-p---l7---lnnm---n-o-n---mnm-l-ml-ljkj---jk---"
    "lmlm-n-m---kh---klm---lk---j---ljkj-kjh-g-hg7---g-"
    "--gl---lk-lkh---k---jlkk---k-j---g---g-h---hgggf-h--"
    "-f---hk7---kj---lk-kjh---kl-m-nm-nmlml---l---lk-kh"
    "---k---kjkl---h-g---ghkg-hggf7---kk---hk---jklkjh-"
    "jkjh---ghjhgh---h-g7---l-mnml---kj---klkkj---k---k7"
    "---k-l---k---k---k---k---k---lj---kl---kl---lmnm---"
    "m-l7---klkkj---kl---lm---l---l---l---mlmlk---kj---"
    "k-lmlm-n-m---l-j-l-nl-m7---l-kjkj-g-g-lg7---o---o-"
    "--oprr---r---rrq---p---prrq---orpqpqroomnm---mnp---p"
)

_16_std = (
    "1---g-fg-f-f-f-fffd-f-gf-ef-d-e-gh-gkhjk-k7-k-jk"
    "-hkghg-fg-gf-fded-d-f-gh-hjkg-g-gfgff-fd-fgfef7-fe7-k-klkk"
    "-hjkj-hhg-hg-h-k-jlkk-kj-hg-hk-k7-k-k-k-klkkjh-jkj-hg-ghk"
    "-kjjhjhgh-hg-d-e-gh7-k-kh-k-kj-j-jlkj-kjhjh-kj-k-l-kjkk"
    "-k7-jkmlk-lml-jlkk-jk-h-mh-m-lnml-mkkj-k-k-k-k-k-jklkj7"
    "-l-lmlmlk-jkljk-jh-hg-k-lml-mklm-m-mnlk-lml-jlkk-kj7-m"
    "-m-m-lm-lk-lmlml-jkj-l-lk-lm-lk-jklk-kj-k-kh7-k-k"
    "-jklkj-l-lmlmlk-jkljk-jh-h-mh-m7-l-j-ln7-l-jkj"
    "-jk-l-k-jh-ghkhj-hg-j-glj-lm-l-l-l-klmnmlm7-ml"
    "-lk-klm-lmlkjk-kj-jk-l-k-kj-h-hklkjklkl-lk7-k-k-jklkjh"
    "-hkjh-hjghgh7-hg-l-lmnml-klkkj-k-lj"
    )

_003r_std = (
    "1---nnln-kln-kl-kl-no-n-o-qo-pr-q-r-pqpo-q7-q-o-qo-q-on"
    "-nopop-o-nmlnon-op-opo-nopono-on-n-noq7-jh-jhghg-hjkl-k"
    "-k-k-k-k-kl-k-k-k-j-h7-j-ghg-fegh-gf-c-d-f-fg-f-f-ghf-"
    "fe7-fgj-jg-h-j-h-g-g-h-g-f-g-f-f-g-hg-h7-g-h-g-g-gh7-g-gkh"
    "-klkkj-k-lmlm-ml-kj-kl-lj-kl-kl-lkkj-j-h-g7-ghkg-hggf-h-k-"
    "kj-kh-gfghgfg-g-hg-g-gh-g-g7-g-lg-lk-lnlmlklk-l-l-nm-no-oq"
    "-l-nm-l-o-o-nml7-ml-kl-lml-ljkj-jk-l-ml-mnm-l-kkj-hg-ghkhj"
    "-hg-g-g7-h-g-h-g-f-g-kh-kj-kh-hghjhj-jh-l-k7-j-lmlm-kl-lj"
    "-l-kj-kl-hg-ghkg-hggf-f-hk-kj-l-kkjh-kl7-m-nm-n-m-l-m-l-"
    "lk-l-lkl-hk-j-klkjh-jkjh-g-ghjh-gh-hg-l-m-n-m-l"
    )

_003v_std = (
    "1---k-l-k-k-j-k-kl-k-lj-k-l-k-l-l-m-nm-ml-mlmlk-kj-kl-ml"
    "-m-n-m7-lklml-m-lkj-kj-l-k7-g-h-hg-hggf-f-h-hklkj-kl7-jl"
    "-lk-k-k-j-k-l-k-j-lkjkj-j-h-g-hg-kk-kh-jklkj-h-jkjh-gh7-j"
    "-h-g-h-h-g-g-g-lg-lk-lnlmlklk-l-nm-n-o-o-p-l7-lnnm-n-o-n-"
    "mnm-l-ml-ljkj-jk-lmlm-n-m-kh-klm-lk-j-ljkj-kjh-g-hg7-g-gl"
    "-lk-lkh-k-jlkk-k-j-g-g-h-hgggf-h-f-hk7-kj-lk-kjh-kl-m-nm"
    "-nmlml-l-lk-kh-k-kjkl-h-g-ghkg-hggf7-kk-hk-jklkjh-jkjh-"
    "ghjhgh-h-g7-l-mnml-kj-klkkj-k-k7-k-l-k-k-k-k-k-lj-kl-kl-"
    "lmnm-m-l7-klkkj-kl-lm-l-l-l-mlmlk-kj-k-lmlm-n-m-l-j-l-nl"
    "-m7-l-kjkj-g-g-lg7-o-o-oprr-r-rrq-p-prrq-orpqpqroomnm-mnp-p"
    )

n_standard = [_16_std, _003r_std, _003v_std]

_W_Coronam_correct_vol = "1---f--g--f--f--f--f--f--f--e--g--h"

_W_EtConstituisti_vol = "1---c--c--c--c--c--c--d--c--c--c--c--c--c--c--c--c--b--d--e"

_W_Tuum_vol = "1---c--c--c--c--d--c--c--c--c--c--b--d--e"

coronam_std = "1---f-g-f-f-f-f-f-f-e-g-h"
etconstituisti_std = "1---c-c-c-c-c-c-d-c-c-c-c-c-c-c-c-c-b-d-e"
tuum_std = "1---c-c-c-c-d-c-c-c-c-c-b-d-e"

w_standard = [coronam_std, etconstituisti_std, tuum_std]

listCorrectOutputs = [_016_correct_vol, _003r_correct_vol, _003v_correct_vol]

listWCorrectOutputs = [_W_Coronam_correct_vol, _W_EtConstituisti_vol, _W_Tuum_vol]

# 016r.mei
listClefs_016r = list("CCCCCCCCCCCCCCCCC")

# CDN-Hsmu_M2149.L4_003r.mei
listClefs_003r = list("CFFFCCCCCCCCCCCCC")

# CDN-Hsmu_M2149.L4_003v.mei
listClefs_003v = list("CCCCCCCCCCCCCCF")

listClefs_W_Coronam = list("G")

listClefs_W_EtConstituisti = list("G")

listClefs_W_Tuum = list("G")

listCorrectClef = [
    listClefs_016r,
    listClefs_003r,
    listClefs_003v,
    listClefs_W_Coronam,
    listClefs_W_EtConstituisti,
    listClefs_W_Tuum,
]

# 016r.mei
listSyls_016r = [
    "es",
    "e",
    "ius",
    "non",
    "e",
    "lon",
    "ga",
    "bun",
    "tur",
    "Mi",
    "se",
    "re",
    "bi",
    "tur",
    "do",
    "mi",
    "nus",
    "ia",
    "cob",
    "et",
    "is",
    "rael",
    "sal",
    "va",
    "bi",
    "tur",
    "Re",
    "ver",
    "te",
    "re",
    "vir",
    "go",
    "is",
    "rael",
    "re",
    "ver",
    "te",
    "re",
    "ad",
    "ci",
    "vi",
    "ta",
    "tes",
    "tu",
    "as",
    "Mi",
    "se",
    "re",
    "Des",
    "cen",
    "det",
    "do",
    "mi",
    "nus",
    "si",
    "cut",
    "plu",
    "vi",
    "a",
    "in",
    "vel",
    "lus",
    "O",
    "ri",
    "e",
    "tur",
    "in",
    "di",
    "e",
    "bus",
    "e",
    "ius",
    "ius",
    "ti",
    "ci",
    "a",
    "et",
    "a",
    "bun",
    "dan",
    "ti",
    "a",
    "pa",
    "cis",
    "Et",
    "a",
    "do",
    "ra",
    "bunt",
    "e",
    "um",
    "om",
    "nes",
    "re",
    "ges",
    "om",
    "nes",
    "gen",
    "tes",
    "ser",
    "vi",
    "ent",
    "e",
    "i",
    "O",
    "ri",
    "e",
    "Ve",
    "ni",
    "do",
    "mi",
    "ne",
    "et",
    "no",
    "li",
    "tar",
    "da",
    "re",
    "re",
    "la",
    "xa",
    "fa",
    "ci",
    "no",
    "ra",
    "ple",
    "bis",
    "tu",
    "e",
    "et",
    "Re",
    "vo",
    "ca",
    "dis",
    "per",
    "sos",
    "in",
    "ter",
    "ram",
    "su",
    "am",
    "A",
    "so",
    "lis",
    "or",
    "tu",
]
# CDN-Hsmu_M2149.L4_003r.mei
listSyls_003r = [
    "ho",
    "nor",
    "et",
    "om",
    "nis",
    "po",
    "pu",
    "lus",
    "tri",
    "bus",
    "et",
    "lin",
    "guae",
    "ser",
    "vi",
    "ent",
    "e",
    "i",
    "Po",
    "te",
    "s",
    "tas",
    "e",
    "jus",
    "po",
    "tes",
    "tas",
    "ae",
    "ter",
    "na",
    "quae",
    "non",
    "au",
    "fe",
    "re",
    "tur",
    "et",
    "reg",
    "num",
    "e",
    "jus",
    "quod",
    "non",
    "cor",
    "rum",
    "pe",
    "tur",
    "Et",
    "da",
    "Mis",
    "sus",
    "est",
    "ga",
    "bri",
    "el",
    "an",
    "ge",
    "lus",
    "ad",
    "ma",
    "ri",
    "am",
    "vir",
    "gi",
    "nem",
    "de",
    "pon",
    "sa",
    "tam",
    "io",
    "seph",
    "nun",
    "ci",
    "ans",
    "e",
    "i",
    "ver",
    "bum",
    "et",
    "ex",
    "pa",
    "ves",
    "cit",
    "vir",
    "go",
    "de",
    "lu",
    "mi",
    "ne",
    "ne",
    "ti",
    "me",
    "as",
    "ma",
    "ri",
    "a",
    "in",
    "ve",
    "nis",
    "ti",
    "gra",
    "ti",
    "am",
    "a",
    "pud",
    "do",
    "mi",
    "num",
    "Ec",
    "ce",
    "con",
    "ci",
    "pi",
    "es",
    "et",
    "pa",
    "ri",
    "es",
    "et",
    "vo",
    "ca",
    "bi",
    "tur",
    "al",
    "tis",
    "si",
    "mi",
    "fi",
    "li",
    "us",
    "A",
]
# CDN-Hsmu_M2149.L4_003v.mei
listSyls_003v = [
    "ve",
    "ma",
    "ri",
    "a",
    "gra",
    "ti",
    "a",
    "ple",
    "na",
    "do",
    "mi",
    "nus",
    "te",
    "cum",
    "A",
    "ve",
    "ma",
    "ri",
    "a",
    "gra",
    "ti",
    "a",
    "ple",
    "na",
    "do",
    "mi",
    "nus",
    "te",
    "cum",
    "spi",
    "ri",
    "tus",
    "san",
    "ctus",
    "su",
    "per",
    "in",
    "ni",
    "et",
    "in",
    "te",
    "et",
    "vir",
    "tus",
    "al",
    "tis",
    "si",
    "mi",
    "o",
    "bum",
    "bra",
    "bit",
    "ti",
    "bi",
    "quod",
    "e",
    "nim",
    "ex",
    "te",
    "nas",
    "ce",
    "tur",
    "san",
    "ctum",
    "vo",
    "ca",
    "bi",
    "tur",
    "fi",
    "li",
    "us",
    "de",
    "i",
    "Quo",
    "mo",
    "do",
    "fi",
    "et",
    "is",
    "tud",
    "quo",
    "ni",
    "am",
    "vi",
    "rum",
    "non",
    "cog",
    "nos",
    "co",
    "et",
    "res",
    "pon",
    "dens",
    "an",
    "ge",
    "lus",
    "di",
    "xit",
    "e",
    "i",
    "Sal",
    "va",
    "to",
    "rem",
    "ex",
    "pec",
    "ta",
    "mus",
    "do",
    "mi",
]

listSyls_W_Coronam = [
    "Co",
    "ro",
    "namw",
    "de",
    "la",
    "pi",
    "de",
    "pre",
    "ci",
    "o",
    "so",
]

listSyls_W_Et = [
    "Et",
    "con-",
    "sti-",
    "tu-",
    "is-",
    "ti",
    "e-",
    "um",
    "su-",
    "per",
    "o-",
    "pe-",
    "ra",
    "ma-",
    "nu-",
    "um",
    "tu-",
    "a-",
    "rum",
]
listSyls_W_Tuum = [
    "Tu-",
    "um",
    "glo",
    "ri-",
    "o-",
    "sum",
    "re-",
    "co-",
    "li-",
    "mus",
    "tri-",
    "um-",
    "phum",
]

listCorrectSyls = [
    listSyls_016r,
    listSyls_003r,
    listSyls_003v,
    listSyls_W_Coronam,
    listSyls_W_Et,
    listSyls_W_Tuum,
]

# 016r.mei
listNotes_016r = list(
    "gfgffffffdfgfefdegagcabcccbcacgagfggffdeddfgaabcgggfgfffdfgfeffeccdcc"
    "abcbaagagacbdcccbagaccccccdccbabcbaggaccbbabagaagdegaccaccbbbdcbcbaba"
    "cbcdcbcccbcedcdedbdccbcaeaedfedeccbcccccbcdcbddededcbcdbcbaagcdedecde"
    "eefdcdedbdcccbeeededcdededbcbddcdedcbcdccbccaccbcdcbddededcbcdbcbaaea"
    "edbdfdbcbbcdcbagacabagbgdbdedddcdefedeeddccdededcbccbbcdccbaacdcbcdcd"
    "dcccbcdcbaacbaabgagaagddefedcdccbcdb"
)

# CDN-Hsmu_M2149.L4_003r.mei
listNotes_003r = list(
    "ffdfcdfcdcdfgfgbgacbcabagbbgbgbgffgagagfedfgfgagagfgagfggfffgbbabagag"
    "abcdccccccdcccbabgagfegagfcdffgffgaffefgbbgabaggagfgffgagagagggaggcac"
    "dccbcdedeedcbcddbcdcddccbbaggacgaggfaccbcagfgagfggagggagggdgdcdfdedcd"
    "cddfefggbdfedggfededcddeddbcbbcdedefedccbaggacabagggagagfgcacbcaagaba"
    "bbadcbdedecddbdcbcdaggacgaggffaccbdccbacdefefededdcddcdacbcdcbabcbagg"
    "abagaagdefed"
)

# CDN-Hsmu_M2149.L4_003v.mei
listNotes_003v = list(
    "cdccbccdcdbcdcddefeedededccbcdedefedcdededcbcbdcgaagaggffaacdcbcdbddc"
    "ccbcdcbdcbcbbagagcccabcdcbabcbagabagaagggdgdcdfdedcdcdfefggaddffefgfe"
    "fededdbcbbcdedefecacdedcbdbcbcbagagggddcdcacbdcccbggaagggfafaccbdccba"
    "cdefefededddccaccbcdaggacgaggfccacbcdcbabcbagabagaagdefedcbcdccbcccdc"
    "ccccdbcdcddefeedcdccbcddedddededccbcdedefedbdfdedcbcbggdggggacccccbaa"
    "ccbgcababcggefeefaa"
)

listNotes_Coronam = list("fgffffffegh")

listNotes_Et = list("ccccccdcccccccccbde")

listNotes_Tuum = list("ccccdcccccbde")

listNotes = [listNotes_016r, listNotes_003r, listNotes_003v]


class TestVolpiano(unittest.TestCase):
    # tests the output of a correct volpiano file vs
    # a generated volpiano sequence

    def test_volpiano_output_1(self):
        f1 = "./resources/neume_mei/016r_reviewed.mei"
        f2 = "./resources/neume_mei/CDN-Hsmu_M2149.L4_003r.mei"
        f3 = "./resources/neume_mei/CDN-Hsmu_M2149.L4_003v.mei"

        files = [f1, f2, f3]

        lib = mei2volpiano.MEItoVolpiano()
        for i, element in enumerate(files):
            with open(element, "r") as f:
                final_string = lib.convert_mei_volpiano(f)
                self.assertEqual(final_string, listCorrectOutputs[i])

    def test_volpiano_output_2(self):
        w1 = "./resources/western_mei/Coronam_de_lapide_precioso_eius_alleluia_alleluia_alleluia.mei"
        w2 = "./resources/western_mei/Et_constituisti_eum_super_opera_manuum_tuarum_alleluia.mei"
        w3 = "./resources/western_mei/Tuum_gloriosum_recolimus_triumphum_alleluia_alleluia_regis_opprobrium.mei"

        wfiles = [w1, w2, w3]

        lib = mei2volpiano.MEItoVolpiano()
        for i, element in enumerate(wfiles):
            with open(element, "r") as f:
                final_string = lib.convert_mei_volpiano(f, True)
                self.assertEqual(final_string, listWCorrectOutputs[i])

    def test_find_clefs(self):
        lib = mei2volpiano.MEItoVolpiano()
        ind = 1
        for mei_file in sys.argv[ind:]:
            with open(mei_file, "r") as f:
                elements = lib.get_mei_elements(mei_file)
                listC = lib.find_clefs(elements)
                self.assertEqual(listC, listCorrectClef[ind - 1])
            ind += 1

    def test_find_notes(self):
        lib = mei2volpiano.MEItoVolpiano()
        ind = 1
        for mei_file in sys.argv[ind:]:
            with open(mei_file, "r") as f:
                elements = lib.get_mei_elements(mei_file)
                listN = lib.find_notes(elements)
                self.assertEqual(listN, listNotes[ind - 1])
            ind += 1

    def test_find_syls(self):
        lib = mei2volpiano.MEItoVolpiano()
        ind = 1
        for mei_file in sys.argv[ind:]:
            with open(mei_file, "r") as f:
                elements = lib.get_mei_elements(mei_file)
                listS = lib.find_syls(elements)
                self.assertEqual(listS, listCorrectSyls[ind - 1])
            ind += 1

    def test_compare_volpianoN(self):
        lib = mei2volpiano.MEItoVolpiano()
        f1 = "./resources/neume_mei/016r_reviewed.mei"
        f2 = "./resources/neume_mei/CDN-Hsmu_M2149.L4_003r.mei"
        f3 = "./resources/neume_mei/CDN-Hsmu_M2149.L4_003v.mei"

        trueN3 = lib.secure_volpiano(str(listNotes[2]))

        self.assertTrue(lib.compare_volpiano_file(listCorrectOutputs[0], f1))
        self.assertFalse(lib.compare_volpiano_file(str(listNotes[1]), f2))
        self.assertFalse(lib.compare_volpiano_file(trueN3, f3))

    def test_compare_volpianoW(self):
        lib = mei2volpiano.MEItoVolpiano()
        w1 = "./resources/western_mei/Coronam_de_lapide_precioso_eius_alleluia_alleluia_alleluia.mei"
        w2 = "./resources/western_mei/Et_constituisti_eum_super_opera_manuum_tuarum_alleluia.mei"
        w3 = "./resources/western_mei/Tuum_gloriosum_recolimus_triumphum_alleluia_alleluia_regis_opprobrium.mei"
        w2_stringVolpiano = lib.secure_volpiano(str(listNotes_Et))  # Taken from listNotes_Et
        w3_stringVolpiano_false = lib.secure_volpiano(str(listNotes_Tuum))
        w3_stringVolpiano_false = f"{w3_stringVolpiano_false}aba"

        self.assertTrue(lib.compare_volpiano_file(_W_Coronam_correct_vol, w1, True))
        self.assertTrue(lib.compare_volpiano_file(w2_stringVolpiano, w2, True))
        self.assertFalse(lib.compare_volpiano_file(w3_stringVolpiano_false, w3, True))
    
    def test_compare_volpiano_volpiano(self):
        lib = mei2volpiano.MEItoVolpiano()

        for i, element in enumerate(listWCorrectOutputs):
            self.assertTrue(lib.compare_volpiano_volpiano(listWCorrectOutputs[i], w_standard[i]))
            self.assertTrue(lib.compare_volpiano_volpiano(listWCorrectOutputs[i], lib.secure_volpiano(listWCorrectOutputs[i])))
            
        
        for i, element in enumerate(listCorrectOutputs):
            self.assertTrue(lib.compare_volpiano_volpiano(listCorrectOutputs[i], n_standard[i]))
            self.assertTrue(lib.compare_volpiano_volpiano(listCorrectOutputs[i], lib.secure_volpiano(listCorrectOutputs[i])))


    def test_standardize_volpianoW(self):
        lib = mei2volpiano.MEItoVolpiano()
        w1 = "./resources/western_mei/Coronam_de_lapide_precioso_eius_alleluia_alleluia_alleluia.mei"
        w2 = "./resources/western_mei/Et_constituisti_eum_super_opera_manuum_tuarum_alleluia.mei"
        w3 = "./resources/western_mei/Tuum_gloriosum_recolimus_triumphum_alleluia_alleluia_regis_opprobrium.mei"

        files = [w1, w2, w3]

        for i, element in enumerate(w_standard):
            func = lib.convert_mei_volpiano(files[i], True)
            func = lib.standardize_volpiano(func)
            self.assertTrue(func, w_standard[i])
    
    def test_standardize_volpianoN(self):
        """This also covers compare_standard since the tesing method and the 
        implementation of the actual method are the same.
        """
        lib = mei2volpiano.MEItoVolpiano()
        f1 = "./resources/neume_mei/016r_reviewed.mei"
        f2 = "./resources/neume_mei/CDN-Hsmu_M2149.L4_003r.mei"
        f3 = "./resources/neume_mei/CDN-Hsmu_M2149.L4_003v.mei"

        files = [f1, f2, f3]

        for i, element in enumerate(n_standard):
            func = lib.convert_mei_volpiano(files[i])
            func = lib.standardize_volpiano(func) 
            self.assertTrue(func, w_standard[i])


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
