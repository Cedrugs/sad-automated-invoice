from PIL import Image, ImageDraw, ImageFont
from urllib.parse import urlparse, parse_qs
from mimetypes import guess_type

import aiohttp
import aiofiles


base_image = Image.open('./assets/templates/boarding-pass.jpg')
font = ImageFont.truetype("./assets/Ticketing.ttf", 110)

name_position = (684, 487)
hobbies_position = (684, 735)
zone_position = (1763, 985)
extra_image_position = (105, 482)

def get_direct_gdrive_url(gdrive_url):
    parsed_url = urlparse(gdrive_url)
    if 'drive.google.com' in parsed_url.netloc:
        query_params = parse_qs(parsed_url.query)
        if 'open' in parsed_url.path or 'id' in query_params:
            file_id = query_params.get('id', [None])[0]
            if file_id:
                return f"https://drive.google.com/uc?export=download&id={file_id}"
    return gdrive_url

async def download_and_crop_image(drive_url):
    drive_url = get_direct_gdrive_url(drive_url)
    for attempt in range(3):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(drive_url) as response:
                    if response.status == 200:
                        content_type = response.content_disposition

                        guessed_type, _ = guess_type(content_type.filename)
                        if not guessed_type or not guessed_type.startswith('image/'):
                            raise Exception("URL did not return an image.")

                    dld_path = f'./assets/profile_pict/{content_type.filename}'
                        
                    async with aiofiles.open(dld_path, 'wb') as dld_img:
                        data = await response.read()
                        await dld_img.write(data)
                        
                try:
                    img = Image.open(dld_path)
                    break
                except Exception as img_exception:
                    print(f"Attempt {attempt + 1} failed to open image: {img_exception}")
                    last_exception = img_exception
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with RequestException: {e}")
            last_exception = e
            continue
    else:
        raise last_exception
    try:
        width, height = img.size
        new_dim = min(width, height)
        left = (width - new_dim) / 2
        top = (height - new_dim) / 2
        right = (width + new_dim) / 2
        bottom = (height + new_dim) / 2
        img_cropped = img.crop((left, top, right, bottom))
    except Exception as e:
        raise Exception(f"Error processing image: {e}")
    return img_cropped

async def generate_image(name, hobbies, zone, image_url, output_path):

    hobbies = str(hobbies).upper() if hobbies else ""
    zone = str(zone).upper() if zone else ""

    try:
        extra_image = await download_and_crop_image(drive_url=image_url)
        extra_image = extra_image.resize((481, 480))
    except Exception as e:
        raise Exception(f"Error generating image {e}")

    image = base_image.copy()
    draw = ImageDraw.Draw(image)
    draw.text(name_position, name, fill="black", font=font)
    draw.text(hobbies_position, hobbies, fill="black", font=font)
    draw.text(zone_position, zone, fill="black", font=font)
    image.paste(extra_image, extra_image_position, extra_image.convert('RGBA'))
    image.save(output_path)
