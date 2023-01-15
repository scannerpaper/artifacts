# coding: utf-8
"""
    captcha.image
    ~~~~~~~~~~~~~

    Generate Image CAPTCHAs, just the normal image CAPTCHAs you are using.
"""

import os
import random
from PIL import Image
from PIL import ImageFilter
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype
import numpy as np

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO
try:
    from wheezy.captcha import image as wheezy_captcha
except ImportError:
    wheezy_captcha = None

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
DEFAULT_FONTS = [os.path.join(DATA_DIR, 'DroidSansMono.ttf')]

if wheezy_captcha:
    __all__ = ['ImageCaptcha', 'WheezyCaptcha']
else:
    __all__ = ['ImageCaptcha']


table  =  []
for  i  in  range( 256 ):
    table.append( int(i * 2.5) )


class _Captcha(object):
    def generate(self, chars, format='png'):
        """Generate an Image Captcha of the given characters.

        :param chars: text to be generated.
        :param format: image file format
        """
        im = self.generate_image(chars)
        out = BytesIO()
        im.save(out, format=format)
        out.seek(0)
        return out

    def write(self, chars, output, format='png'):
        """Generate and write an image CAPTCHA data to the output.

        :param chars: text to be generated.
        :param output: output destination.
        :param format: image file format
        """
        im = self.generate_image(chars)
        return im.save(output, format=format)


class WheezyCaptcha(_Captcha):
    """Create an image CAPTCHA with wheezy.captcha."""
    def __init__(self, width=200, height=75, fonts=None):
        self._width = width
        self._height = height
        self._fonts = fonts or DEFAULT_FONTS

    def generate_image(self, chars):
        text_drawings = [
            wheezy_captcha.warp(),
            wheezy_captcha.rotate(),
            wheezy_captcha.offset(),
        ]
        fn = wheezy_captcha.captcha(
            drawings=[
                wheezy_captcha.background(),
                wheezy_captcha.text(fonts=self._fonts, drawings=text_drawings),
                wheezy_captcha.curve(),
                wheezy_captcha.noise(),
                wheezy_captcha.smooth(),
            ],
            width=self._width,
            height=self._height,
        )
        return fn(chars)


