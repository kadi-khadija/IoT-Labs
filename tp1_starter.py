"""
TP1 - Simulating a connected object in Python
=============================================
Fill in the blanks marked ____ in order: (1), (2), (3)...
Run the program after each part:   python tp1_starter.py
At the bottom of the file, remove the # in front of part2(), part3(), part4()
when you reach that part.
If you see an error that mentions '____', a blank is still empty.
"""
# =========================================================
# PART 0 - Get started
# =========================================================
import json                                  # (1) the module that converts dictionaries to JSON text
import random

# =========================================================
# PART 1 - From an object to a connected device
# =========================================================

def read_temperature():
    """A plain object: it measures, but it cannot send anything."""
    return round(random.uniform(15, 30), 1)


class TemperatureSensor:
    """A device: it has an identity and it can communicate."""

    def __init__(self, sensor_id):
        self.sensor_id = sensor_id                # (2) store the identity received as a parameter

    def read(self):
        return round(random.uniform(15, 30), 1)

    def make_message(self):
        message = {
            "sensor_id": self.sensor_id,
            "type": "temperature",
            "value": self.read(),                    # (3) put the measured value here
            "unit": "C",
        }
        return json.dumps(message)                # (4) turn the dictionary into text


# =========================================================
# PART 2 - The M2M way: the sensor talks directly to the screen
# =========================================================

class Screen:
    def __init__(self, name):
        self.name = name

    def show(self, message):
        data = json.loads(message)                # (5) turn the text back into a dictionary
        print(f"[{self.name}] {data['sensor_id']}: {data['value']} {data['unit']}")


class M2MSensor:
    def __init__(self, sensor_id, screen):
        self.sensor_id = sensor_id
        self.screen = screen                      # (6) direct, fixed link to ONE screen

    def send(self):
        message = json.dumps({"sensor_id": self.sensor_id, "type": "temperature",
                              "value": round(random.uniform(15, 30), 1), "unit": "C"})
        self.screen.show(message)                 # (7) call the screen's display method directly


# =========================================================
# PART 3 - The IoT way: everything goes through a gateway
# =========================================================

class Gateway:
    """A very small broker: receivers register here, and every message
    published by a sensor is forwarded to all registered receivers."""

    def __init__(self):
        self.receivers = []                # (8) start with an empty list of receivers

    def register(self, receiver):
        self.receivers.append(receiver)           # (9) add the receiver to the list
        print(f"[Gateway] {receiver.name} is connected")

    def unregister(self, receiver):
        self.receivers.remove(receiver)           # (14) Part 4: take the receiver out of the list
        print(f"[Gateway] {receiver.name} is disconnected")

    def publish(self, message):
        for receiver in self.receivers:           # (10) loop over all connected receivers
            receiver.receive(message)             # (11) give the message to each receiver


class IoTSensor:
    def __init__(self, sensor_id, sensor_type, unit, low, high, gateway):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.unit = unit
        self.low, self.high = low, high
        self.gateway = gateway                # the sensor only knows the gateway

    def send(self):
        message = json.dumps({"sensor_id": self.sensor_id, "type": self.sensor_type,
                              "value": round(random.uniform(self.low, self.high), 1),
                              "unit": self.unit})
        self.gateway.publish(message)             # (12) the sensor never calls a screen directly


class ScreenReceiver:
    def __init__(self, name):
        self.name = name

    def receive(self, message):
        data = json.loads(message)
        print(f"[{self.name}] {data['sensor_id']} ({data['type']}): {data['value']} {data['unit']}")


class LoggerReceiver:
    def __init__(self, name):
        self.name = name
        self.history = []                     # every message received is kept here

    def receive(self, message):
        self.history.append(json.loads(message))


class AlarmReceiver:
    def __init__(self, name, limit):
        self.name = name
        self.limit = limit

    def receive(self, message):
        data = json.loads(message)
        if data["type"] == "temperature" and data["value"]> self.limit :   # (13) value greater than the limit
            print(f"[{self.name}] ALERT! {data['sensor_id']} = {data['value']} {data['unit']}")


# =========================================================
# PROGRAMS TO RUN
# =========================================================

def part1():
    print("=== Part 1 ===")
    print("Plain object reading:", read_temperature())
    s = TemperatureSensor("T1")
    print("Device message:", s.make_message())


def part2():
    print("\n=== Part 2 (M2M) ===")
    screen = Screen("Screen-1")
    sensor = M2MSensor("T1", screen)
    screen2 = Screen("Screen-2")
    sensor2 = M2MSensor("T2", screen2)
    for _ in range(3):
        sensor.send()
        sensor2.send()


def part3():
    print("\n=== Part 3 (IoT) ===")
    gw = Gateway()
    screen = ScreenReceiver("Screen-1")
    screen2 = ScreenReceiver("Screen-2")
   
    logger = LoggerReceiver("Logger")
    Alarm = AlarmReceiver("Alarm", 25)
    hs=  IoTSensor("H1", "humidity", "%", 30, 80, gw)
    gw.register(screen)
    gw.register(screen2)
    gw.register(Alarm)
    gw.register(logger)
    t1 = IoTSensor("T1", "temperature", "C", 15, 30, gw)
    for _ in range(3):
        t1.send()
        hs.send()
    print("Logger has", len(logger.history), "messages")
    # Task 3.3: add your new devices below this line



def part4():
    print("\n=== Part 4 (devices that come and go) ===")
    gw = Gateway()
    screen = ScreenReceiver("Screen-1")
    logger = LoggerReceiver("Logger")
    gw.register(screen)
    gw.register(logger)
    t1 = IoTSensor("T1", "temperature", "C", 15, 30, gw)
    t1.send()
    gw.unregister(screen)                     # the screen goes offline
    t1.send()
    gw.register(screen)                       # the screen comes back
    t1.send()
    for m in logger.history:
        print("  Logger saved:", m)
    print("Logger has", len(logger.history), "messages")


part1()
part2()
part3()
part4()
