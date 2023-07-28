from skimage import io
import json
import align_to_ocr as align

folder = "[TEST_DATA_FOLDER]"

path_to_transcript = folder + "[TXT FILE]"
path_to_image = folder + "[PNG FILE]"

transcript = align.read_file(path_to_transcript)
raw_image = io.imread(path_to_image)
model_name = "salzinnes_stgall"

result = align.process(raw_image, transcript, model_name)

syl_boxes, image, lines_peak_locs, _ = result
align.draw_results_on_page(raw_image, syl_boxes, lines_peak_locs, folder + "result.png")
outfile_path = folder + "result.json"
with open(outfile_path, "w") as file:
    json.dump(align.to_JSON_dict(syl_boxes, lines_peak_locs), file)
