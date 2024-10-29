import websockets
import asyncio
import json

async def echo(socket):

    async for message in socket:
        print(f"RECIEVED MESSAGE: {message}")
        await socket.send(f'I just got this message: {message}')

async def message_handler(socket, rooms, message):

    try:
        print(message)
        data = json.loads(message)
        command = data.get("type") 

        if command == 'join':
            room_id = data.get('room_id')
            print(f'we are joining room {room_id}')
            await socket.send(json.dumps({"status" : {'success': f'room joined successfully'}}))
            #await handle_room_join(socket, room_id, rooms)

        elif command == 'create-room':
            room_id = data.get('room_id')
            print(f'we are creating room {room_id}')
            await socket.send(json.dumps({'status': {'success': f'room created succesfully'}}))

        elif command == "add":
            print('user is being added...')
            await socket.send(json.dumps({"status" : {'success': f'user added successfully'}}))
        
        elif command == "remove":
            print('user is being removed...')
            await socket.send(json.dumps({"status" : {'success': f'user removed successfully'}}))

        elif command == "ping":
            print('PONG!')
            await socket.send(json.dumps({'status': {'success': 'Pong'}}))

        else:
            await socket.send(json.dumps({"status": {"error": "501 Command is not recognized"}}))

    except json.JSONDecodeError:
        await socket.send(json.dumps({"status": {'error': '400 bad request'}}))



async def handle_room_join(socket, room_address:str, rooms:dict):

    if room_address not in rooms:
        rooms[room_address]= set()

    rooms[room_address].add(socket)
    await socket.send(f'Join room: {room_address}')

    try:
        async for message in socket:
            await broadcast_message(socket, room_address, message, rooms)
    finally:
        rooms[room_address].remove(socket)
        if len(rooms[room_address]) == 0:
            del rooms[room_address]



async def broadcast_message(sender, room_address, message, rooms):

    if room_address in rooms:
        for user in rooms[room_address]:
            if user != sender:
                await user.send(message)

    return

async def handle_connection(socket, rooms):
    try:
        async for message in socket:
            await message_handler(socket, rooms, message)
    
    except websockets.ConnectionClosed:
        print("connection has been closed")

async def main():

    rooms = {}

    async with websockets.serve(lambda ws: handle_connection(ws, rooms), '127.0.0.1', 4444):
        print("the websocket server has started on ws://127.0.0.1:4444")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

