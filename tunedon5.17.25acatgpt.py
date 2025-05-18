import tkinter as tk
from tkinter import Frame, Canvas, Scrollbar, Entry, Button, Listbox, END, Toplevel, Text
import contextlib
import io
import random
import re

# -------------------------------------------------------------
#  Minimal Chat-GPT style UI using pure tkinter
#  ------------------------------------------------------------
#  • Left sidebar with "New Chat" button + list of previous chats
#  • Central conversation pane with message bubbles (assistant left, user right)
#  • Bottom prompt bar with Entry + Send button
#  • Very small placeholder engine (O3MiniCopycat) to generate replies
#  • Code blocks detected and rendered in monospace box with optional Run button
#  ------------------------------------------------------------
#  Written for Python 3.11+.  No external dependencies.
#  Author: ChatGPT (OpenAI o3) – 2025-05-17
# -------------------------------------------------------------


class O3MiniCopycat:
    """Tiny deterministic stub that produces playful replies.
    Replace this with your real model / API calls later."""

    def __init__(self):
        self.history = []
        self.greetings = [
            "Meow! How can I assist you today?",
            "Hello! Catseek R1 at your service, nyah.",
            "Hey! What do you want to hack today?",
        ]
        self.fallbacks = [
            "Hmm, that's interesting! Tell me more.",
            "Mrow? Can you rephrase that?",
            "Sorry, I didn't quite catch that—wanna try again?",
        ]
        self.jokes = [
            "Why did the cat get a laptop? For purr-sonal use!",
            "I'm not lazy, I'm just on low power mode.",
            "If I fits, I sits—especially in Python scripts.",
        ]
        self.affirmations = [
            "You got this, cutie!",
            "Keep going, your code claws are strong.",
            "Every bug is just a feature in disguise, meow.",
        ]
        self.code_examples = [
            "Sure! Here's a Python function that returns a cat sound:\n```python\ndef cat_sound():\n    return 'meow!'\n```",
            "Try this quicksort, nyah:\n```python\ndef quicksort(arr):\n    if len(arr) <= 1: return arr\n    p = arr[0]\n    return quicksort([x for x in arr[1:] if x < p]) + [p] + quicksort([x for x in arr[1:] if x >= p])\n```",
            "Here’s how you print in Python:\n```python\nprint('CATSEEK R1 claws the matrix!')\n```",
        ]

    def tokenize(self, text: str):
        return text.lower().split()

    def _intent(self, tokens):
        if any(w in tokens for w in ("hi", "hello", "hey", "meow")):
            return "greet"
        if any(w in tokens for w in ("joke", "pun", "funny")):
            return "joke"
        if any(w in tokens for w in ("sad", "depressed", "upset", "help", "lonely")):
            return "affirm"
        if any(w in tokens for w in ("code", "python", "script", "function", "def")):
            return "code"
        if "?" in tokens or any(w in tokens for w in ("what", "who", "why", "how", "where")):
            return "question"
        return "fallback"

    def generate(self, prompt: str) -> str:
        tokens = self.tokenize(prompt)
        intent = self._intent(tokens)
        if intent == "greet":
            reply = random.choice(self.greetings)
        elif intent == "joke":
            reply = random.choice(self.jokes)
        elif intent == "affirm":
            reply = random.choice(self.affirmations)
        elif intent == "code":
            reply = random.choice(self.code_examples)
        elif intent == "question":
            reply = "That's a good question — but I'm just a cat-bot. Got tuna?"
        else:
            reply = random.choice(self.fallbacks)
        self.history.append((prompt, reply))
        return reply


def extract_code_blocks(text: str):
    """Return list of python code blocks found in markdown fenced triple-backticks."""
    return re.findall(r"```(?:python)?\n(.*?)```", text, re.DOTALL) or []


