# Image Restoration Script

This python script is designed to batch upscale historic images, with the option to colorize the image as well. The script uses the [Wand](https://pypi.org/project/Wand/) and [Pillow](https://pypi.org/project/Pillow/) libraries to process images. It also uses the [Replicate](https://pypi.org/project/replicate/) library to access pre-trained machine learning models in the cloud for upscaling and colorization.

## Summary

-   Uses AI to colorize (model: bigcolor) and upscale (model: real-esrgan) old photos
-   Utilizes paid replicate.com API for cloud computing
-   Built with Python 3.9.6

## Example

Original Image - [Source](https://www.facebook.com/photo/?fbid=1059495844211293)
![Original Image](https://github.com/linusmimietz/Image-Restoration-Script/blob/main/example-image/original.jpg?raw=true)

Processed Image - Script Result
![Processed Image](https://github.com/linusmimietz/Image-Restoration-Script/blob/main/example-image/result.jpg?raw=true)

## Motivation

This year I wanted to gift my grandma a couple of historic images of her hometown from the time when she grew up. After curating about 130 photos I had the idea of using AI to enhance the low-resolution black-and-white photos. That's why I quickly threw together this script to batch-process the folder of images.

## How to Use

-   Install requirements: `pip3 install -r requirements.txt`
-   Install ImageMagick via terminal (example macOS): `brew install imagemagick`
-   Set replicate.com token with the terminal: `export REPLICATE_API_TOKEN=[token]` (this is recommended for not having to provide the key every time the script runs)
-   Run the script via the terminal like: `python3 script.py`

### Tip to get Wand working with ImageMagick 7 on macOS:

Run in the terminal, and afterward restart the terminal:

```
brew install imagemagick
echo 'export MAGICK_HOME=/opt/homebrew/opt/imagemagick/' >> ~/.zshrc
echo 'export PATH="/opt/homebrew/opt/imagemagick/bin:$PATH"' >> ~/.zshrc
```

## Output

The script will output the processed image to a file with the same name as the input image, but with "\_upscaled" or "\_upscaled_colorized.jpeg" added to the filename. For example, if the input image is "image.png", the output image will be "image_upscaled_colorized.jpeg".

## Limitations

-   The replicate.com API is not free, from my experience it costs about 1 USD for processing 200 images
-   The colorization might not be very accurate. Landscapes and cities work reasonably well, but the AI model seems to struggle a bit with people. (this probably could be improved by manually cherry-picking the best of the five image variants that the bigcolor model produces)
-   Currently, the script only supports JPG and PNG images as input (this probably could be extended quite easily)
