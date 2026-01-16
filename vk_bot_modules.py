import os
import vk_api

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from dotenv import load_dotenv

from db_modules import (get_next_candidate_from_db, add_to_status,
                        get_favorites, add_user_to_db)

load_dotenv()

access_token_bot = os.getenv('TOKEN_BOT')
access_token_user = os.getenv('TOKEN_APP')
user_id = os.getenv('VK_ID')

# Авторизация через токен пользователя (для получения данных)
vk_user_session = vk_api.VkApi(token=access_token_user)
vk_user = vk_user_session.get_api()

# Авторизация через токен группы (для бота)
vk_bot_session = vk_api.VkApi(token=access_token_bot)
vk_bot = vk_bot_session.get_api()
longpoll = VkLongPoll(vk_bot_session)

# Функция создания клавиатуры
def create_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Следующий", VkKeyboardColor.PRIMARY)
    keyboard.add_button("В избранное", VkKeyboardColor.POSITIVE)
    keyboard.add_button("В черный список", VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button("Список избранных", VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()

# Функция отправки сообщений с кнопками
def send_message(user_id, message, attachment=None, keyboard=None):
    vk_bot.messages.send(
        user_id=user_id,
        message=message,
        random_id=get_random_id(),
        attachment=attachment,
        keyboard=keyboard
    )

# Получение данных о пользователе
def get_user_info(user_id):
    user_info = vk_user.users.get(user_ids=user_id, fields="bdate,sex,city")[0]
    return user_info

# Получение 3 самых популярных фотографий пользователя
def get_top3_photos_by_likes(user_id):
    photos = vk_user.photos.get(
        owner_id=user_id,
        album_id='profile',  # Альбом профиля
        extended=1,          # Включает лайки
        count=100            # Получаем 100 фото для выбора
    )

    # Сортируем по лайкам
    sorted_photos = sorted(
        photos['items'],
        key=lambda x: x['likes']['count'],
        reverse=True
    )[:3]

    attachments = []
    for photo in sorted_photos:
        max_size = max(photo['sizes'], key=lambda s: s['width'] * s['height'])
        attachments.append(f"photo{photo['owner_id']}_{photo['id']}")  # Формат для attachment

    return attachments

# Отправка информации о кандидате пользователю
def send_user_info(user_id, first_name, last_name, vk_link, photos):
    name = f"{first_name} {last_name}"
    profile_link = vk_link
    send_message(user_id, f"Имя: {name}\nСсылка на профиль: {profile_link}",
                 attachment=",".join([p for p in photos if p]),
                 keyboard=create_keyboard())

# Словарь для хранения последнего показанного кандидата для каждого пользователя
user_last_candidate = {}

def start_bot():
    print("Бот запущен...")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            text = event.text.lower()

            # Добавляем пользователя в БД, если его еще нет
            add_user_to_db(user_id)

            if text == "привет":
                send_message(user_id,
                             "Привет! Я помогу тебе найти людей для знакомства.\n"
                             "Используй кнопки ниже для взаимодействия.",
                             keyboard=create_keyboard())

            elif text == "следующий":
                last_id = user_last_candidate.get(user_id)
                candidate = get_next_candidate_from_db(user_id, last_id)
                if candidate:
                    user_last_candidate[user_id] = candidate[0]  # id кандидата
                    send_user_info(user_id, candidate[1], candidate[2],
                                   candidate[3], candidate[4])
                else:
                    send_message(user_id, "Больше кандидатов нет.")

            elif text == "в избранное":
                last_id = user_last_candidate.get(user_id)
                if last_id:
                    add_to_status(user_id, last_id, "") # Нужно добавить статус
                    send_message(user_id, "Пользователь добавлен в избранное!")
                else:
                    send_message(user_id, "Сначала выберите кандидата.")

            elif text == "в черный список":
                last_id = user_last_candidate.get(user_id)
                if last_id:
                    add_to_status(user_id, last_id, "") # Нужно добавить статус
                    send_message(user_id, "Пользователь добавлен в черный список!")
                else:
                    send_message(user_id, "Сначала выберите кандидата.")

            elif text == "список избранных":
                favorites = get_favorites(user_id)
                if favorites:
                    message = "\n".join([f"{idx+1}. {f[0]} {f[1]} — {f[2]}"
                                         for idx, f in enumerate(favorites)])
                else:
                    message = "Список избранных пуст."
                send_message(user_id, message)

            else:
                send_message(user_id, "Не понимаю команду. Используй кнопки для взаимодействия.")
