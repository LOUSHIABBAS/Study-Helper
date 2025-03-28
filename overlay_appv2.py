import customtkinter as ctk
import pyautogui
import pytesseract
try:
    from openai import OpenAI  # Updated import statement
except ImportError:
    import openai  # Fallback import
from PIL import Image, ImageSequence
import subprocess
import tempfile
import os
from PIL import ImageGrab
from dotenv import load_dotenv  # You'll need to install this: pip install python-dotenv
import sys
from pathlib import Path
import json

# Define asset paths
SCRIPT_DIR = Path(__file__).parent
ASSETS_DIR = SCRIPT_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
GIFS_DIR = ASSETS_DIR / "gifs"

# Create directories if they don't exist
ASSETS_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)
GIFS_DIR.mkdir(exist_ok=True)

# Load environment variables
load_dotenv()

# Configure Tesseract path
def get_tesseract_path():
    default_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\loush\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
    ]
    
    for path in default_paths:
        if os.path.exists(path):
            return path
    return None

tesseract_path = get_tesseract_path()
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    print("Warning: Tesseract not found. OCR functionality may be limited.")

# Configure OpenAI
def get_api_key():
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            return config.get("api_key")
    except (FileNotFoundError, json.JSONDecodeError):
        return None

api_key = get_api_key()
if api_key:
    try:
        client = OpenAI(api_key=api_key)  # Create client instance
    except NameError:
        openai.api_key = api_key  # Fallback to old style

