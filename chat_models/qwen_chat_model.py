import dashscope
import streamlit as st
from http import HTTPStatus


class QwenChat:
    def __init__(self, model_name, api_key=None) -> None:
        if api_key is None:
            api_key = st.secrets["Qwen"]["DASHSCOPE_API_KEY"]
        dashscope.api_key = api_key
        self.model_name = model_name
        M = dashscope.Generation.Models
        assert model_name in (M.qwen_max, M.qwen_plus, M.qwen_turbo)

    def chat_completion_sync(self, message_list, temperature=0.0, max_tokens=32):
        r = dashscope.Generation.call(
            self.model_name,
            messages=message_list,
            temperature=temperature,
            max_tokens=max_tokens,
            result_format="message",  # set the result to be "message" format.
            stream=False,
        )
        if r.status_code != HTTPStatus.OK:
            print(
                f"Request id: {r.request_id}, Status code: {r.status_code}, error code: {r.code}, error message: {r.message}"
            )
            return None
        print(r)
        answer = r["output"]["choices"][0]["message"]["content"]
        finish_reason = r["output"]["choices"][0]["finish_reason"]
        response = {
            "choices": [
                {
                    "message": {"content": answer, "role": "assistant"},
                    "finish_reason": finish_reason,
                }
            ],
            "usage": {
                "prompt_tokens": r["usage"]["input_tokens"],
                "completion_tokens": r["usage"]["output_tokens"],
                "total_tokens": r["usage"]["total_tokens"],
            },
        }
        return response
