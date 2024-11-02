from typing import List, Dict, Any


class PromptHelper:
    @staticmethod
    async def generate_prompt(
        template_name: str,
        user_input: str,
        templates: Dict[str, Any],
        conversation_memory: Dict[int, List[Dict[str, str]]],
        chat_id: int,
    ) -> str:
        """
        Generate a full prompt for a model using a selected template, current user input,
        and conversation memory.

        Args:
            template_name (str): The name of the template to be used for generating the prompt.
            user_input (str): The current user input to be included in the prompt.
            templates (Dict[str, Any]): A dictionary of templates loaded from a YAML or other source.
            conversation_memory (Dict[int, List[Dict[str, str]]]): A dictionary of previous user inputs and assistant outputs, indexed by chat ID.
            chat_id (int): The unique ID of the chat whose conversation memory is being used.

        Returns:
            str: The full prompt to be sent to the language model.

        Raises:
            ValueError: If the specified template name is not found in the templates dictionary.
        """
        # Retrieve the template data for the specified template name
        template_data = templates.get(template_name)
        if not template_data:
            raise ValueError(f"Template '{template_name}' not found.")

        # Extract the system prompt and prompt template from the template data
        system_prompt = template_data["system_prompt"]
        prompt_template = template_data["prompt_template"]

        # Initialize the messages list with the system prompt
        messages = [{"role": "system", "content": system_prompt}]

        # Retrieve the conversation history for the given chat_id
        chat_conversation = conversation_memory.get(chat_id, [])

        # Add each message from the conversation history to the messages list
        for case in chat_conversation:
            messages.append({"role": "user", "content": case["input"]})
            messages.append({"role": "assistant", "content": case["output"]})

        # Check if the current user input is already in the conversation history
        if not chat_conversation or chat_conversation[-1]["input"] != user_input:
            # Add the current user input to the messages list only if it's not already there
            messages.append({"role": "user", "content": user_input})
            # Add an empty assistant message to prompt for a response
            messages.append({"role": "assistant", "content": ""})

        # Generate the full prompt by applying the appropriate template to each message
        full_prompt = ""
        for message in messages:
            role = message["role"]
            content = message["content"]

            # Apply the correct template based on the message role
            if role == "system":
                full_prompt += prompt_template["header"].format(system_prompt=content)
            elif role == "user":
                full_prompt += prompt_template["user"].format(input=content)
            elif role == "assistant":
                full_prompt += prompt_template["output"].format(output=content)

        return full_prompt
