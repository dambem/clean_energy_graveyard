from dataclasses import dataclass
import json
import os 
from dotenv import load_dotenv
from src.clients import AnthropicClient, BaseClient, MessageResponse
from src.processors.repd_processor import REPDProcessor
from src.prompts import nimby_analysis
from pydantic import BaseModel
load_dotenv()



class NimbyFormat(BaseModel):
    header: str
    nimby_score: int
    certainty: int
    certainty_meta: str
    interesting_information: list[str]

@dataclass 
class AppConfig:
    api_key: str = os.getenv('CLAUDE_API_KEY')

class NimbyAgent:
    def __init__(self, client: BaseClient, repd_source:str | None = 'src/data/REPD_Publication_Q3_2025.csv'):
        self.client = client
        self.repd_processor = REPDProcessor(src=repd_source)

    def run_singular(self, context) -> NimbyFormat:
        """Run singular agent message, add context.

        Args:
            context: Context for message. Serializable into string.

        Returns:
            MessageResponse: Message response
        """
        prompt = nimby_analysis(context=context)
        message = self.client.call_json(prompt, json_model=NimbyFormat)
        
        return message

    def run(self) -> list[NimbyFormat]:
        df = self.repd_processor.load()
        context = self.repd_processor.filter_by_cancelled(df)
        max_values = 1
        current = 0
        messages = []

        for n in context.iterrows():
            if current >= max_values:
                break
            prompt = nimby_analysis(context=n)
            message = self.client.call_json(prompt, json_model=NimbyFormat)
            messages.append(message)
            current += 1

        nimby = [NimbyFormat.model_validate_json(message.text) for message in messages]
        return nimby
    
    def eval(self, context: list[str], outputs: list[NimbyFormat]):
        print('Running Agent Evaluation...')
        print('')




def main():
    cfg = AppConfig()
    client = AnthropicClient(api_key=cfg.api_key)
    agent = NimbyAgent(client=client)
    messages = agent.run()
    for n in messages:
        print(n.certainty)
    return messages

if __name__ == "__main__":
    print(main())    