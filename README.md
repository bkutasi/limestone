# Limestone: An interactive chatbot
<div align=center>
<img src="assets/banner.png" width = "640" alt="banner" align=center />

⚡Limestone is a personalized and highly customizable Telegram bot that allows you to interact with a local instance of LLM, a powerful natural language processing system. With Limestone, you can chat, search, generate content, and more, all within the Telegram app.⚡
</div>

## ✨ Latest News

- [05/11/2023]: Streaming is added! New models, chatting works.
- [04/28/2023]: Initial release with instruction functionality.

## 🤔 Motivation

- Everybody needs an easily accessible way to interact with GPT-like LMMs. Additionally, the project provides way for anyone to run their LLM privately and securely. By using telegram as a frontend, we can ensure that the messaging is secure and the user's data is not being leaked. 

- Personalized chatbots are currently spreading but fear and uncertainty stops them from being a truly personalized solution for the masses.

## 🎬 Get started

### Install

Get oobabooga/text-generation-webui 1 click installer from [here](https://github.com/oobabooga/text-generation-webui#one-click-installers). And leunch it. Follow the instructions on the repo.

Download a model to test from [here](https://huggingface.co/models?filter=llm) download all the files and put it into a folder in `models`. The recommended models are [WizardLM](https://huggingface.co/TheBloke/wizardLM-7B-GPTQ) and [GTP4-X-Alpaca](https://huggingface.co/anon8231489123/gpt4-x-alpaca-13b-native-4bit-128g).

After running txtgen and its working clone this repo:
```bash
git clone https://github.com/bkutasi/limestone
```
Make a telegram bot and get the token. Follow the instructions [here](https://telegram.me/BotFather). More information about bots [here](https://core.telegram.org/bots#6-botfather) and [here](https://core.telegram.org/bots/tutorial).

### Chatbot server launch

```bash
python server.py
```
Every communication is printed to the console for now. Nothing is encrypted on the server side. Do not use this in production without proper security measures. You have been warned.


## 🐼 Models
### Overview of tested models
| Model                         | Backbone |  #Params | Tested               | Open-source data | Claimed language | Post-training (instruction) | VRAM required | Release date |
|-------------------------------|----------|---------:|------------------:|-----------------:|-----------------:|----------------------------:|-----------------------------:|-------------:|
| [GPT4-X-Alpaca](https://huggingface.co/anon8231489123/gpt4-x-alpaca-13b-native-4bit-128g)      | LLaMA    |      13B |                 ✅ |      ✅ |     en |           52K, en | 12 Gb |     04/25/23 |
| [WizardLM](https://github.com/nlpxucan/WizardLM)                          | LLaMA    |       7B |             ✅ |            ✅ |         en |   70K, en,  |                       8 Gb |     04/01/23 |
| [WizardLM-uncensored](https://huggingface.co/ehartford/WizardLM-7B-Uncensored)       | LLaMA    |       7B |                 ✅ |            ✅ |         en |   70K-decen, en |    8 Gb |     05/04/23 |
| [WizardVicunaLM](https://huggingface.co/junelee/wizard-vicuna-13b)        | LLaMA    |       13B |                 ✅ |     ✅ |         en |   70K+conv, en |                    12 Gb |     05/04/23 |
<details><summary><b>The models recommended here have been tested and suitable for usage with limitations.</b></summary>

> The models use the excellent LlaMa as base model fine-tuned with **instructions**. GPT4-X-Alpaca has a low level of filtering and it has tuned with GPT4, while WizardLM has excellent performance and low memory footprint while outperforming ChatGPT(chatgpt-3.5-turbo) on certain domains by using [Evol-Instruct](https://github.com/nlpxucan/evol-instruct). The rationale behind using these models is that the **instruction** data helps to tame language models to adhere to human instructions and fulfill their information requirements.
</details>


## 🧐 Evaluation and Benchmark

One shot instruction performance is the same as the base model. Currently, no memory and thread saving is implemented.


## 👾 Quantization

Currently, the GPTQ 4bit quantization are recommended. GGML is viable if you have an excellent CPU or mac, but it's generally slower than with a recent GPU. If you search for a model on Huggingface and insert -4bit or -GPTQ you will find compatible versions.

## 🏭 Deployment

Docker and maybe orchestration coming soon.

### Launch ooba's text generation webui, after editing the launch parameters in webui.py line 146:
```bash
python server.py --chat --model WizardLM-13B-uncensored-4bit-128g --auto-devices --wbits 4 --groupsize 128 --model_type=llama --gpu-memory 9 --api
```

### Launch the chat server
```bash
python server.py
```
Go into the models section and check if the model is properly loaded.
### Talk with the bot on telegram

Now, you have your custom chatbot!

## 🛣️ Roadmap
🚧 - work in progress
❌ - not yet started
### 🎯 Short Term
 - 🚧 Multiple personalities
 - 🚧 Pseudo streaming.
 - 🚧 Code cleanup and refactoring.
 - 🚧 Save the conversation history to a database per user.
 - 🚧 Implement [long-term-memory](https://github.com/wawawario2/long_term_memory) for each user.
 - 🚧 Investigate more models.
 - 🚧 Increase inference and processing speed, eliminate bottlenecks and bugs.
 - ❌ Implement robust testing and CI/CD.
 - ❌ Allow users to get whitelisted.

### 📈 Medium Term
 - ❌ Integrate with other APIs to allow for document retrieval, search and others.
 - ❌ Integrate [Langchain](https://github.com/hwchase17/langchain#quick-install), [docs](https://python.langchain.com/en/latest/use_cases/question_answering.html).
 - ❌ Vector database for faster search.

### 🌟Long Term
 - ❌ Allow anyone to engage with the bot freely for a limited amount of tokens.
  - ❌ Commercialize the project.


## 🤖 Limitations

All the models one can find on the internet have limitations. The common current limitations of current LLM the models are:

- Hallucinations: the models may generate responses that are factually incorrect or inconsistent with the context of the conversation.

- Lack of common sense: the models may not always have the ability to apply common sense knowledge to situations, which
  can lead to nonsensical or inappropriate responses.

- Limited knowledge domain: the models' knowledge is based on the data it was trained on, and it may not have the
  ability to provide accurate or relevant responses outside that domain.

- Biases: the models may have biases that reflect the biases in the data it was trained on, which can result in
  unintended consequences or unfair treatment.

- Inability to understand emotions: While the models can understand language, it may not always be able to understand
  the emotional tone behind it, which can lead to inappropriate or insensitive responses.

- Misunderstandings due to context: the models may misunderstand the context of a conversation, leading to
  misinterpretation and incorrect responses.

## Acknowledgements

- LLaMA: https://github.com/facebookresearch/llama
- Self-instruct: https://github.com/yizhongw/self-instruct
- Alpaca: https://github.com/tatsu-lab/stanford_alpaca
- Vicuna: https://github.com/lm-sys/FastChat
- Oobabooga: https://github.com/oobabooga
- Other upcoming models
- You, the community