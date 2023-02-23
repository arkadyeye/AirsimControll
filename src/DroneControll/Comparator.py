'''
in this class i want to compare 2 csv files
and give a mark to the difference between them
'''
import numpy as np
import matplotlib.image as mpimg

a_x = []
a_y = []
a_z = []


path_a=""
path_b=""


#load first csv
from csv import reader
import similaritymeasures
import matplotlib.pyplot as plt
# open file in read mode
counter = 0

PathA = "SavedPaths\\long_path_optimal.csv"
PathB = "D:\\Git\\AirsimControll\\2023_02_23_11_38_51_Ark_test_optimal_real\\path.csv"

with open(PathA, 'r') as read_obj:
    # pass the file object to reader() to get the reader object
    csv_reader = reader(read_obj)
    header = next(csv_reader)
    header = next(csv_reader)
    # Iterate over each row in the csv using reader object
    for row in csv_reader:
        # row variable is a list that represents a row in csv
        # print(row)
        a_x.append(row[1])
        a_y.append(row[2])
        a_z.append(row[3])
        counter += 1

exp_data = np.zeros((counter, 3))
exp_data[:, 0] = a_x
exp_data[:, 1] = a_y
exp_data[:, 2] = a_z

print(exp_data)

a_x = []
a_y = []
a_z = []
counter = 0
with open(PathB, 'r') as read_obj:
    # pass the file object to reader() to get the reader object
    csv_reader = reader(read_obj)
    header = next(csv_reader)
    header = next(csv_reader)
    # Iterate over each row in the csv using reader object
    for row in csv_reader:
        # row variable is a list that represents a row in csv
        # print(row)
        a_x.append(row[1])
        a_y.append(row[2])
        a_z.append(row[3])
        counter += 1

ref_data = np.zeros((counter, 3))
ref_data[:, 0] = a_x
ref_data[:, 1] = a_y
ref_data[:, 2] = a_z

print(ref_data)

df = similaritymeasures.frechet_dist(exp_data, ref_data)
print ("df: ",df)

# dtw, d = similaritymeasures.dtw(exp_data, ref_data)
# print ("dtw: ",dtw)
# print ("d: ",d)
#plt.ion()

plt.figure()
plt.plot(ref_data[:, 0], ref_data[:, 1])
plt.plot(exp_data[:, 0], exp_data[:, 1])


fig, ax = plt.subplots()
plt.imshow(mpimg.imread('../1000_map.png'))
circle = plt.Circle((500, 500), 5, color='r')

plt.scatter(500 + ref_data[:, 0]*500/127, 500 + ref_data[:, 1]*500/127,s = 10)
plt.scatter(500 + exp_data[:, 0]*500/127, 500 + exp_data[:, 1]*500/127,s = 5)

# Saves to PDF
plt.savefig('map_plot.pdf')
plt.show()

#input("Press Enter to continue...")