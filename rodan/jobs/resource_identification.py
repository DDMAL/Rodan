import re

import magic


def define_midi(*args, **kwargs):
    # [TODO] should be audio/midi
    return "application/midi"


def define_zip(*args, **kwargs):
    return "application/zip"


def define_json(*args, **kwargs):
    return "application/json"


def define_png(filename, mime=None):
    png_mimetypes = {
        "1-bit grayscale": "image/onebit+png",
        "16-bit grayscale": "image/grey16+png",
    }

    try:
        return png_mimetypes[mime[2][1:]]
    except KeyError:
        pass

    with open(filename) as f:
        data = f.read()

    if data[25].encode("hex") == "06":
        return "image/rgba+png"

    return "image/rgb+png"


def define_jpeg(*args, **kwargs):
    return "image/rgb+jpg"


def define_jp2(*args, **kwargs):
    return "image/jp2"


def define_xml(filename, mime=None):
    with open(filename) as f:
        data = f.readlines()

    xml_mimetypes = {
        """<gamera-database version="2.0">""": "application/gamera+xml",
        """<!DOCTYPE feature_vector_file [""": "application/ace+xml",
    }

    try:
        return xml_mimetypes[data[1].strip()]
    except KeyError:

        # [TODO] application/vnd.recordare.musicxml(+xml)
        if re.search(re.compile(r"""-//Recordare//DTD MusicXML"""), data[1]) is not None:
            return "application/x-muscxml+xml"

        if re.search(r"""<mei xml""", data[1]) is not None:
            return "application/mei+xml"

    return "application/octet-stream", data[1]


def define_text(filename, mime=None):
    with open(filename) as f:
        data = f.readline().strip()

    text_mimetypes = {
        "Indexer,interval.IntervalIndexer,interval.IntervalIndexer,interval.IntervalIndexer,interval.IntervalIndexer,interval.IntervalIndexer,interval.IntervalIndexer": "application/x-vis_vertical_pandas_series+csv",  # noqa
        "Indexer,interval.HorizontalIntervalIndexer,interval.HorizontalIntervalIndexer,interval.HorizontalIntervalIndexer,interval.HorizontalIntervalIndexer,interval.HorizontalIntervalIndexer": "application/x-vis_horizontal_pandas_series+csv",  # noqa
        "Indexer,offset.FilterByOffsetIndexer,offset.FilterByOffsetIndexer,offset.FilterByOffsetIndexer": "application/x-vis_noterest_pandas_series+csv",  # noqa
        "Indexer,ngram.NGramIndexer": "application/x-vis_ngram_pandas_dataframe+csv",
        "@relation Converted_from_ACE_XML": "application/arff",
        "Duration,Acoustic_Guitar_Fraction,Amount_of_Arpeggiation,Average_Melodic_Interval,Average_Note_Duration,Average_Note_To_Note_Dynamics_Change,Average_Number_of_Independent_Voices,Average_Range_of_Glissandos,Average_Time_Between_Attacks,Average_Time_Between_Attacks_For_Each_Voice,Average_Variability_of_Time_Between_Attacks_For_Each_Voice,Brass_Fraction,Changes_of_Meter,Chromatic_Motion,Combined_Strength_of_Two_Strongest_Rhythmic_Pulses,Compound_Or_Simple_Meter,Direction_of_Motion,Distance_Between_Most_Common_Melodic_Intervals,Dominant_Spread,Duration_of_Melodic_Arcs,Electric_Guitar_Fraction,Electric_Instrument_Fraction,Glissando_Prevalence,Harmonicity_of_Two_Strongest_Rhythmic_Pulses,Importance_of_Bass_Register,Importance_of_High_Register,Importance_of_Loudest_Voice,Importance_of_Middle_Register,Initial_Tempo,Interval_Between_Strongest_Pitch_Classes,Interval_Between_Strongest_Pitches,Maximum_Note_Duration,Maximum_Number_of_Independent_Voices,Melodic_Fifths,Melodic_Intervals_in_Lowest_Line,Melodic_Octaves,Melodic_Thirds,Melodic_Tritones,Minimum_Note_Duration,Most_Common_Melodic_Interval,Most_Common_Melodic_Interval_Prevalence,Most_Common_Pitch_Class,Most_Common_Pitch_Class_Prevalence,Most_Common_Pitch,Most_Common_Pitch_Prevalence,Note_Density,Number_of_Common_Melodic_Intervals,Number_of_Common_Pitches,Number_of_Moderate_Pulses,Number_of_Pitched_Instruments,Number_of_Relatively_Strong_Pulses,Number_of_Strong_Pulses,Number_of_Unpitched_Instruments,Orchestral_Strings_Fraction,Overall_Dynamic_Range,Percussion_Prevalence,Pitch_Class_Variety,Pitch_Variety,Polyrhythms,Primary_Register,Quality,Quintuple_Meter,Range,Range_of_Highest_Line,Relative_Note_Density_of_Highest_Line,Relative_Range_of_Loudest_Voice,Relative_Strength_of_Most_Common_Intervals,Relative_Strength_of_Top_Pitch_Classes,Relative_Strength_of_Top_Pitches,Repeated_Notes,Rhythmic_Looseness,Rhythmic_Variability,Saxophone_Fraction,Second_Strongest_Rhythmic_Pulse,Size_of_Melodic_Arcs,Staccato_Incidence,Stepwise_Motion,Strength_of_Second_Strongest_Rhythmic_Pulse,Strength_of_Strongest_Rhythmic_Pulse,Strength_Ratio_of_Two_Strongest_Rhythmic_Pulses,String_Ensemble_Fraction,String_Keyboard_Fraction,Strong_Tonal_Centres,Strongest_Rhythmic_Pulse,Triple_Meter,Variability_of_Note_Duration,Variability_of_Note_Prevalence_of_Pitched_Instruments,Variability_of_Note_Prevalence_of_Unpitched_Instruments,Variability_of_Number_of_Independent_Voices,Variability_of_Time_Between_Attacks,Variation_of_Dynamics,Variation_of_Dynamics_In_Each_Voice,Vibrato_Prevalence,Violin_Fraction,Voice_Equality_-_Dynamics,Voice_Equality_-_Melodic_Leaps,Voice_Equality_-_Note_Duration,Voice_Equality_-_Number_of_Notes,Voice_Equality_-_Range,Voice_Separation,Woodwinds_Fraction,": "application/arff+csv",  # noqa
        ",Basso seguente,Figured bass": "application/x-vis_figuredbass_pandas_series+csv",
        "<features_to_extract>": "application/jsc+txt",
        # This ought not be called a CSV file.
        "imagePath,imagesBinary,name,folio,description,classification,mei,review,dob,project": "text/csv", 
    }

    try:
        return text_mimetypes[data]
    except KeyError:
        # This regex could be better
        if re.search(r"^\[\[", data) is not None and re.search(r"\]\]$", data) is not None:
            return "application/gamera-polygons+txt"

        # JSON could be single line or multi-line.
        # Granted, this is not the best idea, but libmagic won't always figure out that its a
        # json file. This regex could definitely be better.
        if re.search(r"^\{", data) is not None:
            return "application/json"

        # For detecting regular CSV's, we need more than the first line
        # Fallback, also if the newline character messed the json identification in libmagic.
        with open(filename) as f:
            data = f.readlines()

        try:
            # There are no TSV files in Rodan that we could find. This is also no an ideal way
            # to identify a CSV file.
            commas_line1 = data[0].count(",")
            commas_line2 = data[1].count(",")

            if commas_line1 > 0 and commas_line1 == commas_line2:
                return "text/csv"
        except IndexError:
            # If all else fails, then it's a text file.
            pass

    return "text/plain"


