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
            str: The full prompt to be sent to the language model, including the system prompt,
                 conversation history, and the current input.

        Raises:
            ValueError: If the specified template name is not found in the templates dictionary.
        """

        # Extract the template from the dictionary
        template_data = templates.get(template_name)

        if template_data:
            # Extract system prompt and template structure
            system_prompt = template_data["system_prompt"]
            prompt_template = template_data["prompt_template"]

            # Get conversation history for the given chat_id
            chat_conversation = conversation_memory.get(chat_id, [])

            # Start building the prompt from the header
            header = prompt_template["header"].format(system_prompt=system_prompt)

            # Remake the chat conversation so it adds the fluff around the in/outputs
            conversation_history = ""
            for case in chat_conversation:
                # Process user input
                formatted_user = prompt_template["user"].format(input=case["input"])
                # Process assistant output
                formatted_assistant = prompt_template["output"].format(
                    output=case["output"]
                )

                # Add them to conversation history
                conversation_history += formatted_user + formatted_assistant

            # Now add the current user input with an empty output field for the assistant
            current_user = prompt_template["user"].format(input=user_input)
            current_assistant = prompt_template["output"].format(output="")

            # Append the conversation history to the prompt
            full_prompt = (
                header + conversation_history + current_user + current_assistant
            )

            return full_prompt
        else:
            raise ValueError(f"Template '{template_name}' not found.")
