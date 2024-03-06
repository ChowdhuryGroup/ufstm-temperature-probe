# Initial Author: Zhihan Li 2024-03-06

import serial  # import Serial Library
import numpy  # Import numpy
import matplotlib.pyplot as plt  # import matplotlib library
from drawnow import drawnow, figure
from pyfirmata import Arduino, util
import time
from thermocouples_reference import thermocouples
import datetime
from os import getcwd, chdir, startfile, makedirs
from os.path import realpath, exists, join, abspath, dirname
import os, sys
import pandas as pd

board = Arduino("COM3")


Temp3 = []
Temp5 = []
typeK = thermocouples["K"]
plt.ion()  # Tell matplotlib you want interactive mode to plot live data
cnt = 0
os.chdir("C:\\Users\\spmuser\\Desktop")
# os.makedirs('Baking_tempevolution_on_LUMINS')
# os.chdir('C:\\Users\\spmuser\\Desktop\\Baking_tempevolution_on_LUMINS')
# if os.path.exists('parts_temp.csv'):
# pass
# else:
OBJ_temp = pd.DataFrame(columns=["Time", "Romm_ref_temp", "OBJ_port_pin3_temp"])
OBJ_temp.to_csv("OBJ_Temperature monitor.csv", index=False, na_rep="Unknown")

STM_head_temp = pd.DataFrame(columns=["Time", "Romm_ref_temp", "STM head_pin5_temp"])
STM_head_temp.to_csv("STM_head_Temperature monitor.csv", index=False, na_rep="Unknown")


# axs[0,1].set_title('LL_Temperature monitor')      #Plot the title
# axs[0,1].grid(True)                                  #Turn the grid on
# axs[0,1].set_ylabel('Temp C')                            #Set ylabels
# axs[0,1].plot(Temp2, 'ro-', label='LL Temperature #2')       #plot the temperature
# axs[0,1].legend(loc='upper right')
# plt2=plt.twinx()                                #Create a second y axis
# plt2.plot(pressure, 'b^-', label='Pressure (Pa)') #plot pressure data
# plt2.set_ylabel('Pressrue (Pa)')                    #label second y axis
# plt2.ticklabel_format(useOffset=False)           #Force matplotlib to NOT autoscale y axis
# plt2.legend(loc='upper right')                  #plot the legend
def makeFig1():  # Create a function that makes our desired plot
    plt.subplot(211)
    plt.title("OBJ_Temperature monitor")  # Plot the title
    plt.grid(True)  # Turn the grid on
    plt.ylabel("Temp C")  # Set ylabels
    plt.plot(Time, Temp3, "ro-", label="OBJ Temperature pin#3")  # plot the temperature
    plt.legend(loc="upper right")
    plt.subplot(212)
    plt.title("STM head_Temperature monitor")  # Plot the title
    plt.grid(True)  # Turn the grid on
    plt.ylabel("Temp C")  # Set ylabels
    plt.xlabel("Time/s")
    plt.plot(
        Time, Temp5, "ro-", label="STM head Temperature pin#5"
    )  # plot the temperature
    plt.legend(loc="upper right")


i = 0
pin0 = board.get_pin("a:0:i")  # read the line of text from the serial port
pin3 = board.get_pin("a:3:i")  # read the line of text from the serial port
pin5 = board.get_pin("a:5:i")  # read the line of text from the serial port

it = util.Iterator(board)
it.start()
Time = []
Time_elapse = []
j = 0
elapse = []
if os.path.exists("pin5.csv"):
    os.remove("pin5.csv")
if os.path.exists("pin3.csv"):
    os.remove("pin3.csv")
while True:  # While loop that loops forever
    # while (board.inWaiting()==0): #Wait here until there is data
    # pass #do nothing

    time_point = time.time()
    Time_elapse.append(time_point)
    iteration_elapsed_time = time.time() - time_point
    if i >= 1:
        print(
            "time elaspse between two data points:", Time_elapse[i] - Time_elapse[i - 1]
        )

        # Adjust delay to achieve 25 readings per second
    time_to_wait = max(
        0, 1 / 2 - iteration_elapsed_time
    )  # Calculate time to wait until next reading
    time.sleep(time_to_wait)

    Vref = pin0.read()  # Convert first element to floating number and put in temp
    # print('TS0:',Vref)
    ##print(time.time())
    # print(type(V0))
    VTC = pin3.read()  # obj
    # -+#print('TC3:',VTC)
    VTCLL = pin5.read()  # stm head
    start_time = time.time()
    time_point = start_time

    # print('TC5:',VTCLL)
    if i > 0 and 20 != None:
        Time.append(time_point)
        # Tref=Vref*5*100
        # print(Tref)
        print("TC5:", VTCLL)
        # print('TC3:',VTC)
        # TC_VTC=VTC*5*1000/37
        TC_VTCLL = (VTCLL + 0.00444) * 5 * 1000 / 37
        Tref = 20
        # Tref1=20
        # temp3= typeK.inverse_CmV(TC_VTC,Tref=20.0)
        temp3 = 0
        # print('temp3:',temp3)
        # temp3=temp3-Tref+20 #set cold junction as 20C
        # print('temp_read_3',temp3)
        Temp3.append(temp3)  # Build our tempF array by appending temp readings
        temp5 = typeK.inverse_CmV(TC_VTCLL, Tref=20.0)
        # temp2=temp2-Tref+20 #set cold junction as 20C
        print("temp_read_5", temp5)
        Temp5.append(temp5)  # Build our tempF array by appending temp readings

        if j > 0:
            print("measure time elapse:", Time[j] - Time[j - 1])

        print(len(Time), len(Temp5))
        drawnow(makeFig1)

        if j != 0:
            elapse.append(elapse[j - 1] + Time[j] - Time[j - 1])
            temp_time_point_OBJ = pd.DataFrame(
                {
                    "Time/s": [elapse[j]],
                    "Cold junction temp/C": [Tref],
                    "obj_pin3_temp/C": [temp3],
                }
            )
            temp_time_point_OBJ.to_csv("pin3.csv", mode="a", index=False, header=False)
            temp_time_point_STM_head = pd.DataFrame(
                {
                    "Time/s": [elapse[j]],
                    "Cold junction_temp": [Tref],
                    "STM_head_pin5_temp/C": [temp5],
                }
            )
            temp_time_point_STM_head.to_csv(
                "pin5.csv", mode="a", index=False, header=False
            )
        else:
            elapse.append(0)
            temp_time_point_OBJ = pd.DataFrame(
                {
                    "Time/s": [0],
                    "Cold junction temp/C": [Tref],
                    "obj_pin3_temp/C": [temp3],
                }
            )
            temp_time_point_OBJ.to_csv("pin3.csv", mode="a", index=False, header=False)
            temp_time_point_STM_head = pd.DataFrame(
                {
                    "Time/s": [0],
                    "Cold junction_temp": [Tref],
                    "STM_head_pin5_temp/C": [temp5],
                }
            )
            temp_time_point_STM_head.to_csv(
                "pin5.csv", mode="a", index=False, header=False
            )

        j = j + 1

        # start_time = time.time()
        # plt.pause(.00001)                     #Pause Briefly. Important to keep drawnow from crashing

    i = i + 1
