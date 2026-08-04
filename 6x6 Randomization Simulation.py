import random
import numpy as np

# "resistances" stores the ideal values and stays unchanged during running
resistances = [[20, 30, 56, 100, 100, 56], [56, 20, 30, 56, 30, 30], [100, 56, 10, 56, 56, 20],
               [100, 100, 30, 20, 100, 30], [56, 56, 56, 56, 30, 56], [100, 100, 100, 100, 100, 8]]
# "new_resistances" stores the randomized resistance values for each loop of running
new_resistances = [[20, 30, 56, 100, 100, 56], [56, 20, 30, 56, 30, 30], [100, 56, 10, 56, 56, 20],
               [100, 100, 30, 20, 100, 30], [56, 56, 56, 56, 30, 56], [100, 100, 100, 100, 100, 8]]
num_correct = 0     # total number of outputs correctly categorized
num_perfect = 0.0       # number of loops that had perfect accuracy

loop = 10000     # number of loops you want the program to run
k = 0
while k < loop:
    # for each resistance value, find a random value within 10% of it
    # to simulate how WRV works on actual devices
    i = 0
    while i < 6:
        j = 0
        while j < 6:
            min = resistances[i][j] * 0.9
            max = resistances[i][j] * 1.1
            new_resistances[i][j] = random.uniform(min, max)
            j += 1
        i += 1

    # all expected input combinations and proper output for each one
    # sensor order: LMS, LS, MS, RS, RMS, US
    training_situations = np.array([[0.0, 0.0, 0.0, 0.0, 200, 0.0],
                                    [0.0, 0.0, 0.0, 200, 0.0, 0.0],
                                    [0.0, 0.0, 0.0, 200, 200, 0.0],
                                    [0.0, 0.0, 200, 0.0, 0.0, 0.0],
                                    [0.0, 0.0, 200, 200, 0.0, 0.0],
                                    [0.0, 0.0, 200, 200, 200, 0.0],
                                    [0.0, 200, 0.0, 0.0, 0.0, 0.0],
                                    [0.0, 200, 200, 0.0, 0.0, 0.0],
                                    [0.0, 200, 200, 200, 0.0, 0.0],
                                    [0.0, 200, 200, 200, 200, 0.0],
                                    [200, 0.0, 0.0, 0.0, 0.0, 0.0],
                                    [200, 200, 0.0, 0.0, 0.0, 0.0],
                                    [200, 200, 200, 0.0, 0.0, 0.0],
                                    [200, 200, 200, 200, 0.0, 0.0],
                                    [200, 200, 200, 200, 200, 0.0],
                                    [0.0, 0.0, 0.0, 0.0, 0.0, 200],
                                    [0.0, 0.0, 0.0, 0.0, 200, 200],
                                    [0.0, 0.0, 0.0, 200, 0.0, 200],
                                    [0.0, 0.0, 0.0, 200, 200, 200],
                                    [0.0, 0.0, 200, 0.0, 0.0, 200],
                                    [0.0, 0.0, 200, 200, 0.0, 200],
                                    [0.0, 0.0, 200, 200, 200, 200],
                                    [0.0, 200, 0.0, 0.0, 0.0, 200],
                                    [0.0, 200, 200, 0.0, 0.0, 200],
                                    [0.0, 200, 200, 200, 0.0, 200],
                                    [0.0, 200, 200, 200, 200, 200],
                                    [200, 0.0, 0.0, 0.0, 0.0, 200],
                                    [200, 200, 0.0, 0.0, 0.0, 200],
                                    [200, 200, 200, 0.0, 0.0, 200],
                                    [200, 200, 200, 200, 0.0, 200],
                                    [200, 200, 200, 200, 200, 200]], dtype=np.float32)
    # output order: sharp left, left, straight, right, sharp right, stop
    # straight > sharp > regular
    # training_labels = np.array([4, 3, 4, 2, 2, 2, 1, 2, 2, 2, 0, 0, 2, 2, 2, 5, 5, 5,
    #                                 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5], dtype=np.int32)
    # straight > regular > sharp
    training_labels = np.array([4, 3, 3, 2, 2, 2, 1, 2, 2, 2, 0, 1, 2, 2, 2, 5, 5, 5,
                                    5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5], dtype=np.int32)
    # sharp > regular > straight
    # training_labels = np.array([4, 3, 4, 2, 3, 4, 1, 1, 2, 4, 0, 0, 0, 0, 2, 5, 5, 5,
    #                                 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5], dtype=np.int32)

    # perform VMM for each input across the matrix of resistance values
    i = 0
    while i < 31:
        sharpLeft = training_situations[i][0]
        left = training_situations[i][1]
        middle = training_situations[i][2]
        right = training_situations[i][3]
        sharpRight = training_situations[i][4]
        us = training_situations[i][5]

        goStop = (sharpLeft / new_resistances[0][0]) + (left / new_resistances[1][0]) + (middle / new_resistances[2][0]) + \
                (right / new_resistances[3][0]) + (sharpRight / new_resistances[4][0]) + (us / new_resistances[5][0]);
        goSharpLeft = (sharpLeft / new_resistances[0][1]) + (left / new_resistances[1][1]) + (middle / new_resistances[2][1]) + \
                (right / new_resistances[3][1]) + (sharpRight / new_resistances[4][1]) + (us / new_resistances[5][1]);
        goLeft = (sharpLeft / new_resistances[0][2]) + (left / new_resistances[1][2]) + (middle / new_resistances[2][2]) + \
                (right / new_resistances[3][2]) + (sharpRight / new_resistances[4][2]) + (us / new_resistances[5][2]);
        goStraight = (sharpLeft / new_resistances[0][3]) + (left / new_resistances[1][3]) + (middle / new_resistances[2][3]) + \
                (right / new_resistances[3][3]) + (sharpRight / new_resistances[4][3]) + (us / new_resistances[5][3]);
        goRight = (sharpLeft / new_resistances[0][4]) + (left / new_resistances[1][4]) + (middle / new_resistances[2][4]) + \
                (right / new_resistances[3][4]) + (sharpRight / new_resistances[4][4]) + (us / new_resistances[5][4]);
        goSharpRight = (sharpLeft / new_resistances[0][5]) + (left / new_resistances[1][5]) + (middle / new_resistances[2][5]) + \
                (right / new_resistances[3][5]) + (sharpRight / new_resistances[4][5]) + (us / new_resistances[5][5]);

        # if the correct column has the highest value, add to the num_correct count
        if(training_labels[i] == 0 and all(goStop > val for val in (goSharpLeft, goLeft, goStraight, goRight, goSharpRight))):
            num_correct += 1
            num_perfect += 1.0 / 31.0
        elif(training_labels[i] == 1 and all(goSharpLeft > val for val in (goStop, goLeft, goStraight, goRight, goSharpRight))):
            num_correct += 1
            num_perfect += 1.0 / 31.0
        elif(training_labels[i] == 2 and all(goLeft > val for val in (goStop, goSharpLeft, goStraight, goRight, goSharpRight))):
            num_correct += 1
            num_perfect += 1.0 / 31.0
        elif(training_labels[i] == 3 and all(goStraight > val for val in (goStop, goSharpLeft, goLeft, goRight, goSharpRight))):
            num_correct += 1
            num_perfect += 1.0 / 31.0
        elif(training_labels[i] == 4 and all(goRight > val for val in (goStop, goSharpLeft, goLeft, goStraight, goSharpRight))):
            num_correct += 1
            num_perfect += 1.0 / 31.0
        elif(training_labels[i] == 5 and all(goSharpRight > val for val in (goStop, goSharpLeft, goLeft, goStraight, goRight))):
            num_correct += 1
            num_perfect += 1.0 / 31.0
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

print("Accuracy: " + str(num_correct / (31.0 * loop)))
print("% with perfect accuracy: " + str(num_perfect / loop))