from dataclasses import dataclass
from datetime import datetime
import json
import os 
from dotenv import load_dotenv
from src.clients import AnthropicClient, BaseClient, MessageOptions
from src.processors.repd_processor import REPDProcessor
from src.prompts import prompt_nimby_analysis, prompt_evaluator, prompt_reseacher
from pydantic import BaseModel
import pandas as pd 
load_dotenv()

class AgentEval(BaseModel):
    accuracy: str
    reasoning: str

class NimbyFormat(BaseModel):
    header: str
    nimby_score: int
    certainty: int
    certainty_meta: str
    interesting_information: list[str]
    organised_nimby: list[str]

class Evaluation(BaseModel):
    certainty: float
    accuracy: float

class WebResponse(BaseModel):
    summary:str
    potential_sources:list[str] | None
    likelihood:str
    perpetrators:str

@dataclass 
class AppConfig:
    api_key: str = os.getenv('CLAUDE_API_KEY')

class NimbyAgent:
    def __init__(self, client: BaseClient, processor = REPDProcessor):
        self.client = client
        self.search_client = client
        self.repd_processor = processor
    
    def run_search(self, context, prompt_func=prompt_reseacher):
        prompt_val = prompt_func(context=context)
        message = self.client.call_json(prompt_val, json_model=WebResponse, tools='web')
        while message.text.stop_reason == "tool_use":
            tool_use_blocks = [block for block in message.text.content if block.type == "tool_use"]
            message = self.client.call_json(
                prompt_val + tool_use_blocks,  # Or build on the conversation
                json_model=WebResponse,
                tools='web'
            )
        text_blocks = [block.text for block in message.text.content if hasattr(block, 'text')]
        return text_blocks
    
    
    def get_processor(self):
        return self.repd_processor

    def run_singular(self, context, prompt_func=prompt_nimby_analysis) -> NimbyFormat:
        """Run singular agent message, add context.

        Args:
            context: Context for message. Serializable into string.
            prompt: function that returns an initial prompt.

        Returns:
            MessageResponse: Message response
        """
        prompt = prompt_func(context=context)
        message = self.client.call_json(prompt, json_model=NimbyFormat).text.content[0].text
        nimby = NimbyFormat.model_validate_json(message.text)
        return nimby 

    def run(self, max_values:int = 2, prompt_func=prompt_nimby_analysis) -> list[tuple[pd.Series, NimbyFormat]]:
        """Runs across current list of context values

        Args:
            max_values [int]: max values to iterate across on.
            prompt [func]: function containing a prompt to run, defaults to nimby analysis prompt

        Returns:
            list[tuple[pd.Series, NimbyFormat]]: Returns a list of values containing context and output
        """
        df = self.repd_processor.load()
        context = self.repd_processor.filter_by_cancelled(df)
        current = 0
        messages = []

        for _, row in context.iterrows():
            if current >= max_values:
                break
            prompt = prompt_func(context=row.to_dict())
            message = self.client.call_json(prompt, json_model=NimbyFormat).text.content[0].text
            nimby = NimbyFormat.model_validate_json(message.text)
            messages.append((row, nimby))
            current += 1
        return messages
    
    def eval(self, results: list[tuple[pd.Series, NimbyFormat]]) -> Evaluation:
        """Evaluate for certainty and accuracy.

        Args:
            results (list[tuple[pd.Series, NimbyFormat]]): _description_

        Returns:
            Evaluation: _description_
        """
        certainties = []
        accuracies = []

        accuracy_levels = {'certain': 100, 'high': 80, 'medium': 40, 'low': 0}
        options = MessageOptions(max_tokens=150)
        for row, output in results:
            certainties.append(output.certainty)
            prompt = prompt_evaluator(row.to_dict(), output)
            accuracy_eval = self.client.call_json(prompt, json_model=AgentEval, options=options)
            agent_eval = AgentEval.model_validate_json(accuracy_eval.text.strip())
            if agent_eval.accuracy in accuracy_levels:
                accuracies.append(accuracy_levels[agent_eval.accuracy])


        certainty = sum(certainties)/len(certainties)
        accuracies = sum(accuracies)/len(accuracies)
        return Evaluation(
            certainty=certainty,
            accuracy=accuracies
        )

def log_eval(result:dict, path='eval_log.json'):
    result['timestamp'] = datetime.now().isoformat()

    with open(path, 'a') as f:
        f.write(json.dumps(result) + '\n')

async def main_async():
    cfg = AppConfig()
    client = AnthropicClient(api_key=cfg.api_key, temperature= 0.9)
    processor = REPDProcessor()
    agent = NimbyAgent(client=client, processor=processor)
    messages = await agent.run_async()
    return messages

def main():
    cfg = AppConfig()
    client = AnthropicClient(api_key=cfg.api_key, temperature= 0.9)
    processor = REPDProcessor()
    agent = NimbyAgent(client=client, processor=processor)
    messages = agent.run()
    evals = agent.eval(messages)
    log_eval(evals.model_dump())
    return messages

def message_test():
    cfg = AppConfig()
    client = AnthropicClient(api_key=cfg.api_key, temperature= 0.9)
    processor = REPDProcessor()

    data = processor.process_pipeline()

    agent = NimbyAgent(client=client, processor=processor)


if __name__ == "__main__":
    main()
