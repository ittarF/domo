class Memory:
    def __init__(self):
        self.history = []  # list of dicts {"role": "user"|"assistant", "content": str}

    def add_user_message(self, msg: str):
        self.history.append({"role": "user", "content": msg})

    def add_agent_message(self, msg: str):
        self.history.append({"role": "assistant", "content": msg})

    def get_context_prompt(self):
        return self.history[-10:]  # Return last 10 messages (adjust as needed)
