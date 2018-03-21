from argparse import ArgumentParser
from os import remove

import cv2
from PIL import Image
from skimage.measure import compare_ssim


def script_args():
    """Arguments to parse the script.

    Just needs two images to compare.
    """
    parser = ArgumentParser()
    parser.add_argument('-f', '--first', required=True,
                        help='The first input image')
    parser.add_argument('-s', '--second', required=True,
                        help='The second input image')
    return vars(parser.parse_args())


def compare_images(image_one, image_two, ssim_threshold=1.0,
                   save_diff_to='my-diff.png'):
    """Compare two images.

    If the calculated structural similarity index is less than the value
    specified for `ssim_threshold` then a diff of the images will be returned,
    with the differences highlighted on the image.

    Args:
        image_one ():
        image_two ():
        ssim_threshold (float): The acceptable diff between the two images.
            A value of 1.0 will expect an exact match.
        save_diff_to (str): A file path to save the diff to if an image diff
            is created. This file will only be created if the calculated
            structural similarity index value is less than the threshold
            specified by `ssim_threshold`.

    Returns:
        float: The structural similarity index value if the comparison shows
            the image to be within the threshold specified by `ssim_threshold`.

    """
    # Read them in open cv
    _image_one = cv2.imread(image_one)
    _image_two = cv2.imread(image_two)

    # Create greyscale versions to compare
    grayscale_one = cv2.cvtColor(_image_one, cv2.COLOR_BGR2GRAY)
    grayscale_two = cv2.cvtColor(_image_two, cv2.COLOR_BGR2GRAY)

    # Calculate the structural similarity index of the grey images
    # `score` is the SSIM value (decimal up to 1)
    # `diff` is the actual image diff data points, which we need to convert
    # into unsigned integers
    (score, diff) = compare_ssim(grayscale_one, grayscale_two, full=True)
    print('SSIM: {score}'.format(score=score))
    if score < ssim_threshold:
        diff = (diff * 255).astype('uint8')

        # find the threshold of the image diff
        # https://docs.opencv.org/trunk/d7/d4d/tutorial_py_thresholding.html
        threshold = cv2.threshold(diff, 0, 255,
                                  cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        # find the actual contours of that threshold, so the diffs can be
        # highlighted
        contours = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)[1]

        for c in contours:
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(_image_one, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.rectangle(_image_two, (x, y), (x + w, y + h), (0, 0, 255), 2)

        if save_diff_to is not None:
            _save_image_diff(image_one=_image_one, image_two=_image_two,
                             file_path=save_diff_to)

    return score


def _save_image_diff(image_one, image_two, file_path):
    """Save the image diff.

    Creates a file with the highlighted images side by side to show the
    comparison between them.

    Writes them to temp files at first to pillow can read them to combine

    Args:
        image_one (numpy.ndarray): The open cv handle for image one.
        image_two (numpy.ndarray): The open cv handle for image two.
        file_path (str): The path you want to save the image file to.

    """
    # TODO: See if this can be done directly in open CV without writing to a temp file first
    _temp_image_one = '.temp-image-diff-one.png'
    _temp_image_two = '.temp-image-diff-two.png'
    cv2.imwrite(_temp_image_one, image_one)
    cv2.imwrite(_temp_image_two, image_two)

    try:
        images = list(map(Image.open, [_temp_image_one, _temp_image_two]))
        widths, heights = zip(*(i.size for i in images))
        total_width = sum(widths)
        total_height = max(heights)

        diff_image = Image.new('RGB', (total_width, total_height))
        x_offset = 0
        for image in images:
            diff_image.paste(image, (x_offset, 0))
            x_offset += image.size[0]

        diff_image.save(file_path, format='png')

    except:
        pass

    finally:
        remove(_temp_image_one)
        remove(_temp_image_two)


if __name__ == '__main__':
    args = script_args()
    compare_images(image_one=args['first'], image_two=args['second'])
