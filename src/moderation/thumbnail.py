import os
from PIL import Image as Img
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile


from moderation.models import Moderator, Image



def divide_chunks(l, n): 
            # looping till length l 
            for i in range(0, len(l), n):  
                yield l[i:i + n]


def generate_thumbnail():
    moderators_qs = Moderator.objects.filter(public=True)
    moderators = [moderator.socialuser.profile.normalavatar.path for moderator in moderators_qs]
    if not moderators:
        return
    
    width, height = Img.open(moderators[0]).size
    images = [Img.open(img) for img in moderators]
    n = len(images)
    w=7
    h=n/w
    if n/w == n//w:
        h=n/w
    else:
        h=(n//w)+1
    total_width = w*width
    total_height = h*height
    thumbnail = Img.new('RGB', (total_width, total_height))
    x_offset = 0
    y_offset = 0
    for chunk in divide_chunks(images, w):
        for img in chunk:
            thumbnail.paste(img, (x_offset,y_offset))
            x_offset += img.size[0]
        y_offset += img.size[1]
        x_offset = 0
    
    f = BytesIO()
    thumbnail.save(f, format='JPEG')
    image_instance, _ = Image.objects.get_or_create(name="moderators")
    image_instance.img.save('moderators.jpg',
                       InMemoryUploadedFile(f,
                                            None,
                                            'moderators.jpeg',
                                            'image/jpeg',
                                            f.seek(0,os.SEEK_END),
                                            None)
    )
    f.close()
    return image_instance.img.url
    
def get_thumbnail_url():
    try:
        thumbnail = Image.objects.get(name="moderators")
    except Image.DoesNotExist:
        return generate_thumbnail()

    return thumbnail.img.url