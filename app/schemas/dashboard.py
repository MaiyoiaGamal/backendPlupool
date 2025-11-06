from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.technician_task import TechnicianTaskResponse


class MetricItem(BaseModel):
    key: str
    label: str
    value: float | int
    unit: Optional[str] = None
    helper_text: Optional[str] = None


class AccountSection(BaseModel):
    title: str
    metrics: List[MetricItem]


class UserSummary(BaseModel):
    id: int
    full_name: Optional[str]
    role: str
    phone: Optional[str] = None
    profile_image: Optional[str] = None


class NotificationSummary(BaseModel):
    total: int
    unread: int


class ContactChannel(BaseModel):
    label: str
    type: str
    value: str
    link: Optional[str] = None


class NavBarData(BaseModel):
    user: UserSummary
    notifications: NotificationSummary
    contact_channels: List[ContactChannel]


class FooterNavItem(BaseModel):
    label: str
    icon: str
    target: str


class FooterNavigation(BaseModel):
    items: List[FooterNavItem]


class QuickActionCard(BaseModel):
    id: str
    title: str
    subtitle: Optional[str] = None
    image_url: Optional[str] = None
    action_type: str = Field(default="navigate")
    target: str


class OfferCard(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    badge: Optional[str] = None
    service_id: int
    service_name: Optional[str] = None
    original_price: int
    final_price: int
    image_url: Optional[str] = None


class StoreItemCard(BaseModel):
    id: int
    title: str
    original_price: int
    final_price: int
    discount_percentage: Optional[float] = None
    image_url: Optional[str] = None
    badge: Optional[str] = None
    rating: Optional[float] = None


class TestimonialCard(BaseModel):
    id: int
    user_name: str
    user_avatar: Optional[str] = None
    rating: int
    message: str
    created_at: datetime
    relative_time: str


class ProjectCard(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None


class SharedHomeSections(BaseModel):
    quick_actions: List[QuickActionCard]
    special_offers: List[OfferCard]
    store_highlights: List[StoreItemCard]
    testimonials: List[TestimonialCard]
    projects: List[ProjectCard]


class PoolOwnerDashboardResponse(BaseModel):
    nav: NavBarData
    footer: FooterNavigation
    shared: SharedHomeSections
    my_account: AccountSection


class CompanyDashboardResponse(BaseModel):
    nav: NavBarData
    footer: FooterNavigation
    shared: SharedHomeSections
    my_account: AccountSection


class WeeklyDayPlan(BaseModel):
    date: date
    label: str
    is_today: bool
    tasks: List[TechnicianTaskResponse]


class WeeklyOverview(BaseModel):
    start_date: date
    end_date: date
    days: List[WeeklyDayPlan]
    empty_state_message: Optional[str] = None


class TechnicianDashboardResponse(BaseModel):
    nav: NavBarData
    footer: FooterNavigation
    stats: AccountSection
    weekly_overview: WeeklyOverview
    completed_tasks: List[TechnicianTaskResponse]
    store_highlights: List[StoreItemCard]
    projects: List[ProjectCard]
    testimonials: List[TestimonialCard]