# Initial Author: Zhihan Li 2024-03-06
# Modified by: Liam Clink

import matplotlib.pyplot as plt  # import matplotlib library
from drawnow import drawnow
from pyfirmata import Arduino, util
import time
from thermocouples_reference import thermocouples
import os
import pandas as pd


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


Temp3 = []
Temp5 = []
typeK = thermocouples["K"]
plt.ion()  # Tell matplotlib you want interactive mode to plot live data
cnt = 0
os.chdir("C:\\Users\\spmuser\\Desktop")

OBJ_temp = pd.DataFrame(columns=["Time", "Romm_ref_temp", "OBJ_port_pin3_temp"])
OBJ_temp.to_csv("OBJ_Temperature monitor.csv", index=False, na_rep="Unknown")

STM_head_temp = pd.DataFrame(columns=["Time", "Romm_ref_temp", "STM head_pin5_temp"])
STM_head_temp.to_csv("STM_head_Temperature monitor.csv", index=False, na_rep="Unknown")


# Read voltages on analog pin number 5
board = Arduino("COM3")
analog_opamp_pin = board.get_pin("a:5:i")

it = util.Iterator(board)
it.start()
Time = []
Time_elapse = []
elapse = []

if os.path.exists("pin5.csv"):
    os.remove("pin5.csv")
if os.path.exists("pin3.csv"):
    os.remove("pin3.csv")

i = 0
j = 0
while True:
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

    VTCLL = analog_opamp_pin.read()  # stm head
    start_time = time.time()
    time_point = start_time

    if i > 0 and 20 != None:
        Time.append(time_point)
        print("TC5:", VTCLL)
        TC_VTCLL = (VTCLL + 0.00444) * 5 * 1000 / 37
        Tref = 20
        temp3 = 0

        Temp3.append(temp3)  # Build our tempF array by appending temp readings
        temp5 = typeK.inverse_CmV(TC_VTCLL, Tref=20.0)

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
