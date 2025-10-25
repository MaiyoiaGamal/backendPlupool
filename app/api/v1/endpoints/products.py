from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc
from typing import List, Optional
from app.db.database import get_db
from app.models.product import Product, ProductStatus, DiscountType
from app.models.category import Category
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductDetailResponse
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

# ============= Categories APIs =============

@router.get("/categories", response_model=List[CategoryResponse], summary="قائمة الفئات")
def get_all_categories(
    is_active: Optional[bool] = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """الحصول على قائمة بجميع الفئات"""
    query = db.query(Category)
    if is_active is not None:
        query = query.filter(Category.is_active == is_active)
    
    categories = query.offset(skip).limit(limit).all()
    return categories

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED, summary="إضافة فئة (Admin)")
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """إضافة فئة جديدة (للأدمن فقط)"""
    # TODO: التحقق من أن المستخدم أدمن
    
    new_category = Category(**category.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.put("/categories/{category_id}", response_model=CategoryResponse, summary="تحديث فئة (Admin)")
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """تحديث فئة (للأدمن فقط)"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="الفئة غير موجودة")
    
    update_data = category.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="حذف فئة (Admin)")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """حذف فئة (للأدمن فقط)"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="الفئة غير موجودة")
    
    db.delete(db_category)
    db.commit()
    return None

# ============= Products APIs =============

@router.get("/products", response_model=List[ProductDetailResponse], summary="قائمة المنتجات مع البحث والفلترة")
def get_all_products(
    # البحث
    search: Optional[str] = Query(None, description="البحث في اسم المنتج"),
    
    # التصفية
    category_id: Optional[int] = Query(None, description="فلترة حسب الفئة"),
    min_price: Optional[int] = Query(None, ge=0, description="الحد الأدنى للسعر"),
    max_price: Optional[int] = Query(None, ge=0, description="الحد الأقصى للسعر"),
    free_delivery: Optional[bool] = Query(None, description="توصيل مجاني فقط"),
    is_featured: Optional[bool] = Query(None, description="المنتجات المميزة فقط"),
    status: Optional[ProductStatus] = Query(None, description="حالة المنتج"),
    
    # الترتيب
    sort_by: Optional[str] = Query("created_at", description="الترتيب حسب: created_at, price, rating, views, name"),
    order: Optional[str] = Query("desc", description="نوع الترتيب: asc, desc"),
    
    # Pagination
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    الحصول على قائمة المنتجات مع إمكانيات:
    - 🔍 البحث
    - 🎯 التصفية (الفئة، السعر، التوصيل، إلخ)
    - 📊 الترتيب (حسب السعر، التقييم، الأحدث، إلخ)
    """
    
    query = db.query(Product)
    
    # البحث
    if search:
        search_filter = or_(
            Product.name_ar.ilike(f"%{search}%"),
            Product.name_en.ilike(f"%{search}%"),
            Product.description_ar.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # التصفية
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if min_price is not None:
        query = query.filter(Product.final_price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.final_price <= max_price)
    
    if free_delivery is not None:
        query = query.filter(Product.free_delivery == free_delivery)
    
    if is_featured is not None:
        query = query.filter(Product.is_featured == is_featured)
    
    if status:
        query = query.filter(Product.status == status)
    
    # الترتيب
    if sort_by == "price":
        query = query.order_by(desc(Product.final_price) if order == "desc" else asc(Product.final_price))
    elif sort_by == "rating":
        query = query.order_by(desc(Product.rating) if order == "desc" else asc(Product.rating))
    elif sort_by == "views":
        query = query.order_by(desc(Product.views_count) if order == "desc" else asc(Product.views_count))
    elif sort_by == "name":
        query = query.order_by(desc(Product.name_ar) if order == "desc" else asc(Product.name_ar))
    else:  # created_at (default)
        query = query.order_by(desc(Product.created_at) if order == "desc" else asc(Product.created_at))
    
    products = query.offset(skip).limit(limit).all()
    
    # إضافة تفاصيل الفئة
    results = []
    for product in products:
        product_dict = ProductDetailResponse(**product.__dict__)
        if product.category:
            product_dict.category_name = product.category.name_ar
        results.append(product_dict)
    
    return results

@router.get("/products/{product_id}", response_model=ProductDetailResponse, summary="تفاصيل منتج")
def get_product(product_id: int, db: Session = Depends(get_db)):
    """الحصول على تفاصيل منتج معين"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="المنتج غير موجود")
    
    # زيادة عدد المشاهدات
    product.views_count += 1
    db.commit()
    
    # إضافة تفاصيل الفئة
    product_dict = ProductDetailResponse(**product.__dict__)
    if product.category:
        product_dict.category_name = product.category.name_ar
    
    return product_dict

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, summary="إضافة منتج (Admin)")
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """إضافة منتج جديد (للأدمن فقط)"""
    # TODO: التحقق من أن المستخدم أدمن
    
    new_product = Product(**product.dict())
    
    # حساب السعر النهائي
    new_product.final_price = new_product.calculate_final_price()
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.put("/products/{product_id}", response_model=ProductResponse, summary="تحديث منتج (Admin)")
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """تحديث منتج (للأدمن فقط)"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="المنتج غير موجود")
    
    update_data = product.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    # إعادة حساب السعر النهائي
    db_product.final_price = db_product.calculate_final_price()
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="حذف منتج (Admin)")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """حذف منتج (للأدمن فقط)"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="المنتج غير موجود")
    
    db.delete(db_product)
    db.commit()
    return None