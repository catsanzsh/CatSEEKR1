import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import os
import subprocess
import random
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

class DeepSeek7BEngine:
    def __init__(self):
        self.initialized = False
        self.model = None
        self.tokenizer = None
        self.model_path = "./deepseek-7b"
        self.quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16
        )

    def _download_model(self):
        if not os.path.exists(self.model_path):
            snapshot_download(
                repo_id="deepseek-ai/deepseek-llm-7b-base-v1.5",
                local_dir=self.model_path,
                resume_download=True
            )

    def initialize_model(self):
        """Load DeepSeek 7B with 4-bit quantization"""
        self._download_model()
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            device_map="auto",
            quantization_config=self.quant_config,
            trust_remote_code=True
        )
        self.initialized = True

    def generate_response(self, input_text):
        """Generate response using DeepSeek 7B with R1 patterns"""
        prompt = self._create_r1_prompt(input_text)
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        
        outputs = self.model.generate(
            inputs.input_ids,
            max_new_tokens=256,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return self._postprocess_response(response)

    def _create_r1_prompt(self, input_text):
        """Create R1-style prompt with zero pattern formatting"""
        return f'''Human: {input_text}\nAssistant:'''

    def _postprocess_response(self, response):
        """Add Aha Moment patterns and cleanup"""
        aha_triggers = [
            ("insight", "✨ Aha Moment: Neural Pathways Activated"),
            ("realize", "🔍 Pattern Recognized: Cognitive Leap Detected"),
            ("understand", "🎯 Knowledge Integration: Concept Mastered")
        ]
        
        if any(trigger in response.lower() for trigger, _ in aha_triggers):
            aha_msg = random.choice(aha_triggers)[1]
            response += f"\n[NPU SYSTEM]: {aha_msg}"
            
        response += f"\n[Telemetry: VRAM Usage: {self._get_vram_usage()} | Tokens: {len(response.split())}]"
        return response

    def _get_vram_usage(self):
        try:
            result = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,nounits,noheader"],
                encoding="utf-8"
            )
            return f"{result.strip()}MB"
        except:
            return "Unknown"

class CatMind:
    def __init__(self, gui):
        self.gui = gui
        self.engine = DeepSeek7BEngine()
        self.initialized = False
        self.init_thread = threading.Thread(target=self._initialize_async)
        self.init_thread.start()

    def _initialize_async(self):
        self.gui.add_system_message("Initializing DeepSeek-R1 NeuroMatrix...")
        time.sleep(1)
        if not os.path.exists(self.engine.model_path):
            self.gui.add_system_message("Downloading cognitive patterns... (This may take several minutes)")
        else:
            self.gui.add_system_message("Loading local neural weights...")
        
        try:
            self.engine.initialize_model()
            self.initialized = True
            self.gui.add_system_message("System ready! Start chatting with CatGPT!")
            self.gui.enable_input()
        except Exception as e:
            self.gui.add_system_message(f"Initialization failed: {str(e)}")

class CatGPTGUI:
    def __init__(self, master):
        self.master = master
        master.title("CatGPT 1.0")
        master.geometry("600x400")
        master.configure(bg="#1a1a1a")

        # Chat history display
        self.chat_history = scrolledtext.ScrolledText(
            master,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg="#2d2d2d",
            fg="white",
            insertbackground="white"
        )
        self.chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_history.configure(state=tk.DISABLED)

        # Input frame
        input_frame = tk.Frame(master, bg="#1a1a1a")
        input_frame.pack(padx=10, pady=5, fill=tk.X)

        # User input field
        self.user_input = tk.Entry(
            input_frame,
            font=("Arial", 12),
            bg="#3d3d3d",
            fg="white",
            insertbackground="white",
            disabledbackground="#2d2d2d"
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.user_input.bind("<Return>", lambda event: self.send_message())

        # Send button
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            state=tk.DISABLED
        )
        self.send_button.pack(side=tk.RIGHT, padx=(5,0))

        # Initialize AI system
        self.cat_mind = CatMind(self)

    def add_system_message(self, message):
        self.chat_history.configure(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"\n[System] {message}\n", "system")
        self.chat_history.configure(state=tk.DISABLED)
        self.chat_history.see(tk.END)

    def enable_input(self):
        self.user_input.configure(state=tk.NORMAL)
        self.send_button.configure(state=tk.NORMAL)

    def send_message(self):
        user_text = self.user_input.get()
        if not user_text.strip():
            return

        # Display user message
        self.chat_history.configure(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"\n[You] {user_text}\n", "user")
        self.chat_history.configure(state=tk.DISABLED)
        self.user_input.delete(0, tk.END)

        # Disable input during processing
        self.user_input.configure(state=tk.DISABLED)
        self.send_button.configure(state=tk.DISABLED)

        # Process response in thread
        threading.Thread(target=self.generate_response, args=(user_text,)).start()

    def generate_response(self, user_text):
        try:
            response = self.cat_mind.engine.generate_response(user_text)
            self.display_response(response)
        except Exception as e:
            self.add_system_message(f"Error generating response: {str(e)}")
        finally:
            self.user_input.configure(state=tk.NORMAL)
            self.send_button.configure(state=tk.NORMAL)

    def display_response(self, response):
        self.chat_history.configure(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"\n[CatGPT] {response}\n", "assistant")
        self.chat_history.configure(state=tk.DISABLED)
        self.chat_history.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    gui = CatGPTGUI(root)
    root.mainloop()
