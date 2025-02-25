import zmq
import random
import json


def roll_dice(faces, qty, adv=False, dsv=False):
    """
    Args:
        faces (int): Number of faces on the dice
        qty (int): Number of dice to roll
        adv (bool): If True, roll with advantage
        dsv (bool): If True, roll with disadvantage

    Returns:
        tuple: (results, taken, total)
    """
    if adv and dsv:
        raise ValueError("A roll cannot have both advantage and disadvantage")

    # Roll once normally if no advantage/disadvantage
    if not adv and not dsv:
        results = [random.randint(1, faces) for _ in range(qty)]
        taken = results.copy()
        return results, taken, sum(taken)

    # we will roll twice when there is an advantage/disadvantage
    roll1 = [random.randint(1, faces) for _ in range(qty)]
    roll2 = [random.randint(1, faces) for _ in range(qty)]

    sum1 = sum(roll1)
    sum2 = sum(roll2)

    # For advantage, take higher sum
    if adv:
        if sum1 >= sum2:
            # results of each roll, what was taken, total
            return [roll1, roll2], roll1, sum1
        else:
            return [roll1, roll2], roll2, sum2

    # For disadvantage, take lower sum
    if dsv:
        if sum1 <= sum2:
            # results of each roll, what was taken, total
            return [roll1, roll2], roll1, sum1
        else:
            return [roll1, roll2], roll2, sum2


def process_rolls(rolls_data):
    """
    Process a JSON object containing dice roll specifications

    Args:
        rolls_data (dict): Dictionary containing roll specifications

    Returns:
        dict: Original data with results added
    """
    result = rolls_data.copy()

    if "rolls" not in result:
        raise ValueError("Input must contain a 'rolls' key")

    grand_total = 0

    for roll in result["rolls"]:
        faces = roll.get("faces")
        qty = roll.get("qty")
        # if adv not specified, default to false
        adv = roll.get("adv", False)
        # if dsv not specified, default to false
        dsv = roll.get("dsv", False)

        # handle errors
        if not isinstance(faces, int) or faces <= 0:
            raise ValueError("'faces' must be a positive integer")
        if not isinstance(qty, int) or qty <= 0:
            raise ValueError("'qty' must be a positive integer")

        results, taken, total = roll_dice(faces, qty, adv, dsv)

        roll["results"] = results
        roll["taken"] = taken
        roll["roll_total"] = total

        grand_total += total

    result["total"] = grand_total

    return result


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
            
    except json.JSONDecodeError:
        response = json.dumps({"error": "Invalid JSON. Could not parse the request"})
    except ValueError as ve:
        response = json.dumps({"error": str(ve)})
    except Exception as e:
        response = json.dumps({"error": f"Unexpected error: {str(e)}"})

    socket.send_string(response)
