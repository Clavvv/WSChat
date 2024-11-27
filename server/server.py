import websockets
import asyncio
import json
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

async def echo(socket):
    async for message in socket:
        logging.debug(f"Received message: {message}")
        await socket.send(f'I just got this message: {message}')

async def message_handler(socket, rooms, message):
    logging.debug(f"Message: {message}")

    try:
        data = json.loads(message)
        command = data.get("type")

        if command == 'join':
            room_id = data.get('room_id')
            logging.info(f'Joining room {room_id}')
            await handle_room_join(socket, room_id, rooms)
            await socket.send(json.dumps({"status": {'success': f'Room joined successfully', 'room_id': room_id}}))

        elif command == 'create-room':
            room_id = data.get('room_id')
            logging.info(f'Creating room {room_id}')
            await socket.send(json.dumps({'status': {'success': 'Room created successfully'}}))

        elif command == "add":
            logging.info('User is being added...')
            await socket.send(json.dumps({"status": {'success': 'User added successfully'}}))

        elif command == "remove":
            logging.info('User is being removed...')
            await socket.send(json.dumps({"status": {'success': 'User removed successfully'}}))

        elif command == "ping":
            logging.info('PONG!')
            await socket.send(json.dumps({'status': {'success': 'Pong'}}))

        elif command == 'leave':
            logging.debug(f'{data.get("username")} is leaving room {data.get("room_id")}')
            room_id = data.get('room_id')
            username = data.get('username')
            await handle_room_leave(socket, room_id, rooms)

        elif command == 'chat-message':
            username = data.get('username')
            content = data.get('content')
            room_id = data.get('room_id')
            msg = {
                'type': 'chat-message',
                'username': username,
                   'content': content
                   }
            await broadcast_message(socket, room_id, msg, rooms)

        else:
            await socket.send(json.dumps({"status": {"error": "501 Command is not recognized"}}))

    except json.JSONDecodeError:
        await socket.send(json.dumps({"status": {'error': '400 Bad Request'}}))

async def handle_room_join(socket, room_address: str, rooms: dict):
    if room_address not in rooms:
        rooms[room_address] = set()

    rooms[room_address].add(socket)
    await socket.send(json.dumps({'status': {'success': 'Room joined successfully'}}))

async def broadcast_message(sender_socket, room_address, message, rooms):
    logging.debug(f'Broadcasting message: {message}')
    response = json.dumps(message)
    if room_address in rooms:
        for user in rooms[room_address]:
            if user != sender_socket:
                await user.send(response)
                logging.debug(f'Message sent to user {user}: {message}')

async def handle_connection(socket, rooms):
    try:
        async for message in socket:
            await message_handler(socket, rooms, message)
    except websockets.ConnectionClosed:
        logging.warning("Connection has been closed")

async def handle_room_leave(socket, room_address: str, rooms: dict):
    logging.info(f"Handling leave for room {room_address}")
    logging.debug(rooms)
    if room_address not in rooms:
        logging.error(f"No such room: {room_address}")
        await socket.send(json.dumps({'status': {'error': 'Failed to leave room - room not found'}}))
        return

    if socket in rooms[room_address]:
        rooms[room_address].remove(socket)
        logging.info(f"Socket removed from room {room_address}")
        if not rooms[room_address]:
            del rooms[room_address]
            logging.info(f"Room {room_address} deleted (empty)")
        await socket.send(json.dumps({'status': {'success': f'Left room {room_address}'}}))
    else:
        logging.error(f"Socket not found in room {room_address}")
        await socket.send(json.dumps({'status': {'error': f'Failed to leave room - not a member of {room_address}'}}))

async def TEST_PRINTROOMINFO(rooms):
    while True:
        logging.debug(f"Rooms state: {rooms}")
        await asyncio.sleep(10)

async def main():
    rooms = {}
    log_rooms = asyncio.create_task(TEST_PRINTROOMINFO(rooms))

    async with websockets.serve(lambda ws: handle_connection(ws, rooms), '127.0.0.1', 4444):
        logging.info("WebSocket server started on ws://127.0.0.1:4444")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
