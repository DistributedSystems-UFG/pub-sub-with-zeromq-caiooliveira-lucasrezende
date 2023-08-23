import rpyc

test = []
myReferences = set()
myNames = set()

class MyService(rpyc.Service):
    def on_connect(self, conn):
        self.fn = None

    def exposed_serverPrint(self, user, destination):
        global myReferences
        myReferences = {(fn, name) for fn, name in myReferences if name != user}
        for i in myReferences:
            if i[1] == destination and i[0] is not self.fn:
                i[0](f"{user} joined the room")

    def exposed_serverExit(self, name):
        global myReferences
        myReferences = {(fn, n) for fn, n in myReferences if n != name}

    def exposed_serverPrintMessage(self, message, destination):
        for i in myReferences:
            if i[1] == destination and i[0] is not self.fn:
                i[0](message)

    def exposed_replyWith(self, number):
        return test[number]

    def exposed_replyLength(self, length):
        return len(test)

    def exposed_setCallback(self, fn, name):
        self.fn = fn
        myReferences.add((fn, name))
        myNames.add(name)

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(MyService, port=18888)
    t.start()
