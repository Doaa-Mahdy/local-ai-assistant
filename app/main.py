import gradio as gr
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama:7b-instruct"


def stream_response(prompt, history):
    system_prompt = (
        "You are an expert competitive programming assistant. "
        "Return clean, efficient C++ code. Keep explanations minimal."
    )

    full_prompt = system_prompt + "\n\n"

    for user, assistant in history:
        full_prompt += f"User: {user}\nAssistant: {assistant}\n"

    full_prompt += f"User: {prompt}\nAssistant:"

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": full_prompt,
            "stream": True
        },
        stream=True
    )

    result = ""
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode("utf-8"))
                chunk = data.get("response", "")
                result += chunk
                yield result
            except:
                continue


def chat(user_input, history):
    history = history or []
    output = ""

    for partial in stream_response(user_input, history):
        output = partial
        yield history + [(user_input, output)]

    history.append((user_input, output))


def clear_chat():
    return []


# 🎨 Custom CSS (THIS is the magic)
custom_css = """
#chatbot {
    height: 500px;
    overflow: auto;
}

.gradio-container {
    max-width: 900px !important;
    margin: auto;
}

textarea {
    font-size: 16px !important;
}

button {
    height: 50px !important;
    border-radius: 12px !important;
}
"""

with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as app:

    gr.Markdown(
        """
        # 💻 Local AI Coding Assistant  
        ### ⚡ Fast • Local • C++ Focused
        """
    )

    chatbot = gr.Chatbot(
        elem_id="chatbot",
        bubble_full_width=False,
        show_label=False
    )

    with gr.Row():
        msg = gr.Textbox(
            placeholder="Ask for code (e.g., segment tree, binary search...)",
            lines=2,
            scale=4,
            show_label=False
        )
        send = gr.Button("🚀", scale=1)

    clear = gr.Button("🗑 Clear Chat")

    state = gr.State([])

    send.click(chat, [msg, state], chatbot)
    msg.submit(chat, [msg, state], chatbot)

    clear.click(fn=lambda: [], outputs=chatbot, queue=False)

app.queue().launch()