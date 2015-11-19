import tingbot
from tingbot import *
import feedparser
from urlparse import urlparse
import os
import urllib
from HTMLParser import HTMLParser

class ImgExtractor(HTMLParser):
    def __init__(self, *args, **kwargs):
        self.images = []
        HTMLParser.__init__(self, *args, **kwargs)

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            # ignore the tracking pixels
            attrs_dict = dict(attrs)
            if attrs_dict['height'] == '1':
                return

            self.images.append(attrs_dict['src'])


def truncate(string, max_chars=36):
    return (string[:max_chars-3] + '...') if len(string) > max_chars else string

imgur_rss_url = 'http://feeds.feedburner.com/itsnicethat/SlXC'
state = {}

@every(minutes=10)
def refresh_feed():
    posts = []
    d = feedparser.parse(imgur_rss_url)
    
    for entry in d['entries']:
        post = {}
        post['title'] = entry['title']

        content = entry['summary']

        img_extractor = ImgExtractor()
        img_extractor.feed(content)

        if len(img_extractor.images) == 0:
            continue

        post['image_url'] = img_extractor.images[0]
        post['author'] = entry['author']

        posts.append(post)

        if len(posts) >= 10:
            continue

    state['posts'] = posts

    download_images()

    state['index'] = 0

def download_images():
    for post in state['posts']:
        url = post['image_url']
        filename = '/tmp/int-' + os.path.basename(urlparse(url).path)

        if not os.path.exists(filename):
            print 'Downloading image %s' % filename
            urllib.urlretrieve(url, filename)

        post['image'] = Image.load(filename)

@every(seconds=10)
def next_post():
    if 'posts' not in state:
        return

    posts = state['posts']
    state['index'] += 1

    if state['index'] >= len(posts):
        state['index'] = 0

def loop():
    if 'posts' not in state:
        screen.fill(color='white')
        screen.image('logo.png', scale=0.6)
        screen.text(
            'Loading...',
            xy=(160, 180),
            font_size=12,
            color='black',
        )
        return

    post = state['posts'][state['index']]
    image = post['image']

    width_sf = 320.0 / image.size[0]
    height_sf = 190.0 / image.size[1]

    sf = max(width_sf, height_sf)

    screen.fill(color='white')
    screen.image(
        image,
        xy=(160, 95),
        scale=sf)

    screen.rectangle(
        color='white',
        size=(320, 50),
        align='bottom',

    )
    screen.image(
        'minilogo.png',
        xy=(10, 231),
        align='bottomleft',
    )
    screen.text(
        truncate(post['title']),
        align='left',
        xy=(52, 222),
        color='black',
        font_size=14,
        font='OpenSans-Semibold.ttf',
    )
    screen.text(
        post['author'],
        align='left',
        xy=(52, 205),
        color='grey',
        font_size=10,
        font='OpenSans-Semibold.ttf',
    )

# run the app
tingbot.run(loop)
