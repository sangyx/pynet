import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# 随机字母:
def rndChar():
    return chr(random.randint(65, 90))

# 随机颜色1:
def rndColor():
    return (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))

# 随机颜色2:
def rndColor2():
    return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))

def get_rnd(w=30, h=60):
    rnd = ''
    # 240 x 60:
    width = w * 4
    height = h
    image = Image.new('RGB', (width, height), (255, 255, 255))
    # 创建Font对象:
    font = ImageFont.truetype('arial.ttf', 36)
    # 创建Draw对象:
    draw = ImageDraw.Draw(image)
    # 填充每个像素:
    for x in range(width):
        for y in range(height):
            draw.point((x, y), fill=rndColor())
    # 输出文字:
    for t in range(4):
        rc = rndChar()
        draw.text((30 * t + 10, 10), rc, font=font, fill=rndColor2())
        rnd += rc
    # 模糊:
    image = image.filter(ImageFilter.BLUR)
    image.save('code.png')
    # 将字符串转为小写返回
    return rnd.lower()