class ImageCaptcha(_Captcha):
    """Create an image CAPTCHA.

    Many of the codes are borrowed from wheezy.captcha, with a modification
    for memory and developer friendly.

    ImageCaptcha has one built-in font, DroidSansMono, which is licensed under
    Apache License 2. You should always use your own fonts::

        captcha = ImageCaptcha(fonts=['/path/to/A.ttf', '/path/to/B.ttf'])

    You can put as many fonts as you like. But be aware of your memory, all of
    the fonts are loaded into your memory, so keep them a lot, but not too
    many.

    :param width: The width of the CAPTCHA image.
    :param height: The height of the CAPTCHA image.
    :param fonts: Fonts to be used to generate CAPTCHA images.
    :param font_sizes: Random choose a font size from this parameters.
    """
    def __init__(self, width=160, height=60, fonts=None, font_sizes=None):
        self._width = width
        self._height = height
        self._fonts = fonts or DEFAULT_FONTS
        self._font_sizes = font_sizes or (42, 50, 56)
        self._truefonts = []

    @property
    def truefonts(self):
        if self._truefonts:
            return self._truefonts
        self._truefonts = tuple([
            truetype(n, s)
            for n in self._fonts
            for s in self._font_sizes
        ])
        return self._truefonts

    @staticmethod
    def create_noise_curve(image, color, count=1, max_thickness=10):
        w, h = image.size
        for _ in range(count):
            color = random_color(0, 200, random.randint(220, 255))
            x1 = random.randint(0, w // 2)
            x2 = random.randint(w // 2 + 1, w)
            y1 = random.randint(0, h - 1)
            y2 = random.randint(y1 + 1, h)
            thickness = random.randint(1, max_thickness)
            points = [x1, y1, x2, y2]
            end = random.randint(0, 359)
            start = random.randint(0, 359)
            Draw(image).arc(points, start, end, fill=color, width=thickness)
        return image

    @staticmethod
    def create_noise_dots(image, color, width=3, number=30):
        draw = Draw(image)
        w, h = image.size
        while number:
            x1 = random.randint(0, w)
            y1 = random.randint(0, h)
            draw.line(((x1, y1), (x1 - 1, y1 - 1)), fill=color, width=width)
            number -= 1
        return image

    def create_captcha_image(self, chars, color, background, return_bbox=False):
        """Create the CAPTCHA image itself.

        :param chars: text to be generated.
        :param color: color of the text.
        :param background: color of the background.

        The color should be a tuple of 3 numbers, such as (0, 255, 255).
        """
        # image = Image.new('RGB', (self._width, self._height), background)
        image = self.generate_background(background[0], background[1])
        draw = Draw(image)

        def _draw_character(c):
            font = random.choice(self.truefonts)
            w, h = draw.textsize(c, font=font)

            # dx = random.randint(0, 4)
            # dy = random.randint(0, 6)
            im = Image.new('RGBA', (w, h))
            color = random_color(0, 200, random.randint(220, 255))
            Draw(im).text((0, 0), c, font=font, fill=color)

            # rotate
            im = im.crop(im.getbbox())
            im = im.rotate(random.uniform(-30, 30), Image.BILINEAR, expand=1)

            # warp
            dx = w * random.uniform(0.1, 0.3)
            dy = h * random.uniform(0.2, 0.3)
            x1 = int(random.uniform(-dx, dx))
            y1 = int(random.uniform(-dy, dy))
            x2 = int(random.uniform(-dx, dx))
            y2 = int(random.uniform(-dy, dy))
            w2 = w + abs(x1) + abs(x2)
            h2 = h + abs(y1) + abs(y2)
            data = (
                x1, y1,
                -x1, h2 - y2,
                w2 + x2, h2 + y2,
                w2 - x2, -y1,
            )
            im = im.resize((w2, h2))
            im = im.transform((w, h), Image.QUAD, data)
            im = im.crop(im.getbbox())
            return im

        images = []
        is_chars = []
        for c in chars:
            # if random.random() > 0.5:
            #     is_chars.append(False)
            #     images.append(_draw_character(" "))
            is_chars.append(True)
            images.append(_draw_character(c))

        text_width = sum([im.size[0] for im in images])

        width = max(text_width, self._width)
        image = image.resize((width, self._height))
        offset_ratio = width / text_width

        average = int(text_width / len(chars))
        # rand = int(0.25 * average)
        offset = int(average * 0.1)

        bboxes = []
        for im, is_char in zip(images, is_chars):
            w, h = im.size
            y = int((self._height - h) / 2)
            y = y + random.randint(-y // 2, y // 2)
            # mask = im.convert('L')#.point(table)
            # mask = np.asarray(mask)
            # mask = (mask / np.percentile(mask, 90) * 255).clip(0, 255).astype('uint8')
            # mask = Image.fromarray(mask)
            mask = im.getchannel('A')
            # x = int(offset * offset_ratio)
            x = offset
            image.paste(im, (x, y), mask=mask)
            if is_char:
                bboxes.append([x, y, w, h])
            offset = offset + w + random.randint(0, w // 3)

        if width > self._width:
            image = image.resize((self._width, self._height))
            r = self._width / width
            for bbox in bboxes:
                bbox[0] = int(r * bbox[0])
                bbox[2] = int(r * bbox[2])

        if return_bbox:
            return image, bboxes
        else:
            return image

    def generate_image(self, chars, return_bbox=False):
        """Generate the image of the given characters.

        :param chars: text to be generated.
        """
        background1 = random_color(238, 255)
        background2 = random_color(50, 255)
        background = (background1, background2)
        color = random_color(0, 200, random.randint(220, 255))
        im = self.create_captcha_image(chars, color, background, return_bbox=return_bbox)
        if return_bbox:
            im, bbox = im
        # self.create_noise_dots(im, color, number=60)
        # self.create_noise_curve(im, color, 10, 3)
        # im = im.filter(ImageFilter.SMOOTH)
        if return_bbox:
            return im, bbox
        else:
            return im

    def generate_background(self, color1, color2):
        if random.random() > 0.5:
            color1, color2 = color2, color1
        
        color = np.linspace(color1, color2, self._width).astype(np.uint8)
        image = np.tile(color, (self._height, 1, 1))
        image = Image.fromarray(image)
        return image


def random_color(start, end, opacity=None):
    red = random.randint(start, end)
    green = random.randint(start, end)
    blue = random.randint(start, end)
    if opacity is None:
        return (red, green, blue)
    return (red, green, blue, opacity)
