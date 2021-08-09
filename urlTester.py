import socket
import requests
import time
from urllib import error
import re

ptrn = re.compile('http(s)*\://')

def req_tester(server:str,timeout:float):
    try:
        init_time = time.perf_counter()
        requests.get(server, timeout=timeout)
        total_time = round(time.perf_counter()-init_time, 4)
        return (server,total_time)
    except socket.gaierror as e:
        # print(f"{e}  --> {server}")
        return
    except requests.Timeout as e:
        # print(f"{e}  --> {server}")
        return
    except requests.ConnectionError as e:
        # print(f"{e}  --> {server}")
        return
    except requests.HTTPError as e:
        return
    except socket.timeout as e:
        # print(f"{e}  --> {server}")
        return



def sock_tester(server, timeout, port=80):
    swp = re.sub(ptrn, '', server).split('/')[0].split(":")
    if len(swp) == 2:
        SERVER = swp[0]
        PORT = int(swp[1])
    else:
        SERVER = swp[0]
        PORT = port

    s = socket.socket()
    s.settimeout(timeout)
    try:
        connect_time = time.perf_counter()
        s.connect((SERVER, PORT))
        taken_time = time.perf_counter() - connect_time
        # return "\n{} \t{:.4f}".format(server, taken_time)
        return (server, round(taken_time,4))
    except socket.timeout as e:
        return
    except socket.gaierror as e:
        # print("Gai Error",server)
        return
    except OSError as e:
        #no internet connection
        return
    except error.URLError as e:
        # This server does't give you proper speed
        return
    except ConnectionRefusedError as e:
        return
    except ConnectionError as e:
        #no internet connection
        return
    finally:
        s.close()