class APIKeyManager(ctk.CTkToplevel):
    def __init__(self, parent, callback, is_first_time=False):
        super().__init__(parent)
        
        self.callback = callback
        self.is_first_time = is_first_time
        self.title("OpenAI API Key Setup")
        self.geometry("600x500")
        
        # Center the window on screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 500) // 2
        self.geometry(f"600x500+{x}+{y}")
        
        # Handle window closing differently for first-time users
        if is_first_time:
            self.protocol("WM_DELETE_WINDOW", self.on_first_time_closing)
        else:
            self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Make it stay on top and set minimum size
        self.attributes('-topmost', True)
        self.minsize(600, 500)
        self.configure(fg_color="#2d2d2d")
        
        # Create widgets
        self.setup_widgets()

    def setup_widgets(self):
        main_container = ctk.CTkFrame(
            self,
            fg_color="#2d2d2d",
            corner_radius=20,
        )
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Only show back button if not first time
        if not self.is_first_time:
            self.back_btn = ctk.CTkButton(
                main_container,
                text="← Back",
                command=self.on_closing,
                width=100,
                height=35,
                corner_radius=8,
                fg_color="#4a9eff",
                hover_color="#2d7de0",
                font=("Arial", 12, "bold"),
                border_width=1,
                border_color="#6ab0ff"
            )
            self.back_btn.place(relx=0.02, rely=0.02)

        # Title
        title = ctk.CTkLabel(
            main_container,
            text="OpenAI API Key Setup",
            font=("Arial Bold", 28),
            text_color="#4a9eff"
        )
        title.pack(pady=(30, 20))
        
        # Instructions
        instructions = ctk.CTkLabel(
            main_container,
            text="Please enter your OpenAI API Key below:",
            font=("Arial", 16),
            wraplength=500,
            text_color="#e0e0e0"
        )
        instructions.pack(pady=(0, 20))
        
        # API Key entry
        self.api_key_entry = ctk.CTkEntry(
            main_container,
            width=400,
            height=45,
            font=("Arial", 14),
            show="•",
            fg_color="#232323",
            border_color="#4a4a4a",
            text_color="#ffffff"
        )
        self.api_key_entry.pack(pady=(0, 15))
        
        # Show/Hide button with blue styling
        self.show_hide_btn = ctk.CTkButton(
            main_container,
            text="Show API Key",
            command=self.toggle_api_key_visibility,
            width=150,
            height=35,
            font=("Arial", 13),
            fg_color="#4a9eff",  # Changed to blue
            hover_color="#2d7de0",
            border_width=1,
            border_color="#6ab0ff"
        )
        self.show_hide_btn.pack(pady=(0, 20))
        
        # Save button
        save_btn = ctk.CTkButton(
            main_container,
            text="Save API Key",
            command=self.save_api_key,
            width=200,
            height=45,
            font=("Arial Bold", 14),
            fg_color="#4a9eff",
            hover_color="#2d7de0"
        )
        save_btn.pack(pady=(0, 20))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            main_container,
            text="",
            font=("Arial", 13),
            wraplength=400
        )
        self.status_label.pack(pady=(0, 20))

    def toggle_api_key_visibility(self):
        if self.api_key_entry.cget("show") == "":
            self.api_key_entry.configure(show="•")
            self.show_hide_btn.configure(text="Show API Key")
        else:
            self.api_key_entry.configure(show="")
            self.show_hide_btn.configure(text="Hide API Key")

    def save_api_key(self):
        api_key = self.api_key_entry.get().strip()
        
        if not api_key:
            self.status_label.configure(
                text="Please enter an API key",
                text_color="red"
            )
            return
            
        if not api_key.startswith("sk-"):
            self.status_label.configure(
                text="Invalid API key format. Should start with 'sk-'",
                text_color="red"
            )
            return
        
        try:
            # Test the API key
            openai.api_key = api_key
            # Try a simple API call that doesn't cost tokens
            openai.api_key = api_key
            
            # If we get here, the API key is valid
            # Save to config.json instead of .env
            config = {"api_key": api_key}
            with open("config.json", "w") as f:
                json.dump(config, f)
            
            # Check if running as exe or script
            if getattr(sys, 'frozen', False):
                # Running as exe
                self.status_label.configure(
                    text="API key saved successfully! Please close and reopen the application.",
                    text_color="green"
                )
                # Add a button to close the application
                close_btn = ctk.CTkButton(
                    self,
                    text="Close Application",
                    command=lambda: sys.exit(),
                    width=200,
                    height=45,
                    font=("Arial Bold", 14),
                    fg_color="#4a9eff",
                    hover_color="#2d7de0"
                )
                close_btn.pack(pady=(20, 0))
            else:
                # Running as script - keep original restart behavior
                self.status_label.configure(
                    text="API key saved successfully! Restarting application...",
                    text_color="green"
                )
                if self.is_first_time:
                    self.after(1000, self.restart_application)
                else:
                    self.callback(True)
                    self.after(1000, self.destroy)
            
        except Exception as e:
            error_msg = str(e).lower()
            if "invalid api key" in error_msg or "incorrect api key" in error_msg:
                self.status_label.configure(
                    text="Invalid API key. Please check and try again.",
                    text_color="red"
                )
            elif "expired" in error_msg:
                self.status_label.configure(
                    text="API key has expired. Please provide a new one.",
                    text_color="red"
                )
            else:
                self.status_label.configure(
                    text=f"Error: {str(e)}",
                    text_color="red"
                )
            self.callback(False)

    def restart_application(self):
        """Restart the entire application"""
        self.destroy()
        self.master.destroy()
        
        # Start a new process
        import subprocess
        script_path = sys.argv[0]
        subprocess.Popen([sys.executable, script_path])
        
        # Exit current process
        sys.exit()

    def on_first_time_closing(self):
        """Handle window closing for first-time users"""
        self.destroy()
        self.master.destroy()  # Close the entire application
        sys.exit()  # Ensure complete termination

    def on_closing(self):
        """Handle window closing for returning users"""
        self.callback(False)
        self.destroy()
        self.master.deiconify()

