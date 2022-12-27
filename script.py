from io import BytesIO
from itertools import repeat
from wand.image import Image
from PIL import Image as PILImage
import os, re, numpy, requests, replicate, multiprocessing, tqdm
threadCount = 4

def upscaleImage(args):
    imagePath, colorization = args
    if not os.path.isfile(imagePath) or not re.search(r'\.(png|jpg|jpeg)$', imagePath):
        print("Error: File does not exist or is not a JPG/PNG image: " + imagePath)
        exit()
    imagePathWithoutExtension = re.sub(r'\.(png|jpg|jpeg)$', "", imagePath)
    tempFolderName = "temp-" + str(numpy.random.randint(1000000000))
    os.makedirs(tempFolderName)
    
    if colorization:
        # downscale and recolor image
        with Image(filename=imagePath) as img:
            img.transform(resize="1000x1000>")
            # convert to grayscale
            imgPil = PILImage.open(BytesIO(img.make_blob("png"))).convert("L")
            imgPil.save(tempFolderName + "/grayscale.png")
            # recolor image
            model = replicate.models.get("cjwbw/bigcolor")
            version = model.versions.get("9451bfbf652b21a9bccc741e5c7046540faa5586cfa3aa45abc7dbb46151a4f7")
            outputArray = version.predict(image=open(tempFolderName + "/grayscale.png", "rb"))
            os.system("rm " + tempFolderName + "/grayscale.png")
            imageUrls = [i["image"] for i in outputArray]
            imageUrls.pop() # remove last image because it's often ugly
        # create average image from four recolored images
        for imageUrl in imageUrls:
            response = requests.get(imageUrl)
            if response.status_code != 200:
                print("Error", str(response.status_code) + ":", response.text)
                exit()
            with Image(blob=response.content) as img:
                img.quality = 100
                img.save(filename=tempFolderName + "/" + imageUrl.replace("https://replicate.delivery/pbxt/", "").replace("/output.png", "") + ".png")
        os.system("convert " + tempFolderName + "/*.png -average " + tempFolderName + "/average.png")

    # upscale the image
    if colorization:
        os.rename(tempFolderName + "/average.png", tempFolderName + "/low-res.png")
    else:
        os.system("cp " + imagePath + " " + tempFolderName + "/low-res.png")
    model = replicate.models.get("nightmareai/real-esrgan")
    version = model.versions.get("42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738c1d7b")
    imageUrl = version.predict(image=open(tempFolderName + "/low-res.png", "rb"),scale=4,face_enhance=False)
    os.system("rm -rf " + tempFolderName)
    # download and save the image
    response = requests.get(imageUrl)
    if response.status_code != 200:
        print("Error in downloading upscaled image", str(response.status_code) + ":", response.text)
        exit()
    with Image(blob=response.content) as img:
        img.quality = 80
        img.save(filename=imagePathWithoutExtension + ("_upscaled_colorized.jpeg" if colorization else "_upscaled.jpeg"))

if __name__ == "__main__":
    apiKey = os.getenv('REPLICATE_API_TOKEN')
    if apiKey == None:
        apiKey = input("Please enter your Replicate API key: ").rstrip()
        if apiKey == "":
            print("Error: API key is empty")
            exit()
        os.environ['REPLICATE_API_TOKEN'] = apiKey
    folderPath = input("Please enter the folder path of the target images: ").rstrip().replace("\\", "")
    if not os.path.isdir(folderPath):
        print("Error: Folder does not exist")
        exit()
    colorizationInput = input("Colorize images? (y/n): ").lower()
    colorization = True if colorizationInput == "y" or colorizationInput == "yes" else False
    files = [folderPath + "/" + f for f in os.listdir(folderPath) if os.path.isfile(os.path.join(folderPath, f))]
    files = [f for f in files if re.search(r'\.(png|jpg|jpeg)$', f, re.IGNORECASE)]
    files = [f for f in files if not re.search(r'(_upscaled_colorized|_upscaled)\.jpeg$', f, re.IGNORECASE)]
    if len(files) == 0:
        print("Error: No JPG/PNG images found in folder")
        exit()
    pool = multiprocessing.Pool(threadCount)
    for _ in tqdm.tqdm(pool.imap_unordered(upscaleImage, zip(files, repeat(colorization))), total=len(files)):
        pass
    pool.close()
    pool.join()
    print("Script complete")