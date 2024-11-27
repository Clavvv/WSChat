import json
import zmq


def addUsername(username:str) -> bool:

    context = zmq.Context()
    print('connecting to service ... ')
    client_sock = context.socket(zmq.REQ)
    client_sock.connect("tcp://localhost:5555")

    query = {
        "action": "add",
        "username": username
    }

    str_request = json.dumps(query)

    bin_msg = str_request.encode('utf-8')
    client_sock.send(bin_msg)
    response = client_sock.recv()
    str_response = response.decode('utf-8')

    server_json = json.loads(str_response)

    if server_json['success']:
        return True
    
    else:
        return False
    
def deleteUsername(username:str) -> bool:

    
    context = zmq.Context()
    print('connecting to service ... ')
    client_sock = context.socket(zmq.REQ)
    client_sock.connect("tcp://localhost:5555")

    query = {
        "action": "delete",
        "username": username
    }

    str_request = json.dumps(query)

    bin_msg = str_request.encode('utf-8')
    client_sock.send(bin_msg)
    response = client_sock.recv()
    str_response = response.decode('utf-8')

    server_json = json.loads(str_response)

    if server_json['success']:
        return True
    
    else:
        return False


