from tts import TTS

class TTSAdapter:
    def __init__(self):
        self.tts_engine = TTS()  # Initialize the TTS engine

    def handle_tts_command(self, command, params):
        """
        Processes the TTS-related commands.
        Supported commands: speak, set_rate, get_rate
        """
        if command == "speak":
            text = ' '.join(params)
            print(f"speaking \"{text}\"")
            self.tts_engine.speak(text)
            return f"Speaking: {text}"

        elif command == "set_rate":
            if len(params) != 1 or not params[0].isdigit():
                return "Error: 'set_rate' expects a numeric rate parameter."
            rate = int(params[0])
            return self.tts_engine.set_rate(rate)

        elif command == "get_rate":
            current_rate = self.tts_engine.get_rate()
            return f"Current speech rate: {current_rate}"

        else:
            return f"Unknown TTS command: {command}"
