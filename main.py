import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.client.default import DefaultBotProperties
from datetime import datetime
import config
from keyboards import *
from google_sheets import GoogleSheets
from payments import PaymentManager
from database import Database
from reminders import ReminderSystem

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация
storage = MemoryStorage()
bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher(storage=storage)
db = Database()

try:
    gsheets = GoogleSheets()
    if not gsheets.is_connected():
        logger.warning("Google Sheets не подключен, работаем только с локальной БД")
except Exception as e:
    logger.error(f"Ошибка инициализации Google Sheets: {e}")
    gsheets = None

payment_manager = PaymentManager()
reminder_system = ReminderSystem(gsheets)


# Состояния для FSM
class BookingState(StatesGroup):
    waiting_for_support = State()
    waiting_for_delivery = State()
    admin_support_reply = State()
    project_completed = State()


# 📍 ОСНОВНЫЕ КОМАНДЫ

@dp.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = """
Привет! Я Айви. Через меня проходит 99% коммуникации.

Вам нужно создать адаптивный рабочий сайт и настроить рекламу в Яндексе? Специалист с 5-летним опытом в маркетинге и дизайне сделает это для Вас за 1 день! Без долгив переписок, подрядчиков и ожиданий.

С чего начнём?
    """

    await message.answer(welcome_text, reply_markup=get_main_keyboard())


@dp.message(F.text == "🗓️ Забронировать день")
async def book_day(message: Message):
    info_text = """
📅 <b>Бронирование дня</b>

Я работаю только по понедельникам, средам и пятницам. 
В неделю доступно всего 3 рабочих дня — бронируйте заранее!

Выберите месяц для просмотра доступных дат:
    """

    # Получаем забронированные даты из обоих источников
    booked_dates = []
    if gsheets:
        booked_dates = gsheets.get_booked_dates()

    # Также получаем забронированные даты из локальной базы
    from database import Database
    db = Database()

    # Получаем все активные бронирования с предоплатой
    all_bookings = db.conn.cursor().execute('''
        SELECT booking_date FROM bookings 
        WHERE deposit_paid = TRUE AND status = 'active'
    ''').fetchall()

    # Добавляем даты из базы в формате DD.MM.YYYY
    for booking in all_bookings:
        date_obj = datetime.strptime(booking[0], "%Y-%m-%d")
        booked_dates.append(date_obj.strftime("%d.%m.%Y"))

    await message.answer(info_text, reply_markup=get_months_keyboard())


@dp.message(F.text == "❓ Как всё проходит?")
async def how_it_works(message: Message):
    text = """
Процесс простой и быстрый 👇

1️⃣ Вы бронируете день и вносите предоплату (4 000 ₽)
2️⃣ Заполняете бриф (если чего-то нет, создадим сами, потом сможете заменить.)
3️⃣ В выбранный день выполняется работа.
4️⃣ Вы оплачиваете оставшуюся сумму (11 000 ₽)
5️⃣ Отправляем вам весь проект + инструкции до 8 вечера по МСК

Весь процесс — 1 день. Без ожиданий и сложностей.

<b>НО! Есть несколько правил:</b>

- если специалист по любым причинам не выполнил проект вовремя — вся сумма в полном размере возвращается клиенту в ближашие 12 часов.

- если клиент не заполнил бриф до назначенного дня — проект закрывается, предоплата не возвращается.

- если клиент не оплатил вторую часть суммы в назначенный день — проект закрывается, предоплата не возвращается.
    """
    await message.answer(text)


@dp.message(F.text == "💰 Услуги/оплата")
async def services_payment(message: Message):
    text = """
<b>В проект входит:</b>

1️⃣ Сбор ключевых слов (для написания seo-текстов и рекламы в Яндексе)
2️⃣ Создание лендинга (одностраничного сайта). Сайт адаптирован под несколько разрешений экрана. 
3️⃣ Оформление сайта для поисковой выдачи + настройка аналитики/ подключение форм заявок
4️⃣ Создание 2-3 рекламных кампании в Яндекс.Директ. Продвижение рекламы по интересам пользователей и по ключевым словам.
5️⃣ Написание инструкции, если понадобится пополнить баланс в рекламе, изменить фото на сайте и другое

После запуска реклама начнёт работать, сайт будет полностью готов к приёму заявок, а аналитика — собираться автоматически. Никаких дополнительных действий не потребуется.

<b>ВАЖНО!</b> Реклама требует внимания. Да, мы создаем стартовую рекламу и подключаем аналитику. Но далее вы можете адаптироваться самостоятельно или обратиться к маркетологу. Без должного внимания реклама будет не качественной и вы будете сливать большой бюджет вникуда. 

💰 <b>Стоимость данного пакета — 15 000 ₽</b>

Предоплата 4 000 ₽ — это необходимо для того, чтобы специалист выделил день на ваш проект.

После оплаты появится ссылка на бриф и закрепится дата выполнения.
    """
    await message.answer(text)


