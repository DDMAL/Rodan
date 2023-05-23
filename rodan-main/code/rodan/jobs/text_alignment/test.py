from skimage import io
import json
import align_to_ocr as align

# folder = "./example_data/May2023-MS73/unhealthy/"
folder = "./example_data/healthy/"

path_to_transcript = folder + "transcript.txt"
path_to_image = folder + "image.png"

transcript = align.read_file(path_to_transcript)
raw_image = io.imread(path_to_image)
# model_name = "develop/htr+"
model_name = "develop/deep3"
# model_name = "gothic_salzinnes_2021"

result = align.process(raw_image, transcript, model_name)

syl_boxes, image, lines_peak_locs, _ = result
align.draw_results_on_page(raw_image, syl_boxes, lines_peak_locs, folder + "result.png")
outfile_path = folder + "result.json"
with open(outfile_path, "w") as file:
    json.dump(align.to_JSON_dict(syl_boxes, lines_peak_locs), file)
