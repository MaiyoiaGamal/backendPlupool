"""
Script لإنشاء أول أدمن في النظام
يتم تشغيله من الباك اند فقط - لا يمكن من التطبيق
"""
import sys
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.models.enums import UserRole
from app.core.validators import Validators

def create_admin(phone: str, full_name: str):
    """
    إنشاء حساب أدمن
    """
    db: Session = SessionLocal()
    try:
        # فصل كود الدولة عن رقم التليفون
        phone_number, country_code = Validators.parse_phone_number(phone)
        
        # التحقق من وجود المستخدم
        existing_user = db.query(User).filter(User.phone == phone_number).first()
        
        if existing_user:
            # إذا كان موجود، تحويله إلى أدمن
            if existing_user.role == UserRole.ADMIN:
                print(f"المستخدم {phone_number} أدمن بالفعل!")
                return existing_user
            
            existing_user.role = UserRole.ADMIN
            existing_user.is_active = True
            existing_user.is_approved = True
            existing_user.country_code = country_code
            if full_name:
                existing_user.full_name = full_name
            
            db.commit()
            db.refresh(existing_user)
            print(f"تم تحويل المستخدم {phone_number} إلى أدمن بنجاح!")
            return existing_user
        else:
            # إنشاء مستخدم جديد كأدمن
            new_admin = User(
                phone=phone_number,
                country_code=country_code,
                full_name=full_name,
                role=UserRole.ADMIN,
                is_active=True,
                is_approved=True,
                is_phone_verified=True  # نعتبره مفعّل لأننا ننشئه من الباك اند
            )
            db.add(new_admin)
            db.commit()
            db.refresh(new_admin)
            print(f"تم إنشاء حساب أدمن جديد للمستخدم {phone_number} بنجاح!")
            return new_admin
            
    except Exception as e:
        db.rollback()
        print(f"حدث خطأ: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("الاستخدام: python create_admin.py <phone_number> [full_name]")
        print("مثال: python create_admin.py +201234567890 'أحمد محمد'")
        sys.exit(1)
    
    phone = sys.argv[1]
    full_name = sys.argv[2] if len(sys.argv) > 2 else "Admin User"
    
    create_admin(phone, full_name)

