# importing modules
import csv
import datetime

from PIL import ImageDraw
import PIL.Image as PilImage
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from datetime import datetime

'''
Option one - ugly function
params[0] = name
params[1] = id
params[2] = has license
params[3] = has adhd
params[4] = starting time
params[5] = has flight experience (remote)
params[6] = time spent
params[7] = distance
params[8] = difference between tracks
params[9] = drawing of map
params[10] = drawing of map
params[11] = drawing of map
params[12] = drawing of map

Option two - object
'''


class PDFMaker:
    STAGE_NOT_IN_GAME = "not_in_game"
    STAGE_TRAINING = "training"
    STAGE_MAIN_PATH = "main"
    STAGE_FREE_STYLE_1 = "free1"
    STAGE_FREE_STYLE_2 = "free2"

    time_spent = 0
    starting_time = 0
    distance = 0
    f_dist = 0
    difference_between_tracks = 0
    date_today = "{:%Y:%m:%d %H:%M}".format(datetime.now())
    current_phase = 0

    # Training phase
    train_time = 0
    train_dist = 0
    train_f_dist = 0

    # Real phase
    real_time = 0
    real_dist = 0
    real_f_dist = 0

    # Freestyle 1 phase
    frees1_time = 0
    frees1_dist = 0

    # Freestyle 2 phase
    frees2_time = 0
    frees2_dist = 0

    def __init__(self, folder_name, user_name, age, gender, has_license, has_flight_experience, adhd):

        self.folder_name = folder_name
        self.free_style_2_path = None
        self.free_style_1_path = None
        self.real_user_path = None
        self.train_user_path = None
        self.real_optimal_path = None
        self.train_optimal_path = None
        self.id_number = user_name
        self.age = age
        self.gender = gender
        self.has_license = has_license
        self.has_flight_experience = has_flight_experience
        self.adhd = adhd

    # reset the current distances and times
    def reset_timer(self):
        self.time_spent = 0
        self.starting_time = 0
        self.distance = 0

    def update_timer(self, time_spent, start_time, distance):
        self.time_spent = time_spent
        self.starting_time = start_time
        self.distance = distance

    # At the end of each phase -> use function -> save current time and stats -> reset timer
    def update_phase(self, stage, time, distance, fr_distance, optimal_path, user_path):
        if stage == self.STAGE_TRAINING:
            # self.current_phase = 1
            self.train_time = time
            self.train_dist = distance
            self.train_f_dist = fr_distance
            self.train_optimal_path = optimal_path
            self.train_user_path = user_path
            self.reset_timer()

        if stage == self.STAGE_MAIN_PATH:
            # self.current_phase = 2
            self.real_time = time
            self.real_dist = distance
            self.real_f_dist = fr_distance
            self.real_optimal_path = optimal_path
            self.real_user_path = user_path
            self.reset_timer()

        if stage == self.STAGE_FREE_STYLE_1:
            # self.current_phase = 3
            self.frees1_time = time
            self.frees1_dist = distance
            self.free_style_1_path = user_path
            self.reset_timer()

        if stage == self.STAGE_FREE_STYLE_2:
            # self.current_phase = 4
            self.frees2_time = time
            self.frees2_dist = distance
            self.free_style_2_path = user_path
            self.reset_timer()

    def map_plotter(self, stage, user_path, optimal_path):
        # Load the image
        image_path = "SavedPaths//map_v2.png"
        image = PilImage.open(image_path)

        # Draw red points on the image with the given coordinates
        draw = ImageDraw.Draw(image)

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
        output_path = "img_" + stage + ".png"
        image.save(self.folder_name + output_path)

    def generate_pdf(self):
        # initializing variables with values
        file_name = str(self.id_number) + '_' + str(self.date_today) + '.pdf'
        # Each image[1..4] turns the input CSV to a plotted image
        self.map_plotter("training", self.train_user_path, self.train_optimal_path)
        self.map_plotter("main", self.real_user_path, self.real_optimal_path)
        self.map_plotter("free1", self.free_style_1_path, None)
        self.map_plotter("free2", self.free_style_2_path, None)
        # Define the data for the subtitles and images
        data = {
            'date': str(self.date_today),
            'id_number': str(self.id_number),
            'age': str(self.age),
            'gender': str(self.gender),
            'has_license': str(self.has_license),
            'has_flight_experience': str(self.has_flight_experience),
            'has_adhd': str(self.adhd),
            'images': [self.folder_name + "img_training.png", self.folder_name + "img_main.png",
                       self.folder_name + "img_free1.png", self.folder_name + "img_free2.png"]
        }

        # Define the styles for the subtitles and text
        title_style = ParagraphStyle(
            name='Title',
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=14,
            textColor=colors.black,
            alignment=TA_LEFT
        )
        text_style = ParagraphStyle(
            name='Text',
            fontName='Helvetica',
            fontSize=12,
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

        table_style_img = TableStyle(
            [('ALIGN', (1, 1), (-1, -1), 'CENTER')]
        )

        space_width = 0.15

        # Create a list of Flowable objects
        flowables = []

        text_data = [
            ["Name: " + data['id_number'], "Date: " + data['date']],
            ["Age/Gender: " + data['age'] + "/" + data['gender'], "Driving license: " + data['has_license']],
            ["ADHD: " + data['has_adhd'], "Flying exp.: " + data['has_flight_experience']]
        ]
        flowables.append(Table(text_data, colWidths=[4 * inch, 2 * inch], style=table_style))

        track_info_space = '&nbsp;' * 2

        flowables.append(Spacer(1, 0.3 * inch))

        # Training and Real headings
        flowables.append(
            Paragraph(('&nbsp;' * 10) + '<b>Training - short</b>' + ('&nbsp;' * 65) + '<b>Real - long</b>', text_style))
        flowables.append(Spacer(1, 0.1 * inch))

        # Create a list of lists for the images and data
        image_size = 3.8

        image_data = [
            [Image(data['images'][0], width=image_size * inch, height=image_size * inch),
             Image(data['images'][1], width=image_size * inch, height=image_size * inch)],
            [Paragraph('Time : ' + str(self.train_time) + "s "+track_info_space + ' Dist : ' + str(self.train_dist) + track_info_space + 'F.Dist : ' + str(
                self.train_f_dist), text_style),
             Paragraph('Time : ' + str(self.real_time) + "s "+track_info_space + ' Dist : ' + str(self.real_dist) + track_info_space + 'F.Dist : ' + str(
                 self.real_f_dist), text_style)]
        ]
        flowables.append(Table(image_data, colWidths=[4 * inch, 4 * inch], style=table_style_img))

        flowables.append(Spacer(1, 0.2 * inch))

        # Free1 and Free2 headings
        flowables.append(Paragraph(('&nbsp;' * 15) + '<b>Free1</b>' + ('&nbsp;' * 80) + '<b>Free2</b>', text_style))
        flowables.append(Spacer(1, 0.1 * inch))

        # Create a list of lists for the images and data
        image_data = [
            [Image(data['images'][2], width=image_size * inch, height=image_size * inch),
             Image(data['images'][3], width=image_size * inch, height=image_size * inch)],
            [Paragraph('Time : ' + str(self.frees1_time) + "s " + track_info_space + 'Dist : ' + str(self.frees1_dist), text_style),
             Paragraph('Time : ' + str(self.frees2_time) + "s " + track_info_space + 'Dist : ' + str(self.frees2_dist), text_style)]
        ]
        flowables.append(Table(image_data, colWidths=[4 * inch, 4 * inch], style=table_style_img))
        doc = SimpleDocTemplate(self.folder_name + file_name, pagesize=A4, showBoundary=0, topMargin=inch * 0.25)
        doc.build(flowables)


'''
How to call - 
1) initialize object - id_number, name, has_license, adhd, has_flight_experience
2) update_timer - time_spent, start_time, distance
3) update_phase - num of phase from 1 to 4
'''

if __name__ == '__main__':
    x = PDFMaker("../", 204355846, 20, "f", "No", "yes", "yes")

    x.update_phase("training", 10, 10, 10, [[10, 10, 10], [10, 10, 10]], [[10, 10, 10], [10, 10, 10]])
    x.update_phase("main", 10, 10, 10, [[10, 10, 10], [10, 10, 10]], [[10, 10, 10], [10, 10, 10]])
    x.update_phase("free1", 10, 10, 10, [[10, 10, 10], [10, 10, 10]], [[10, 10, 10], [10, 10, 10]])
    x.update_phase("free2", 10, 10, 10, [[10, 10, 10], [10, 10, 10]], [[10, 10, 10], [10, 10, 10]])

    x.generate_pdf()
