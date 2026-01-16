def get_next_candidate_from_db(user_id, last_id=None):
    """
    Берет следующего кандидата из БД, исключая черный список. Должна возвращать
    id - id кандидата, для записи в last_id
    first_name - имя кандидата,
    last_name - фамилия кандидата,
    vk_link - ссылка на профиль кандидата,
    photos - массив из 3 фотографий
    """
    pass

def add_to_status(user_id, candidate_id, status):
    """
    Добавляет пользователя в избранное или черный список
    user_id - id пользователя, который общается с ботом,
    candidate_id - id кандидата, у которого меняется статус,
    status - статус, например like/dislike
    """
    pass

def get_favorites(user_id):
    """
    Получает список избранных пользователей
    Эти данные должны быть в формате списка с именами, фамилиями и ссылками
    на их профили (например, [('Иван', 'Иванов', 'vk.com/ivanov')])
    """
    pass

def add_user_to_db(user_id):
    """
    Добавляет пользователя в БД, если его еще нет
    get_user_info и get_top3_photos_by_likes из vk_bot_modules поможет получить
    информацию из VK
    """
    pass
