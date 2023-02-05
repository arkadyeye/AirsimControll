# importing modules
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors


class ExportData:
    #             parameters = (self.user_name, self.age, self.gender, self.driving_license,
    #                           self.flying_experience, self.time_train, self.time_finished)

    def exp_data(self, parameters):
        # initializing variables with values
        fileName = parameters[0] + '_report.pdf'
        documentTitle = 'Report'
        title = parameters[0] + ' report'
        subTitle = 'The largest thing now!!'
        textLines = [
            'Name = '+ parameters[0],
            'Age = ' + parameters[1],
            'Gender '+ parameters[2],
            'Driving License = ' + parameters[3],
            'Flying Experience = ' + parameters[4],
            'Training Time  = ' + parameters[5],
            'Real Time  = ' + parameters[6]
        ]
        #image = 'image.jpg'

        # creating a pdf object
        pdf = canvas.Canvas(fileName)

        # setting the title of the document
        pdf.setTitle(documentTitle)

        # registering a external font in python
        pdfmetrics.registerFont(TTFont('TNR', 'times.ttf'))

        # creating the title by setting it's font
        # and putting it on the canvas
        pdf.setFont('TNR', 36)
        pdf.drawCentredString(300, 770, title)

        # creating the subtitle by setting it's font,
        # colour and putting it on the canvas
        pdf.setFillColorRGB(0, 0, 255)
        pdf.setFont("Courier-Bold", 24)
        pdf.drawCentredString(290, 720, subTitle)

        # drawing a line
        pdf.line(30, 710, 550, 710)

        # creating a multiline text using
        # textline and for loop
        text = pdf.beginText(40, 680)
        text.setFont("Courier", 18)
        text.setFillColor(colors.red)
        for line in textLines:
            text.textLine(line)
        pdf.drawText(text)

        # drawing a image at the
        # specified (x.y) position
        #pdf.drawInlineImage(image, 130, 400)

        # saving the pdf
        pdf.save()
