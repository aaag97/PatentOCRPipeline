from pdf2image import convert_from_path
import os
import argparse
import cv2
import json

"""
function to convert the coordinates of bounding boxes from label studio units (percentages) to box file units (pixels
Args:
result - a result entry from a label studio annotations json file
"""
def convert_from_ls(result):
    if 'original_width' not in result or 'original_height' not in result:
        return None

    value = result['value']
    w, h = result['original_width'], result['original_height']

    if all([key in value for key in ['x', 'y', 'width', 'height']]):
        return w * value['x'] / 100.0, \
               h * value['y'] / 100.0, \
               w * value['width'] / 100.0, \
               h * value['height'] / 100.0

"""
function to convert a label studio json file to a box file
Args:
json - path to json file
output_path - path to box file
Returns:
None
"""
def convert_label_studio_json_to_box(json_path, output_path):
    with open(json_path, 'r') as f:
        json_dict = json.load(f)
    with open(output_path, 'w') as f:
        for result in json_dict[0]['annotations'][0]['result']:
            if result['from_name'] == "transcription":
                xmin, ymin, width, height = convert_from_ls(result)
                f.write('{} {} {} {} {} {}\n'.format(result['value']['text'][0], xmin, ymin, xmin+width-1, ymin+height-1, result['value']['rotation']))


def main():
    parser = argparse.ArgumentParser(description='Convert a label studio json file to a Tesseract box file')
    parser.add_argument('-i','--input', help='path to the label studio json file', required=True)
    parser.add_argument('-o','--output', help='path to the box file to be created', required=True)
    args = vars(parser.parse_args())
    input_ = args['input']
    output_path = args['output']
    convert_label_studio_json_to_box(input_, output_path)

if __name__ == "__main__":
    main()