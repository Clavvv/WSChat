import asyncio
import websockets
import json
import sys

#Global Variables
socket = None

class UserMessage:

    def __init__(self, text:str):
        '''
        Values in valid command will correspond  to a function which will execute the desired outcome
        '''
        self.text= text.strip().lower()
        self._isCommand = len(text) > 0 and self.text[0] == '.'

    @classmethod
    async def create(cls, text:str):

        self = cls(text)
        if self._isCommand:
            await self.process_command()

        return self


    async def process_command(self):
        global socket
        
        userInput = self.text.split(' ')
        command, parameters = userInput[0], userInput[1:]

        match command:
            case ".join":
                if len(parameters) == 1:
                    await send_message_to_server('join', room= parameters[0])
                else:
                    print("Error: Invalid format for room_id. Please use the following format:\n"
                        ".join room_name_goes_here\n"
                        "Make sure to replace room_name_goes_here with the actual name of the room you want to join."
                    )
            case '.msg':
                print("A function to message another user will go here")
            case '.help':
                self._help() 
            case '.exit':
                if socket is not None:
                    await socket.close()
                sys.exit(0)
            case '.add':
                print('a function to add another user as a friend will go here eventually')
            case '.remove':
                print('a function to remove a user as a friend will go here eventually')
            case _:
                print(f"{command} is not a recognized command, type '.help' to view a list of commands")


    def _help(self):
        help_message = '''
            Commands:
            ------------------------------------------------------
            .join <room_number>      - Join a specific chat room by its number
            .msg <username>          - Send a private message to a user
            .help                    - Display this help message
            .exit                    - Exit the program
            .add <username>          - Add a user as a friend
            .remove <username>       - Remove a user from your friends list
        '''
        print(help_message)


async def send_message_to_server(message_type, room=None, user=None):

    if socket is None or socket.closed:
        print("Something went wrong you are not connected to the server")
        return
    
    message = {
        "type": message_type
    }

    if room:
        message['room_id']= room
    
    elif user:
        message['user']= user

    await socket.send(json.dumps(message))
    print(f'sent message to server: {message}')

async def connect_to_server():
    global socket
    uri = "ws://127.0.0.1:4444"
    socket = await websockets.connect(uri)

async def ping():

    while True:
        print('ping')

        if socket is not None and not socket.closed:
            await socket.send(json.dumps({"type": "ping"}))
            await asyncio.sleep(30)

        else:
            return
        
async def get_user_input(message_queue):
    while True:
        loop = asyncio.get_event_loop()
        user_input = await loop.run_in_executor(None, input, '> ')
        await message_queue.put(user_input)




async def main():
    queue = asyncio.Queue()
    connection_task = asyncio.create_task(connect_to_server())
    await connection_task
    keep_alive_task = asyncio.create_task(ping())
    input_task = asyncio.create_task(get_user_input(queue))

    while True:
        message = await queue.get()
        message = await UserMessage.create(message)



if __name__ == "__main__":
    asyncio.run(main())