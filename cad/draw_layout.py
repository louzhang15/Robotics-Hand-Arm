"""Draw a 2D layout schematic; does not evaluate or validate OpenSCAD geometry."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'generated'
OUT.mkdir(exist_ok=True)
im = Image.new('RGB', (1440, 1160), '#f4f6f8')
d = ImageDraw.Draw(im)
font_path = 'C:/Windows/Fonts/segoeui.ttf'
title = ImageFont.truetype(font_path, 38)
body = ImageFont.truetype(font_path, 23)
small = ImageFont.truetype(font_path, 19)
ox, oy, s = 100, 190, 5


def rect(x, y, w, h, fill, outline='#536273', width=2):
    d.rectangle((ox+x*s, oy+y*s, ox+(x+w)*s, oy+(y+h)*s),
                fill=fill, outline=outline, width=width)


def circle(x, y, radius, fill, outline='#536273'):
    d.ellipse((ox+(x-radius)*s, oy+(y-radius)*s,
               ox+(x+radius)*s, oy+(y+radius)*s), fill=fill, outline=outline, width=2)


d.text((100, 42), 'Seven-servo bench integration concept', font=title, fill='#13283d')
d.text((100, 96), '2D layout schematic | unmeasured defaults | not an OpenSCAD render', font=body, fill='#a8441c')
rect(0, 0, 248, 156, '#d2d9df')
rect(1, 48, 38, 60, '#e99a70')
circle(20, 78, 10, '#f4f6f8')
for dx in [-12, 12]:
    for dy in [-22, 22]:
        circle(20+dx, 78+dy, 1.8, '#f4f6f8')
positions = [(62,37),(62,119),(114,37),(114,119),(166,37),(166,119),(218,78)]
for i, (x,y) in enumerate(positions):
    rect(x-21,y-33,42,66,'#b6d8e7')
    rect(x-11,y-30.75,22,10,'#4295b6')
    rect(x-11,y+20.75,22,10,'#4295b6')
    rect(x-9.85,y-20.35,19.7,40.7,'#3b4d5c')
    circle(x,y+10.15,17,'#eac272')
    for bx in [-16,16]:
        for by in [-29,29]:
            circle(x+bx,y+by,1.8,'#f4f6f8')
    d.text((ox+(x-17)*s,oy+(y-20)*s),f'C{i+1}',font=small,fill='#f8fbfe')
# Dimension labels and scale: physical dimensions, not screen scale.
d.line((ox,oy-28,ox+248*s,oy-28),fill='#536273',width=2)
for xx in [ox,ox+248*s]:
    d.line((xx,oy-36,xx,oy-20),fill='#536273',width=2)
d.text((ox+106*s,oy-65),'248 mm',font=body,fill='#13283d')
d.text((100,1004),'Replaceable service adapter: 20 mm cable opening; elbow bearing and clevis pending.',font=body,fill='#13283d')
d.text((100,1044),'Blue = removable cartridge  |  dark = servo case  |  amber = pulley clearance envelope',font=small,fill='#536273')
d.text((100,1080),'Wide bench layout. Tendon routing, loaded mechanics, mass and print fit remain unverified.',font=small,fill='#a8441c')
im.save(OUT/'forearm-layout-schematic.png')
print(OUT/'forearm-layout-schematic.png')
