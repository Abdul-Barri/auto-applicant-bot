import json
import re
import time
import os
import google.generativeai as genai
from playwright.sync_api import sync_playwright

# --- CONFIGURATION ---
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
    # Using gemini-2.0-flash for higher rate limits and speed.
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
    except:
        model = genai.GenerativeModel('gemini-1.5-flash')
else:
    print("⚠️ GEMINI_API_KEY not found. AI generation will be disabled.")
    model = None

def load_profile(filepath="user_profile.json"):
    with open(filepath, "r") as f:
        return json.load(f)

def normalize_label(text):
    return re.sub(r'[^a-z0-9]', '', text.lower())

def generate_essay(prompt, profile):
    """Uses LLM to generate a custom answer."""
    if not model:
        return profile.get("statements", {}).get("bio", "No AI Key provided.")
    
    context = json.dumps(profile, indent=2)
    full_prompt = f"""
    You are an assistant applying for a job/university for this user.
    
    User Profile:
    {context}
    
    The application form asks: "{prompt}"
    
    Write a professional, concise response (under 200 words) tailored to this question using the user's background. Do not include placeholders.
    """
    try:
        print(f"🤖 Generating AI response for: '{prompt}'...")
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"❌ AI Generation failed: {e}")
        return profile.get("statements", {}).get("bio", "Error generating response.")

def find_value_in_profile(label_text, profile, element_type="input"):
    """Heuristic matching + AI delegation."""
    normalized = normalize_label(label_text)
    
    # 1. Exact/Keyword Matches
    p = profile.get("personal_info", {})
    if "firstname" in normalized or "givenname" in normalized: return p.get("first_name")
    if "lastname" in normalized or "surname" in normalized or "familyname" in normalized: return p.get("last_name")
    if normalized == "name" or normalized == "fullname": return f"{p.get('first_name')} {p.get('last_name')}"
    if "email" in normalized: return p.get("email")
    if "phone" in normalized or "mobile" in normalized: return p.get("phone")
    if "address" in normalized: return p.get("address")
    if "city" in normalized: return p.get("city")
    if "state" in normalized or "province" in normalized: return p.get("state")
    if "zip" in normalized or "postal" in normalized: return p.get("zip")
    if "linkedin" in normalized: return p.get("linkedin")
    if "github" in normalized: return p.get("github")
    
    # 2. AI Generation for Long Text (Textareas)
    # If it's a textarea OR the label looks like a question ("why", "describe", "statement")
    is_essay_question = "why" in normalized or "describe" in normalized or "statement" in normalized or "about" in normalized
    
    if element_type == "textarea" or is_essay_question:
        return generate_essay(label_text, profile)
    
    return None

def handle_login(page, profile):
    print("🔐 Checking for login fields...")
    password_input = page.query_selector("input[type='password']")
    if not password_input:
        return False

    creds = profile.get("credentials", {})
    username = creds.get("username")
    password = creds.get("password")

    print("🔑 Login detected.")
    
    # Fill Username
    for selector in ["input[type='email']", "input[name*='user']", "input[name*='login']"]:
        try:
            if page.query_selector(selector):
                page.fill(selector, username)
                print(f"✅ Filled username: {username}")
                break
        except: pass

    # Fill Password
    try:
        password_input.fill(password)
        print("✅ Filled password.")
        password_input.press("Enter")
        print("↵ Pressed Enter.")
    except: pass

    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except: pass
    
    return True

def handle_captcha(page):
    """Detects and handles CAPTCHAs."""
    print("🛡️ Checking for CAPTCHA...")
    # Common captcha selectors
    captcha_frames = page.query_selector_all("iframe[src*='recaptcha'], iframe[src*='turnstile'], iframe[src*='hcaptcha']")
    
    if captcha_frames:
        print("⚠️ CAPTCHA Detected!")
        
        # Strategy 1: Check for 2Captcha API Key
        api_key = os.environ.get("2CAPTCHA_API_KEY")
        if api_key:
            print("🤖 Attempting auto-solve with 2Captcha...")
            # Placeholder for actual 2Captcha logic
            # verify_captcha(api_key, page.url, site_key)
            print("❌ 2Captcha implementation pending.")
            return False
            
        # Strategy 2: Human Handoff (Interactive Mode)
        print("✋ Manual intervention required. Please solve the CAPTCHA in the browser.")
        print("... Waiting 30 seconds for human solution ...")
        # In a real headful mode, we would wait for a specific element to disappear
        time.sleep(30)
        
        # Check if still present
        if page.query_selector("iframe[src*='recaptcha']"):
             print("❌ CAPTCHA still present after wait.")
             return False
             
        print("✅ CAPTCHA seemingly cleared.")
        return True
    
    return True

def process_page(page, profile):
    print(f"👀 Scanning page: {page.url}")
    
    # 0. Check for CAPTCHA first
    handle_captcha(page)
    
    # 1. Text Inputs & Textareas
    elements = page.query_selector_all("input:not([type='hidden']):not([type='password']):not([type='file']), textarea")
    for el in elements:
        # Get label or placeholder
        label_text = ""
        el_id = el.get_attribute("id")
        if el_id:
            label_el = page.query_selector(f"label[for='{el_id}']")
            if label_el: label_text = label_el.inner_text()
        
        if not label_text:
            label_text = el.get_attribute("placeholder") or el.get_attribute("name") or ""
            
        if label_text:
            tag_name = el.evaluate("el => el.tagName.toLowerCase()")
            value = find_value_in_profile(label_text, profile, element_type=tag_name)
            
            if value:
                try:
                    if not el.input_value():
                        el.fill(value)
                        print(f"✅ Filled '{label_text}' -> '{value[:30]}...'")
                except: pass

    # 2. Radio Buttons (Gender)
    try:
        page.click("label:has-text('Male')", timeout=500)
        print("✅ Clicked Radio: Male")
    except: pass

    # 3. File Uploads
    file_inputs = page.query_selector_all("input[type='file']")
    for file_input in file_inputs:
        input_name = file_input.get_attribute("name") or ""
        docs = profile.get("documents", {})
        if "cv" in input_name.lower():
            file_input.set_input_files(docs.get("cv"))
            print("✅ Uploaded CV")

def run_applicant(url):
    print(f"🚀 Starting Auto-Applicant for: {url}")
    profile = load_profile()
    
    with sync_playwright() as p:
        print("🌍 Launching browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"❌ Error loading: {e}")
            return

        if handle_login(page, profile):
            page.screenshot(path="after_login.png")

        process_page(page, profile)
        
        page.screenshot(path="final_state.png")
        print("\n✨ Complete. Screenshot saved to final_state.png")
        browser.close()

if __name__ == "__main__":
    import sys
    target_url = sys.argv[1] if len(sys.argv) > 1 else "https://ultimateqa.com/filling-out-forms/"
    run_applicant(target_url)
