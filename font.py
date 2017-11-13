import bdggeom
import drawcontext

FEZ_STR = "Squdgy fez, blank jimp crwth vox!"
TV_STR = "Mr. Jock, TV quiz PhD, bags few lynx."
WALTZ_STR = "Waltz, nymph, for quick jigs vex Bud."
SPHINX_STR = "Sphinx of black quartz, judge my vow."
JUG_STR = "Pack my box with five dozen liquor jugs."
MAZE_STR = "10 PRINT CHR$(205.5 + RND(1));: GOTO 10"
HOME_STR = "There's No Place Like 127.0.0.1"
PYTHAG_STR = "111132^2 - 2002^2 = 123458769"
MULT_STR = "12 * 483 = 5796"


fontS2 = {
    'A': [0, 0, 0, 1, 1, 2, 2, 1, 2, 0, -1, 0, 1, 2, 1, -1],
    'B': [0, 1, 2, 1, 1, 0, 0, 0, 0, 2, 1, 2, 2, 1, -1],
    'C': [2, 2, 1, 2, 0, 1, 1, 0, 2, 0, -1],
    'D': [0, 2, 1, 2, 2, 1, 1, 0, 0, 0, 0, 2, -1],
    'E': [2, 2, 0, 2, 0, 0, 2, 0, -1, 0, 1, 1, 1, -1],
    'F': [2, 2, 0, 2, 0, 0, -1, 0, 1, 1, 1, -1],
    'G': [2, 2, 1, 2, 0, 1, 1, 0, 2, 0, 2, 1, 1, 1, -1],
    'H': [0, 2, 0, 0, -1, 0, 1, 2, 1, -1, 2, 2, 2, 0, -1],
    'I': [0, 2, 2, 2, -1, 1, 2, 1, 0, -1, 0, 0, 2, 0],
    'J': [2, 2, 2, 0, 1, 0, 0, 1],
    'K': [0, 2, 0, 0, -1, 0, 1, 1, 1, 2, 2, -1, 1, 1, 2, 0],
    'L': [0, 2, 0, 0, 2, 0],
    'M': [0, 0, 0, 2, 1, 1, 2, 2, 2, 0],
    'N': [0, 0, 0, 2, 2, 0, 2, 2],
    'O': [1, 2, 2, 1, 1, 0, 0, 1, 1, 2],
    'P': [0, 0, 0, 2, 1, 2, 2, 1, 0, 1],
    'Q': [1, 2, 2, 1, 1, 0, 0, 1, 1, 2, -1, 1, 1, 2, 0],
    'R': [0, 0, 0, 2, 1, 2, 2, 1, 0, 1, -1, 1, 1, 2, 0],
    'S': [2, 2, 1, 2, 0, 1, 2, 1, 1, 0, 0, 0],
    'T': [0, 2, 2, 2, -1, 1, 2, 1, 0],
    'U': [0, 2, 0, 0, 2, 0, 2, 2],
    'V': [0, 2, 0, 1, 1, 0, 2, 1, 2, 2],
    'W': [0, 2, 0, 0, 1, 1, 2, 0, 2, 2],
    'X': [0, 2, 2, 0, -1, 0, 0, 2, 2],
    'Y': [0, 2, 1, 1, 2, 2, -1, 1, 1, 1, 0],
    'Z': [0, 2, 2, 2, 0, 0, 2, 0],
    
    ' ': [-1],
    '.': [0.9, 0.1, 1.1, 0.1, 1.1, -0.1, 0.9, -0.1, 0.9, 0.1],
    ',': [0.9, 0.1, 1.1, 0.1, 1.1, -0.3, 0.9, -0.1, 0.9, 0.1],
    "'": [1, 1.5, 1, 2],
    '0': [2, 2, 0, 2, 0, 0, 2, 0, 2, 2, 0, 0],
    '1': [0, 1, 1, 2, 1, 0, -1, 0, 0, 2, 0],
    '2': [0, 1, 1, 2, 2, 1, 1, 1, 0, 0, 2, 0],
    '3': [0, 2, 2, 2, 1, 1, 2, 1, 1, 0, 0, 0],
    '4': [1, 2, 0, 1, 2, 1, -1, 2, 2, 2, 0],
    '5': [2, 2, 0, 2, 0, 1, 2, 1, 1, 0, 0, 0],
    '6': [2, 2, 1, 2, 0, 1, 0, 0, 2, 0, 2, 1, 0, 1],
    '7': [0, 2, 2, 2, 1, 1, 1, 0],
    '8': [2, 1, 2, 2, 0, 2, 0, 0, 2, 0, 2, 1, 0, 1],
    '9': [2, 1, 0, 1, 0, 2, 2, 2, 2, 0, 0, 0],
    '!': [1, 2, 1, 1, -1, 0.9, 0.1, 1.1, 0.1, 1.1, -0.1, 0.9, -0.1, 0.9, 0.1],
    '?': [0, 2, 2, 2, 1, 1, 0.9, 0.1, 1.1, 0.1, 1.1, -0.1, 0.9, -0.1, 0.9, 0.1],
    '@': [1, 1, 2, 1, 2, 2, 0, 2, 0, 0, 2, 0],
    '#': [0.4, 2, 0.4, 0, -1, 0.6, 2, 0.6, 0, -1, 0, 0.6, 2, 0.6, -1, 0, 0.4, 2, 0.4],
    '$': [2, 1.5, 0.5, 1.5, 0, 1, 2, 1, 1.5, 0.5, 0, 0.5, -1, 1, 2, 1, 0],
    '%': [0, 0, 2, 2, -1, 0, 2, 0.5, 2, 0.5, 1.5, 0, 1.5, 0, 2, -1, 2, 0, 1.5, 0, 1.5, 0.5, 2.0, 0.5, 2, 0],
    '^': [0, 1, 1, 2, 2, 1],
    '&': [2, 0, 0, 2, 1, 2, 0, 1, 0, 0, 2, 2],
    '*': [1, 2, 1, 0, -1, 0, 1.5, 2, 0.5, -1, 0, 0.5, 2, 1.5],
    '(': [1, 0, 0.5, 0.5, 0.5, 1.5, 1, 2],
    ')': [1, 0, 1.5, 0.5, 1.5, 1.5, 1, 2],
    '+': [1, 0.5, 1, 1.5, -1, 0.5, 1, 1.5, 1],
    '-': [0.5, 1, 1.5, 1],
    ':': [0.9, 1.6, 1.1, 1.6, 1.1, 1.4, 0.9, 1.4, 0.9, 1.6, -1,
          0.9, 0.6, 1.1, 0.6, 1.1, 0.4, 0.9, 0.4, 0.9, 0.6],
    ';': [0.9, 1.6, 1.1, 1.6, 1.1, 1.4, 0.9, 1.4, 0.9, 1.6, -1,
          0.9, 0.6, 1.1, 0.6, 1.1, 0.0, 0.9, 0.0, 0.9, 0.6],
    '=': [0.5, 0.5, 1.5, 0.5, -1,
          0.5, 1.5, 1.5, 1.5],
    '/': [0, 0, 2, 2],
    '\\': [0, 2, 2, 0],
    
    
    
}

