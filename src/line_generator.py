import copy
import math
import random
import sys
import numpy as np

from PIL import Image
from PIL import ImageDraw

BLACK = (0, 0, 0, 255)
LINES = 30
QUALITY = 95
INPUT_NAME = "Me.png"
OUTPUT_DIRECTORY = "/home/mintyque/evolution"
OUTPUT_NAME = "result"
MUTATION = 4


class Line(object):
    def __init__(self, color=None, points=[]):
        self.color = color
        self.points = points

    def mutate(self, size):
        rand = random.random()
        if rand <= 0.5:
            idx = random.randrange(0, 4)
            value = random.randrange(0, 256)
            color = list(self.color)
            color[idx] = value
            self.color = tuple(color)
        else:
            idx = random.randrange(0, 2)
            point = generate_point(size)
            self.points[idx] = point


class DNA(object):
    def __init__(self, img_width, cur_line, lines=[]):
        self.img_width = img_width
        self.cur_line = cur_line
        self.lines = lines

    def mutate(self):
        lines = copy.deepcopy(self.lines)
        rand = random.randrange(0, len(lines)//MUTATION)
        for i in range(rand):
            rand_ind = random.randrange(0, len(lines))
            random_line = lines[rand_ind]
            random_line.mutate(self.img_width)
        return DNA(self.img_width, self.cur_line, lines)

    def draw(self, background=BLACK):
        size = (self.img_width, 1)
        img = Image.new('RGB', size, background)
        draw = Image.new('RGBA', size)
        pdraw = ImageDraw.Draw(draw)
        for line in self.lines:
            color = line.color
            points = line.points
            pdraw.line(points, fill=color, width=1)
            img.paste(draw, mask=draw)
        return img


class Result(object):
    def __init__(self, img_size, rows=[]):
        self.img_size = img_size
        self.rows = rows

    def display(self):
        size = self.img_size
        img = Image.new('RGB', size, BLACK)
        draw = Image.new('RGBA', size)
        pdraw = ImageDraw.Draw(draw)
        offset = -1
        for row in self.rows:
            offset += 1
            for line in row.lines:
                color = line.color
                points = line.points
                point_a = list(points[0])
                point_b = list(points[1])
                point_a[1] += offset
                point_b[1] += offset
                points = (tuple(point_a), tuple(point_b))
                pdraw.line(points, fill=color, width=1)
                img.paste(draw, mask=draw)
        out_path = "{}/{}.png".format(OUTPUT_DIRECTORY, OUTPUT_NAME)
        img.save(out_path)
        print("saving image to {}".format(out_path))

    def add_row(self, row):
        self.rows.append(row)


def fitness(pixels, dna_img):
    diff = 0.0
    dna_pixels = get_line(dna_img)
    for i in range(0, len(pixels)):
        pixel = pixels[i]
        r1 = pixel[0]
        g1 = pixel[1]
        b1 = pixel[2]
        dna_pixel = dna_pixels[i]
        r2 = dna_pixel[0]
        g2 = dna_pixel[1]
        b2 = dna_pixel[2]
        d_r = r1 - r2
        d_g = g1 - g2
        d_b = b1 - b2
        pixel_diff = math.sqrt(d_r * d_r + d_g * d_g + d_b * d_b)
        diff += pixel_diff
    max_diff = len(pixels) * 440
    fit = (1 - diff/max_diff) * 100
    return fit


def generate_point(width):
    x = random.randrange(0, width, 1)
    y = 0
    return x, y


def generate_color():
    red = random.randrange(0, 256)
    green = random.randrange(0, 256)
    blue = random.randrange(0, 256)
    alpha = random.randrange(0, 256)
    return red, green, blue, alpha


def generate_dna(img_width, cur_line):
    lines = []
    width = img_width

    for i in range(LINES):
        points = []
        point_1 = generate_point(width)
        point_2 = generate_point(width)
        points.append(point_1)
        points.append(point_2)
        color = generate_color()
        line = Line(color, points)
        lines.append(line)

    dna = DNA(width, cur_line, lines)
    return dna


def load_image(path):
    img = Image.open(path)
    img = img.convert('RGB')
    return img


def get_line(img, idx=0):
    width = img.size[0]
    pixels = np.zeros(width, dtype=tuple)
    for i in range(0, width):
        pixels[i] = img.getpixel((i, idx))
    return pixels


def main():
    img = load_image(INPUT_NAME)
    print("Image loaded")
    img_size = img.size
    img_width = img_size[0]
    result = Result(img_size)
    print("Starting to generate")
    for i in range(img_width):
        dna = generate_dna(img_width, i)
        in_row = get_line(img, dna.cur_line)
        parent = dna.draw()
        fitness_parent = fitness(in_row, parent)
        count = 1
        while fitness_parent < QUALITY:
            dna_mutated = dna.mutate()
            child = dna_mutated.draw()
            fitness_child = fitness(in_row, child)
            if fitness_child > fitness_parent:
                dna = dna_mutated
                fitness_parent = fitness_child
            count += 1
        print("row {} took {} operations".format(i, count))
        result.add_row(dna)
    result.display()
    return sys.exit(0)


if __name__ == "__main__":
    main()