@dp.message(F.text == "📊 Примеры работ")
async def examples(message: Message):
    text = """
Несколько проектов, выполненных через Айви 👇

- https://example-site1.com
- https://example-site2.com  
- https://example-site3.com

Нажав на кнопку "Примеры рекламы" вы увидите рекламные объявления для этих же проектов.
    """
    await message.answer(text, reply_markup=get_examples_keyboard())


@dp.message(F.text == "👨‍💼 Поддержка")
async def support(message: Message, state: FSMContext):
    # Проверяем, завершен ли проект у пользователя
    user_id = message.from_user.id
    cursor = db.conn.cursor()
    cursor.execute('''
        SELECT status FROM bookings 
        WHERE user_id = ? AND status = 'completed'
        ORDER BY created_at DESC LIMIT 1
    ''', (user_id,))

    completed_project = cursor.fetchone()

    if completed_project:
        text = """
💬 <b>Связь с поддержкой</b>

Напишите ваш вопрос ниже, и я передам его специалисту. Он ответит вам в ближайшее время.

<i>Пожалуйста, опишите вопрос максимально подробно.</i>
        """
    else:
        text = """
💬 <b>Связь с поддержкой</b>

Напишите ваш вопрос ниже, и я передам его специалисту. Он ответит вам в ближайшее время.

<i>Пожалуйста, опишите вопрос максимально подробно.</i>
        """

    await message.answer(text)
    await state.set_state(BookingState.waiting_for_support)


# 📍 ИНЛАЙН КНОПКИ

@dp.callback_query(F.data.startswith("month_"))
async def select_month(callback: CallbackQuery):
    month_key = callback.data.split("_")[1]

    # Получаем забронированные даты только из Google Sheets
    booked_dates = []
    if gsheets:
        booked_dates = gsheets.get_booked_dates()

    # Логируем для отладки
    logger.info(f"Отображение календаря для {month_key}, забронированные даты: {booked_dates}")

    await callback.message.edit_text(
        "📅 Выберите доступную дату:",
        reply_markup=get_days_keyboard(month_key, booked_dates)
    )
    await callback.answer()

@dp.callback_query(F.data == "back_to_months")
async def back_to_months(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите месяц для просмотра доступных дат:",
        reply_markup=get_months_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "occupied")
async def date_occupied(callback: CallbackQuery):
    await callback.answer("❌ Эта дата уже занята. Выберите другую.", show_alert=True)


@dp.callback_query(F.data.startswith("book_"))
async def select_date(callback: CallbackQuery):
    date_str = callback.data.split("_")[1]
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    text = f"""
📅 <b>Вы выбрали дату:</b> {date_obj.strftime('%d.%m.%Y')}

Для бронирования необходимо внести предоплату <b>4 000 ₽</b>

После оплаты:
• Дата будет закреплена за вами
• Вы получите ссылку на бриф для заполнения
• Мы приступим к работе в выбранный день

Нажмите "💳 Оплатить 4000 ₽" чтобы перейти к оплате.
    """

    await callback.message.edit_text(
        text,
        # Показываем только кнопку оплаты, без кнопки "Я оплатил"
        reply_markup=get_payment_keyboard(config.DEPOSIT_AMOUNT, date_str, show_check_button=False)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("pay_deposit_"))
