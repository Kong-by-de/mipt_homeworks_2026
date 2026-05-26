from openai import OpenAI


class LLMClient:
    def __init__(self, api_key, api_host, temperature=0.7):
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_host,
        )
        self.temperature = temperature

    def ask(self, messages, stream=False):
        try:
            response = self.client.chat.completions.create(
                model='default',
                messages=messages,
                temperature=self.temperature,
                stream=stream,
            )

            if stream:
                # выводим ответ по мере генерации, чтобы пользователь видел прогресс
                full_text = ''
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        token = chunk.choices[0].delta.content
                        print(token, end='', flush=True)
                        full_text += token
                print()  # новая строка после полного ответа
                return full_text
            else:
                return response.choices[0].message.content

        except KeyboardInterrupt:
            # перехватываем ctrl c только во время ожидания ответа от модели
            print('\n[Запрос прерван пользователем]')
            return None
        except Exception as e:
            print(f'\n[Ошибка API: {e}]')
            return None