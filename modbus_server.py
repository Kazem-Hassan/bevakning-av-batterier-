#!/usr/bin/env python3
import os
import json
import time
import threading

from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock

# Ange katalog med JSON-filer
FOLDER_PATH = "/home/pi/jsondata"

def list_json_files(folder_path):
    """
    Returnerar en sorterad lista över alla .json-filer i mappen.
    T.ex. ["filA.json", "filB.json", ...].
    Du kan sortera efter namn eller mtime beroende på behov.
    """
    all_files = []
    for fname in os.listdir(folder_path):
        if fname.endswith(".json"):
            full_path = os.path.join(folder_path, fname)
            all_files.append(full_path)
    # Sortera efter filnamn (eller ändringstid) om du vill
    all_files.sort()
    return all_files

# Hämta alla .json-filer en gång i början
json_file_list = list_json_files(FOLDER_PATH)

# Skapa en Modbus-databutik (exempel: 10 holding registers)
store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0]*10)
)
context = ModbusServerContext(slaves=store, single=True)

def read_register(address, count=1):
    """
    Läs holding registers (funktion 3) från store.
    address = startadress, count = antal register
    Returnerar en lista med heltalsvärden.
    """
    return store.getValues(3, address, count)

def write_register(address, values):
    """
    Skriv holding registers (funktion 3) till store.
    values = lista med heltalsvärden.
    """
    store.setValues(3, address, values)

def load_data_into_registers(file_index):
    """
    1) Öppna fil med givet index i json_file_list
    2) Läs dess JSON-innehåll
    3) Plocka ut några värden och lagra dem i Modbus-register
    """
    if file_index < 0 or file_index >= len(json_file_list):
        print(f"Ogiltigt filindex: {file_index}")
        # Om index är ogiltigt, nollställ register 1–9
        write_register(1, [0]*9)
        return
    
    file_path = json_file_list[file_index]
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Fel vid läsning av {file_path}: {e}")
        # Nollställ register om fel
        write_register(1, [0]*9)
        return
    
    # Exempel: antag att JSON-filen ser ut så här:
    # {
    #   "timestamp": "2025-01-16T12:00:00",
    #   "temperature": 23.5,
    #   "humidity": 45.2,
    #   "status": "OK"
    # }
    #
    # Du kan själva anpassa vilka värden du vill läsa:
    
    temperature = data.get("temperature", 0.0)
    humidity    = data.get("humidity", 0.0)
    status_str  = data.get("status", "NONE")
    
    # Exempel: lägg in "temperature" i register 1, "humidity" i register 2
    # Notera att Modbus-register är 16 bitar. Om du vill behålla decimaler
    # kan du *100 t.ex.
    temp_reg = int(temperature * 100)
    hum_reg  = int(humidity * 100)

    # "status" är en sträng -> om du vill lagra den, måste du konvertera
    # antingen lägga bokstavskod i flera register, eller bara en kod (t.ex. 1 = OK).
    # Här gör vi en enkel: "OK" -> 1, "FAIL" -> 2, etc.
    status_code = 0
    if status_str == "OK":
        status_code = 1
    elif status_str == "FAIL":
        status_code = 2
    # (du kan bygga ut mer logik)

    # Skriv dessa värden till register 1, 2, 3 ...
    write_register(1, [temp_reg, hum_reg, status_code])

    # Eventuellt fler data om du vill ...

def monitor_file_index():
    """
    En bakgrundstråd som hela tiden kollar holding register 0 (filindex).
    Om det ändras läses motsvarande fil och data skrivs in i register 1–9.
    """
    last_index = None
    while True:
        # Läs filindex från register 0
        current_index = read_register(0, 1)[0]
        
        # Om nytt index -> ladda om data
        if current_index != last_index:
            print(f"Filindex ändrat till {current_index}, laddar fil...")
            load_data_into_registers(current_index)
            last_index = current_index
        
        time.sleep(1)

if __name__ == "__main__":
    print("Tillgängliga JSON-filer:")
    for i, path in enumerate(json_file_list):
        print(f"  Index {i}: {path}")
    
    # Starta bakgrundstråden som övervakar register 0
    t = threading.Thread(target=monitor_file_index, daemon=True)
    t.start()

    # Starta Modbus TCP-server
    # OBS! Port 502 kräver root, annars välj en högre port (t.ex. 1502).
    print("\nStartar Modbus TCP-server på port 502...")
    StartTcpServer(context, address=("0.0.0.0", 502))
