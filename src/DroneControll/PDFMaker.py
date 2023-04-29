# importing modules
import csv
import datetime

from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table

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
    time_spent = 0
    starting_time = 0
    distance = 0
    f_dist = 0
    difference_between_tracks = 0
    date_today = datetime.datetime.now().date()
    current_phase = 0

    # Training phase
    train_time = 0
    train_dist = 0
    train_f_dist = 0
    training_map = None  # Map - list of csv

    # Real phase
    real_time = 0
    real_dist = 0
    real_f_dist = 0
    real_map = None  # Map - list of csv

    # Freestyle 1 phase
    frees1_time = 0
    frees1_dist = 0
    free_style_1_map = None  # Map - list of csv

    # Freestyle 2 phase
    frees2_time = 0
    frees2_dist = 0
    free_style_2_map = None  # Map - list of csv

    def __init__(self, id_number, name, has_license, adhd, has_flight_experience):
        self.id_number = id_number
        self.name = name
        self.has_license = has_license
        self.adhd = adhd
        self.has_flight_experience = has_flight_experience

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
    def update_phase(self, num, current_map):
        if num == 1:
            self.current_phase = 1
            self.train_time = self.time_spent
            self.train_dist = self.distance
            self.train_f_dist = self.f_dist
            self.training_map = current_map
            self.reset_timer()

        if num == 2:
            self.current_phase = 2
            self.real_time = self.time_spent
            self.real_dist = self.distance
            self.real_f_dist = self.f_dist
            self.real_map = current_map
            self.reset_timer()

        if num == 3:
            self.current_phase = 3
            self.frees1_time = self.time_spent
            self.frees1_dist = self.time_spent
            self.free_style_1_map = current_map
            self.reset_timer()

        if num == 4:
            self.current_phase = 4
            self.frees2_time = self.time_spent
            self.frees2_dist = self.time_spent
            self.free_style_2_map = current_map
            self.reset_timer()

    def map_plotter(image_path, coordinates_path):
        # Load the image
        # image_path = "map_v2.png"
        image = Image.open(image_path)

        # OPTION A -
        # Load the coordinates
        # coordinates = [(100, 200), (300, 400), (500, 600)]

        # OPTION B -
        # # Load the coordinates from a CSV file
        coordinates = []
        with open(str(coordinates_path)) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                coordinates.append((int(row[0]), int(row[1])))

        # Draw red points on the image with the given coordinates
        draw = ImageDraw.Draw(image)
        point_size = 13
        for coord in coordinates:
            draw.ellipse((coord[0] - point_size, coord[1] - point_size, coord[0] + point_size, coord[1] + point_size),
                         fill="red")

        # Save the image with the red points drawn
        # output_path = "output.png"
        # image.save(output_path)
        return image

    def generate_pdf(self):
        # initializing variables with values
        file_name = str(self.id_number) + '_' + str(self.date_today) + '.pdf'
        # Each image[1..4] turns the input CSV to a plotted image
        # image1 = self.map_plotter(self.training_map)
        # image2 = self.map_plotter(self.real_map)
        # image3 = self.map_plotter(self.free_style_1_map)
        # image4 = self.map_plotter(self.free_style_2_map)
        # Define the data for the subtitles and images
        data = {
            'date': str(self.date_today),
            'name': str(self.name),
            'id_number': str(self.id_number),
            'has_license': str(self.has_license),
            'has_adhd': str(self.adhd),
            'has_flight_experience': str(self.has_flight_experience),
            'images': ['image1.jpg', 'image2.jpg', 'image3.jpg', 'image4.jpg']
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

        # Create a list of Flowable objects
        flowables = []

        space = '&nbsp;' * 30
        # Date and license
        flowables.append(
            Paragraph('Date:&nbsp;' + data['date'] + space + 'Has license:&nbsp;' + str(data['has_license']),
                      text_style))
        flowables.append(Spacer(1, 0.5 * inch))

        # Name and ADHD
        flowables.append(
            Paragraph('Name:&nbsp;' + data[
                'name'] + space + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Has ADHD:&nbsp;' + str(data['has_adhd']),
                      text_style))
        flowables.append(Spacer(1, 0.5 * inch))

        # ID number and flight experience
        flowables.append(Paragraph(
            'ID:&nbsp;&nbsp;' + data[
                'id_number'] + space + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Has flight experience (remote):&nbsp;' + str(
                data['has_flight_experience']), text_style))
        flowables.append(Spacer(1, 0.5 * inch))
        # Training and Real headings
        flowables.append(
            Paragraph(('&nbsp;' * 20) + '<b>Training - short</b>' + ('&nbsp;' * 40) + '<b>Real - long</b>', text_style))
        flowables.append(Spacer(1, 0.2 * inch))

        # Create a list of lists for the images and data
        image_data = [
            [Image(data['images'][0], width=2.5 * inch, height=2.5 * inch),
             Image(data['images'][1], width=2.5 * inch, height=2.5 * inch)],
            [Paragraph('time - ' + str(self.train_time) + '\n\ndist - ' + str(self.train_dist) + '\n\n f.dist - ' + str(
                self.train_f_dist), text_style),
             Paragraph('time - ' + str(self.real_time) + '\n\ndist - ' + str(self.real_dist) + '\n\nf.dist - ' + str(
                 self.real_f_dist), text_style)]
        ]
        flowables.append(Table(image_data, colWidths=[3 * inch, 3 * inch]))

        flowables.append(Spacer(1, 0.5 * inch))

        # Free1 and Free2 headings
        flowables.append(Paragraph(space + '<b>Free1</b>' + ('&nbsp;' * 50) + '<b>Free2</b>', text_style))
        flowables.append(Spacer(1, 0.2 * inch))

        # Create a list of lists for the images and data
        image_data = [
            [Image(data['images'][2], width=2.5 * inch, height=2.5 * inch),
             Image(data['images'][3], width=2.5 * inch, height=2.5 * inch)],
            [Paragraph('time - ' + str(self.frees1_time) + '\ndist - ' + str(self.frees1_dist), text_style),
             Paragraph('time - ' + str(self.frees2_time) + '\ndist - ' + str(self.frees2_dist), text_style)]
        ]
        flowables.append(Table(image_data, colWidths=[3 * inch, 3 * inch]))
        doc = SimpleDocTemplate(file_name, pagesize=letter)
        doc.build(flowables)


'''
How to call - 
1) initialize object - id_number, name, has_license, adhd, has_flight_experience
2) update_timer - time_spent, start_time, distance
3) update_phase - num of phase from 1 to 4

if __name__ == '__main__':
    x = PDFMaker(204355846, "OHAD", "Yes", "No", "Maybe")

    x.generate_pdf()
'''