async def process_deposit_payment(callback: CallbackQuery):
    date_str = callback.data.split("_")[2]
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    # Создаем платеж
    payment = await payment_manager.create_payment(
        amount=config.DEPOSIT_AMOUNT,
        description=f"Предоплата за бронирование {date_str}",
        user_id=callback.from_user.id,
        booking_date=date_str
    )

    if payment:
        # Сохраняем в базу
        db.add_booking(
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            full_name=callback.from_user.full_name,
            booking_date=date_str
        )

        # Добавляем в Google Sheets
        if gsheets:
            user_data = {
                'user_id': callback.from_user.id,
                'username': callback.from_user.username,
                'full_name': callback.from_user.full_name
            }
            gsheets.add_booking(user_data, date_obj, payment.id)

        # РЕДАКТИРУЕМ текущее сообщение
        await callback.message.edit_text(
            f"💳 <b>Оплата предоплаты</b>\n\n"
            f"Сумма: {config.DEPOSIT_AMOUNT} ₽\n"
            f"Дата брони: {date_obj.strftime('%d.%m.%Y')}\n\n"
            f"Для оплаты перейдите по ссылке:\n{payment.confirmation.confirmation_url}\n\n"
            f"<i>После успешной оплаты нажмите кнопку '✅ Я оплатил'</i>",
            # Теперь показываем кнопку "Я оплатил"
            reply_markup=get_payment_keyboard(config.DEPOSIT_AMOUNT, date_str, show_check_button=True)
        )
    else:
        await callback.message.edit_text("❌ Ошибка создания платежа. Попробуйте позже.")

    await callback.answer()


