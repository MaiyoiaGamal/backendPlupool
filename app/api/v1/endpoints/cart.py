from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.cart_item import CartItem
from app.models.product import Product
from app.schemas.cart import (
    CartItemCreate, CartItemUpdate, CartItemResponse, CartResponse
)

router = APIRouter()

@router.post("/cart/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    إضافة منتج إلى السلة
    Add product to cart
    """
    # التحقق من وجود المنتج
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="المنتج غير موجود"
        )
    
    if product.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="المنتج غير متاح حالياً"
        )
    
    # التحقق من الكمية المتاحة
    if product.stock_quantity < item.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"الكمية المتاحة: {product.stock_quantity} فقط"
        )
    
    # البحث عن عنصر موجود في السلة
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == item.product_id
    ).first()
    
    if existing_item:
        # تحديث الكمية
        existing_item.quantity += item.quantity
        if existing_item.quantity > product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"الكمية المتاحة: {product.stock_quantity} فقط"
            )
        db.commit()
        db.refresh(existing_item)
        cart_item = existing_item
    else:
        # إضافة عنصر جديد
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
    
    # إرجاع الاستجابة
    return CartItemResponse(
        id=cart_item.id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity,
        product_name_ar=product.name_ar,
        product_image_url=product.image_url,
        unit_price=float(product.final_price),
        total_price=float(product.final_price * cart_item.quantity),
        created_at=cart_item.created_at
    )

@router.get("/cart", response_model=CartResponse)
async def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    الحصول على محتويات السلة
    Get cart contents
    """
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()
    
    items = []
    total_amount = 0.0
    delivery_fee = 50.0  # رسوم التوصيل الافتراضية
    
    for cart_item in cart_items:
        product = cart_item.product
        if not product or product.status != "active":
            # حذف العناصر للمنتجات غير المتاحة
            db.delete(cart_item)
            continue
        
        item_total = float(product.final_price * cart_item.quantity)
        total_amount += item_total
        
        # إذا كان المنتج توصيل مجاني، لا نضيف رسوم التوصيل
        if product.free_delivery:
            delivery_fee = 0.0
        
        items.append(CartItemResponse(
            id=cart_item.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            product_name_ar=product.name_ar,
            product_image_url=product.image_url,
            unit_price=float(product.final_price),
            total_price=item_total,
            created_at=cart_item.created_at
        ))
    
    db.commit()
    
    # حساب إجمالي الكمية
    total_items = sum(item.quantity for item in items)
    
    # إذا كان الإجمالي 0، لا رسوم توصيل
    if total_amount == 0:
        delivery_fee = 0.0
    
    grand_total = total_amount + delivery_fee
    
    return CartResponse(
        items=items,
        total_items=total_items,
        total_amount=total_amount,
        delivery_fee=delivery_fee,
        grand_total=grand_total
    )

@router.put("/cart/items/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: int,
    item_update: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    تحديث كمية منتج في السلة
    Update cart item quantity
    """
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="العنصر غير موجود في السلة"
        )
    
    product = cart_item.product
    if not product or product.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="المنتج غير متاح"
        )
    
    if item_update.quantity > product.stock_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"الكمية المتاحة: {product.stock_quantity} فقط"
        )
    
    cart_item.quantity = item_update.quantity
    db.commit()
    db.refresh(cart_item)
    
    return CartItemResponse(
        id=cart_item.id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity,
        product_name_ar=product.name_ar,
        product_image_url=product.image_url,
        unit_price=float(product.final_price),
        total_price=float(product.final_price * cart_item.quantity),
        created_at=cart_item.created_at
    )

@router.delete("/cart/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    حذف منتج من السلة
    Remove product from cart
    """
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="العنصر غير موجود في السلة"
        )
    
    db.delete(cart_item)
    db.commit()
    return None

@router.delete("/cart", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    مسح السلة بالكامل
    Clear entire cart
    """
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()
    
    for item in cart_items:
        db.delete(item)
    
    db.commit()
    return None

