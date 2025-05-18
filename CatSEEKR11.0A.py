
# tset.py - CATSEEK R1 GUI Core
import tkinter as tk
from tkinter import scrolledtext
import time
import random

class CatMind:
    def __init__(self):
        self.knowledge = {
            'responses': {
                'hello': ["Meow!", "Purr...", "*head bump*"],
                'question': ["Maybe yes, maybe no. Where's the food?", 
                           "Ancient feline secret"],
                'default': ["*tail flick*", "Napping engine engaged"]
            }
        }
        
    def generate_response(self, input_text):
        # Removed blocking sleep, added proper response selection
        if '?' in input_text:
            category = 'question'
        elif any(greet in input_text.lower() for greet in ['hi', 'hello', 'hey']):
            category = 'hello'
        else:
            category = 'default'
        return random.choice(self.knowledge['responses'][category])

class CatSeekGUI:
    def __init__(self, master):
        self.master = master
        master.title("CATSEEK R1")
        master.geometry("600x400")
        master.resizable(False, False)
        
        # Configure main container
        self.frame = tk.Frame(master, bg="#1e1e1e")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Fixed ScrolledText initialization
        self.chat_display = scrolledtext.ScrolledText(
            self.frame, wrap=tk.WORD, bg="#2d2d2d", fg="white", 
            font=("Consolas", 10), insertbackground="white"
        )
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Input controls
        input_frame = tk.Frame(self.frame, bg="#1e1e1e")
        input_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.user_input = tk.Entry(input_frame, width=50, bg="#3c3c3c", fg="white")
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.user_input.bind("<Return>", lambda e: self.send_message())
        
        send_btn = tk.Button(input_frame, text="Send", command=self.send_message,
                           bg="#404040", fg="white", relief=tk.FLAT)
        send_btn.pack(side=tk.LEFT, padx=5)
        
        # Control buttons
        ctrl_frame = tk.Frame(self.frame, bg="#1e1e1e")
        ctrl_frame.pack(pady=5)
        
        tk.Button(ctrl_frame, text="Imagine", command=self.start_imagination,
                bg="#404040", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(ctrl_frame, text="Exit", command=master.destroy,
                bg="#404040", fg="white").pack(side=tk.LEFT, padx=5)
        
        self.mind = CatMind()
        self.imagination_running = False

    def send_message(self):
        user_text = self.user_input.get().strip()
        if not user_text:
            return
        
        self._update_display(f"You: {user_text}", "white")
        self.user_input.delete(0, tk.END)
        
        # Schedule response generation to prevent GUI freeze
        self.master.after(10, self._generate_and_display_response, user_text)

    def _generate_and_display_response(self, user_text):
        response = self.mind.generate_response(user_text)
        self._update_display(f"Cat: {response}", "#569cd6")

    def _update_display(self, text, color):
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, text + "\n", color)
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.yview(tk.END)

    def start_imagination(self):
        if self.imagination_running:
            return
        
        self.imagination_running = True
        imagine_window = tk.Toplevel(self.master)
        imagine_window.title("Cat Vision")
        imagine_window.resizable(False, False)
        
        canvas = tk.Canvas(imagine_window, bg="black", width=200, height=150)
        canvas.pack()
        
        frames = [
            (r"/\_/\ ", 50, 30),
            (r"( o.o )", 50, 50),
            (r" > ^ < ", 50, 70)
        ]
        
        def animate(frame=0):
            if not self.imagination_running:
                return
                
            canvas.delete("all")
            # Smoother animation using sine wave
            y_offset = int(10 * (1 + (frame % 60)/30))
            for text, x, y in frames:
                canvas.create_text(x, y + y_offset, text=text, fill="white")
            imagine_window.after(16, animate, frame + 1)
        
        animate()
        imagine_window.protocol("WM_DELETE_WINDOW", lambda: self._stop_imagination(imagine_window))

    def _stop_imagination(self, window):
        self.imagination_running = False
        window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CatSeekGUI(root)
    root.mainloop()
