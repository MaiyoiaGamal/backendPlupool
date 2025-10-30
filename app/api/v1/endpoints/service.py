from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.service import Service, ServiceType
from app.models.pool_type import PoolType
from app.models.maintenance_package import MaintenancePackage, PackageDuration
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from app.schemas.pool_type import PoolTypeCreate, PoolTypeUpdate, PoolTypeResponse
from app.schemas.maintenance_package import (
    MaintenancePackageCreate, 
    MaintenancePackageUpdate, 
    MaintenancePackageResponse
)
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole

router = APIRouter()

# ============= Services APIs =============

@router.get("/services", response_model=List[ServiceResponse], summary="قائمة الخدمات")
def get_all_services(
    service_type: Optional[ServiceType] = Query(None, description="فلترة حسب نوع الخدمة"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """الحصول على قائمة بجميع الخدمات (إنشاء وصيانة)"""
    query = db.query(Service).filter(Service.status == "active")
    
    if service_type:
        query = query.filter(Service.service_type == service_type)
    
    services = query.offset(skip).limit(limit).all()
    return services

# ============= Customized Services APIs by User Type =============

@router.get("/services/pool-owner", response_model=List[ServiceResponse], summary="خدمات مخصصة لصاحب الحمام")
def get_pool_owner_services(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    الحصول على الخدمات المخصصة لصاحب الحمام
    - التركيز على خدمات الصيانة
    """
    if current_user.role != UserRole.POOL_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذه الصفحة مخصصة لأصحاب المسابح فقط"
        )
    
    # صاحب الحمام يحتاج خدمات الصيانة بشكل أساسي
    services = db.query(Service).filter(
        Service.status == "active",
        Service.service_type == ServiceType.MAINTENANCE
    ).offset(skip).limit(limit).all()
    
    return services

@router.get("/services/company", response_model=List[ServiceResponse], summary="خدمات مخصصة للشركة")
def get_company_services(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    الحصول على جميع الخدمات المتاحة للشركة
    - جميع أنواع الخدمات (إنشاء وصيانة)
    """
    if current_user.role != UserRole.COMPANY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذه الصفحة مخصصة للشركات فقط"
        )
    
    # الشركة تحتاج جميع أنواع الخدمات
    services = db.query(Service).filter(
        Service.status == "active"
    ).offset(skip).limit(limit).all()
    
    return services

@router.get("/services/technician", response_model=List[ServiceResponse], summary="خدمات مخصصة للفني")
def get_technician_services(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    الحصول على الخدمات المخصصة للفني
    - خدمات الصيانة فقط (مجال عمله)
    """
    if current_user.role != UserRole.TECHNICIAN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="هذه الصفحة مخصصة للفنيين فقط"
        )
    
    # الفني يعمل في مجال الصيانة
    services = db.query(Service).filter(
        Service.status == "active",
        Service.service_type == ServiceType.MAINTENANCE
    ).offset(skip).limit(limit).all()
    
    return services

@router.get("/services/{service_id}", response_model=ServiceResponse, summary="تفاصيل خدمة")
def get_service(service_id: int, db: Session = Depends(get_db)):
    """الحصول على تفاصيل خدمة معينة"""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الخدمة غير موجودة"
        )
    return service

@router.post("/services", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED, summary="إضافة خدمة جديدة")
def create_service(
    service: ServiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """إضافة خدمة جديدة (للأدمن فقط)"""
    # TODO: تحقق من أن المستخدم أدمن
    
    new_service = Service(**service.dict())
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

@router.put("/services/{service_id}", response_model=ServiceResponse, summary="تحديث خدمة")
def update_service(
    service_id: int,
    service: ServiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """تحديث بيانات خدمة (للأدمن فقط)"""
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if not db_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الخدمة غير موجودة"
        )
    
    update_data = service.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_service, field, value)
    
    db.commit()
    db.refresh(db_service)
    return db_service

@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT, summary="حذف خدمة")
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """حذف خدمة (للأدمن فقط)"""
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if not db_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الخدمة غير موجودة"
        )
    
    db.delete(db_service)
    db.commit()
    return None

# ============= Pool Types APIs =============

@router.get("/pool-types", response_model=List[PoolTypeResponse], summary="أنواع المسابح")
def get_all_pool_types(
    is_active: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """الحصول على قائمة بجميع أنواع المسابح"""
    query = db.query(PoolType)
    if is_active is not None:
        query = query.filter(PoolType.is_active == is_active)
    
    pool_types = query.offset(skip).limit(limit).all()
    return pool_types

@router.get("/pool-types/{pool_type_id}", response_model=PoolTypeResponse, summary="تفاصيل نوع مسبح")
def get_pool_type(pool_type_id: int, db: Session = Depends(get_db)):
    """الحصول على تفاصيل نوع مسبح معين"""
    pool_type = db.query(PoolType).filter(PoolType.id == pool_type_id).first()
    if not pool_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="نوع المسبح غير موجود"
        )
    return pool_type

@router.post("/pool-types", response_model=PoolTypeResponse, status_code=status.HTTP_201_CREATED, summary="إضافة نوع مسبح")
def create_pool_type(
    pool_type: PoolTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """إضافة نوع مسبح جديد (للأدمن فقط)"""
    new_pool_type = PoolType(**pool_type.dict())
    db.add(new_pool_type)
    db.commit()
    db.refresh(new_pool_type)
    return new_pool_type

@router.put("/pool-types/{pool_type_id}", response_model=PoolTypeResponse, summary="تحديث نوع مسبح")
def update_pool_type(
    pool_type_id: int,
    pool_type: PoolTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """تحديث بيانات نوع مسبح (للأدمن فقط)"""
    db_pool_type = db.query(PoolType).filter(PoolType.id == pool_type_id).first()
    if not db_pool_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="نوع المسبح غير موجود"
        )
    
    update_data = pool_type.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_pool_type, field, value)
    
    db.commit()
    db.refresh(db_pool_type)
    return db_pool_type

@router.delete("/pool-types/{pool_type_id}", status_code=status.HTTP_204_NO_CONTENT, summary="حذف نوع مسبح")
def delete_pool_type(
    pool_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """حذف نوع مسبح (للأدمن فقط)"""
    db_pool_type = db.query(PoolType).filter(PoolType.id == pool_type_id).first()
    if not db_pool_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="نوع المسبح غير موجود"
        )
    
    db.delete(db_pool_type)
    db.commit()
    return None

# ============= Maintenance Packages APIs =============

@router.get("/maintenance-packages", response_model=List[MaintenancePackageResponse], summary="باقات الصيانة")
def get_all_maintenance_packages(
    duration: Optional[PackageDuration] = Query(None, description="فلترة حسب المدة"),
    is_active: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """الحصول على قائمة بجميع باقات الصيانة"""
    query = db.query(MaintenancePackage)
    
    if is_active is not None:
        query = query.filter(MaintenancePackage.is_active == is_active)
    
    if duration:
        query = query.filter(MaintenancePackage.duration == duration)
    
    packages = query.offset(skip).limit(limit).all()
    return packages

@router.get("/maintenance-packages/{package_id}", response_model=MaintenancePackageResponse, summary="تفاصيل باقة")
def get_maintenance_package(package_id: int, db: Session = Depends(get_db)):
    """الحصول على تفاصيل باقة معينة"""
    package = db.query(MaintenancePackage).filter(MaintenancePackage.id == package_id).first()
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الباقة غير موجودة"
        )
    return package

@router.post("/maintenance-packages", response_model=MaintenancePackageResponse, status_code=status.HTTP_201_CREATED, summary="إضافة باقة")
def create_maintenance_package(
    package: MaintenancePackageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """إضافة باقة صيانة جديدة (للأدمن فقط)"""
    new_package = MaintenancePackage(**package.dict())
    db.add(new_package)
    db.commit()
    db.refresh(new_package)
    return new_package

@router.put("/maintenance-packages/{package_id}", response_model=MaintenancePackageResponse, summary="تحديث باقة")
def update_maintenance_package(
    package_id: int,
    package: MaintenancePackageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """تحديث بيانات باقة (للأدمن فقط)"""
    db_package = db.query(MaintenancePackage).filter(MaintenancePackage.id == package_id).first()
    if not db_package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الباقة غير موجودة"
        )
    
    update_data = package.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_package, field, value)
    
    db.commit()
    db.refresh(db_package)
    return db_package

@router.delete("/maintenance-packages/{package_id}", status_code=status.HTTP_204_NO_CONTENT, summary="حذف باقة")
def delete_maintenance_package(
    package_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """حذف باقة (للأدمن فقط)"""
    db_package = db.query(MaintenancePackage).filter(MaintenancePackage.id == package_id).first()
    if not db_package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الباقة غير موجودة"
        )
    
    db.delete(db_package)
    db.commit()
    return None