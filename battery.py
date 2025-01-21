#!/usr/bin/env python3
import json
import time
import random
import os
from datetime import datetime

def generate_random_voltage():
    """
    Genererar ett slumpmässigt volttal (simulerad).
    Exempel: Mellan 3.0 och 4.2 V för litiumjonceller.
    """
    return round(random.uniform(3.0, 4.2), 2)

def generate_random_temperature():
    """
    Genererar en slumpmässig temperatur i Celsius (simulerad).
    Exempel: Mellan 20°C och 40°C.
    """
    return round(random.uniform(20.0, 40.0), 1)

def create_cabinet_data(cabinet_serial, tray_serials):
    """
    Skapar ett dataobjekt för skåpet, där varje bricka innehåller 10 celler
    med simulerade mätvärden (voltage, temperature).
    
    Fältordningen är: timestamp, cabinet_serial_number, trays
    """
    trays_data = []
    for tray_serial in tray_serials:
        cells_data = []
        for cell_idx in range(1, 11):  # 10 celler per bricka
            cell_data = {
                "cell_index": cell_idx,
                "voltage": generate_random_voltage(),
                "temperature": generate_random_temperature()
            }
            cells_data.append(cell_data)

        tray_data = {
            "tray_serial_number": tray_serial,
            "cells": cells_data
        }
        trays_data.append(tray_data)

    # Lägg "timestamp" först i ordföljden
    cabinet_data = {
        "timestamp": datetime.now().isoformat(),
        "cabinet_serial_number": cabinet_serial,
        "trays": trays_data
    }
    return cabinet_data

def append_data_as_line(data, file_path):
    """
    Lägger till (append) en rad i filen, där raden är ett JSON-objekt med mätdata.
    Varje rad = ett mätningstillfälle.
    """
    # Säkerställ att katalogen finns innan vi skriver
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # Öppna filen i append-läge ('a') och skriv en rad
    with open(file_path, 'a') as f:
        f.write(json.dumps(data))
        f.write('\n')  # Radbrytning, så varje mätning blir en egen rad

def main():
    # Unikt serienummer för skåpet
    CABINET_SERIAL_NUMBER = "CAB-12345"

    # Exempel: tre brickor i skåpet
    TRAY_SERIAL_NUMBERS = ["TRAY-A", "TRAY-B", "TRAY-C"]

    # En bestämd fil där all data sparas (alla mätdatapunkter på varsin rad)
    SAVE_FILE_PATH = "/home/pi/simdata/battery_data.log"

    # Hur ofta vi vill göra en ny mätning, i sekunder
    INTERVAL_SECONDS = 5

    print("Startar simulatorn. Avbryt med Ctrl+C för att avsluta.")
    try:
        while True:
            # Skapa ett JSON-objekt för hela skåpet
            cabinet_data = create_cabinet_data(
                cabinet_serial=CABINET_SERIAL_NUMBER,
                tray_serials=TRAY_SERIAL_NUMBERS
            )

            # Skriv ut (valfritt för felsökning)
            print("Genererat data:")
            print(json.dumps(cabinet_data, indent=4))

            # Spara varje mätning som en rad i samma fil
            append_data_as_line(cabinet_data, SAVE_FILE_PATH)
            print(f"Data sparades i filen: {SAVE_FILE_PATH}\n")

            # Vänta tills nästa mätning
            time.sleep(INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("Avslutar simulatorn.")

if __name__ == "__main__":
    main()
