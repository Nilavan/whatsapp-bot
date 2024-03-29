import asyncio
from rasa.core.agent import Agent

class Model:
    def __init__(self, url: str) -> None:
        self.agent = Agent.load(model_path=url)
        print("NLU model loaded")

    def message(self, message: str) -> str:
        message = message.strip()
        result = asyncio.run(self.agent.parse_message(message))
        return result['intent']['name'], result['intent']['confidence']

model1 = Model("models/nlu-20240326-232920-purple-compete.tar.gz")
intent, conf = model1.message("forest fire")
print(intent, conf)

model2 = Model("models/nlu-20240327-191236-icy-aside.tar.gz")
intent, conf = model2.message("social media")
print(intent, conf)