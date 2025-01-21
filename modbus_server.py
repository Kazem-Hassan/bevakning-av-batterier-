#!/usr/bin/env python3
import os
import json
import time
import threading

from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock

# Ange den katalog där JSON-filerna ligger
FOLDER_PATH = "/home/pi/jsondata"

# Skapa en Modbus-databutik med t.ex. 10 holding registers (address 0-9)
store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0]*10)
)
context = ModbusServerContext(slaves=store, single=True)

def find_latest_json_file(folder_path):
    """
    Returnerar sökvägen till den senaste JSON-filen i foldern,
    baserat på senast ändrad tid (mtime).
    Om ingen JSON-fil hittas returneras None.
    """
    latest_file = None
    latest_mtime = 0

    # Loopar igenom alla filer i katalogen
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            full_path = os.path.join(folder_path, file_name)
            
            # Hämta "mtime" (senast ändrad tid) för filen
            mtime = os.path.getmtime(full_path)
            
            # Om detta är den senaste hittills, spara undan
            if mtime > latest_mtime:
                latest_mtime = mtime
                latest_file = full_path
    
    return latest_file

def write_register(address, values):
    """
    Skriv holding registers (funktion 3) till store.
    values = lista med heltalsvärden.
    """
    store.setValues(3, address, values)

def monitor_latest_file():
    """
    Bakgrundstråd som regelbundet kollar den senaste JSON-filen i FOLDER_PATH.
    Om det är en nyare fil än tidigare, läser den filen och uppdaterar Modbus-register.
    """
    last_file_path = None
    
    while True:
        latest_file_path = find_latest_json_file(FOLDER_PATH)

        if latest_file_path and latest_file_path != last_file_path:
            print(f"Nyaste fil: {latest_file_path}")
            last_file_path = latest_file_path

            # Läs in JSON-innehåll
            try:
                with open(latest_file_path, 'r') as f:
                    data = json.load(f)

                # Exempel: anta filen har "temperature", "humidity", "status" (sträng) etc.
                temperature = data.get("temperature", 0.0)
                humidity    = data.get("humidity", 0.0)
                status_str  = data.get("status", "NONE")

                # Konvertera float -> int, t.ex. multiply by 100
                temp_reg = int(temperature * 100)
                hum_reg  = int(humidity * 100)

                # Om status är en sträng: koda den till en int
                status_code = 0
                if status_str == "OK":
                    status_code = 1
                elif status_str == "FAIL":
                    status_code = 2
                # ... med mera

                # Skriv dessa värden till register 0, 1, 2
                write_register(0, [temp_reg, hum_reg, status_code])

                # Om du vill skriva fler fält, anpassa regi strering och index

            except Exception as e:
                print(f"Fel vid läsning av JSON: {e}")
                # Vid fel sätter vi t.ex. alla register till 0
                write_register(0, [0]*3)
        
        # Vänta några sekunder innan vi kollar igen
        time.sleep(2)

if __name__ == "__main__":
    # Starta bakgrundstråd
    t = threading.Thread(target=monitor_latest_file, daemon=True)
    t.start()

    # Starta Modbus-server
    print("Startar Modbus TCP-server på port 502 (kräver root eller port forwarding).")
    StartTcpServer(context, address=("0.0.0.0", 502))
