# Prova di script da usare in matlab per il controllo della memoria

import psutil as ps

#TABELLA NB
"""
Print system memory information.
$ python scripts/meminfo.py
MEMORY
------
Total      :    9.7G
Available  :    4.9G
Percent    :    49.0
Used       :    8.2G
Free       :    1.4G
Active     :    5.6G
Inactive   :    2.1G
Buffers    :  341.2M
Cached     :    3.2G
SWAP
----
Total      :      0B
Used       :      0B
Free       :      0B
Percent    :     0.0
Sin        :      0B
Sout       :      0B
"""

#Funzione per convertire in num leggibili i byte della memoria usata
#modificata da quella trovata online per restituire solo un float
def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            #return '%.1f%s' % (value, s)  #Tenere per ricordare come si possono restituire in string dei float approssimati
            return value
    #return "%sB" % n  #Tenere per sicurezza
    return n

def main():
    memory = ps.virtual_memory()
    used_atm = memory.used
    print('%s' % bytes2human(used_atm))

if __name__ == '__main__':
    main()
