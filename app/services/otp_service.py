import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional
import httpx
from app.core.config import settings

class OTPService:
    """Service for handling OTP generation and WhatsApp sending"""
    
    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """Generate a random OTP code"""
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def get_expiry_time(minutes: int = 5) -> datetime:
        """Get OTP expiry time with timezone"""
        return datetime.now(timezone.utc) + timedelta(minutes=minutes)
    
    @staticmethod
    async def send_whatsapp_otp(phone: str, otp_code: str) -> bool:
        """
        Send OTP via WhatsApp using Twilio or similar service
        
        For development, just print the OTP
        For production, integrate with:
        - Twilio WhatsApp API
        - WhatsApp Business API
        - Or other WhatsApp gateway
        """
        
        # TODO: Integrate with actual WhatsApp API
        # Example with Twilio:
        # from twilio.rest import Client
        # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        # message = client.messages.create(
        #     from_='whatsapp:+14155238886',
        #     body=f'رمز التحقق الخاص بك هو: {otp_code}',
        #     to=f'whatsapp:{phone}'
        # )
        
        # For development - just log it
        print(f"📱 WhatsApp OTP for {phone}: {otp_code}")
        print(f"   Message: رمز التحقق الخاص بك في Plupool هو: {otp_code}")
        print(f"   Valid for 5 minutes")
        
        return True
    
    @staticmethod
    def verify_otp(stored_otp: str, stored_expiry: datetime, provided_otp: str) -> bool:
        """Verify if OTP is valid"""
        # Make current time timezone-aware
        current_time = datetime.now(timezone.utc)
        
        # Ensure stored_expiry is timezone-aware
        if stored_expiry.tzinfo is None:
            stored_expiry = stored_expiry.replace(tzinfo=timezone.utc)
        
        # Check if OTP expired
        if current_time > stored_expiry:
            return False
        
        # Check if OTP matches
        return stored_otp == provided_otp