def drawLetterToDrawContext(drawContext, char, font, posVec, height):
    penDown = False
    p = drawContext.beginPath()
    if not (char in font):
        return
    strokes = font[char]
    while strokes:
        i1 = strokes[0]
        if i1 == -1:
            penDown = False
            strokes=strokes[1:]
            continue
        i2 = strokes[1]
        strokes = strokes[2:]
        x = i1 * height + posVec.x
        y = i2 * height + posVec.y
        if penDown:
            p.lineTo(x,y)
        else:
            p.moveTo(x,y)
            penDown = True
    drawContext.drawPath(p)
    

def drawStringToDrawContext(drawContext, string, font, posVec, height):
    string = string.upper()
    for ci, char in enumerate(string):
        x = posVec.x + ci * 3 * height
        y = posVec.y
        charVec = bdggeom.Vec2f(x,y)
        drawLetterToDrawContext(drawContext, char, font, charVec, height)
    


def test_strings():
    c = drawcontext.DrawContext("testfont", ".", 8, 8)

    c.setStrokeColorRGB(1, 0, 0)

    drawStringToDrawContext(c, FEZ_STR,
                            fontS2,
                            bdggeom.Vec2f(0.5, 0.5),
                            0.05)

    drawStringToDrawContext(c, TV_STR,
                            fontS2,
                            bdggeom.Vec2f(0.5, 1.0),
                            0.05)

    drawStringToDrawContext(c, WALTZ_STR,
                            fontS2,
                            bdggeom.Vec2f(0.5, 1.5),
                            0.05)

    drawStringToDrawContext(c, SPHINX_STR,
                            fontS2,
                            bdggeom.Vec2f(0.5, 2.0),
                            0.05)

    drawStringToDrawContext(c, JUG_STR,
                            fontS2,
                            bdggeom.Vec2f(0.5, 2.5),
                            0.05)

    drawStringToDrawContext(c, MAZE_STR,
                            fontS2,
                            bdggeom.Vec2f(0.5, 3.0),
                            0.05)

    drawStringToDrawContext(c, HOME_STR,
                            fontS2,
                            bdggeom.Vec2f(0.5, 3.5),
                            0.05)
    
    drawStringToDrawContext(c, PYTHAG_STR,
                            fontS2,
                            bdggeom.Vec2f(0.5, 4.0),
                            0.05)
    
    drawStringToDrawContext(c, MULT_STR,
                            fontS2,
                            bdggeom.Vec2f(0.5, 4.5),
                            0.05)
                       

    c.save()


if __name__ == "__main__":
    test_strings()

