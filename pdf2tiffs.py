from pdf2image import convert_from_path
import os
import argparse

"""
function to convert a pdf file to a folder of images such that each image is a pdf page
Args:
* input_: path of input pdf
* output_folder: path to folder where another folder will be created for the output
* image_format: format for the images to be stored (eg 'TIFF', 'JPEG', 'PNG')
"""
def convert(input_,output_folder,image_format):
    patent = input_.split('/')[-1].split('.')[0]
    images = convert_from_path(input_)
    if output_folder[-1] == '/':
        image_path = output_folder + patent
    else:
        image_path = output_folder + '/' + patent
    os.mkdir(image_path)
    for i in range(len(images)):
        images[i].save(image_path + '/eng.times.{}_{}.{}'.format(patent, str(i), image_format.lower()), image_format)

def main():
    parser = argparse.ArgumentParser(description='Convert a PDF file into a folder with images such that each image is a PDF page')
    parser.add_argument('-i','--input', help='path to the PDF file', required=True)
    parser.add_argument('-o','--output', help='path to the a directory where the folder of images will be created', required=True)
    parser.add_argument('-f','--format', help='format of the images to be created', required=True)
    args = vars(parser.parse_args())
    input_ = args['input']
    output_folder = args['output']
    image_format = args['format']
    convert(input_,output_folder,image_format)

if __name__ == "__main__":
    main()