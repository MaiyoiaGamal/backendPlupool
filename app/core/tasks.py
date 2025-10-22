# app/core/tasks.py
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models import notification as notif_model, booking as booking_model, user as user_model

def send_daily_notifications():
    db_gen = get_db()
    db: Session = next(db_gen)

    today = datetime.utcnow().date()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())

    # 1. حجوزات اليوم
    bookings = db.query(booking_model.Booking).filter(
        booking_model.Booking.date >= start_of_day,
        booking_model.Booking.date <= end_of_day
    ).all()

    for booking in bookings:
        user = db.query(user_model.User).filter(user_model.User.id == booking.user_id).first()
        if user:
            db.add(notif_model.Notification(
                user_id=user.id,
                title="تذكير بموعدك اليوم",
                message=f"مرحبًا {user.name}، لديك موعد {booking.service} اليوم الساعة {booking.time}.",
                type="booking"
            ))

    # 2. مستخدمين غير نشطين (>7 أيام)
    week_ago = datetime.utcnow() - timedelta(days=7)
    inactive_users = db.query(user_model.User).filter(user_model.User.last_active < week_ago).all()
    for user in inactive_users:
        db.add(notif_model.Notification(
            user_id=user.id,
            title="نحن نفتقدك!",
            message="احجز الآن واحصل على خصم 10%.",
            type="inactivity"
        ))

    db.commit()
    db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_notifications, 'cron', hour=8)  # 8 صباحًا يوميًا