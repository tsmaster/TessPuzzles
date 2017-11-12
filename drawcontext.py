from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


class DrawContext:
    def __init__(self, filename, widthInInches, heightInInches, pdf=True, svg=True):
        self.filename = filename
        self.pdfCanvas = None
        if pdf:
            self.pdfCanvas = canvas.Canvas(filename+".pdf",
                                           pagesize=(widthInInches * inch + inch,
                                                     heightInInches * inch + inch))
            self.pdfCanvas.translate(0.5 * inch,
                                     0.5 * inch)
        else:
            self.pdfCanvas = None
            
        if svg:
            # TODO set this up
            self.svgCanvas = None
        else:
            self.svgCanvas = None

    def save(self):
        if self.pdfCanvas:
            self.pdfCanvas.save()
        if self.svgCanvas:
            self.svgCanvas.save()

    def beginPath(self):
        if self.pdfCanvas:
            self.pdfPath = self.pdfCanvas.beginPath()
        if self.svgCanvas:
            pass

        return PathContext(self, self.pdfPath)

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
        if self.pdfCanvas:
            self.pdfCanvas.setStrokeColorRGB(r, g, b)
        if self.svgCanvas:
            # TODO
            pass

    def setFillColorRGB(self, r, g, b):
        if self.pdfCanvas:
            self.pdfCanvas.setFillColorRGB(r, g, b)
        if self.svgCanvas:
            # TODO
            pass


class PathContext:
    def __init__(self, drawContext, pdfPath):
        self.drawContext = drawContext
        self.pdfPath = pdfPath

    def moveTo(self, x, y):
        self.pdfPath.moveTo(x * inch, y * inch)

    def lineTo(self, x, y):
        self.pdfPath.lineTo(x * inch, y * inch)
        
