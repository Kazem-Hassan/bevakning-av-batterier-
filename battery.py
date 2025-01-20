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
    med simulerade mätvärden för voltage och temperatur.
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

    cabinet_data = {
        "cabinet_serial_number": cabinet_serial,
        "timestamp": datetime.now().isoformat(),
        "trays": trays_data
    }

    return cabinet_data

def save_data_to_unique_json_file(data, directory):
    """
    Skapar en ny fil (med tidsstämpel i filnamnet) för varje mätning.
    Filen innehåller data för hela skåpet (alla brickor och celler).
    """
    # Skapa en tidsstämpel som del av filnamnet, t.ex. 20250117_153045_123456
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    file_name = f"battery_data_{timestamp_str}.json"

    # Säkerställ att katalogen finns
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, file_name)

    # Skriv data till den nya filen
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

    return file_path

def main():
    # Unikt serienummer för skåpet
    CABINET_SERIAL_NUMBER = "CAB-12345"

    # Exempel: tre brickor i skåpet
    TRAY_SERIAL_NUMBERS = ["TRAY-A", "TRAY-B", "TRAY-C"]

    # Katalog där vi sparar alla filer (på en Raspberry Pi kan du använda valfri sökväg)
    SAVE_DIRECTORY = "/home/pi/simdata"

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

            # Spara varje mätning i en ny fil
            saved_file = save_data_to_unique_json_file(cabinet_data, SAVE_DIRECTORY)
            print(f"Data sparades i fil: {saved_file}\n")

            # Vänta tills nästa mätning
            time.sleep(INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("Avslutar simulatorn.")

if __name__ == "__main__":
    main()
