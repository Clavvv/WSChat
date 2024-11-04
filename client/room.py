import websockets
import json
import asyncio
import sys
import subprocess
import multiprocessing

class Listener:
    def __init__(self, incoming_queue):
        self.incoming_queue = incoming_queue

    def start(self):
        while True:
            # Check if there are any messages in the incoming queue
            if not self.incoming_queue.empty():
                message = self.incoming_queue.get()
                self.process_message(message)

    def process_message(self, message):
        # Handle the incoming message (you can customize this method)
        print(f'{message}')


class RoomInstance:

    def __init__(self, room_id, incoming_queue, outgoing_queue):

        self.room_id = room_id
        self.local_queue = asyncio.Queue()  #this is a thread queue to prevent locking by user input
        self.incoming_queue = Listener(incoming_queue)
        self.outgoing_queue = outgoing_queue

    async def get_user_input(message_queue):
        while True:
            loop = asyncio.get_event_loop()
            user_input = await loop.run_in_executor(None, input, '> ')
            await message_queue.put(user_input)


            #If I don't exit here it causes a delay because of the way the input function works
            if user_input == '.exit':
                break 

    def start(self):

        if not self.incoming_queue.empty():
            message = self.incoming_queue.get()
            self.process_messages(message)



if __name__ == "__main__":

    if len(sys.argv != 3):
        print('Usage Pythong room.py <read_queue><write_queue>')
        sys.exit(1)

    read_queue_name = sys.argv[1]   #argument 1 pased via cli
    write_queue_name = sys.argv[2]  #argument 2 passed via cli