@dp.message(Command("project_status"))
async def check_project_status(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("Использование: /project_status user_id")
            return

        user_id = int(parts[1])

        cursor = db.conn.cursor()
        cursor.execute('''
            SELECT booking_date, status, deposit_paid, final_paid, brief_completed
            FROM bookings WHERE user_id = ? ORDER BY created_at DESC LIMIT 1
        ''', (user_id,))

        project = cursor.fetchone()

        if project:
            status_text = {
                'active': 'Активный',
                'completed': 'Завершен',
                'cancelled': 'Отменен'
            }

            await message.answer(
                f"📊 <b>Статус проекта пользователя {user_id}</b>\n\n"
                f"📅 Дата брони: {project[0]}\n"
                f"📋 Статус: {status_text.get(project[1], project[1])}\n"
                f"💰 Предоплата: {'✅ Оплачена' if project[2] else '❌ Не оплачена'}\n"
                f"💰 Финальная оплата: {'✅ Оплачена' if project[3] else '❌ Не оплачена'}\n"
                f"📝 Бриф: {'✅ Заполнен' if project[4] else '❌ Не заполнен'}\n"
            )
        else:
            await message.answer("❌ Проект не найден")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.callback_query(F.data == "check_payment")
async def check_payment_status(callback: CallbackQuery):
    """Проверяет статус платежа вручную"""
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} нажал 'Я оплатил'")

    # Получаем активное бронирование
    booking = db.get_user_active_booking(user_id)

    if booking:
        booking_date = booking[4]  # booking_date field (формат: YYYY-MM-DD)
        booking_id = booking[0]  # id field
        payment_type = "deposit"  # Определяем тип платежа

        # Проверяем, это предоплата или финальная оплата
        if callback.message.text and "Финальная оплата" in callback.message.text:
            payment_type = "final"
            # Обновляем статус финальной оплаты в базе
            cursor = db.conn.cursor()
            cursor.execute('''
                UPDATE bookings SET final_paid = TRUE 
                WHERE id = ? AND user_id = ?
            ''', (booking_id, user_id))
            db.conn.commit()
            logger.info(f"Финальная оплата подтверждена в локальной БД")

            # Обновляем Google Sheets
            google_sheets_success = False
            if gsheets:
                try:
                    google_sheets_success = gsheets.update_booking_status(user_id, booking_date, "Полная оплата")
                    logger.info(f"Статус в Google Sheets обновлен: {google_sheets_success}")
                except Exception as e:
                    logger.error(f"Ошибка при работе с Google Sheets: {e}")
                    google_sheets_success = False

            # Редактируем текущее сообщение
            await callback.message.edit_text(
                f"✅ <b>Финальная оплата подтверждена!</b>\n\n"
                f"Спасибо за оплату! Теперь мы можем отправить вам готовый проект.\n\n"
                f"<i>Ожидайте материалы в течение дня.</i>"
            )

            # Уведомляем админа о готовности к отправке проекта
            from keyboards import get_admin_delivery_keyboard
            await bot.send_message(
                config.ADMIN_ID,
                f"🎉 <b>Финальная оплата получена!</b>\n\n"
                f"👤 Пользователь: {callback.from_user.full_name}\n"
                f"📱 @{callback.from_user.username}\n"
                f"📅 Дата: {booking_date}\n"
                f"💰 Финальная оплата: {config.FINAL_AMOUNT} ₽\n\n"
                f"<i>Теперь можно отправить клиенту готовый проект.</i>",
                reply_markup=get_admin_delivery_keyboard(user_id, booking_date, is_final_paid=True)
            )


        else:
            # Это предоплата (старая логика)
            deposit_paid = booking[6]  # deposit_paid field
            logger.info(f"Бронирование найдено: ID={booking_id}, дата={booking_date}, deposit_paid={deposit_paid}")

            # Обновляем статус оплаты в базе
            cursor = db.conn.cursor()
            cursor.execute('''
                UPDATE bookings SET deposit_paid = TRUE 
                WHERE id = ? AND user_id = ?
            ''', (booking_id, user_id))
            db.conn.commit()
            logger.info(f"Статус предоплаты обновлен в локальной БД")

            # Обновляем Google Sheets
            google_sheets_success = False
            if gsheets:
                try:
                    google_sheets_success = gsheets.update_booking_status(user_id, booking_date, "Предоплата получена")
                    logger.info(f"Статус в Google Sheets обновлен: {google_sheets_success}")
                except Exception as e:
                    logger.error(f"Ошибка при работе с Google Sheets: {e}")
                    google_sheets_success = False

            # Редактируем текущее сообщение
            success_message = "✅ <b>Платеж подтвержден!</b>" if google_sheets_success else "⚠️ <b>Платеж подтвержден локально!</b>"
            google_warning = "" if google_sheets_success else "\n\n<i>Примечание: возникли проблемы с синхронизацией с Google Таблицей, но ваша бронь сохранена.</i>"

            await callback.message.edit_text(
                f"{success_message}\n\n"
                f"Дата {booking_date} забронирована за вами.\n\n"
                f"📝 <b>Теперь заполните бриф:</b>\n{config.BRIEF_FORM_URL}\n\n"
                f"<i>Важно: бриф нужно заполнить до назначенной даты.</i>"
                f"{google_warning}"
            )

            # Уведомляем админа
            from keyboards import get_admin_delivery_keyboard
            await bot.send_message(
                config.ADMIN_ID,
                f"🎉 <b>Новое бронирование!</b>\n\n"
                f"👤 Пользователь: {callback.from_user.full_name}\n"
                f"📱 @{callback.from_user.username}\n"
                f"📅 Дата: {booking_date}\n"
                f"💰 Предоплата: {config.DEPOSIT_AMOUNT} ₽",
                reply_markup=get_admin_delivery_keyboard(user_id, booking_date, is_final_paid=False)
            )

    else:
        logger.warning(f"Не найдено активных бронирований для пользователя {user_id}")
        await callback.message.edit_text("❌ Не найдено активных бронирований.")

    await callback.answer()


@dp.callback_query(F.data == "waiting_final_payment")
async def handle_waiting_payment(callback: CallbackQuery):
    """Обработчик для неактивной кнопки ожидания оплаты"""
    await callback.answer("⏳ Ожидание финальной оплаты от клиента", show_alert=True)


@dp.callback_query(F.data == "cancel_payment")
async def cancel_booking(callback: CallbackQuery):
    """Отменяет бронирование"""
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} отменил бронирование")

    # Удаляем последнее бронирование пользователя
    bookings = db.get_user_bookings(user_id)
    if bookings:
        latest_booking = bookings[0]
        booking_date = latest_booking[4]

        # Удаляем бронирование из базы
        cursor = db.conn.cursor()
        cursor.execute('DELETE FROM bookings WHERE user_id = ? AND booking_date = ?',
                       (user_id, booking_date))
        db.conn.commit()

        logger.info(f"Бронирование {booking_date} удалено для пользователя {user_id}")

    # Редактируем сообщение
    await callback.message.edit_text(
        "❌ <b>Ваша бронь отменена</b>\n\n"
        "Может быть, выберете другую дату?",
        reply_markup=get_months_keyboard()  # Возвращаем к выбору месяца
    )
    await callback.answer()

