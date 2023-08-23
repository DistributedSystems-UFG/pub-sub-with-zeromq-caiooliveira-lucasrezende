import rpyc
import zmq
from threading import Thread

reach = 0
net = None
input_var = None
user_name = None

def myprint(message):
    print(message)

def checkAndPrint():
    global reach, net
    while True:
        length = conn.root.replyLength(1)
        if input_var == "exit":
            break
        while reach < length:
            net = conn.root.replyWith(reach)
            reach += 1
            print(net)

def receive_messages():
    context = zmq.Context()
    s_sub = context.socket(zmq.SUB)
    s_sub.connect(f"tcp://{SERVER}:{PORT}")
    s_sub.setsockopt_string(zmq.SUBSCRIBE, "GROUP")

    while True:
        message = s_sub.recv().decode()
        if not message.startswith(f"GROUP {user_name}:"):
            print(message)

option = input("Do you want to send a direct message or a group message? (direct/group): ")

if option == "direct":
    conn = rpyc.connect(SERVER, PORT)
    conn.root.setCallback(myprint, user_name)

    user_name = input("Please enter your name: ")
    destination = input("Please enter the name of the person you want to talk to: ")
    print("Type exit to leave the conversation")
    conn.root.serverPrint(user_name, destination)
    reach = conn.root.replyLength(1)

    t = Thread(target=checkAndPrint)
    t.start()

    while True:
        input_var = input()
        if input_var == "exit":
            time.sleep(1)
            input_var = f"{user_name} has left the conversation"
            conn.root.setCallback(myprint, user_name)
            conn.root.serverPrintMessage(input_var)
            conn.root.serverExit(user_name)
            break
        reach += 1
        input_var = f"{user_name}:{input_var}"
        conn.root.setCallback(myprint, user_name)
        conn.root.serverPrintMessage(input_var, destination)

elif option == "group":
    user_name = input("Please enter your name: ")

    t = Thread(target=receive_messages)
    t.start()

    context = zmq.Context()
    s = context.socket(zmq.PUB)
    s.bind(f"tcp://{SERVER}:{PORT}")

    while True:
        msg = input("Enter a message: ")
        s.send_string(f"GROUP {user_name}:{msg}")
