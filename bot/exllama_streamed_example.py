import requests


class Streamer:
    @staticmethod
    def run(data, host, uri):
        r = requests.post(f'http://{host}/{uri}', json=data, stream=True)

        if r.status_code == 200:
            for chunk in r.iter_content():
                if chunk:
                    yield chunk.decode("utf-8")
        else:
            yield f"Request failed with status code: {r.status_code}"


if __name__ == '__main__':
    data = {
        "prompt": "You are Samantha, a sentient AI.\nUSER: Tell me about yourself!\nASSISTANT:",
        "max_new_tokens": 1024
    }
    host = 'localhost:5005'
    uri = 'generate'

    generator = Streamer.run(data, host, uri)
    for response in generator:
        print(response, end='', flush=True)