@dp.callback_query(F.data == "pay_final")
async def process_final_payment(callback: CallbackQuery):
    """Обработка финальной оплаты"""
    user_id = callback.from_user.id
    bookings = db.get_user_bookings(user_id)

    if bookings:
        latest_booking = bookings[0]
        booking_date = latest_booking[4]

        payment = await payment_manager.create_payment(
            amount=config.FINAL_AMOUNT,
            description=f"Финальная оплата за проект {booking_date}",
            user_id=user_id,
            booking_date=booking_date,
            is_final=True
        )

        if payment:
            # РЕДАКТИРУЕМ текущее сообщение
            await callback.message.edit_text(
                f"💳 <b>Финальная оплата</b>\n\n"
                f"Сумма: {config.FINAL_AMOUNT} ₽\n\n"
                f"Для оплаты перейдите по ссылке:\n{payment.confirmation.confirmation_url}\n\n"
                f"<i>После успешной оплаты нажмите кнопку '✅ Я оплатил'</i>",
                # Показываем кнопку "Я оплатил" для финальной оплаты
                reply_markup=get_payment_keyboard(config.FINAL_AMOUNT, is_final=True, show_check_button=True)
            )
        else:
            await callback.message.edit_text("❌ Ошибка создания платежа.")
    else:
        await callback.message.edit_text("❌ Не найдено активных бронирований.")

    await callback.answer()


@dp.callback_query(F.data == "show_ads")
async def show_ads_examples(callback: CallbackQuery):
    """Показывает примеры рекламы"""
    try:
        media_group = []
        for i, photo_path in enumerate(config.EXAMPLES['ads']):
            try:
                photo = FSInputFile(photo_path)
                media_group.append(types.InputMediaPhoto(
                    media=photo,
                    caption="Пример рекламного объявления" if i == 0 else ""
                ))
            except FileNotFoundError:
                logger.warning(f"Файл не найден: {photo_path}")

        if media_group:
            await callback.message.answer_media_group(media_group)
        else:
            await callback.message.answer("❌ Фотографии примеров временно недоступны.")

    except Exception as e:
        logger.error(f"Ошибка отправки медиагруппы: {e}")
        await callback.message.answer("❌ Ошибка загрузки примеров рекламы.")

    await callback.answer()


@dp.callback_query(F.data == "cancel_payment")
async def cancel_booking(callback: CallbackQuery):
    """Отменяет бронирование"""
    user_id = callback.from_user.id
    logger.info(f"Пользователь {user_id} отменил бронирование")

    # Удаляем последнее бронирование пользователя
    bookings = db.get_user_bookings(user_id)
    if bookings:
        latest_booking = bookings[0]
        booking_date = latest_booking[4]

        # Удаляем бронирование из базы
        cursor = db.conn.cursor()
        cursor.execute('DELETE FROM bookings WHERE user_id = ? AND booking_date = ?',
                       (user_id, booking_date))
        db.conn.commit()

        logger.info(f"Бронирование {booking_date} удалено для пользователя {user_id}")

    # Редактируем сообщение
    await callback.message.edit_text(
        "❌ <b>Ваша бронь отменена</b>\n\n"
        "Может быть, выберете другую дату?",
        reply_markup=get_months_keyboard()  # Возвращаем к выбору месяца
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("deliver_"))
async def deliver_project(callback: CallbackQuery, state: FSMContext):
    """Начало процесса отправки проекта клиенту"""
    parts = callback.data.split("_")
    user_id = int(parts[1])
    booking_date = parts[2]

    # Проверяем, оплачена ли финальная часть
    cursor = db.conn.cursor()
    cursor.execute('''
        SELECT final_paid FROM bookings 
        WHERE user_id = ? AND booking_date = ?
    ''', (user_id, booking_date))

    result = cursor.fetchone()

    if not result or not result[0]:
        await callback.answer("❌ Финальная оплата еще не получена!", show_alert=True)
        return

    await state.update_data(
        target_user_id=user_id,
        booking_date=booking_date,
        delivered_parts=0,  # Счетчик отправленных частей
        total_parts=4  # Всего нужно отправить 4 части
    )

    await callback.message.answer(
        f"📤 <b>Отправка проекта клиенту</b>\n\n"
        f"👤 Пользователь: {user_id}\n"
        f"📅 Дата: {booking_date}\n\n"
        f"Отправьте по порядку:\n"
        f"1. Ссылку на готовый сайт\n"
        f"2. Фото рекламных объявлений (до 3 шт)\n"
        f"3. Инструкцию (текст или документ)\n"
        f"4. Финальное сообщение для клиента\n\n"
        f"<i>Отправляйте материалы по одному сообщению.</i>\n"
        f"<b>Прогресс: 0/4</b>"
    )

    await state.set_state(BookingState.waiting_for_delivery)
    await callback.answer()


