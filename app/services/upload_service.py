import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from app.core.config import settings

class UploadService:
    """Service for handling file uploads"""
    
    @staticmethod
    def ensure_upload_dir() -> Path:
        """إنشاء مجلد الرفع إذا لم يكن موجوداً"""
        upload_path = Path(settings.UPLOAD_DIR)
        upload_path.mkdir(parents=True, exist_ok=True)
        return upload_path
    
    @staticmethod
    def validate_image_file(file: UploadFile) -> None:
        """التحقق من نوع وحجم الصورة"""
        # التحقق من نوع الملف
        if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"نوع الملف غير مدعوم. الأنواع المدعومة: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
            )
        
        # التحقق من الحجم (سيتم التحقق من الحجم الفعلي بعد القراءة)
        # لكن يمكن إضافة تحقق أولي هنا
    
    @staticmethod
    def get_file_extension(content_type: str) -> str:
        """الحصول على امتداد الملف من نوعه"""
        extension_map = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp"
        }
        return extension_map.get(content_type, ".jpg")
    
    @staticmethod
    async def upload_profile_image(file: UploadFile, user_id: int) -> str:
        """
        رفع صورة البروفايل للمستخدم
        Returns: URL للصورة المحفوظة
        """
        # التحقق من الملف
        UploadService.validate_image_file(file)
        
        # إنشاء مجلد الرفع
        upload_dir = UploadService.ensure_upload_dir()
        profiles_dir = upload_dir / "profiles"
        profiles_dir.mkdir(exist_ok=True)
        
        # إنشاء اسم فريد للملف
        file_extension = UploadService.get_file_extension(file.content_type)
        unique_filename = f"{user_id}_{uuid.uuid4().hex}{file_extension}"
        file_path = profiles_dir / unique_filename
        
        # قراءة المحتوى والتحقق من الحجم
        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"حجم الملف كبير جداً. الحد الأقصى: {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
            )
        
        # حفظ الملف
        with open(file_path, "wb") as f:
            f.write(content)
        
        # إرجاع URL للصورة
        image_url = f"{settings.BASE_URL}/static/uploads/profiles/{unique_filename}"
        return image_url
    
    @staticmethod
    def delete_image(image_url: str) -> bool:
        """
        حذف صورة من السيرفر
        Returns: True إذا تم الحذف بنجاح
        """
        try:
            # استخراج مسار الملف من URL
            if "/static/uploads/" in image_url:
                relative_path = image_url.split("/static/uploads/")[1]
                file_path = Path(settings.UPLOAD_DIR) / relative_path
                
                if file_path.exists():
                    file_path.unlink()
                    return True
            return False
        except Exception:
            return False

