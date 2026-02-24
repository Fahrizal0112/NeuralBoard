import os
import requests
import warnings

# Suppress google.generativeai deprecation warning for now
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import google.generativeai as genai

from openai import OpenAI

def process_text(text: str, system_prompt: str, provider: str, model_name: str, api_key: str, base_url: str = "") -> str:
    if not api_key and provider != "Custom":
        raise ValueError(f"API Key for {provider} is required. Please set it in the application settings.")
        
    if provider == "OpenAI":
        return process_openai(text, system_prompt, model_name, api_key)
    elif provider == "Gemini":
        return process_gemini(text, system_prompt, model_name, api_key)
    elif provider == "GLM":
        return process_glm(text, system_prompt, model_name, api_key)
    elif provider == "OpenRouter":
        return process_openrouter(text, system_prompt, model_name, api_key)
    elif provider == "Custom":
        return process_custom(text, system_prompt, model_name, api_key, base_url)
    else:
        raise ValueError(f"Unknown provider: {provider}")

def process_openai(text: str, system_prompt: str, model_name: str, api_key: str) -> str:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()

def process_gemini(text: str, system_prompt: str, model_name: str, api_key: str) -> str:
    genai.configure(api_key=api_key)
    model_obj = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_prompt
    )
    response = model_obj.generate_content(text)
    return response.text.strip()

def process_openrouter(text: str, system_prompt: str, model_name: str, api_key: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]["content"].strip()

def process_glm(text: str, system_prompt: str, model_name: str, api_key: str) -> str:
    # BigModel (ZhipuAI/GLM) has an OpenAI compatible endpoint
    client = OpenAI(
        api_key=api_key,
        base_url="https://open.bigmodel.cn/api/paas/v4/"
    )
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()

def process_custom(text: str, system_prompt: str, model_name: str, api_key: str, base_url: str) -> str:
    if not base_url:
        raise ValueError("Custom base URL is required for Custom provider.")
        
    headers = {
        "Content-Type": "application/json"
    }
    # Jika api_key diisi, baru tambahkan ke headers
    if api_key and api_key.strip():
        headers["Authorization"] = f"Bearer {api_key}"
        
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]
    }
    
    response = requests.post(base_url, headers=headers, json=data)
    
    try:
        result = response.json()
    except Exception:
        response.raise_for_status()
        return response.text.strip()
        
    if not response.ok:
        # Menampilkan detail error dari provider custom jika status code bukan 200-299
        error_msg = result.get("error", result)
        raise ValueError(f"API Error {response.status_code}: {error_msg}")
        
    # Deteksi berbagai macam kemungkinan format response
    if "choices" in result and len(result["choices"]) > 0:
        return result["choices"][0]["message"]["content"].strip()
    elif "message" in result and "content" in result["message"]:
        return result["message"]["content"].strip()
    elif "response" in result:
        return result["response"].strip()
    else:
        # Apabila format JSON tidak dikenali, tampilkan langsung
        import json
        return "Unknown Response Format: " + json.dumps(result)
