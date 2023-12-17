import streamlit as st
from typing import List


class ConversationCompressConfig:
    def __init__(
        self,
        *,
        enabled,
        max_human_conv_reserve_count=None,
        max_robot_conv_reserve_count=None,
        enable_first_conv=None,
    ) -> None:
        self.enabled = enabled
        self.max_human_conv_reserve_count = max_human_conv_reserve_count
        self.max_robot_conv_reserve_count = max_robot_conv_reserve_count
        self.enable_first_conv = enable_first_conv

    def get_message_list(
        self, system_prompt: str, conv_users: List[str], conv_robots: List[str]
    ):
        if self.enabled:
            return self._get_compressed_message_list(
                system_prompt, conv_users, conv_robots
            )
        else:
            return self._get_full_message_list(system_prompt, conv_users, conv_robots)

    @property
    def message_tokens(self):
        if self.enabled:
            return self.compressed_message_tokens
        else:
            return self.full_message_tokens

    @property
    def full_message_tokens(self):
        ms = self._get_full_message_list()
        txt = "".join(m["content"] for m in ms)
        tokens = get_tokenizer().tokenize(txt)
        return len(tokens)

    @property
    def compressed_message_tokens(self):
        ms = self._get_compressed_message_list()
        txt = "".join(m["content"] for m in ms)
        tokens = get_tokenizer().tokenize(txt)
        return len(tokens)

    def _get_full_message_list(
        self, system_prompt: str, conv_users: List[str], conv_robots: List[str]
    ):
        """Get full message list (for Chat Completion)"""
        message_list = []
        # Add system prompt
        if system_prompt:
            message_list.append({"role": "system", "content": system_prompt})
        # Add history conversations
        for conv_user, conv_robot in zip(conv_users, conv_robots):
            message_list.append({"role": "user", "content": conv_user})
            message_list.append({"role": "assistant", "content": conv_robot})
        return message_list

    def _get_compressed_message_list(
        self, system_prompt: str, conv_users: List[str], conv_robots: List[str]
    ):
        """Get compressed message list (for Chat Completion)"""
        message_list = []
        # Add system prompt
        if system_prompt:
            message_list.append({"role": "system", "content": system_prompt})
        # Add history conversations but compressed
        turns_count = min(len(conv_users), len(conv_robots))
        for turn_idx in range(turns_count):
            should_keep_human = False  # should keep human conversations at this turn
            should_keep_robot = False  # should keep robot conversations at this turn
            if turn_idx == 0 and self.enable_first_conv:
                should_keep_human, should_keep_robot = True, True
            if turn_idx + self.max_human_conv_reserve_count >= turns_count:
                should_keep_human = True
            if turn_idx + self.max_robot_conv_reserve_count >= turns_count:
                should_keep_robot = True
            # Add conversations to message_list
            if should_keep_human or should_keep_robot:
                conv_user = conv_users[turn_idx] if should_keep_human else ""
                conv_robot = conv_robots[turn_idx] if should_keep_robot else ""
                message_list.append({"role": "user", "content": conv_user})
                message_list.append({"role": "assistant", "content": conv_robot})

        return message_list
