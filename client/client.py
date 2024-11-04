import asyncio
import websockets
import json
import sys

#Global Variables
socket = None
room = None
username = None

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
        global room
        global username
        
        userInput = self.text.split(' ', 1)
        command, parameters = userInput[0], userInput[1:]

        match command:
            case ".join":
                if len(parameters) == 1:

                    msg = {
                        'type': 'join',
                        'room_id': parameters[0],
                        'username': username
                    }
                    room= parameters[0]
                    await send_message_to_server(msg)

                else:
                    print("Error: Invalid format for room_id. Please use the following format:\n"
                        ".join room_name_goes_here\n"
                        "Make sure to replace room_name_goes_here with the actual name of the room you want to join."
                    )
            case '.msg':
                print("A function to message another user will go here")
            case '.say':

                if not username:
                    print('please set a username before messaging')
                    return
                
                elif not room:
                    print('you must join a room before attempt to send a message')
                    return
                
                elif len(parameters) <= 0:
                    print('message must have content of length 1 or greater')

                msg = {
                        'type': 'chat-message',
                        'room_id': room,
                        'username': username,
                        'content': parameters[0]
                    }
                
                try:
                    await send_message_to_server(msg)
                
                except:
                    print('something went wrong restart your application')



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
            case '.username':
                if len(parameters) <= 0:
                    print('username cannot be empty')
                username = parameters[0]
                print(f'username set: {username}')
            case _:
                print(f"{command} is not a recognized command, type '.help' to view a list of commands")


    def _help(self):
        help_message = '''
            Commands:
            ------------------------------------------------------
            .join <room_number>      - Join a specific chat room by its number  
            .msg <username>          - Send a private message to a user     [NOT IMPLEMENTED]
            .help                    - Display this help message
            .exit                    - Exit the program
            .add <username>          - Add a user as a friend               [NOT IMPLEMENTED]
            .remove <username>       - Remove a user from your friends list [NOT IMPLEMENTED]
            .username <username>     - Set your display name
        '''
        print(help_message)

async def send_message_to_server(message):

    if socket is None or socket.closed:
        print("Something went wrong you are not connected to the server")
        return
    
    await socket.send(json.dumps(message))

async def connect_to_server():
    global socket
    uri = "ws://127.0.0.1:4444"
    socket = await websockets.connect(uri)

async def ping():

    while True:
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


        #If I don't exit here it causes a delay because of the way the input function works
        if user_input == '.exit':
            break

def process_chat_message(response):
    user = response.get('username')
    content = response.get('content')
    print(f'{user}: {content}')

async def listen_to_server():
    while True:
        try:
            if socket and not socket.closed:

                message = await socket.recv()
                if message:
                    message_data = json.loads(message)

                    if message_data.get('type') == 'chat-message':
                        process_chat_message(message_data)

                    if (room_id := message_data.get('status', {}).get('room_id')):
                        print(f"Successfully joined room: {room_id}")



        except json.JSONDecodeError as e:
            print(message)
            print(f"Error decoding JSON message: {e}")
        except Exception as e:
            print(f"Error receiving message: {e}")
            break



async def main():
    queue = asyncio.Queue()
    connection_task = asyncio.create_task(connect_to_server())
    await connection_task
    keep_alive_task = asyncio.create_task(ping())
    input_task = asyncio.create_task(get_user_input(queue))
    listen_task = asyncio.create_task(listen_to_server())
    welcome_message = """
        ==========================================================
                     Welcome to WS Chat!                 
        ==========================================================
        
        Hello! We're glad you're here.
        
        To help you get started, here are a few quick tips:

        - Type .help to see a list of commands you can use to 
        navigate and interact in the chat.
        - Set your display name by typing .username [your_name] 
        so others can recognize you!

        Please set your username with '.username {name}' to begin chatting:

        ==========================================================
        """
    
    print(welcome_message)

    while True:
        message = await queue.get()
        message = await UserMessage.create(message)



if __name__ == "__main__":
    asyncio.run(main())