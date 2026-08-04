import random
import numpy as np

# "resistances" stores the ideal values and stays unchanged during running
resistances = [[8, 14, 100, 14], [20, 14, 20, 20], [100, 14, 8, 14], [100, 100, 100, 6]]
# "new_resistances" stores the randomized resistance values for each loop of running
new_resistances = [[9, 20, 100, 20], [20, 11, 20, 20], [100, 20, 9, 20], [100, 100, 100, 7]]
num_correct = 0     # total number of outputs correctly categorized
num_perfect = 0.0       # number of loops that had perfect accuracy

loop = 10000     # number of loops you want the program to run
k = 0
while k < loop:
    # for each resistance value, find a random value within 10% of it
    # to simulate how WRV works on actual devices
    i = 0
    while i < 4:
        j = 0
        while j < 4:
            min = resistances[i][j] * 0.9
            max = resistances[i][j] * 1.1
            new_resistances[i][j] = random.uniform(min, max)
            j += 1
        i += 1

    # all expected input combinations and proper output for each one
    # sensor order: left, middle, right, us
    training_situations = np.array([[0.0, 0.0, 200, 0.0],
                                    [0.0, 200, 0.0, 0.0],
                                    [0.0, 200, 200, 0.0],
                                    [200, 0.0, 0.0, 0.0],
                                    [200, 200, 0.0, 0.0],
                                    [200, 200, 200, 0.0],
                                    [0.0, 0.0, 0.0, 200],
                                    [0.0, 0.0, 200, 200],
                                    [0.0, 200, 0.0, 200],
                                    [0.0, 200, 200, 200],
                                    [200, 0.0, 0.0, 200],
                                    [200, 200, 0.0, 200],
                                    [200, 200, 200, 200]], dtype=np.float32)
    # output order: left, straight, right, stop
    training_labels = np.array([2, 1, 2, 0, 0, 1, 3, 3, 3, 3, 3, 3, 3], dtype=np.int32)

    # perform VMM for each input across the matrix of resistance values
    i = 0
    while i < 13:
        left = training_situations[i][0]
        middle = training_situations[i][1]
        right = training_situations[i][2]
        us = training_situations[i][3]

        goLeft = (left / new_resistances[0][0]) + (middle / new_resistances[1][0]) + (right / new_resistances[2][0]) + (us / new_resistances[3][0]);
        goStraight = (left / new_resistances[0][1]) + (middle / new_resistances[1][1]) + (right / new_resistances[2][1]) + (us / new_resistances[3][1]);
        goRight = (left / new_resistances[0][2]) + (middle / new_resistances[1][2]) + (right / new_resistances[2][2]) + (us / new_resistances[3][2]);
        goStop = (left / new_resistances[0][3]) + (middle / new_resistances[1][3]) + (right / new_resistances[2][3]) + (us / new_resistances[3][3]);

        # if the correct column has the highest value, add to the num_correct count
        if(training_labels[i] == 0 and goLeft > goStraight and goLeft > goRight and goLeft > goStop):
            num_correct += 1
            num_perfect += 1.0 / 13.0
        elif(training_labels[i] == 1 and goStraight > goLeft and goStraight > goRight and goStraight > goStop):
            num_correct += 1
            num_perfect += 1.0 / 13.0
        elif(training_labels[i] == 2 and goRight > goLeft and goRight > goStraight and goRight > goStop):
            num_correct += 1
            num_perfect += 1.0 / 13.0
        elif(training_labels[i] == 3 and goStop > goLeft and goStop > goStraight and goStop > goRight):
            num_correct += 1
            num_perfect += 1.0 / 13.0
        # otherwise, let us know one was incorrect
        else:
            print("incorrect: ", i)
            # print(new_resistances)
        i += 1
    if num_perfect % 1 > 0.99:
        num_perfect = np.ceil(num_perfect)
    else:
        num_perfect = np.floor(num_perfect)
    k += 1

print("Accuracy: " + str(num_correct / (13.0 * loop)))
print("% with perfect accuracy: " + str(num_perfect / loop))
