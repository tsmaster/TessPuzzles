from reportlab.pdfgen import canvas
from reportlab.lib.units import inch as pdfInch
import svgwrite
from svgwrite import inch as svgInch

import os

import bdggeom

SVG_EDGE_WIDTH = "0.01mm"
# to test
#SVG_EDGE_WIDTH = "0.5mm"

class DrawContext:
    def __init__(self, filename, outputdir, widthInInches, heightInInches, pdf=True, svg=True):
        self.filename = filename
        self.outputdir = outputdir
        self.pdfCanvas = None
        self.heightInInches = heightInInches
        self.widthInInches = widthInInches
        self.strokeColor = (0, 0, 0)
        if pdf:
            self.pdfCanvas = canvas.Canvas(os.path.join(outputdir, filename+".pdf"),
                                           pagesize=(widthInInches * pdfInch + pdfInch,
                                                     heightInInches * pdfInch + pdfInch))
            self.pdfCanvas.translate(0.5 * pdfInch,
                                     0.5 * pdfInch)
        else:
            self.pdfCanvas = None
            
        if svg:
            self.svgCanvas = svgwrite.drawing.Drawing(filename=os.path.join(outputdir, filename+".svg"),
                                                      size=(widthInInches * svgInch,
                                                            heightInInches * svgInch))
        else:
            self.svgCanvas = None


    def save(self):
        if self.pdfCanvas:
            self.pdfCanvas.save()
        if self.svgCanvas:
            self.svgCanvas.save()

    def beginPath(self):
        self.pdfPath = None

        if self.pdfCanvas:
            self.pdfPath = self.pdfCanvas.beginPath()

        return PathContext(self, self.pdfPath, bdggeom.Vec2f(0,0))

    def drawPath(self, pathContext):
        if self.pdfCanvas:
            self.pdfCanvas.drawPath(pathContext.pdfPath, stroke = 1)
        if self.svgCanvas:
            #TODO
            pass

    def drawFilledPath(self, pathContext):
        if self.pdfCanvas:
            self.pdfCanvas.drawPath(pathContext.pdfPath, fill = 1)
        if self.svgCanvas:
            #TODO
            pass

    def setStrokeColorRGB(self, r, g, b):
        self.strokeColor = (r, g, b)
        if self.pdfCanvas:
            self.pdfCanvas.setStrokeColorRGB(r, g, b)

    def setFillColorRGB(self, r, g, b):
        if self.pdfCanvas:
            self.pdfCanvas.setFillColorRGB(r, g, b)
        if self.svgCanvas:
            # TODO
            pass

    def svgColor(self, r, g, b):
        """ r,g,b are all within 0-1 """
        return svgwrite.utils.rgb(r=int(r * 255),
                                  g=int(g * 255),
                                  b=int(b * 255))

    def drawSVGLine(self, vec1, vec2):
        if not self.svgCanvas:
            return

        self.svgCanvas.add(self.svgCanvas.line(start = (vec1.x * svgInch,
                                                        (self.heightInInches - vec1.y) * svgInch),
                                               end = (vec2.x * svgInch,
                                                      (self.heightInInches - vec2.y) * svgInch),
                                               stroke = self.svgColor(*self.strokeColor),
                                               fill = "none",
                                               stroke_width = SVG_EDGE_WIDTH))


class PathContext:
    def __init__(self, drawContext, pdfPath, startVec):
        self.drawContext = drawContext
        self.pdfPath = pdfPath
        self.position = startVec

    def moveTo(self, x, y):
        if not (self.pdfPath is None):
            self.pdfPath.moveTo(x * pdfInch, y * pdfInch)
        self.position = bdggeom.Vec2f(x, y)

    def lineTo(self, x, y):
        if not (self.pdfPath is None):
            self.pdfPath.lineTo(x * pdfInch, y * pdfInch)
        newPosn = bdggeom.Vec2f(x,y)
        self.drawContext.drawSVGLine(self.position, newPosn)
        self.position = newPosn
        
