from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from datetime import datetime
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.cart_item import CartItem
from app.models.order import Order, OrderStatus, PaymentMethod
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderResponse, OrderSummaryResponse, OrderItemResponse

router = APIRouter()

def generate_order_number() -> str:
    """إنشاء رقم طلب فريد"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    import random
    random_suffix = random.randint(1000, 9999)
    return f"#{timestamp}{random_suffix}"

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    إنشاء طلب جديد من السلة
    Create new order from cart
    """
    # الحصول على عناصر السلة
    cart_items = db.query(CartItem).filter(
        CartItem.user_id == current_user.id
    ).all()
    
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="السلة فارغة"
        )
    
    # حساب الإجماليات
    total_amount = 0.0
    delivery_fee = 50.0  # رسوم التوصيل الافتراضية
    order_items_data = []
    
    for cart_item in cart_items:
        product = cart_item.product
        if not product or product.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"المنتج {product.name_ar if product else 'غير موجود'} غير متاح"
            )
        
        if cart_item.quantity > product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"الكمية المتاحة للمنتج {product.name_ar}: {product.stock_quantity} فقط"
            )
        
        item_total = float(product.final_price * cart_item.quantity)
        total_amount += item_total
        
        # إذا كان أي منتج توصيل مجاني، لا رسوم توصيل
        if product.free_delivery:
            delivery_fee = 0.0
        
        order_items_data.append({
            "product": product,
            "cart_item": cart_item,
            "unit_price": float(product.final_price),
            "quantity": cart_item.quantity,
            "total_price": item_total
        })
    
    grand_total = total_amount + delivery_fee
    
    # إنشاء الطلب
    order = Order(
        user_id=current_user.id,
        order_number=generate_order_number(),
        total_amount=total_amount,
        delivery_fee=delivery_fee,
        grand_total=grand_total,
        delivery_address=order_data.delivery_address,
        delivery_phone=order_data.delivery_phone,
        payment_method=order_data.payment_method,
        payment_status="pending",
        status=OrderStatus.CONFIRMED
    )
    db.add(order)
    db.flush()  # للحصول على order.id
    
    # إنشاء عناصر الطلب
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data["product"].id,
            product_name_ar=item_data["product"].name_ar,
            product_image_url=item_data["product"].image_url,
            unit_price=item_data["unit_price"],
            quantity=item_data["quantity"],
            total_price=item_data["total_price"]
        )
        db.add(order_item)
        
        # تحديث المخزون
        item_data["product"].stock_quantity -= item_data["quantity"]
    
    # حذف عناصر السلة
    for cart_item in cart_items:
        db.delete(cart_item)
    
    db.commit()
    db.refresh(order)
    
    # جلب عناصر الطلب
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        total_amount=order.total_amount,
        delivery_fee=order.delivery_fee,
        grand_total=order.grand_total,
        delivery_address=order.delivery_address,
        delivery_phone=order.delivery_phone,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        status=order.status,
        created_at=order.created_at,
        delivered_at=order.delivered_at,
        order_items=[
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name_ar=item.product_name_ar,
                product_image_url=item.product_image_url,
                unit_price=item.unit_price,
                quantity=item.quantity,
                total_price=item.total_price
            ) for item in order_items
        ]
    )

@router.get("/orders", response_model=List[OrderSummaryResponse])
async def get_orders(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    الحصول على تاريخ الطلبات (مشترياتي)
    Get order history (My Purchases)
    """
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
    
    result = []
    for order in orders:
        items_count = db.query(OrderItem).filter(OrderItem.order_id == order.id).count()
        result.append(OrderSummaryResponse(
            order_number=order.order_number,
            created_at=order.created_at,
            total_amount=order.total_amount,
            delivery_fee=order.delivery_fee,
            grand_total=order.grand_total,
            status=order.status,
            items_count=items_count,
            payment_method=order.payment_method
        ))
    
    return result

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    الحصول على تفاصيل طلب معين
    Get order details
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الطلب غير موجود"
        )
    
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        total_amount=order.total_amount,
        delivery_fee=order.delivery_fee,
        grand_total=order.grand_total,
        delivery_address=order.delivery_address,
        delivery_phone=order.delivery_phone,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        status=order.status,
        created_at=order.created_at,
        delivered_at=order.delivered_at,
        order_items=[
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name_ar=item.product_name_ar,
                product_image_url=item.product_image_url,
                unit_price=item.unit_price,
                quantity=item.quantity,
                total_price=item.total_price
            ) for item in order_items
        ]
    )

