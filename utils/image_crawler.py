from urlparse import urlparse, urljoin
import base64
from bs4 import BeautifulSoup

''' download the image from the article '''

IMAGE_PREFIX = "/static/download-image/"
IMAGE_DOWNLOAD_FOLDER = ""


def get_absolute_url(article_url, image_url):
    urlcomponent = urlparse(article_url)
    host = urlcomponent.netloc

    image_url = image_url.strip()

    if image_url.startswith("http://") \
        or image_url.startswith("https://"):
        return image_url

    if image_url.startswith("/"):
        return host + image_url

    return urljoin(article_url, image_url)

def get_name(url):
    name = base64.b64encode(url)
    dot_index = url.rfind('.')
    question_mark_index = url.rfind('?')
    if(question_mark_index > dot_index):
        return name + url[dot_index:question_mark_index]
    return name + url[dot_index:]

## this is export to use
def change_image(article):
    soup = BeautifulSoup(article.content)

    ## ''.join(soup.body.contents)
    for img in soup.find_all('img'):
        src = img.get('src', None)
        if src:
            absolute_url = get_absolute_url(article.original_url, src)
            name = get_name(absolute_url)
            img['src'] = IMAGE_PREFIX + name
            # download image

    article.content = ''.join(map(str, soup.body.contents))
    article.save()



def download_image(image_url, new_name):
    pass







