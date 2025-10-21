import asyncio
from datetime import datetime, timedelta
import logging
from database import Database
import config

logger = logging.getLogger(__name__)
db = Database()


class ReminderSystem:
    def __init__(self, gsheets=None):  # Добавляем параметр gsheets
        self.gsheets = gsheets

    async def send_booking_reminders(self, bot):
        """Отправляет напоминания о бронированиях"""
        try:
            # Используем локальную базу данных вместо Google Sheets для напоминаний
            today_bookings = db.get_today_bookings()

            for booking in today_bookings:
                user_id = booking[1]  # user_id field from database
                booking_date = booking[4]  # booking_date field
                final_paid = booking[7]  # final_paid field

                try:
                    # Если финальная оплата еще не произведена
                    if not final_paid:
                        from keyboards import get_payment_keyboard
                        await bot.send_message(
                            user_id,
                            f"🔄 <b>Ваш проект в разработке!</b>\n\n"
                            f"Сегодня ({booking_date}) мы работаем над вашим проектом. "
                            f"Пожалуйста, оплатите оставшуюся сумму <b>11 000 ₽</b> до 20:00 по МСК, "
                            f"чтобы мы могли отправить вам готовый проект.\n\n"
                            f"<i>После оплаты вы получите:</i>\n"
                            f"• Ссылку на готовый сайт\n"
                            f"• Рекламные объявления\n"
                            f"• Инструкцию по работе",
                            parse_mode="HTML",
                            reply_markup=get_payment_keyboard(config.FINAL_AMOUNT, is_final=True,
                                                              show_check_button=True)
                        )
                        logger.info(f"Напоминание о финальной оплате отправлено пользователю {user_id}")
                    else:
                        logger.info(f"Пользователь {user_id} уже оплатил финальную часть")

                except Exception as e:
                    logger.error(f"Ошибка отправки напоминания пользователю {user_id}: {e}")

            logger.info(f"Отправлены напоминания для {len(today_bookings)} бронирований")

        except Exception as e:
            logger.error(f"Ошибка отправки напоминаний: {e}")

    async def start_reminder_scheduler(self, bot):
        """Запускает планировщик напоминаний"""
        while True:
            now = datetime.now()

            # Проверяем каждый день в указанное время
            if now.hour == config.REMINDER_HOUR and now.minute == 20:
                await self.send_booking_reminders(bot)
                # Ждем 1 минуту чтобы не запускать повторно в течение часа
                await asyncio.sleep(60)

            await asyncio.sleep(60)  # Проверяем каждую минуту