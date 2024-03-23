import asyncio
from rasa.core.agent import Agent

class Model:
    def __init__(self, url: str) -> None:
        self.agent = Agent.load(model_path=url)
        print(self.agent)
        print("NLU model loaded")

    def message(self, message: str) -> str:
        message = message.strip()
        result = asyncio.run(self.agent.parse_message(message))
        print(result)
        return result['intent']['name']

model1 = Model("nlu-20240313-095913-ascent-originator.tar.gz")
intent = model1.message("forest fires")
print(intent)