from dataclasses import dataclass
import os 
from dotenv import load_dotenv
from src.clients import AnthropicClient
load_dotenv()

@dataclass 
class AppConfig:
    api_key: str = os.getenv('CLAUDE_API_KEY')

def main():
    print('test')


if __name__ == "__main__":
    cfg = AppConfig()
    message = AnthropicClient(api_key=cfg.api_key).call("What is the capital of France?")
    print(message.text)
    print(message.input_tokens)
    print(message.output_tokens)
    main()