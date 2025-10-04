import re
from typing import Optional

class ValidationError(Exception):
    """Custom validation error"""
    pass

class Validators:
    """Server-side validators matching the Flutter client validators"""
    
    @staticmethod
    def _is_null_or_empty(value: Optional[str]) -> bool:
        """Check if value is None or empty after trimming"""
        return value is None or value.strip() == ""
    
    @staticmethod
    def required(value: Optional[str], field_name: str = "الحقل") -> str:
        """Validate required field"""
        if Validators._is_null_or_empty(value):
            raise ValidationError(f"{field_name} مطلوب")
        return value.strip()
    
    @staticmethod
    def name(value: Optional[str], min_length: int = 3, max_length: int = 50) -> str:
        """Validate name field"""
        if Validators._is_null_or_empty(value):
            raise ValidationError("الاسم مطلوب")
        
        clean_value = value.strip()
        
        if len(clean_value) < min_length:
            raise ValidationError(f"الاسم قصير جدًا (يجب أن يكون {min_length} أحرف على الأقل)")
        
        if len(clean_value) > max_length:
            raise ValidationError(f"الاسم طويل جدًا (بحد أقصى {max_length} حرف)")
        
        return clean_value
    
    @staticmethod
    def phone(value: Optional[str], min_digits: int = 8, max_digits: int = 15) -> str:
        """Validate phone number (digits only, length 8-15)"""
        if Validators._is_null_or_empty(value):
            raise ValidationError("رقم الموبايل مطلوب")
        
        # Extract only digits
        digits = re.sub(r'\D', '', value)
        
        if len(digits) < min_digits or len(digits) > max_digits:
            raise ValidationError(f"رقم الموبايل غير صحيح (يجب أن يكون بين {min_digits} و {max_digits} رقم)")
        
        return value.strip()
    
    @staticmethod
    def email(value: Optional[str]) -> str:
        """Validate email address"""
        if Validators._is_null_or_empty(value):
            raise ValidationError("البريد الإلكتروني مطلوب")
        
        clean_value = value.strip()
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        
        if not re.match(pattern, clean_value):
            raise ValidationError("البريد الإلكتروني غير صحيح")
        
        return clean_value
    
    @staticmethod
    def password(
        value: Optional[str],
        min_length: int = 6,
        require_number: bool = True,
        require_upper: bool = False
    ) -> str:
        """Validate password"""
        if Validators._is_null_or_empty(value):
            raise ValidationError("كلمة المرور مطلوبة")
        
        if len(value) < min_length:
            raise ValidationError(f"كلمة المرور يجب ألا تقل عن {min_length} أحرف")
        
        if require_number and not re.search(r'[0-9]', value):
            raise ValidationError("كلمة المرور يجب أن تحتوي على رقم واحد على الأقل")
        
        if require_upper and not re.search(r'[A-Z]', value):
            raise ValidationError("كلمة المرور يجب أن تحتوي على حرف كبير واحد على الأقل")
        
        return value
    
    @staticmethod
    def confirm_password(value: Optional[str], original: Optional[str]) -> str:
        """Validate password confirmation"""
        if Validators._is_null_or_empty(value):
            raise ValidationError("تأكيد كلمة المرور مطلوب")
        
        if value != original:
            raise ValidationError("كلمة المرور غير متطابقة")
        
        return value
    
    @staticmethod
    def number(value: Optional[str], field_name: str = "الرقم") -> float:
        """Validate that value is a number"""
        if Validators._is_null_or_empty(value):
            raise ValidationError(f"{field_name} مطلوب")
        
        try:
            return float(value.strip())
        except ValueError:
            raise ValidationError(f"{field_name} يجب أن يكون رقمًا")
    
    @staticmethod
    def email_or_phone(value: Optional[str]) -> str:
        """Validate email OR phone"""
        if Validators._is_null_or_empty(value):
            raise ValidationError("هذا الحقل مطلوب")
        
        clean_value = value.strip()
        
        # Check email pattern
        email_pattern = r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$'
        # Check phone pattern (with optional country code)
        phone_pattern = r'^(?:\+?\d{1,3})?[0-9]{8,14}$'
        
        is_email = re.match(email_pattern, clean_value)
        is_phone = re.match(phone_pattern, clean_value)
        
        if not is_email and not is_phone:
            raise ValidationError("أدخل بريد إلكتروني صالح أو رقم هاتف صحيح")
        
        return clean_value
