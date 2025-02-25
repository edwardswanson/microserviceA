# Microservice A

Starting the server:
  - Make sure to have ZeroMQ installed and enabled
  - Run the following code on your terminal (port 5050)
    - python3 diceroller.py


How to connect and send data to the server (microservice):
  - To send data to the server, the client needs to make sure it's on the right port (localhost) and set up ZMQ socket connections.
  - For example, the client can run python code similar to this
        import zmq
        import json
        
        
        def send_dice_request(port=5050):
            """Send JSON data directly to the dice roller microservice"""
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect(f"tcp://localhost:{port}")
        
            # send sample json data
            roll_data = {
                "rolls": [
                    {
                        "faces": 20,
                        "qty": 1,
                        "adv": True,
                        "dsv": False
                    },
                    {
                        "faces": 6,
                        "qty": 2,
                        "adv": False,
                        "dsv": False
                    }
                ]
            }
        
            print("Sending JSON data to microservice...")
            socket.send_string(json.dumps(roll_data))
            
            print("Waiting for response...")
            response = socket.recv_string()
            data = json.loads(response)
            
            print("Response received:")
            print(json.dumps(data))


        send_dice_request(port=5050)


How to receive data from the server (these lines are at the bottom the code sample given just above):

            response = socket.recv_string()
            data = json.loads(response)
            print(json.dumps(data))


The server (microservice) will recieve data on port 5050 via ZeroMQ, following code similar to as follows:
      
      # zeroMQ context and socket setup
      context = zmq.Context()
      # setup a reply socket
      socket = context.socket(zmq.REP)
      # bind to port 5050
      socket.bind("tcp://*:5050")
      
      print("microservice is running")
      
      while True:
          # receive request from the client
          request = socket.recv_string()
          print(f"received request: {request}")
      
          try:
              # Parse the received JSON data
              roll_data = json.loads(request)
              
              # Process the roll data directly
              if "rolls" in roll_data and isinstance(roll_data["rolls"], list):
                  processed_data = process_rolls(roll_data)
                  response = json.dumps(processed_data)
              else:
                  response = json.dumps({"error": "Invalid JSON format. Must contain a 'rolls' array"})
                  
          except Exception as e:
              response = json.dumps({"error": f"Unexpected error: {str(e)}"})
      
          socket.send_string(response)


UML Sequence Diagram:
  1. Main program sends JSON data directly to microservice (no seperate JSON file needed)
  2. Microservice reads the data, processes the results, and sends back JSON file with results appended to it
  3. Microservice awaits another call

     
<img width="679" alt="Screenshot 2025-02-24 at 5 12 56 PM" src="https://github.com/user-attachments/assets/ef615536-13ce-4168-b3b1-27688e837dd2" />
