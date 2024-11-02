# Limestone: An interactive chatbot

<center>

![banner](assets/banner.png)

Limestone is a personalized and highly customizable Telegram bot that allows you to interact with a local instance of an LLM. With Limestone, you can chat, search, generate content, and more, all within the Telegram app.

</center>

## Project Overview

This project aims to provide an accessible way to interact with GPT-based Language Models. By utilizing Telegram as a frontend, we ensure secure messaging and protect user data from potential leaks. The project enables users to run their Language Models privately and securely as long as you trust Telegram as a platform.

## Getting Started

### Installation

1. Set up and launch [SGLang](https://github.com/sgl-project/sglang) with your preferred model and configuration.

3. Clone the repository:
```bash
git clone https://github.com/bkutasi/limestone
```

4. Create a new virtual environment with Python 3.13
```bash	
pyton -m venv env
source env/bin/activate
```

5. Install required packages
```bash
pip install -r requirements.txt
```

7. Create a Telegram bot and obtain the token through [BotFather](https://telegram.me/BotFather). Additional bot documentation is available [here](https://core.telegram.org/bots#6-botfather) and [here](https://core.telegram.org/bots/tutorial). Then make you config.yaml file based on the config.example.yml file

### Server Launch

```bash
python main.py
```

Note: Server-side encryption is not implemented. Not recommended for production use without proper security measures.

## Supported Models

For models, pick your choice form [Open LLM leaderboard](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard)

## Development Roadmap

### Short Term
- Streaming implementation (Completed)
- Multiple personalities (In Progress)
- Code cleanup and refactoring (First pass complete)
- Conversation history implementation (First pass complete)
- Model testing and integration
- Performance optimization
- Long-term memory implementation
- AgentOoba integration
- Testing and CI/CD implementation
- User whitelisting system

### Medium Term
- API integration for document retrieval and search
- Langchain integration
- Vector database implementation
- Concurrent request handling (Completed)

### Long Term
- Public deployment with token/message limitations

## Technical Limitations

Current LLM limitations include:
- Potential for generating incorrect or inconsistent responses
- Limited common sense reasoning
- Knowledge constraints based on training data
- Potential training data biases
- Limited emotional understanding
- Context interpretation challenges

## Acknowledgements

- [LLaMA](https://github.com/facebookresearch/llama)
- [Self-instruct](https://github.com/yizhongw/self-instruct)
- [Alpaca](https://github.com/tatsu-lab/stanford_alpaca)
- [Vicuna](https://github.com/lm-sys/FastChat)
- [Oobabooga](https://github.com/oobabooga)
- Additional upcoming models
- Community contributors
