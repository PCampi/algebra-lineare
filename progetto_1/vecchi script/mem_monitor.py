#Parte relativa soltanto al monitoring della memoria attualmente in utilizzo
import psutil
import sys
import os

def mem_mon(pID):
    current_process = psutil.Process(pID)
    used_atm = current_process.memory_info().vms
    return used_atm

if __name__ == '__main__':
    value_to_mem = int(sys.argv[1])
    sys.stdout.write('%s' % mem_mon(value_to_mem))