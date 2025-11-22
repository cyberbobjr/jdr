"""
History processors for PydanticAI agents.
Handles message summarization to manage token limits.
"""

import tiktoken
from typing import List
from pydantic_ai import Agent, ModelMessage
from pydantic_ai.messages import ModelResponse, TextPart, UserPromptPart, SystemPromptPart
from back.config import get_llm_config

# Initialize tokenizer (using cl100k_base which is standard for GPT-4/3.5/DeepSeek)
try:
    tokenizer = tiktoken.get_encoding("cl100k_base")
except Exception:
    # Fallback if encoding not found
    tokenizer = tiktoken.get_encoding("gpt2")

def count_tokens(text: str) -> int:
    """
    Count tokens in a text string.
    """
    return len(tokenizer.encode(text))

def estimate_history_tokens(messages: List[ModelMessage]) -> int:
    """
    Estimate total tokens in a message history.
    Iterates through parts of each message.
    """
    total = 0
    for msg in messages:
        if hasattr(msg, 'parts'):
            for part in msg.parts:
                if hasattr(part, 'content') and isinstance(part.content, str):
                    total += count_tokens(part.content)
    return total

async def summarize_old_messages(messages: List[ModelMessage]) -> List[ModelMessage]:
    """
    Summarize old messages if the total token count exceeds the configured limit.
    
    Strategy:
    1. Check if token count > limit.
    2. If yes, keep the last N messages (configured).
    3. Keep the system prompt (assumed to be the first message if present).
    4. Summarize the messages in between.
    5. Return [SystemPrompt, SummaryMessage, ...RecentMessages].
    """
    llm_config = get_llm_config()
    token_limit = llm_config.token_limit
    keep_last_n = llm_config.keep_last_n_messages

    current_tokens = estimate_history_tokens(messages)
    
    if current_tokens <= token_limit:
        return messages

    # If we have fewer messages than the keep limit + 1, we can't summarize much.
    if len(messages) <= keep_last_n:
        return messages

    # Identify System Prompt
    system_prompt_msg = None
    start_index = 0
    if messages and isinstance(messages[0].parts[0], SystemPromptPart):
        system_prompt_msg = messages[0]
        start_index = 1

    # Split messages
    # Messages to summarize: from start_index up to (total - keep_last_n)
    # Recent messages: last keep_last_n
    end_index = len(messages) - keep_last_n
    
    if start_index >= end_index:
        return messages

    msgs_to_summarize = messages[start_index:end_index]
    recent_messages = messages[end_index:]

    # Create a temporary agent for summarization
    # We use a lightweight prompt
    summarizer_agent = Agent(
        model=llm_config.model, # Use same model for now
        system_prompt="You are a helpful assistant that summarizes conversation history.",
    )

    # Format messages for the summarizer
    # We can't pass ModelMessage objects directly as context easily if they contain tool calls 
    # that the summarizer doesn't know about. 
    # Safest is to convert to a text transcript.
    transcript = ""
    for msg in msgs_to_summarize:
        role = "unknown"
        content = ""
        for part in msg.parts:
            if isinstance(part, UserPromptPart):
                role = "User"
                content += str(part.content)
            elif isinstance(part, ModelResponse): # ModelResponse is a message, not a part usually, but structure varies
                 pass # PydanticAI structure is Message -> Parts
            elif hasattr(part, 'content'):
                 content += str(part.content)
            
            # Determine role from message type if possible, or part type
            # Simplified for transcript:
        
        # Better approach: just extract text content
        # PydanticAI messages are complex. Let's try to just dump them to string representation
        transcript += f"{msg}\n"

    summary_prompt = (
        "Please summarize the following conversation history into a single concise paragraph. "
        "Retain key information, decisions, and current state. "
        "Ignore specific tool call details unless they changed the state significantly.\n\n"
        f"TRANSCRIPT:\n{transcript}"
    )

    try:
        result = await summarizer_agent.run(summary_prompt)
        summary_text = result.data
    except Exception as e:
        # Fallback if summarization fails
        summary_text = f"[Error during summarization: {e}. Previous context omitted.]"

    # Create the summary message
    # We present it as a ModelResponse or a UserPrompt? 
    # Usually it's better to present it as a System note or a previous Model response.
    # Let's make it a ModelResponse to fit the flow, or a SystemPromptPart if we could merge it.
    # But we want to return a list of ModelMessage.
    
    # We will insert a User message saying "Previous summary:" and a Model message with the summary?
    # Or just a System message? PydanticAI agents usually take a list of messages.
    # Let's create a ModelResponse that acts as the "memory".
    
    summary_message = ModelResponse(
        parts=[TextPart(content=f"**SYSTEM SUMMARY OF PAST EVENTS**:\n{summary_text}")]
    )

    new_history = []
    if system_prompt_msg:
        new_history.append(system_prompt_msg)
    
    new_history.append(summary_message)
    new_history.extend(recent_messages)

    return new_history
