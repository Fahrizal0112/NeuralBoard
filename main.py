import flet as ft
import keyboard
import pyperclip
import threading
import time
import json
import os
from ai_handler import process_text

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_settings_to_file(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except Exception as e:
        print(f"Error saving settings: {e}")

# Global state
app_state = {
    "is_listening": False,
    "active_mode": "Code Fixer",
    "provider": "OpenAI",
    "model_name": "gpt-4o-mini",
    "api_key": "",
    "page": None,
    "log_area": None
}

MODES = {
    "Code Fixer": "You are an expert programmer. Fix the code/error provided and return ONLY the corrected code without any markdown formatting or explanation.",
    "Grammar Polish": "You are a professional editor. Fix the grammar and improve the sentence structure to make it formal. Return ONLY the polished text.",
    "Summarizer": "Summarize the provided text into exactly 3 concise bullet points.",
    "Professional Email": "Transform the following text/sentence into a polite and professional email. Return ONLY the email content."
}

def on_trigger():
    if not app_state["is_listening"]:
        return
        
    log("Hotkey triggered! Processing...")
    
    # 1. Get old_text
    old_text = pyperclip.paste()
    if not old_text:
        log("Clipboard is empty.")
        return
        
    log(f"Original text length: {len(old_text)}")
    
    # 2. Get prompt based on mode
    system_prompt = MODES.get(app_state["active_mode"], MODES["Code Fixer"])
    
    # 3. Process with AI
    try:
        new_text = process_text(
            text=old_text, 
            system_prompt=system_prompt, 
            provider=app_state["provider"],
            model_name=app_state["model_name"],
            api_key=app_state["api_key"]
        )
        
        # 4. Overwrite clipboard
        pyperclip.copy(new_text)
        log("Clipboard updated. Simulating Paste...")
        
        # 5. Simulate Ctrl+V to paste
        time.sleep(0.2) # Small delay to ensure physical keys don't interfere
        keyboard.send("ctrl+v")
        log("Respond selesai !")
        
    except Exception as e:
        log(f"Error: {e}")

def keyboard_listener():
    # Register hotkey
    try:
        keyboard.add_hotkey("ctrl+alt+v", on_trigger, suppress=True)
        keyboard.wait()
    except Exception as e:
        print(f"Failed to start keyboard listener: {e}")

def clipboard_monitor():
    recent_value = ""
    while True:
        try:
            current_value = pyperclip.paste()
            if current_value != recent_value:
                recent_value = current_value
                if app_state["is_listening"] and current_value.strip() != "":
                    preview = current_value[:30].replace("\n", " ") + ("..." if len(current_value) > 30 else "")
                    log(f"Clipboard updated: '{preview}'")
        except Exception:
            pass
        time.sleep(1.0)

def log(message):
    print(message)
    if app_state["page"]:
        # Push message using Flet's pubsub to ensure thread-safe UI refreshing
        try:
            app_state["page"].pubsub.send_all(message)
        except Exception:
            pass

def main(page: ft.Page):
    app_state["page"] = page
    
    def on_log_message(msg):
        # Depending on Flet version, msg is either string or PubSubEvent
        m = msg if isinstance(msg, str) else msg.data if hasattr(msg, "data") else str(msg)
        if app_state["log_area"]:
            current_logs = app_state["log_area"].value
            timestamp = time.strftime("%H:%M:%S")
            new_logs = f"[{timestamp}] {m}\n" + (current_logs if current_logs else "")
            app_state["log_area"].value = new_logs
            page.update()
            
    page.pubsub.subscribe(on_log_message)
    page.title = "NeuralBoard - AI Smart Clipboard"
    page.window.width = 500
    page.window.height = 750
    page.window.always_on_top = True
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # Retrieve saved settings if available
    settings = load_settings()
    saved_provider = settings.get("provider", "OpenAI")
    saved_model = settings.get("model_name", "gpt-4o-mini")
    saved_api_key = settings.get(f"{saved_provider}_api_key", "")
    
    app_state["provider"] = saved_provider
    app_state["model_name"] = saved_model
    app_state["api_key"] = saved_api_key

    def toggle_listening(e):
        app_state["is_listening"] = e.control.value
        log(f"Smart Paste {'Enabled' if app_state['is_listening'] else 'Disabled'}")

    def mode_changed(e):
        app_state["active_mode"] = e.control.value
        log(f"Mode changed to: {app_state['active_mode']}")
        
    def provider_changed(e):
        app_state["provider"] = e.control.value
        
        # Load API key for this provider from storage
        current_settings = load_settings()
        saved_key = current_settings.get(f"{app_state['provider']}_api_key", "")
        api_key_input.value = saved_key
        
        # Set default model name hint based on provider
        if app_state["provider"] == "OpenAI":
            model_name_input.value = "gpt-4o-mini"
        elif app_state["provider"] == "Gemini":
            model_name_input.value = "gemini-1.5-flash"
        elif app_state["provider"] == "GLM":
            model_name_input.value = "glm-4-flash"
        elif app_state["provider"] == "OpenRouter":
            model_name_input.value = "google/gemini-2.5-pro"
            
        page.update()
        
    def save_settings(e):
        app_state["model_name"] = model_name_input.value.strip()
        app_state["api_key"] = api_key_input.value.strip()
        
        # Save to local storage
        current_settings = load_settings()
        current_settings["provider"] = app_state["provider"]
        current_settings["model_name"] = app_state["model_name"]
        current_settings[f"{app_state['provider']}_api_key"] = app_state["api_key"]
        save_settings_to_file(current_settings)
        
        log(f"Settings Saved | Provider: {app_state['provider']} | Model: {app_state['model_name']}")
        
        # Show snackbar notification
        page.overlay.append(ft.SnackBar(ft.Text("Settings saved successfully!"), open=True))
        page.update()

    # UI Elements
    title = ft.Text("NeuralBoard", size=28, weight=ft.FontWeight.BOLD)
    subtitle = ft.Text("AI Smart Clipboard", size=14, color=ft.Colors.GREY_400)
    
    toggle_switch = ft.Switch(label="Enable Smart Paste (Ctrl+Alt+V)", value=False, on_change=toggle_listening)
    
    mode_dropdown = ft.Dropdown(
        label="Personality Mode",
        options=[ft.dropdown.Option(k) for k in MODES.keys()],
        value="Code Fixer",
        on_select=mode_changed,
    )
    
    provider_dropdown = ft.Dropdown(
        label="AI Provider",
        options=[
            ft.dropdown.Option("OpenAI"),
            ft.dropdown.Option("Gemini"),
            ft.dropdown.Option("GLM"),
            ft.dropdown.Option("OpenRouter")
        ],
        value=saved_provider,
        on_select=provider_changed,
    )
    
    model_name_input = ft.TextField(
        label="Model Name (e.g. gpt-4o-mini, gemini-1.5-flash)", 
        value=saved_model
    )
    
    api_key_input = ft.TextField(
        label="API Key", 
        value=saved_api_key,
        password=True, 
        can_reveal_password=True
    )
    
    save_btn = ft.ElevatedButton(
        "Save Settings", 
        icon=ft.Icons.SAVE, 
        on_click=save_settings,
        width=200
    )
    
    app_state["log_area"] = ft.TextField(
        multiline=True,
        read_only=True,
        expand=True,
        text_size=12,
        label="Activity Log",
        min_lines=6
    )

    # Layout
    page.add(
        title,
        subtitle,
        ft.Divider(),
        toggle_switch,
        mode_dropdown,
        ft.Divider(),
        ft.Text("Model Settings", weight=ft.FontWeight.BOLD),
        provider_dropdown,
        model_name_input,
        api_key_input,
        ft.Row([save_btn], alignment=ft.MainAxisAlignment.END),
        ft.Divider(),
        app_state["log_area"]
    )
    
    log("App started. Configure Model and API Settings above.")

if __name__ == "__main__":
    # Start keyboard listener in background
    listener_thread = threading.Thread(target=keyboard_listener, daemon=True)
    listener_thread.start()
    
    # Start clipboard monitor in background
    clipboard_thread = threading.Thread(target=clipboard_monitor, daemon=True)
    clipboard_thread.start()
    
    # Start Flet app with compatibility switch for older/newer versions
    if hasattr(ft, "run"):
        ft.run(main)
    else:
        ft.app(target=main)
