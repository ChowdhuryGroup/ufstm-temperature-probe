# Initial Author: Zhihan Li 2024-03-06
# Modified by: Liam Clink

import matplotlib.pyplot as plt  # import matplotlib library
from drawnow import drawnow
from pyfirmata import Arduino, util
import time
from thermocouples_reference import thermocouples
import os
import pandas as pd


def makeFig1():
    # Makes real time plot of temperature data
    plt.subplot(211)
    plt.title("OBJ_Temperature monitor")  # Plot the title
    plt.grid(True)  # Turn the grid on
    plt.ylabel("Temp C")  # Set ylabels
    plt.plot(
        Time, pin_3_temperature_list, "ro-", label="OBJ Temperature pin#3"
    )  # plot the temperature
    plt.legend(loc="upper right")
    plt.subplot(212)
    plt.title("STM head_Temperature monitor")  # Plot the title
    plt.grid(True)  # Turn the grid on
    plt.ylabel("Temp C")  # Set ylabels
    plt.xlabel("Time/s")
    plt.plot(
        Time, pin_5_temperature_list, "ro-", label="STM head Temperature pin#5"
    )  # plot the temperature
    plt.legend(loc="upper right")


def pin_value_to_volts(pin_value: float) -> float:
    # Arduino analog pin measures 0-5V, and gives a value between 0 and 1
    return pin_value * 5.0


def opamp_correction(pin_value: float) -> float:
    # Takes voltage output by OpAmp measured by an arduino pin
    # and converts to what input voltage must've been in milliVolts
    offset_voltage = 0.0222
    gain_scale = 0.027

    return (pin_value_to_volts(pin_value) + offset_voltage) * gain_scale * 1000


pin_3_temperature_list = []
pin_5_temperature_list = []
typeK_thermocouple_reference = thermocouples["K"]
plt.ion()  # Tell matplotlib you want interactive mode to plot live data

OBJ_temp = pd.DataFrame(columns=["Time", "Romm_ref_temp", "OBJ_port_pin3_temp"])
OBJ_temp.to_csv("OBJ_Temperature monitor.csv", index=False, na_rep="Unknown")

STM_head_temp = pd.DataFrame(columns=["Time", "Romm_ref_temp", "STM head_pin5_temp"])
STM_head_temp.to_csv("STM_head_Temperature monitor.csv", index=False, na_rep="Unknown")


# Read voltages on analog pin number 5
board = Arduino("COM3")
pin_3 = board.get_pin("a:3:i")
pin_5 = board.get_pin("a:5:i")

# PyFirmata, which is being used to interface with the Arduino, for some reason calls
# the function that reads and handles data from the microcontroller over the serial port: board.iterate()
# This util.Iterator class is a child of threading.Thread that's used to repeatedly capture output from the serial port
it = util.Iterator(board)
it.start()
Time = []
time_point_list = []
elapse = []

if os.path.exists("pin5.csv"):
    os.remove("pin5.csv")
if os.path.exists("pin3.csv"):
    os.remove("pin3.csv")

i = 0
j = 0
Tref = 20
while True:
    time_point = time.time()
    time_point_list.append(time_point)
    iteration_elapsed_time = time.time() - time_point
    if i >= 1:
        print(
            "time elapsed between two data points:",
            time_point_list[i] - time_point_list[i - 1],
        )

    # Adjust delay to achieve 25 readings per second
    time_to_wait = max(
        0, 1 / 2 - iteration_elapsed_time
    )  # Calculate time to wait until next reading
    time.sleep(time_to_wait)

    pin_5_value = pin_5.read()
    start_time = time.time()
    time_point = start_time

    if i == 0:
        i += 1
        continue

    Time.append(time_point)
    print("Pin 5 Value [0-1]:", pin_5_value)
    pin_5_voltage = opamp_correction(pin_5_value)

    temp3 = 0
    pin_3_temperature_list.append(
        temp3
    )  # Build our tempF array by appending temp readings

    # inverse_CmV() converts mV to Celsius based on thermocouple type
    pin_5_temperature = typeK_thermocouple_reference.inverse_CmV(
        pin_5_voltage, Tref=20.0
    )
    print("Pin 5 Temperature (C)", pin_5_temperature)
    pin_5_temperature_list.append(
        pin_5_temperature
    )  # Build our tempF array by appending temp readings

    print(len(Time), len(pin_5_temperature_list))
    drawnow(makeFig1)

    if j != 0:
        print("measure time elapse:", Time[j] - Time[j - 1])
        elapse.append(elapse[j - 1] + Time[j] - Time[j - 1])
        temp_time_point_OBJ = pd.DataFrame(
            {
                "Time/s": [elapse[j]],
                "Cold junction temp/C": [Tref],
                "obj_pin3_temp/C": [temp3],
            }
        )
        temp_time_point_STM_head = pd.DataFrame(
            {
                "Time/s": [elapse[j]],
                "Cold junction_temp": [Tref],
                "STM_head_pin5_temp/C": [pin_5_temperature],
            }
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
        temp_time_point_STM_head = pd.DataFrame(
            {
                "Time/s": [0],
                "Cold junction_temp": [Tref],
                "STM_head_pin5_temp/C": [pin_5_temperature],
            }
        )
    temp_time_point_OBJ.to_csv("pin3.csv", mode="a", index=False, header=False)
    temp_time_point_STM_head.to_csv("pin5.csv", mode="a", index=False, header=False)

    j = j + 1
    i += 1