def define_stream(filename, mime=None):
    with open(filename, "rb") as f:
        data = f.read()

    if data[0:2] == b"\x80\x02":
        # [TODO] Change to application/x-ocropus+pyrnn
        return "application/ocropus+pyrnn"
    
    if data[0:4] == b"\x89\x48\x44\x46":
        # TODO: Change to application/x-hdf 
        return "keras/model+hdf5"

    return "application/octet-stream"


def fileparse(filename):
    magic_mime = magic.from_file(filename, mime=True)
    text_description = magic.from_file(filename).split(",")

    mimetype_translation = {
        "text/plain": define_text,

        # Depends how libmagic feels: RFC 7303 or RFC 3023
        "text/xml": define_xml,
        "application/xml": define_xml,

        "image/png": define_png,
        "image/jpeg": define_jpeg,
        "image/jp2": define_jp2,
        "audio/midi": define_midi,
        "application/zip": define_zip,
        "application/json": define_json,
        "application/octet-stream": define_stream,
        "application/x-hdf": define_stream,
    }

    try:
        return mimetype_translation[magic_mime](filename, text_description)
    except KeyError:
        # If all else fails then give a tuple, crash rodan, and tell me what mimetype you found.
        pass

    with open(filename) as f:
        data = f.readline()
    return "application/octet-stream", magic_mime, data


if __name__ == "__main__":
    """
    Duplicated in tests for simplicity when adding more rodan types.

    Either run:
        python manage.py test rodan.test.test_mimetype_identification
    or:
        python resource_identification.py
    """

    if True:
        assert fileparse("../test/files/LLIA") == "application/ace+xml"
        assert fileparse("../test/files/AWKQ") == "application/arff"
        assert fileparse("../test/files/XSNA") == "application/arff+csv"
        assert fileparse("../test/files/ZHAH") == "application/gamera-polygons+txt"
        assert fileparse("../test/files/DXUA") == "application/gamera+xml"
        assert fileparse("../test/files/PKAF") == "application/jsc+txt"
        assert fileparse("../test/files/AHSK") == "application/mei+xml"
        assert fileparse("../test/files/PAOS") == "application/midi"
        assert fileparse("../test/files/TQOA") == "image/grey16+png"
        assert fileparse("../test/files/WYAG") == "image/jp2"
        assert fileparse("../test/files/EQRQ") == "image/onebit+png"
        assert fileparse("../test/files/YASH") == "image/rgb+jpg"
        assert fileparse("../test/files/GWJA") == "application/x-muscxml+xml"
        assert fileparse("../test/files/AOGO") == "application/x-vis_figuredbass_pandas_series+csv"
        assert fileparse("../test/files/DUKU") == "application/x-vis_horizontal_pandas_series+csv"
        assert fileparse("../test/files/BYKA") == "application/x-vis_vertical_pandas_series+csv"
        assert fileparse("../test/files/7W4A") == "application/x-vis_ngram_pandas_dataframe+csv"
        assert fileparse("../test/files/KGRA") == "application/x-vis_noterest_pandas_series+csv"
        assert fileparse("../test/files/KASD") == "application/zip"
        assert fileparse("../test/files/UZFA") == "application/json"
        assert fileparse("../test/files/ZTAS") == "application/ocropus+pyrnn"
        assert fileparse("../test/files/GAZG") == "application/json"
        assert fileparse("../test/files/QIWR") == "application/json"
        assert fileparse("../test/files/PXCV") == "image/rgba+png"
        assert fileparse("../test/files/OASD") == "image/rgb+png"
        assert fileparse("../test/files/APFX") == "keras/model+hdf5"
        assert fileparse("../test/files/2FKA") == "text/csv"

        print("[+] Success - Current Filetypes work")