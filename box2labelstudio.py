from pdf2image import convert_from_path
import os
import argparse
import cv2
import pytesseract
import json

"""
function to convert the coordinates of bounding boxes to label studio units (percentages)
Args:
x - the xmin coordinate in the number of pixels unit
y - the ymin coordinate in the number of pixels unit
width - the width number of pixels
height - the height number of pixels
original_width - the width of the entire image in number of pixels
original_height - the height of the entire image in number of pixels
"""
def convert_to_ls(x, y, width, height, original_width, original_height):
    return x / original_width * 100.0, y / original_height * 100.0, \
           width / original_width * 100.0, height / original_height * 100

"""
function to get tesseract bounding boxes for a given image (base tesseract model)
Args:
input_ - path to image
Returns:
img - the image as it is read by cv2
boxes - the boxes string returned by tesseract
"""
def tesseract_get_bounding_boxes(input_):
    img = cv2.imread(input_)
    boxes = pytesseract.image_to_boxes(img) 
    return img, boxes

"""
function to convert tesseract's bounding box output to a json output which is compatible with label studio (given the buggy nature of label studio, this function might need some work before usage)
Args:
input_ - path to image
json_id - id to use for the json file
annotations_id - the id to use for the annotations
label_box_img_path - image path as it appears on label studio
label_box_img_name - image name as it appears on label studio
project_number - label studio project number
task_number - the task number on label studio
output_path - output to output json file
Returns:
None, the conversion result is written in output_path
"""
def convert_box_to_labelstudio(input_,json_id, annotations_id, label_box_img_name, label_box_img_path, project_number, task_number, output_path):
    img, boxes = tesseract_get_bounding_boxes(input_)
    og_height, og_width, c = img.shape
    boxes_list = boxes.split('\n')
    boxes_list = [el.split() for el in boxes_list]
    boxes_list
    output = [{"id":json_id,"annotations":[{"id":annotations_id,"completed_by":1,"result":[],"was_cancelled":False,"ground_truth":False,"prediction":{}, "task":task_number, "parent_prediction":None, "parent_annotation":None}], "file_upload":label_box_img_name, "drafts":[],"predictions":[],"data":{"ocr":label_box_img_path},"meta":{},"project":project_number}]
    empty_transcriptions = 0
    for box_i in range(len(boxes_list)):
        try:
            label, xmin, ymin, xmax, ymax, rot = boxes_list[box_i]
            xmin = float(xmin)
            ymin = float(ymin)
            xmax = float(xmax)
            ymax = float(ymax)
            rot = float(rot)
            x_perc, y_perc, width_perc, height_perc = convert_to_ls(xmin, ymin, xmax-xmin+1, ymax-ymin+1, og_width, og_height)
            print('here')

            transcript_dict = {"original_width":og_width,
                        "original_height":og_height,
                        "image_rotation":0,
                        "value":{                   
                           "x":x_perc,
                             "y":y_perc,
                             "width":width_perc,
                             "height":height_perc,
                             "rotation":rot,
                            "text": [
                            label
                              ]},                 
                        "id":str(box_i),
                        "from_name": "transcription",
                        "to_name": "image",
                        "type": "textarea",
                        "origin":"manual"}
            bbox_dict = {
                "original_width":og_width,
                "original_height":og_height,
                "image_rotation":0,
                "id":str(box_i),
                "from_name": "bbox",
                "to_name": "image",
                "type": "rectangle",
                "value": {
                     "x":x_perc,
                     "y":y_perc,
                     "width":width_perc,
                     "height":height_perc,
                     "rotation":rot
                }
                ,"origin":"manual"
              }

            output[0]["annotations"][0]["result"].append(bbox_dict)
            output[0]["annotations"][0]["result"].append(transcript_dict)
        except:
            empty_transcriptions = empty_transcriptions + 1
    with open(output_path, 'w') as f:
        json.dump(output, f)
    print('Done with the conversion! Number of empty transcriptions in box file: {}'.format(empty_transcriptions))    

def main():
    parser = argparse.ArgumentParser(description='Convert a Tesseract box file to a Label Studio json file')
    parser.add_argument('-i','--input', help='path to the image file', required=True)
    parser.add_argument('-f','--filename', help='the name of the image on label studio', required=True)
    parser.add_argument('-a','--filepath', help='the path of the image on label studio', required=True)
    parser.add_argument('-n','--jsonid', help='the id of the json file', required=True)
    parser.add_argument('-s','--annotationsid', help='the id of the annotations', required=True)
    parser.add_argument('-p','--projnum', help='the project number on label studio', required=True)
    parser.add_argument('-t','--tasknum', help='the task number on label studio', required=True)
    parser.add_argument('-o','--output', help='path to the json file to be created', required=True)
    args = vars(parser.parse_args())
    input_ = args['input']
    label_box_img_name = args['filename']
    label_box_img_path = args['filepath']
    json_id = args['jsonid']
    annotations_id = args['annotationsid']
    project_number = args['projnum']
    task_number = args['tasknum']
    output_path = args['output']
    convert_box_to_labelstudio(input_,json_id, annotations_id, label_box_img_name, label_box_img_path, project_number, task_number, output_path)

if __name__ == "__main__":
    main()