# 📍 ПОДДЕРЖКА

@dp.message(BookingState.waiting_for_support)
async def handle_support_message(message: Message, state: FSMContext):
    # Сохраняем ID пользователя для ответа
    await state.update_data(support_user_id=message.from_user.id)

    # Пересылаем сообщение владельцу с кнопкой ответа
    support_text = f"""
💬 <b>Новый вопрос от клиента</b>

👤 <b>Пользователь:</b> {message.from_user.full_name}
📱 <b>Username:</b> @{message.from_user.username}
🆔 <b>ID:</b> {message.from_user.id}

<b>Вопрос:</b>
{message.text}
    """

    # Создаем клавиатуру для ответа
    reply_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Ответить", callback_data=f"reply_support_{message.from_user.id}")]
    ])

    await bot.send_message(config.ADMIN_ID, support_text, reply_markup=reply_keyboard)
    await message.answer("✅ Ваш вопрос отправлен специалисту. Ответим в ближайшее время!")

    # Возвращаем в главное меню
    await message.answer("Чем ещё могу помочь?", reply_markup=get_main_keyboard())
    await state.clear()


# 📍 ОТВЕТЫ АДМИНА НА ВОПРОСЫ ПОДДЕРЖКИ

@dp.callback_query(F.data.startswith("reply_support_"))
async def start_support_reply(callback: CallbackQuery, state: FSMContext):
    """Начинает процесс ответа на вопрос поддержки"""
    user_id = int(callback.data.split("_")[2])

    await state.update_data(support_target_user_id=user_id)
    await callback.message.answer(
        f"💬 <b>Ответ клиенту</b>\n\n"
        f"ID пользователя: {user_id}\n\n"
        f"Напишите ваш ответ:"
    )

    await state.set_state(BookingState.admin_support_reply)
    await callback.answer()


@dp.message(BookingState.admin_support_reply)
async def handle_support_reply(message: Message, state: FSMContext):
    """Обрабатывает ответ админа и отправляет клиенту"""
    data = await state.get_data()
    user_id = data.get('support_target_user_id')

    if not user_id:
        await message.answer("❌ Ошибка: не найден пользователь для ответа")
        await state.clear()
        return

    try:
        # Отправляем ответ клиенту
        await bot.send_message(
            user_id,
            f"💬 <b>Ответ от поддержки:</b>\n\n{message.text}\n\n"
            f"<i>Если у вас есть дополнительные вопросы, напишите нам снова.</i>"
        )

        await message.answer("✅ Ответ отправлен клиенту!")

    except Exception as e:
        logger.error(f"Ошибка отправки ответа поддержки: {e}")
        await message.answer("❌ Ошибка отправки ответа. Пользователь可能 заблокировал бота.")

    await state.clear()


# 📍 ОБРАБОТКА ДОСТАВКИ ПРОЕКТА

