# PatentOCRPipeline

This repository contains files relating to the starts of an OCR pipeline for patent digitization.

## What has been done in this project

This project consisted mostly of a thorough examination and selection of patents from a set of British patents dating from before 1900. The result of this selection is stored in _noise&layout_groundtruth.xlsx_. Please note that only the most prominent layout/noise anomaly has been specified e.g. some patents that have been given a certain noise or layout class may also have some characteristics pretaining to other classes. In the case where some classes were all equally prominent for one given patent, said patent was categorized as having all these classes (i.e. the values for all these classes for that patent are all 1).

An exploration of how the ground truth could be built was carried out after this selection process. Four methods have been explored:
* [Lace](http://heml.mta.ca/lace/faq.html) was set up using eXist-db. Given the lack of documentation, we could not properly upload images and their corresponding box files.
* [Qt-box-editor](https://zdenop.github.io/qt-box-editor/) was also explored as it was [recommended by some tesseract users](https://medium.com/quantrium-tech/training-tesseract-using-qt-box-editor-1c089ae3029). It seems to be outdated.
* [Label Studio](https://labelstud.io/) was explored but given its lack of documentation, finding the proper way of feeding it pre-annotations was challenging. Reverse-engineering the pre-annotation format worked at the end. However, the program crashed afterwards. This was probably due to the number of bounding boxes needed to perform OCR on patents.
* [Tesseract web box editor](http://johanjunkka.com/tesseract-web-box-editor/) was the last tool to be explored. It works in a fairly straightforward fashion but it is inefficient (e.g. deleting bounding boxes in bulk is impossible, simple actions can cause a lag)

After a very thorough exploration of the available tools, it is suggested to either outsource the task (e.g. [Amazon Mechanical Turk](https://www.mturk.com/worker)) or that a tool be built inhouse and used for all annotations needed in the lab (mostly for OCR tasks).

## How to use provided scripts

### Turning PDF files to images

The script `pdf2imgs.py` converts PDF files into a folder with images such as each image corresponds to a PDF page. It can be used as follows - 

`python3 pdf2imgs.py -i <input> -o <output> -f <format>`

such that `<input>` is the path to the PDF file, `<output>` is the path to the folder where a folder of the images will be created and `<format>` is the format to write the images in (e.g. "TIFF", "PNG", "JPEG").

### Getting pre-annotations for [Label Studio](https://labelstud.io/)

The script `box2labelstudio.py` converts box files (as they are output by [Tesseract](https://github.com/tesseract-ocr/tesseract)) into a json file which is compatible with Label Studio.

The format that is given by Tesseract is a box file. It is a text file composed of one line for each annotation on a given image. Each line has the structure "_label xmin ymin xmax ymax rotation_" such that _label_ is the character that is recognized, _xmin_ is the minimum x coordinate of the bounding box, _ymin_ is the minimum y coordinate of the bounding box,  _xmax_ is the maximum x coordinate of the bounding box, _ymax_ is the maximum y coordinate of the bounding box,It can be used as follows (all in number of pixels) and _rotation_ is the rotation of the recognized character.

According to documentation, the format that is accepted by the standard OCR configuration of Label Studio is a json file that has the following structure

```json
{
   "data":{
      "ocr":<name_of_file>
   },
   "predictions":[
      {
         "result":[
         ],
         "score":<score>
      }
   ]
}
```

such that <name_of_file> is the name of the image (that is on label studio) corresponding to the annotations, \<score\> is the prediction score (and is optional), and the list `result` should contain two entries for each bounding box. These two entries should take the form

```json
{
   "original_width":<og_width>,
   "original_height":<og_height>,
   "image_rotation":<og_rotation>,
   "value":{
      "x":<xmin>,
      "y":<ymin>,
      "width":<width>,
      "height":<height>,
      "rotation":<rotation>
   },
   "id":<id>,
   "from_name":"bbox",
   "to_name":"image",
   "type":"rectangle"
}
```
and 

```json
{
   "original_width":<og_width>,
   "original_height":<og_height>,
   "image_rotation":<og_rotation>,
   "value":{
      "x":<xmin>,
      "y":<ymin>,
      "width":<width>,
      "height":<height>,
      "rotation":<rotation>,
      "text":[
         <text>
      ]
   },
   "id":<id>,
   "from_name":"transcription",
   "to_name":"image",
   "type":"textarea",
   "score":<score>
}
```

where <og_width> is the width of the whole image, <og_height> is the height of the whole image, <og_rotation> is the rotation of the whole image, <xmin> is the minimum x coordinate of the bounding box, <ymin> is the minimum y coordinate of the bounding box, <width> is the width of the bounding box, <height> is the height of the bounding box (please note that <xmin>, <ymin>, <width> and <height> are in percentage of the size of the whole image; a conversion function is available [here](https://labelstud.io/guide/predictions.html)), <rotation> is the rotation of the recognized character, <text> is the recognized text, <id> is the identifier of the annotation (by convention should be a string) and <score> is the prediction score given to the annotation. Please note that the common parameters have to match for each pair of entries (given that each pair corresponds to one annotation).

Given that feeding Label Studio pre-annotations in this format (which is the one specified in the documentation) did not work, reverse engineering was used to inspect which format should be used for Label Studio. It is presented as follows - 

```json
[{
   "id":<id>,
   "annotations":
      [{"id":<annotations_id>,
      "completed_by":1,
      "result":[],
      "was_cancelled":false,
      "ground_truth":false,
      "prediction":{},
      "task":<task_number>,
      "parent_prediction":null,
      "parent_annotation":null}],
   "file_upload":<filename>,
   "drafts":[],
   "predictions":[],
   "data":
      {"ocr":<filepath>},
   "meta":{},
   "project":<project_number>}]
```
   
where <id> is the identifier of the json file (by convention an integer), <annotations_id> is the identifier for the annotations (by convention an integer), <filename> is the filename of the image as it is visible on Label Studio, <task_number> is the number of the task as indicated by Label Studio, <filepath> is the whole path to the image (including the image filename) as visible on Label Studio, <project_number> is the number of the project as given by Label Studio and `results` should contain the same two entries per annotation as indicated above, with the following exceptions -

* an additional field `origin` the value of which should be `manual` should be added.
* the `score` field should not be included.

`box2labelstudio.py` is provided to convert from the box format output by Tesseract to the format which is accepted by Label Studio. It can be used as follows -

`python3 box2labelstudio.py -i <input> -f <filename> -a <filepath> -n <jsonid> -s <annotationsid> -p <projnum> -t <tasknum> -o <output>`

such that `<input>` is the path to the image,  `<filename>` is the name of the image on Label Studio, `<filepath>` is the path of the image on Label Studio, `<jsonid>` is the identifier to give to the json file, `<annotations_id>` is the identifier of the annotations to be written, `<projnum>` is the number of the project as indicated on Label Studio, `<tasknum>` is the task number as indicated on Label Studio and `<output>` is the path to the json file to be created.

It should be noted that even when Label Studio accepted this format, it lagged considerably.

### Turning [Label Studio](https://labelstud.io/) annotations into Tesseract box files

In order to convert a Label Studio json file to a Tesseract box file, `labelstudio2box.py` is provided. It can be used as follows - 

`python3 labelstudio2box.py -i <input> -o <output>`

such that <input> is the input json file and <output> is the output box file.

## Suggestions for future work

### Ground truth selection

#### There are three potential ways to proceed
* Use compiled database of noise/layout to classify patents automatically, and obtain patents across a wide range of noise/layout changes to be used in training an OCR model.
* Compute statistics on the compiled database to estimate how many patents to label and use in order to cover a wide range of noise and layout.
* Randomly sample the corpus.

### Ground truth building
* Try to get Lace to work. It seems to work well with kraken/ocropus but the documentation for it is unclear and outdated.
* Use Tesseract web box editor. It works directly with the Tesseract box format so there is no need for format conversions, however it is inefficient.
* Build a custom annotation tool. This is the option takes some time but it could be worthwhile given the lack of open source OCR annotation tools which are currently available.

### Model training and evaluation
* kraken: It seems to work well with Lace and in particular with historical documents, but its documentation is unclear and my initial results with it have not been promising.

* Tesseract: It is the most widely used and it is well documented. However, it has trouble with noisy documents.
