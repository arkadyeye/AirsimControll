from PIL import ImageDraw
import PIL.Image as PilImage
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from datetime import datetime


# Phase class which contains name,time,dist,f_dist
class Phase:
    img_path = ""  # The path of the image will be saved here

    # p stands for phase
    def __init__(self, current_phase, p_time, p_dist, p_f_dist, p_user_path, p_optimal_path):
        self.current_phase = current_phase  # Phase name
        self.p_time = p_time  # Phase time
        self.p_dist = p_dist  # Phase dist
        self.p_f_dist = p_f_dist  # Phase f_dist (can be none)
        self.p_user_path = p_user_path
        self.p_optimal_path = p_optimal_path  # Phase optimal path (can be none)


class PDFMaker:
    difference_between_tracks = 0
    date_today = "{:%Y:%m:%d %H:%M}".format(datetime.now())



    # List of phases
    phases = []

    def __init__(self, folder_name, user_name, age, gender, has_license, has_flight_experience, adhd):

        self.folder_name = folder_name
        self.id_number = user_name
        self.age = age
        self.gender = gender
        self.has_license = has_license
        self.has_flight_experience = has_flight_experience
        self.adhd = adhd



    # At the end of each phase -> use function -> save current time and stats -> reset timer
    def update_phase(self, stage, time, distance, fr_distance, optimal_path, user_path):
        self.phases.append(Phase(stage, time, distance, fr_distance, optimal_path, user_path))

    def map_plotter(self, stage, user_path, optimal_path):

        # Load the image
        image_path = "SavedPaths//map_v2_jpg.jpg"
        self.image = PilImage.open(image_path)

        # The resolution of each saved image, the lower, the less size it takes
        #size = (450, 450)  # Declare a resolution here
        #image = image.resize(size)  # Resize the image file

        # Draw red points on the image with the given coordinates
        draw = ImageDraw.Draw(self.image)

        if optimal_path is not None:
            point_size = 7
            for i in range(1, len(optimal_path)):
                x = 500 + optimal_path[i][0] * 500 / 127
                y = 500 + optimal_path[i][1] * 500 / 127

                draw.ellipse((x - point_size, y - point_size, x + point_size, y + point_size),
                             fill=str("orange"))

        if user_path is not None:
            point_size = 3
            for i in range(1, len(user_path)):
                x = 500 + user_path[i][0] * 500 / 127
                y = 500 + user_path[i][1] * 500 / 127

                draw.ellipse((x - point_size, y - point_size, x + point_size, y + point_size),
                             fill=str("blue"))

        # Save the image with the red points drawn
        output_path = "img_" + stage + ".jpg"
        self.image.save(self.folder_name + output_path)

    def generate_pdf(self):
        # initializing variables with values
        file_name = str(self.id_number) + '_report.pdf'
        # Each image[1...len(self.phases)] turns the input CSV to a plotted image
        for phase in self.phases:
            self.map_plotter(phase.current_phase, phase.p_user_path, phase.p_optimal_path)

        # Define the data for the subtitles and images
        for i in self.phases:
            i.img_path = self.folder_name + "img_" + i.current_phase + ".jpg"

        data = {
            'date': str(self.date_today),
            'id_number': str(self.id_number),
            'age': str(self.age),
            'gender': str(self.gender),
            'has_license': str(self.has_license),
            'has_flight_experience': str(self.has_flight_experience),
            'has_adhd': str(self.adhd),
        }

        # Define the styles for the subtitles and text
        title_style = ParagraphStyle(
            name='Title',
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=14,
            textColor=colors.black,
            alignment=TA_LEFT
        )
        text_style = ParagraphStyle(
            name='Text',
            fontName='Helvetica',
            fontSize=15,
            leading=12,
            textColor=colors.black,
            alignment=TA_LEFT
        )

        table_style = TableStyle(
            [('LINEABOVE', (0, 0), (-1, 0), 2, colors.green),
             ('LINEABOVE', (0, 1), (-1, -1), 0.25, colors.black),
             ('LINEBELOW', (0, -1), (-1, -1), 2, colors.green),
             ('FONTSIZE', (0, 0), (5, 5), 12),
             ('ALIGN', (0, 0), (-1, -1), 'LEFT')]
        )

        # Create a list of Flowable objects
        flowables = []

        text_data = [
            ["Name: " + data['id_number'], "Date: " + data['date']],
            ["Age/Gender: " + data['age'] + "/" + data['gender'], "Driving license: " + data['has_license']],
            ["ADHD: " + data['has_adhd'], "Flying exp.: " + data['has_flight_experience']]
        ]
        flowables.append(Table(text_data, colWidths=[4 * inch, 2 * inch], style=table_style))

        track_info_space = '&nbsp;' * 2
        flowables.append(Spacer(1, 9.5 * inch))

        # Iterates over each phase
        for phase in self.phases:
            # If phase have no f_dist (freestyle for instance)
            if phase.p_f_dist is None:
                time_dist_text = 'Time : ' + str(phase.p_time) + "s " + track_info_space + ' Dist : ' + str(
                    phase.p_dist)
            else:
                time_dist_text = 'Time : ' + str(phase.p_time) + "s " + track_info_space + ' Dist : ' + str(
                    phase.p_dist) + track_info_space + 'F.Dist : ' + str(phase.p_f_dist)

            tbl_data = [
                [flowables.append(Paragraph('&nbsp;' * 40 + '<b>' + phase.current_phase + '</b>', title_style))],
                [Image(phase.img_path, width=7.5 * inch, height=7.5 * inch)],
                [flowables.append(Spacer(1, 0.1 * inch))],
                [Paragraph(time_dist_text, text_style)]
            ]

            tbl = Table(tbl_data, colWidths=[4 * inch, 8 * inch])

            # Add some styling to the table
            tbl_style = TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 0),
                ('TOPPADDING', (0, -1), (-1, -1), 0),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER')
            ])
            tbl.setStyle(tbl_style)

            flowables.append(Spacer(1, 0.2 * inch))
            flowables.append(tbl)
            flowables.append(Spacer(1, 1.5 * inch))

        doc = SimpleDocTemplate(self.folder_name + file_name, pagesize=A4, showBoundary=0, topMargin=inch * 0.25)
        doc.build(flowables)


'''
How to call - 
1) initialize object - id_number, name, has_license, adhd, has_flight_experience
2) update_timer - time_spent, start_time, distance
3) update_phase - num of phase from 1 to 4


if __name__ == '__main__':
    x = PDFMaker("../", 123465, 20, "f", "No", "yes", "yes")

    x.update_phase("training", 10, 10, 10, [[10, 10, 10], [10, 10, 10]], [[10, 10, 10], [10, 10, 10]])
    x.update_phase("main", 10, 10, 10, [[10, 10, 10], [10, 10, 10]], [[10, 10, 10], [10, 10, 10]])
    x.update_phase("free1", 10, 10, None, [[10, 10, 10], [10, 10, 10]], [[10, 10, 10], [10, 10, 10]])
    x.update_phase("free2", 10, 10, 10, [[10, 10, 10], [10, 10, 10]], [[10, 10, 10], [10, 10, 10]])

    x.generate_pdf()
'''