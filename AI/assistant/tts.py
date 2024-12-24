import pyttsx3

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()

class TTS:
    def __init__(self, rate=150):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)  # Set default rate
        # self.engine.startLoop(False)

    def speak(self, text):
        print("speaking... 1/3")
        self.engine.say(text)
        print("speaking... 2/3")
        # self.engine.startLoop()
        self.engine.runAndWait()
        print("speaking... 3/3")
        # self.engine.startLoop()
        # self.engine.startLoop(False)

    def set_rate(self, rate):
        self.engine.setProperty('rate', rate)
        return f"Speech rate set to {rate}"

    def get_rate(self):
        return self.engine.getProperty('rate')