@dp.message(BookingState.waiting_for_delivery)
async def handle_project_delivery(message: Message, state: FSMContext):
    data = await state.get_data()
    target_user_id = data.get('target_user_id')
    booking_date = data.get('booking_date')
    delivered_parts = data.get('delivered_parts', 0)
    total_parts = data.get('total_parts', 4)

    if not target_user_id:
        await message.answer("❌ Ошибка: не найден пользователь для отправки")
        await state.clear()
        return

    try:
        # Увеличиваем счетчик отправленных частей
        delivered_parts += 1
        await state.update_data(delivered_parts=delivered_parts)

        # Пересылаем сообщение клиенту
        if message.text:
            caption = ""
            if delivered_parts == 1:
                caption = "🌐 <b>Ссылка на готовый сайт</b>"
            elif delivered_parts == 2:
                caption = "📱 <b>Рекламные объявления</b>"
            elif delivered_parts == 3:
                caption = "📄 <b>Инструкция по работе</b>"
            elif delivered_parts == 4:
                caption = "💬 <b>Финальное сообщение</b>"

            await bot.send_message(target_user_id, f"{caption}\n\n{message.text}")

        elif message.photo:
            await bot.send_photo(
                target_user_id,
                message.photo[-1].file_id,
                caption="📱 <b>Рекламное объявление</b>"
            )
        elif message.document:
            await bot.send_document(
                target_user_id,
                message.document.file_id,
                caption="📄 <b>Инструкция по работе</b>"
            )

        # Проверяем, все ли части доставлены
        if delivered_parts >= total_parts:
            # Отправляем финальное сообщение клиенту
            await bot.send_message(
                target_user_id,
                "🎉 <b>Проект полностью доставлен!</b>\n\n"
                "Все материалы были отправлены. Ваш проект завершен!\n\n"
                "Если у вас есть вопросы, вы можете обратиться в поддержку через меню бота.\n\n"
                "<i>Спасибо, что выбрали наши услуги! 🚀</i>"
            )

            # Уведомляем админа
            await message.answer(
                "✅ <b>Проект полностью доставлен клиенту!</b>\n\n"
                f"👤 Пользователь: {target_user_id}\n"
                f"📅 Дата: {booking_date}\n\n"
                "<i>Все материалы отправлены, проект завершен.</i>"
            )

            # Обновляем статус в базе данных
            cursor = db.conn.cursor()
            cursor.execute('''
                UPDATE bookings SET status = 'completed' 
                WHERE user_id = ? AND booking_date = ?
            ''', (target_user_id, booking_date))
            db.conn.commit()

            # Обновляем Google Sheets
            if gsheets:
                gsheets.update_booking_status(target_user_id, booking_date, "Проект завершен")

            await state.clear()
        else:
            # Показываем прогресс админу
            progress_text = f"✅ Материал {delivered_parts}/{total_parts} отправлен клиенту!"
            if delivered_parts == 1:
                progress_text += "\n\nОжидаю ссылку на рекламные объявления..."
            elif delivered_parts == 2:
                progress_text += "\n\nОжидаю инструкцию..."
            elif delivered_parts == 3:
                progress_text += "\n\nОжидаю финальное сообщение для клиента..."

            await message.answer(progress_text)

    except Exception as e:
        logger.error(f"Ошибка отправки проекта: {e}")
        await message.answer("❌ Ошибка отправки материала")

# 📍 АДМИН ПАНЕЛЬ

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        return

    text = """
👨‍💼 <b>Админ панель</b>

Доступные команды:
/bookings - Посмотреть бронирования
/stats - Статистика
/remind - Отправить напоминания
/project_status user_id - Статус проекта

Также используйте кнопки доставки проекта из уведомлений о бронированиях.
    """
    await message.answer(text)


@dp.message(Command("remind"))
async def send_manual_reminders(message: Message):
    if message.from_user.id != config.ADMIN_ID:
        return

    await reminder_system.send_booking_reminders(bot)
    await message.answer("✅ Напоминания отправлены")


@dp.message(Command("refund"))
async def process_refund(message: Message):
    """Обработка возврата средств (только для админа)"""
    if message.from_user.id != config.ADMIN_ID:
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("Использование: /refund payment_id [amount]")
            return

        payment_id = parts[1]
        amount = float(parts[2]) if len(parts) > 2 else None

        success = await PaymentManager.process_refund(payment_id, amount)
        if success:
            await message.answer("✅ Возврат успешно обработан")
        else:
            await message.answer("❌ Ошибка возврата")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


# 📍 ЗАПУСК БОТА

async def start_schedulers():
    """Запускает все планировщики"""
    asyncio.create_task(reminder_system.start_reminder_scheduler(bot))


async def main():
    logger.info("Бот Айви запущен!")
    await start_schedulers()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())