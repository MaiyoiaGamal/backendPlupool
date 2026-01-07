import re
from typing import Optional, Tuple

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
    def parse_phone_number(value: Optional[str]) -> Tuple[str, str]:
        """
        فصل كود الدولة عن رقم التليفون
        Returns: (phone_number, country_code)
        Examples:
            "+20 1234567890" -> ("1234567890", "+20")
            "+201234567890" -> ("1234567890", "+20")
            "1234567890" -> ("1234567890", "+20")  # default
        """
        if Validators._is_null_or_empty(value):
            raise ValidationError("رقم الموبايل مطلوب")
        
        value = value.strip()
        
        # كودات الدول الشائعة (يمكن إضافة المزيد)
        country_codes = {
            "+20": "+20",  # مصر
            "+966": "+966",  # السعودية
            "+971": "+971",  # الإمارات
            "+965": "+965",  # الكويت
            "+974": "+974",  # قطر
            "+973": "+973",  # البحرين
            "+968": "+968",  # عمان
            "+961": "+961",  # لبنان
            "+962": "+962",  # الأردن
            "+212": "+212",  # المغرب
            "+213": "+213",  # الجزائر
            "+216": "+216",  # تونس
            "+249": "+249",  # السودان
            "+964": "+964",  # العراق
            "+963": "+963",  # سوريا
            "+967": "+967",  # اليمن
            "+218": "+218",  # ليبيا
        }
        
        # البحث عن كود الدولة في بداية الرقم
        for code in country_codes.keys():
            # مع مسافة: "+20 1234567890"
            if value.startswith(code + " "):
                phone_number = value[len(code) + 1:].strip()
                # إزالة أي أحرف غير رقمية من الرقم
                phone_number = re.sub(r'\D', '', phone_number)
                return (phone_number, code)
            # بدون مسافة: "+201234567890"
            elif value.startswith(code):
                phone_number = value[len(code):].strip()
                # إزالة أي أحرف غير رقمية من الرقم
                phone_number = re.sub(r'\D', '', phone_number)
                return (phone_number, code)
        
        # إذا لم يوجد كود دولة، نستخدم القيمة الافتراضية
        # إزالة أي أحرف غير رقمية من الرقم
        phone_number = re.sub(r'\D', '', value)
        return (phone_number, "+20")
    
    @staticmethod
    def phone(value: Optional[str], min_digits: int = 8, max_digits: int = 15) -> str:
        """
        Validate phone number and return clean phone (without country code)
        رقم التليفون يجب أن يكون بدون كود الدولة
        """
        if Validators._is_null_or_empty(value):
            raise ValidationError("رقم الموبايل مطلوب")
        
        # فصل كود الدولة عن الرقم
        phone_number, _ = Validators.parse_phone_number(value)
        
        # Extract only digits from phone number
        digits = re.sub(r'\D', '', phone_number)
        
        if len(digits) < min_digits or len(digits) > max_digits:
            raise ValidationError(f"رقم الموبايل غير صحيح (يجب أن يكون بين {min_digits} و {max_digits} رقم)")
        
        return digits
    
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