class ChatGPTClone:
    SIDEBAR_BG = "#202123"
    SIDEBAR_WIDTH = 220
    MSG_BG_USER = "#343541"
    MSG_BG_ASSIST = "#40414f"
    CODE_BG = "#20232a"

    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("ChatGPT • Local")
        root.configure(bg=self.SIDEBAR_BG)
        root.geometry("960x680")
        root.minsize(800, 600)

        # Sidebar ----------------------------------------------------
        sidebar = Frame(root, bg=self.SIDEBAR_BG, width=self.SIDEBAR_WIDTH)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        new_btn = Button(
            sidebar, text="+  New Chat", anchor="w",
            bg="#444654", fg="#ececf1", activebackground="#55596b",
            bd=0, font=("Segoe UI", 11, "bold"), padx=14, pady=8,
            command=self.new_chat
        )
        new_btn.pack(fill="x", pady=(12, 6), padx=10)

        self.chat_list = Listbox(
            sidebar, bg=self.SIDEBAR_BG, fg="#f0f0f0", highlightthickness=0,
            bd=0, activestyle='none', selectbackground="#55596b", font=("Segoe UI", 10)
        )
        self.chat_list.pack(fill="both", expand=True, padx=10, pady=(0, 12))
        self.chat_list.bind("<<ListboxSelect>>", self.on_chat_select)

        # Main area --------------------------------------------------
        main = Frame(root, bg=self.MSG_BG_USER)
        main.pack(side="right", fill="both", expand=True)

        # Canvas for messages + scrollbar
        self.canvas = Canvas(main, bg=self.MSG_BG_USER, highlightthickness=0)
        self.scrollbar = Scrollbar(main, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.msg_frame = Frame(self.canvas, bg=self.MSG_BG_USER)
        self.canvas.create_window((0, 0), window=self.msg_frame, anchor="nw")
        self.msg_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Prompt bar -------------------------------------------------
        prompt_bar = Frame(main, bg=self.MSG_BG_USER)
        prompt_bar.pack(fill="x", side="bottom", pady=(2, 6))

        self.entry = Entry(
            prompt_bar, bd=0, relief="flat", font=("Segoe UI", 13),
            bg="#40414f", fg="#ececf1", insertbackground="#ececf1"
        )
        self.entry.pack(fill="both", expand=True, side="left", padx=(12, 4), ipady=10)
        self.entry.bind("<Return>", lambda e: self.send())

        send_btn = Button(
            prompt_bar, text="➤", font=("Segoe UI", 15, "bold"),
            bg="#19c37d", fg="#ffffff", bd=0, relief="flat", padx=14,
            activebackground="#15b26b", command=self.send
        )
        send_btn.pack(side="right", padx=(4, 12), ipady=6)

        # Internal state -------------------------------------------
        self.engine = O3MiniCopycat()
        self.conversations = [[]]  # list of list[(role,text)]
        self.current_conv_idx = 0
        self.refresh_chat_list()

        # Initial greet ------------------------------------------------
        self._assistant_msg("Hello! I\'m your local ChatGPT-style assistant. How can I help?")

    # ---------- UI helpers -------------------------------------------
    def _create_bubble(self, text: str, is_user: bool):
        bg = self.MSG_BG_USER if is_user else self.MSG_BG_ASSIST
        anchor = "e" if is_user else "w"
        max_width = 500

        # Split regular text from code blocks
        code_blocks = extract_code_blocks(text)
        if code_blocks:
            before = text.split("```", 1)[0].strip()
            if before:
                self._text_label(before, bg, anchor, max_width)
            for code in code_blocks:
                self._code_block(code, anchor)
        else:
            self._text_label(text, bg, anchor, max_width)

        self.canvas.after_idle(lambda: self.canvas.yview_moveto(1.0))

    def _text_label(self, txt: str, bg: str, anchor: str, wrap: int):
        tk.Label(
            self.msg_frame, text=txt, bg=bg, fg="#ececf1", justify="left",
            font=("Segoe UI", 12), wraplength=wrap, padx=14, pady=10,
        ).pack(anchor=anchor, pady=2, padx=24)

    def _code_block(self, code: str, anchor: str):
        frame = Frame(self.msg_frame, bg=self.CODE_BG, bd=1, relief="solid")
        frame.pack(anchor=anchor, padx=32, pady=4, fill="x")

        text_widget = Text(
            frame, bg=self.CODE_BG, fg="#b5e853", font=("Consolas", 11), wrap="none",
            height=min(12, code.count("\n") + 2), borderwidth=0, highlightthickness=0
        )
        text_widget.insert("1.0", code.rstrip())
        text_widget.config(state="disabled")
        text_widget.pack(side="left", fill="both", expand=True, padx=(6, 2), pady=4)

        Button(
            frame, text="Run", bg="#19c37d", fg="#fff", font=("Segoe UI", 9, "bold"),
            bd=0, relief="flat", padx=8, pady=1, activebackground="#15b26b",
            command=lambda c=code: self._run_code_popup(c)
        ).pack(side="right", padx=8, pady=4)

    def _run_code_popup(self, code: str):
        win = Toplevel(self.root)
        win.title("Sandbox Output")
        win.geometry("520x300")
        Frame(win, bg="#1e1e1e").pack(fill="both", expand=True)
        output_box = Text(win, bg="#181e1b", fg="#e2e8f0", font=("Consolas", 12),
                          wrap="word", height=14, width=68)
        output_box.pack(padx=14, pady=16, fill="both", expand=True)

        f = io.StringIO()
        try:
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                exec(code, {"__builtins__": {"print": print, "range": range, "len": len, "int": int, "float": float}}, {})
        except Exception as e:
            f.write(f"\nError: {e}\n")
        output = f.getvalue()
        output_box.insert("1.0", output if output.strip() else "[No output]")
        output_box.config(state="disabled")

    # ---------- Conversation actions ---------------------------------
    def send(self):
        txt = self.entry.get().strip()
        if not txt:
            return
        self.entry.delete(0, END)
        self._user_msg(txt)
        self.root.after(200, lambda: self._assistant_msg(self.engine.generate(txt)))

    def _user_msg(self, text: str):
        self.conversations[self.current_conv_idx].append(("user", text))
        self._create_bubble(text, is_user=True)

    def _assistant_msg(self, text: str):
        self.conversations[self.current_conv_idx].append(("assistant", text))
        self._create_bubble(text, is_user=False)

    # ---------- Chat list management ---------------------------------
    def new_chat(self):
        self.current_conv_idx = len(self.conversations)
        self.conversations.append([])
        self.refresh_chat_list()
        # Clear canvas
        for w in self.msg_frame.winfo_children():
            w.destroy()
        self.engine = O3MiniCopycat()  # fresh engine state per chat
        self._assistant_msg("New conversation started! What\'s up?")

    def refresh_chat_list(self):
        self.chat_list.delete(0, END)
        for i, conv in enumerate(self.conversations):
            title = conv[0][1][:30] + "…" if conv else f"Chat {i + 1}"
            self.chat_list.insert(END, title)
        self.chat_list.select_set(self.current_conv_idx)

    def on_chat_select(self, event):
        if not self.chat_list.curselection():
            return
        idx = self.chat_list.curselection()[0]
        if idx == self.current_conv_idx:
            return
        self.current_conv_idx = idx
        self._load_conversation()

    def _load_conversation(self):
        for w in self.msg_frame.winfo_children():
            w.destroy()
        conv = self.conversations[self.current_conv_idx]
        for role, txt in conv:
            self._create_bubble(txt, is_user=(role == "user"))
        self.canvas.after_idle(lambda: self.canvas.yview_moveto(1.0))
        self.refresh_chat_list()


if __name__ == "__main__":
    tk.Tk.report_callback_exception = lambda *args: None  # suppress noisy traceback dialogs
    root = tk.Tk()
    ChatGPTClone(root)
    root.mainloop()
