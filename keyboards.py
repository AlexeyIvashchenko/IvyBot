from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta
import calendar
import config


def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🗓️ Забронировать день")],
            [KeyboardButton(text="❓ Как всё проходит?"), KeyboardButton(text="💰 Услуги/оплата")],
            [KeyboardButton(text="📊 Примеры работ"), KeyboardButton(text="👨‍💼 Поддержка")]
        ],
        resize_keyboard=True
    )


def get_months_keyboard():
    """Клавиатура выбора месяцев"""
    builder = InlineKeyboardBuilder()
    today = datetime.now()

    # Показываем 6 месяцев вперед
    for i in range(6):
        month_date = today.replace(day=1) + timedelta(days=32 * i)
        month_name = month_date.strftime("%B %Y")
        builder.button(
            text=month_name,
            callback_data=f"month_{month_date.strftime('%Y-%m')}"
        )

    builder.adjust(2)
    return builder.as_markup()


def get_days_keyboard(year_month, booked_dates):
    """Клавиатура выбора дней для конкретного месяца"""
    builder = InlineKeyboardBuilder()
    year, month = map(int, year_month.split('-'))

    # Получаем календарь месяца
    cal = calendar.monthcalendar(year, month)

    for week in cal:
        for day in week:
            if day != 0:
                date_obj = datetime(year, month, day)
                # Проверяем только пн, ср, пт
                if date_obj.weekday() in [0, 2, 4]:
                    date_str = date_obj.strftime("%d.%m.%Y")  # Формат для сравнения с booked_dates
                    date_iso = date_obj.strftime("%Y-%m-%d")  # Формат для callback
                    weekday_ru = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"][date_obj.weekday()]

                    if date_str in booked_dates:
                        builder.button(
                            text=f"❌ {day:02d} ({weekday_ru})",
                            callback_data="occupied"
                        )
                    else:
                        builder.button(
                            text=f"✅ {day:02d} ({weekday_ru})",
                            callback_data=f"book_{date_iso}"  # Используем ISO формат
                        )

    builder.button(text="🔙 Назад к месяцам", callback_data="back_to_months")
    builder.adjust(3)
    return builder.as_markup()


def get_payment_keyboard(amount, booking_date=None, is_final=False, show_check_button=False):
    """Клавиатура для оплаты"""
    builder = InlineKeyboardBuilder()

    if booking_date and not is_final:
        builder.button(
            text=f"💳 Оплатить {amount} ₽",
            callback_data=f"pay_deposit_{booking_date}"
        )
    elif is_final:
        builder.button(
            text=f"💳 Оплатить {amount} ₽",
            callback_data="pay_final"
        )

    # Кнопка "Я оплатил" показывается только если show_check_button=True
    if show_check_button:
        builder.button(text="✅ Я оплатил", callback_data="check_payment")

    builder.button(text="❌ Отмена", callback_data="cancel_payment")
    builder.adjust(1)
    return builder.as_markup()


def get_examples_keyboard():
    """Клавиатура для примеров работ"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📱 Примеры рекламы", callback_data="show_ads")
    # УБРАЛИ кнопку "Назад"
    builder.adjust(1)
    return builder.as_markup()


def get_admin_delivery_keyboard(user_id, booking_date, is_final_paid=False):
    """Клавиатура для отправки проекта клиенту"""
    builder = InlineKeyboardBuilder()

    if is_final_paid:
        builder.button(
            text="📤 Отправить проект клиенту",
            callback_data=f"deliver_{user_id}_{booking_date}"
        )
    else:
        builder.button(
            text="⏳ Ожидание финальной оплаты",
            callback_data="waiting_final_payment"
        )

    builder.adjust(1)
    return builder.as_markup()