import requests
import os

class LLMHelper:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.base_url = 'https://api.openai.com/v1/chat/completions'

    def generate_explanation(self, diagnosis, input_values):
        if not self.api_key:
            return "LLM не настроен. Пожалуйста, установите OPENAI_API_KEY."

        prompt = f"Объясни диагноз '{diagnosis}' на основе следующих значений признаков: {input_values}. Используй простой язык."

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 200
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"Ошибка при генерации объяснения: {str(e)}"