import imaplib
import email
import re
import os
import time

class EmailHandler:
    def __init__(self, email_user, email_pass, imap_server="imap.gmail.com"):
        self.email_user = email_user
        self.email_pass = email_pass
        self.imap_server = imap_server
        self.mail = None

    def connect(self):
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            self.mail.login(self.email_user, self.email_pass)
            return True
        except Exception as e:
            print(f"❌ Email Connection Failed: {e}")
            return False

    def get_latest_otp(self, sender_filter=None, subject_filter=None, wait_seconds=60):
        """Waits for an email and extracts a 4-6 digit OTP."""
        if not self.mail:
            if not self.connect(): return None
            
        print(f"📧 Waiting {wait_seconds}s for OTP email...")
        self.mail.select("inbox")
        
        start_time = time.time()
        while time.time() - start_time < wait_seconds:
            # Search for unseen emails
            status, messages = self.mail.search(None, '(UNSEEN)')
            if status == "OK":
                for num in messages[0].split():
                    status, data = self.mail.fetch(num, '(RFC822)')
                    raw_email = data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    sender = msg["From"]
                    subject = msg["Subject"]
                    
                    # Basic filtering
                    if sender_filter and sender_filter.lower() not in sender.lower():
                        continue
                        
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                    else:
                        body = msg.get_payload(decode=True).decode()
                        
                    # Regex for 4-8 digit codes
                    otp_match = re.search(r'\b\d{4,8}\b', body)
                    if otp_match:
                        otp = otp_match.group(0)
                        print(f"✅ Found OTP: {otp} from {sender}")
                        return otp
            
            time.sleep(5)
            
        print("❌ OTP Timeout.")
        return None
