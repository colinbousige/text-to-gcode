#!/usr/bin/python3
#pylint: disable=no-member

from enum import Enum
import os
import math
import argparse
import numpy as np

class Instr:
    class Type(Enum):
        move = 0,
        write = 1,

    def __init__(self, *args):
        if len(args) == 1 and type(args[0]) is str: # args must be a data str
            attributes = args[0].split(' ')
            # G_ X__ Y__
            self.type = Instr.Type.move if attributes[0][1] == '0' else Instr.Type.write
            self.x = float(attributes[1][1:])
            self.y = float(attributes[2][1:])
        elif len(args) == 3 and type(args[0]) is Instr.Type and type(args[1]) is float and type(args[2]) is float:
            self.type, self.x, self.y = args
        else:
            raise TypeError("Instr() takes one (str) or three (Instr.Type, float, float) arguments")

    def __repr__(self):
        return "G%d X%.2f Y%.2f" % (self.type.value[0], self.x, self.y)

    def translated(self, x, y):
        return Instr(self.type, self.x + x, self.y + y)

class Letter:
    def __init__(self, *args):
        if len(args) == 1 and type(args[0]) is str:
            self.instructions = []
            for line in args[0].split('\n'):
                if line != "":
                    self.instructions.append(Instr(line))

            pointsOnX = [instr.x for instr in self.instructions]
            self.width = max(pointsOnX) - min(pointsOnX)
        elif len(args) == 2 and type(args[0]) is list and type(args[1]) is float:
            self.instructions = args[0]
            self.width = args[1]
        else:
            raise TypeError("Letter() takes one (str) or two (list, float) arguments")

    def __repr__(self):
        return "\n".join([repr(instr) for instr in self.instructions]) + "\n"

    def translated(self, x, y):
        return Letter([instr.translated(x, y) for instr in self.instructions], self.width)


def readLetters(directory):
    letters = {
        " ": Letter([], 4.0),
        "\n": Letter([], math.inf)
    }
    for root,_,filenames in os.walk(directory):
        for filename in filenames:
            file = open(os.path.join(root,filename),"r")
            letterRepr = file.readline()[1]
            letter = Letter(file.read())
            letters[letterRepr] = letter
    return letters


def reverse(mylet):
    stext = mylet.split("\n")[:-1]
    rtext = np.flip(stext)
    return("\n".join(rtext)+"\n")


def repeat(mylet, N, baseline=0):
    if mylet != "\n":
        out = mylet
        if N > 1:
            i = 1
            while i < N:
                if i % 2 == 1:
                    out += reverse(mylet)
                else:
                    out += mylet
                i += 1
        gs = out.split("\n")[:-1]
        g, x, y, c = [], [], [], []
        for i in range(len(gs)):
            if len(gs[i].split(" ")) == 4:
                gg, xx, yy, cc = gs[i].split(" ")
                g.append(gg)
                x.append(float(xx.replace("X", "")))
                y.append(float(yy.replace("Y", "")))
                c.append(cc)
        x = np.array(x)
        y = np.array(y)
        return(f"G0 X{min(x):.5f} Y{baseline:.5f} {c[0]}\n{out}G0 X{max(x):.5f} Y{baseline:.5f} {c[0]}\n")
    else:
        return(mylet)


def textToGcode(letters, text, lineLength, lineSpacing, padding, N=1, baseline=0):
    # used for fast string concatenation
    gcodeLettersArray = []

    offsetX, offsetY = 0, 0
    for char in text:
        letter = letters[char].translated(offsetX, offsetY)
        mylet = repr(letter).replace("\n", f" #{char}\n")
        if char != " ":
            if char != "\n":
                gcodeLettersArray.append(repeat(mylet, N, baseline + offsetY))
        else:
            gcodeLettersArray.append(mylet)

        offsetX += letter.width + padding
        if offsetX >= lineLength:
            offsetX = 0
            offsetY -= lineSpacing

    return "".join(gcodeLettersArray)


def parseArgs(namespace):
    argParser = argparse.ArgumentParser(fromfile_prefix_chars="@",
        description="Compiles text into 2D gcode for plotters")

    argParser.add_argument_group("Data options")
    argParser.add_argument("-i", "--input", type=argparse.FileType('r'), default="-", metavar="FILE",
        help="File to read characters from")
    argParser.add_argument("-o", "--output", type=argparse.FileType('w'), required=True, metavar="FILE",
        help="File in which to save the gcode result")
    argParser.add_argument("-g", "--gcode-directory", type=str, default="./ascii_gcode/", metavar="DIR",
        help="Directory containing the gcode information for all used characters")

    argParser.add_argument_group("Text options")
    argParser.add_argument("-l", "--line-length", type=float, required=True,
        help="Maximum length of a line")
    argParser.add_argument("-s", "--line-spacing", type=float, default=8.0,
        help="Distance between two subsequent lines")
    argParser.add_argument("-p", "--padding", type=float, default=1.5,
        help="Empty space between characters")

    argParser.parse_args(namespace=namespace)

def main():
    class Args: pass
    parseArgs(Args)

    letters = readLetters(Args.gcode_directory)
    data = Args.input.read()
    gcode = textToGcode(letters, data, Args.line_length, Args.line_spacing, Args.padding)
    Args.output.write(gcode)


if __name__ == '__main__':
    main()