class StudyHelper(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set window icon
        icon_path = IMAGES_DIR / "icon.ico"
        if icon_path.exists():
            self.iconbitmap(icon_path)
        
        # Check for API key before proceeding
        if not self.check_api_key():
            self.withdraw()  # Hide main window
            self.api_key_manager = APIKeyManager(self, self.on_api_key_setup, is_first_time=True)
            return
        
        self.setup_main_window()

    def check_api_key(self):
        """Check if API key exists and is valid"""
        try:
            # Load from config.json instead of .env
            import json
            try:
                with open("config.json", "r") as f:
                    config = json.load(f)
                    api_key = config.get("api_key")
            except FileNotFoundError:
                return False
            
            if not api_key:
                return False
                
            if not api_key.startswith("sk-"):
                return False
            
            openai.api_key = api_key
            # Try a simple API call that doesn't cost tokens
            openai.api_key = api_key
            return True
        except Exception as e:
            print(f"API key validation error: {str(e)}")
            return False

    def on_api_key_setup(self, success):
        """Callback for API key setup"""
        if success:
            self.deiconify()  # Show main window
            self.setup_main_window()
        else:
            # Keep the API key manager open
            pass

    def setup_main_window(self):
        """Setup the main application window"""
        # Window setup
        self.geometry("800x600")
        self.title("Study Helper")
        self.wm_attributes("-topmost", True)
        self.configure(fg_color="#1a1a1a")

        # Initialize GIF handling
        self.gif_frames = {}
        self.current_frames = {}
        self.is_playing = {}
        
        # Load GIFs
        self.load_gifs()

        # Create background frame for GIF
        self.background_frame = ctk.CTkFrame(
            self,
            fg_color="#1a1a1a",
            corner_radius=0
        )
        self.background_frame.pack(fill="both", expand=True)
        
        # Create background GIF label
        self.background_gif = ctk.CTkLabel(
            self.background_frame,
            text=""
        )
        self.background_gif.pack(fill="both", expand=True)
        
        # Re-enable the background animation
        self.play_gif("loading", self.background_gif)

        # Main frame with rounded corners and padding
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="#2d2d2d",
            corner_radius=20,
            border_width=2,
            border_color="#4a4a4a",
            bg_color="#1a1a1a"
        )
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)

        # Add API Key button at the top of main_frame with proper alignment
        self.api_key_btn = ctk.CTkButton(
            self.main_frame,
            text="Update API Key",
            command=self.show_api_key_manager,
            width=120,
            height=35,
            corner_radius=8,
            fg_color="#4a9eff",
            hover_color="#2d7de0",
            font=("Arial", 12, "bold"),
            border_width=1,
            border_color="#6ab0ff"
        )
        self.api_key_btn.place(relx=0.95, rely=0.03, anchor="ne")  # Adjusted position to match padding

        # Title with animation
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Study Helper",
            font=("Arial Bold", 32),
            text_color="#4a9eff"
        )
        self.title_label.pack(pady=(40, 20))

        # Question display with better styling
        self.question_label = ctk.CTkLabel(
            self.main_frame,
            text="Capture anything you need help with",
            font=("Arial", 16),
            wraplength=600,
            text_color="#e0e0e0"
        )
        self.question_label.pack(pady=(0, 30))  # More spacing below

        # Image display with frame
        self.image_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="#232323",
            corner_radius=10
        )
        # Don't pack the frame initially
        
        self.image_label = ctk.CTkLabel(
            self.image_frame,
            text="",
            corner_radius=8
        )
        self.image_label.pack(pady=10, padx=10)

        # Button frame with gradient effect
        self.button_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.button_frame.pack(fill="x", padx=100, pady=15)  # Centered buttons

        # Styled buttons
        self.capture_btn = ctk.CTkButton(
            self.button_frame,
            text="Capture Question",
            command=self.capture_question,
            font=("Arial Bold", 14),
            height=45,  # Taller buttons
            width=200,  # Fixed width
            corner_radius=12,
            fg_color="#4a9eff",  # Matching blue
            hover_color="#2d7de0",
            border_width=1,
            border_color="#6ab0ff"  # Light border for depth
        )
        self.capture_btn.pack(side="left", padx=10, expand=True)

        # Create but don't pack the get help button initially
        self.get_help_btn = ctk.CTkButton(
            self.button_frame,
            text="Get Help",
            command=self.get_help,
            font=("Arial Bold", 14),
            height=45,
            width=200,
            corner_radius=12,
            fg_color="#50c878",  # Nice green
            hover_color="#3da75d",
            border_width=1,
            border_color="#72d894"
        )

        # Status label with animation
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Ready",
            font=("Arial", 13),
            text_color="#a0a0a0"
        )
        self.status_label.pack(pady=(30, 10))

        # Store current question
        self.current_question = ""

        # Create loading animation label (but don't pack it yet)
        self.loading_label = ctk.CTkLabel(
            self.main_frame,
            text="",
        )

    def animate_title(self):
        """Animate the title with a fade-in effect"""
        def update_opacity(step):
            if step <= 10:  # 10 steps for animation
                opacity = step / 10
                # Convert opacity to hex color (from gray to white)
                color_value = int(opacity * 255)
                color = f"#{color_value:02x}{color_value:02x}{color_value:02x}"
                self.title_label.configure(text_color=color)
                self.after(50, lambda: update_opacity(step + 1))
        update_opacity(0)

    def update_status(self, text, color):
        """Animate status updates with a bounce effect"""
        def bounce_animation(scale, step=0):
            if step <= 5:  # 5 steps for bounce
                # Calculate bounce scale (1.1 -> 1.0)
                current_scale = 1 + (0.1 * (5 - step) / 5)
                self.status_label.configure(font=("Arial", int(13 * current_scale)))
                self.after(50, lambda: bounce_animation(scale, step + 1))
            
        self.status_label.configure(text=text, text_color=color)
        bounce_animation(1.1)

    def capture_question(self):
        """Capture and process question using Windows Snip & Sketch"""
        try:
            # Minimize window
            self.iconify()  # This minimizes the window instead of hiding it
            
            # Wait for window to minimize before launching snip
            self.after(500, lambda: self._launch_snip())
            
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")
            self.deiconify()

    def _launch_snip(self):
        """Launch Snip & Sketch and handle window restoration"""
        try:
            # Launch Snip & Sketch
            pyautogui.hotkey('win', 'shift', 's')
            
            # Update status
            self.status_label.configure(
                text="Use Snip & Sketch to capture. After capturing, click 'Get Help'", 
                text_color="orange"
            )
            
            # Wait longer before restoring window to allow for screenshot
            self.after(3000, self.deiconify)  # Wait 3 seconds before showing window
            self.after(5000, self.process_clipboard)  # Process clipboard after 5 seconds
            
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")
            self.deiconify()

    def process_clipboard(self):
        """Process the captured image from clipboard"""
        try:
            # Get image from clipboard
            screenshot = ImageGrab.grabclipboard()
            
            if screenshot:
                # If we're in an expanded state, reset the UI
                if hasattr(self, 'chat_container'):
                    # Reset window size
                    self.geometry("800x600")
                    
                    # Remove chat container and its contents
                    self.chat_container.destroy()
                    delattr(self, 'chat_container')
                    
                    # Clear conversation history
                    self.conversation_history = []
                
                # Pack the image frame and get help button
                self.image_frame.pack(pady=10, padx=20, fill="x")
                self.get_help_btn.pack(side="left", padx=10, expand=True)
                
                # Update capture button text and style
                self.capture_btn.configure(
                    text="Capture Another?",
                    fg_color="#3d5afe",  # Different blue shade
                    hover_color="#304ffe",
                    border_color="#5c77ff"
                )
                
                # Store the original screenshot
                self.last_screenshot = screenshot
                
                # Fixed reasonable size for display
                max_width = 600
                max_height = 200
                
                # Calculate scaling while maintaining aspect ratio
                img_width, img_height = screenshot.size
                scale = min(
                    max_width / img_width,
                    max_height / img_height
                )
                
                display_width = int(img_width * scale)
                display_height = int(img_height * scale)
                
                photo = ctk.CTkImage(
                    light_image=screenshot, 
                    dark_image=screenshot, 
                    size=(display_width, display_height)
                )
                self.image_label.configure(image=photo)
                self.image_label.image = photo
                
                # Update status
                self.update_status("Question captured! Click 'Get Help' to proceed.", "#4caf50")
            else:
                self.update_status("No image found in clipboard", "#ff9800")
                
        except Exception as e:
            self.update_status(f"Error: {str(e)}", "#ff6b6b")

    def get_help(self):
        """Get help with current question using GPT-4o"""
        if not hasattr(self, 'last_screenshot'):
            self.update_status("Please capture a question first", "#ff6b6b")
            return

        try:
            # Animate window expansion
            self._animate_window_expansion()
            
            # Create chat container frame
            self.chat_container = ctk.CTkFrame(
                self.main_frame,
                fg_color="#232323",
                corner_radius=10
            )
            self.chat_container.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Chat history display - make it read-only
            self.answer_text = ctk.CTkTextbox(
                self.chat_container,
                height=300,
                font=("Arial", 12),
                fg_color="#2d2d2d",
                corner_radius=8,
                wrap="word",
                state="disabled"  # Make it read-only
            )
            self.answer_text.pack(fill="both", expand=True, padx=10, pady=5)
            
            # Add chat input area with placeholder
            self.chat_frame = ctk.CTkFrame(
                self.chat_container,
                fg_color="transparent"
            )
            self.chat_frame.pack(fill="x", padx=10, pady=(0, 10), side="bottom")
            
            # Chat input with placeholder text - updated colors and text
            self.chat_input = ctk.CTkTextbox(
                self.chat_frame,
                height=40,
                font=("Arial", 12),
                fg_color="#2d2d2d",
                corner_radius=8,
                wrap="word",
                text_color="#e0e0e0"  # Lighter text color for better visibility
            )
            self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 5))
            
            # Add placeholder text and set cursor to beginning
            self.chat_input.insert("0.0", "Type your question here...")
            self.chat_input.configure(text_color="#666666")  # Dimmed placeholder text
            self.chat_input.mark_set("insert", "0.0")  # Set cursor to beginning
            self.chat_input.focus_set()  # Give focus to input box
            
            # Bind focus events for placeholder behavior
            self.chat_input.bind("<FocusIn>", self._on_entry_click)
            self.chat_input.bind("<FocusOut>", self._on_focus_out)
            self.chat_input.bind("<Return>", self._on_enter_press)  # Enter to send
            
            # Improved send button
            self.send_btn = ctk.CTkButton(
                self.chat_frame,
                text="Send ➤",  # Added arrow for better UX
                command=self.send_message,
                font=("Arial Bold", 13),
                width=80,
                height=40,
                corner_radius=8,
                fg_color="#2962ff",
                hover_color="#1e88e5"
            )
            self.send_btn.pack(side="right")
            
            # Store conversation history
            self.conversation_history = []
            
            # Process initial analysis
            self._process_image()
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}", "#ff6b6b")

    def _on_entry_click(self, event):
        """Handle click on chat input"""
        # Clear placeholder text immediately when user clicks
        self.chat_input.delete("0.0", "end")
        self.chat_input.configure(text_color="#e0e0e0")  # Lighter text color when typing
        self.chat_input.mark_set("insert", "0.0")  # Set cursor to beginning

    def _on_focus_out(self, event):
        """Handle focus out of chat input"""
        current_text = self.chat_input.get("0.0", "end").strip()
        if not current_text or current_text == "Type your question here...":
            self.chat_input.delete("0.0", "end")  # Clear everything
            self.chat_input.insert("0.0", "Type your question here...")
            self.chat_input.configure(text_color="#666666")  # Dimmed placeholder text
            self.chat_input.mark_set("insert", "0.0")  # Set cursor position

    def _on_enter_press(self, event):
        """Handle enter key press"""
        if not event.state & 0x1:  # Check if shift is not pressed
            self.send_message()
            return "break"  # Prevents default newline

    def _process_image(self):
        """Process the initial image analysis"""
        try:
            # Get API key from config.json
            import json
            try:
                with open("config.json", "r") as f:
                    config = json.load(f)
                    api_key = config.get("api_key")
            except FileNotFoundError:
                self.update_status("API key not found. Please update it.", "#ff6b6b")
                self.show_api_key_manager()
                return

            # Create new client instance with the API key
            openai.api_key = api_key

            # Convert PIL Image to bytes and encode
            import io, base64
            img_byte_arr = io.BytesIO()
            self.last_screenshot.save(img_byte_arr, format='PNG')
            base64_image = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            
            # Initial message with image - updated to be more general
            initial_messages = [
                {
                    "role": "system",
                    "content": """You are a highly knowledgeable AI assistant. Analyze the image provided and:
                    1. Identify the type of question or content
                    2. Provide a clear, detailed explanation
                    3. If it's a question, provide the answer or solution
                    4. If relevant, explain the reasoning or methodology
                    Be thorough but concise in your responses."""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please analyze this image and help me understand it."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ]
            
            # Load environment variables again in case they were updated
            load_dotenv()
            
            # Update the API call based on which import was successful
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=initial_messages,
                    max_tokens=500
                )
                ai_message = response.choices[0].message.content
            except NameError:
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=initial_messages,
                    max_tokens=500
                )
                ai_message = response['choices'][0]['message']['content']
            
            # Store the conversation
            self.conversation_history = initial_messages + [
                {"role": "assistant", "content": ai_message}
            ]
            
            # Enable text widget temporarily to insert text
            self.answer_text.configure(state="normal")
            self.answer_text.delete("0.0", "end")
            self.answer_text.insert("0.0", ai_message, "assistant")
            self.answer_text.configure(state="disabled")
            
            # Update status
            self.update_status("Analysis complete! You can now chat for more help.", "#4caf50")
            
        except Exception as e:
            error_msg = str(e)
            if "API key" in error_msg or "authentication" in error_msg.lower():
                self.update_status("API key is invalid or expired. Please update it.", "#ff6b6b")
                self.show_api_key_manager()
            else:
                self.update_status(f"Error: {error_msg}", "#ff6b6b")

    def send_message(self):
        """Send a message and get response"""
        try:
            # Get API key from config.json
            import json
            try:
                with open("config.json", "r") as f:
                    config = json.load(f)
                    api_key = config.get("api_key")
            except FileNotFoundError:
                self.update_status("API key not found. Please update it.", "#ff6b6b")
                self.show_api_key_manager()
                return

            # Create new client instance with the API key
            openai.api_key = api_key

            # Get user message
            user_message = self.chat_input.get("0.0", "end").strip()
            if user_message == "Type your question here..." or not user_message:
                return
                
            # Clear input properly
            self.chat_input.delete("0.0", "end")
            self.chat_input.configure(text_color="#e0e0e0")
            self.chat_input.mark_set("insert", "0.0")
            self.chat_input.focus_set()
            
            # Update status to show processing
            self.update_status("Processing your question...", "#2196f3")
            
            # Add user message to conversation
            self.conversation_history.append({"role": "user", "content": user_message})
            
            # Load environment variables again in case they were updated
            load_dotenv()
            
            # Update the API call based on which import was successful
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=self.conversation_history,
                    max_tokens=500
                )
                ai_message = response.choices[0].message.content
            except NameError:
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=self.conversation_history,
                    max_tokens=500
                )
                ai_message = response['choices'][0]['message']['content']
            
            # Add response to conversation
            self.conversation_history.append({"role": "assistant", "content": ai_message})
            
            # Update display with user message in a different color
            self.answer_text.tag_config("user", foreground="#4a9eff")
            self.answer_text.tag_config("assistant", foreground="#50c878")
            
            # Enable text widget temporarily to insert text
            self.answer_text.configure(state="normal")
            self.answer_text.insert("end", "\n\nYou: ", "user")
            self.answer_text.insert("end", user_message, "user")
            self.answer_text.insert("end", "\n\nAssistant: ", "assistant")
            self.answer_text.insert("end", ai_message, "assistant")
            self.answer_text.see("end")
            self.answer_text.configure(state="disabled")
            
            # Update status
            self.update_status("Ready for your next question!", "#4caf50")
            
        except Exception as e:
            error_msg = str(e)
            if "API key" in error_msg or "authentication" in error_msg.lower():
                self.update_status("API key is invalid or expired. Please update it.", "#ff6b6b")
                self.show_api_key_manager()
            else:
                self.update_status(f"Error: {error_msg}", "#ff6b6b")

    def _animate_window_expansion(self):
        """Animate the window expansion smoothly"""
        current_height = 600
        target_height = 1100  # Increased from 1000 to 1100 for better chat visibility
        steps = 20  # More steps for smoother animation
        height_increment = (target_height - current_height) / steps
        
        def expand_step(current):
            if current < target_height:
                next_height = min(current + height_increment, target_height)
                self.geometry(f"800x{int(next_height)}")
                
                # Resize GIF frames for new window size
                self.resize_background_gif(800, int(next_height))
                
                self.after(16, lambda: expand_step(next_height))  # Exactly 16ms for 60 FPS
        
        expand_step(current_height)

    def resize_background_gif(self, width, height):
        """Resize the background GIF frames to match window size"""
        if "loading" in self.gif_frames:
            frames = []
            # Make the GIF larger than the window to ensure full coverage
            target_size = (width + 400, height + 400)  # Increased padding
            
            # Get original frames
            original_frames = self.gif_frames["loading"]
            
            # Resize each frame
            for frame in original_frames:
                frame_image = ctk.CTkImage(
                    light_image=frame._light_image,
                    dark_image=frame._dark_image,
                    size=target_size
                )
                frames.append(frame_image)
            
            # Update frames
            self.gif_frames["loading"] = frames
            
            # Force update the current frame
            if self.is_playing.get("loading", False):
                current_frame = self.current_frames["loading"]
                self.background_gif.configure(image=frames[current_frame])

    def load_gifs(self):
        """Load all GIFs from the gifs directory"""
        try:
            # Load loading animation with the specific file name
            loading_path = GIFS_DIR / "Soothing Black And White GIF by xponentialdesign.gif"
            if loading_path.exists():
                print(f"Found loading GIF at {loading_path}")
                self.load_gif("loading", loading_path)
                print("Successfully loaded loading GIF")
            else:
                print(f"Loading GIF not found at {loading_path}")
                print(f"Looking in: {GIFS_DIR}")
                # List all files in the directory for debugging
                print("Files in directory:", list(GIFS_DIR.glob('*')))
            
        except Exception as e:
            print(f"Failed to load GIFs: {e}")

    def load_gif(self, name, path):
        """Load a specific GIF and store its frames"""
        if path.exists():
            frames = []
            gif = Image.open(path)
            
            # Get frame dimensions
            width, height = gif.size
            
            # Different sizes for background vs loading indicator
            if name == "loading":
                # Initial size slightly larger than window
                target_size = (1000, 800)  # Initial size
            else:
                target_size = (50, 50)  # Small size for loading indicator
            
            for frame in ImageSequence.Iterator(gif):
                # Convert and resize frame
                frame_image = ctk.CTkImage(
                    light_image=frame.convert('RGBA'),
                    dark_image=frame.convert('RGBA'),
                    size=target_size
                )
                frames.append(frame_image)
            
            self.gif_frames[name] = frames
            self.current_frames[name] = 0
            self.is_playing[name] = False

    def play_gif(self, name, widget):
        """Play a specific GIF on a widget"""
        if name in self.gif_frames and not self.is_playing.get(name, False):
            self.is_playing[name] = True
            self._animate_gif(name, widget)

    def stop_gif(self, name):
        """Stop a specific GIF animation"""
        self.is_playing[name] = False

    def _animate_gif(self, name, widget):
        """Animate a specific GIF frame by frame"""
        if self.is_playing.get(name, False) and name in self.gif_frames:
            frames = self.gif_frames[name]
            if frames:
                # Update to next frame
                self.current_frames[name] = (self.current_frames[name] + 1) % len(frames)
                widget.configure(image=frames[self.current_frames[name]])
                
                # Exactly 16ms for consistent 60 FPS
                self.after(16, lambda: self._animate_gif(name, widget))

    def show_api_key_manager(self):
        """Show the API key manager for updates"""
        self.withdraw()  # Hide main window
        self.api_key_manager = APIKeyManager(self, self.on_api_key_setup, is_first_time=False)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = StudyHelper()
    app.mainloop()