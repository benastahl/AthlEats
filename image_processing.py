from PIL import ImageDraw, Image
import numpy


# rezise image with new width
def rezise_image(image, new_width=150, ):
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)
    resized_image = image.resize((new_width, new_height))
    return resized_image

# convert to greyscale
def grayimage(image):
    grayscale_image = image.convert("L")
    return grayscale_image

def save_text_to_image(text_to_convert, image, new_width=150):

    # make an image with the same dimensions
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)

    # multiply by pixel of character with added room for error
    new_width = (new_width*6)+20
    new_height *= 15

    # set back ground color to black
    black = (0, 0, 0)

    # remove pesky black at the top of the screen and borders a tad
    x = 20
    y = 60
    w = new_width-x
    h = new_height-y
    im = img.crop((x,y,w,h))

    # makes the image webcam friendly
    final_image = im.resize((128,128))
    return(numpy.array(final_image))