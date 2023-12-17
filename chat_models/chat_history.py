from chat_models.qwen_chat_model import QwenChat
from chat_models.conversation_config import ConversationCompressConfig


class ChatHistory:
    def __init__(self, llm_model_name: str, cc_config: ConversationCompressConfig):
        self.history = []

        self.model_name = llm_model_name
        self.client = QwenChat(self.model_name)
        self.cc_config = cc_config

        self._system_prompt = ""
        self._conv_users = []
        self._conv_bots = []

    def reset(self, system_prompt: str):
        self._system_prompt = system_prompt
        self._conv_users = []
        self._conv_bots = []

    def call_chat(self, chat_text: str) -> str:
        # get history message list
        message_list = self.cc_config.get_message_list(
            self._system_prompt, self._conv_users, self._conv_bots
        )
        message_list.append({"role": "user", "content": chat_text})
        # call model then get answer
        response = self.client.chat_completion_sync(message_list)
        answer = response["choices"][0]["message"]["content"]
        # add to conv history
        self._add_user_chat(chat_text)
        self._add_bot_chat(answer)
        return answer

    def _add_user_chat(self, chat_text: str):
        self._conv_users.append({"role": "user", "content": chat_text})

    def _add_bot_chat(self, chat_text: str):
        self._conv_bots.append({"role": "assistant", "content": chat_text})
