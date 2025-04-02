import asyncio
import json
import logging
import sys

from logger import logger
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, URLInputFile, ReplyKeyboardRemove
from states import *
from commands import *
from commands import BOT_COMMANDS
from config import BOT_TOKEN as TOKEN
from data import get_films, add_film
from keyboards import films_keyboard_markup, FilmCallback
from models import Film
from aiogram.fsm.context import FSMContext
from collections import Counter

dp = Dispatcher()


@dp.message(EDIT_FILM_COMMAND)
async def edit_film(message: Message, state: FSMContext) -> None:
    all_films = get_films()
    if not all_films:
        await message.answer("Список фільмів порожній!")
        return
    await state.update_data(all_films=all_films)
    await state.set_state(FilmEdit.edit_query)
    await message.answer(
        "Оберіть фільм для редагування з клавіатури або введіть назву вручну:",
        reply_markup=films_keyboard_markup(all_films)
    )
    logger.info("Запущено редагування фільму")


@dp.callback_query(FilmCallback.filter(), FilmEdit.edit_query)
async def process_edit_callback(callback: CallbackQuery, callback_data: FilmCallback, state: FSMContext) -> None:
    film_name = callback_data.name
    data = await state.get_data()
    all_films = data['all_films']
    film_index = next((i for i, film in enumerate(all_films) if film['name'].lower() == film_name.lower()), -1)

    if film_index == -1:
        await callback.message.answer("Фільм не знайдено!")
        await state.clear()
        return

    await state.update_data(film_index=film_index)
    await state.set_state(FilmEdit.name)
    await callback.message.answer(
        f"Ви обрали '{all_films[film_index]['name']}'. Введіть нову назву (поточна: {all_films[film_index]['name']}):"
    )
    logger.info(f"Обрано фільм через callback: {all_films[film_index]['name']}")
    await callback.answer()


@dp.message(FilmEdit.edit_query)
async def process_edit_query(message: Message, state: FSMContext) -> None:
    film_name = message.text.lower()
    data = await state.get_data()
    all_films = data['all_films']
    film_index = next((i for i, film in enumerate(all_films) if film['name'].lower() == film_name), -1)

    if film_index == -1:
        await message.answer("Фільм не знайдено!")
        await state.clear()
        return

    await state.update_data(film_index=film_index)
    await state.set_state(FilmEdit.name)
    await message.answer(
        f"Ви обрали '{all_films[film_index]['name']}'. Введіть нову назву (поточна: {all_films[film_index]['name']}):"
    )
    logger.info(f"Обрано фільм через введення: {all_films[film_index]['name']}")


@dp.message(FilmEdit.name)
async def edit_name(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    film_index = data['film_index']
    all_films = data['all_films']

    new_name = message.text.strip()
    if new_name:
        all_films[film_index]['name'] = new_name
        logger.info(f"Назву змінено на: {new_name}")

    await state.set_state(FilmEdit.description)
    await message.answer(
        f"Введіть новий опис (поточний: {all_films[film_index]['description']}):"
    )


@dp.message(FilmEdit.description)
async def edit_description(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    film_index = data['film_index']
    all_films = data['all_films']

    new_desc = message.text.strip()
    if new_desc:
        all_films[film_index]['description'] = new_desc
        logger.info(f"Опис змінено на: {new_desc}")

    await state.set_state(FilmEdit.rating)
    await message.answer(
        f"Введіть новий рейтинг (поточний: {all_films[film_index]['rating']}):"
    )


@dp.message(FilmEdit.rating)
async def edit_rating(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    film_index = data['film_index']
    all_films = data['all_films']

    new_rating = message.text.strip()
    if new_rating:
        try:
            all_films[film_index]['rating'] = float(new_rating)
            logger.info(f"Рейтинг змінено на: {new_rating}")
        except ValueError:
            await message.answer("Рейтинг має бути числом!")

    await state.set_state(FilmEdit.genre)
    await message.answer(
        f"Введіть новий жанр (поточний: {all_films[film_index]['genre']}):"
    )


@dp.message(FilmEdit.genre)
async def edit_genre(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    film_index = data['film_index']
    all_films = data['all_films']

    new_genre = message.text.strip()
    if new_genre:
        all_films[film_index]['genre'] = new_genre
        logger.info(f"Жанр змінено на: {new_genre}")

    await state.set_state(FilmEdit.year)
    await message.answer(
        f"Введіть новий рік (поточний: {all_films[film_index]['year']}):"
    )


@dp.message(FilmEdit.year)
async def edit_film_year(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    film_index = data['film_index']
    all_films = data['all_films']

    new_year = message.text.strip()
    if new_year:
        try:
            year = int(new_year)
            if 1900 <= year <= 2100:
                all_films[film_index]['year'] = year
                logger.info(f"Рік змінено на: {year}")
            else:
                await message.answer("Рік має бути від 1900 до 2100!")
                return
        except ValueError:
            await message.answer("Введіть рік числом!")
            return

    await state.set_state(FilmEdit.actors)
    await message.answer(
        f"Введіть нових акторів через ', ' (поточні: {', '.join(all_films[film_index]['actors'])}):"
    )


@dp.message(FilmEdit.actors)
async def edit_actors(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    film_index = data['film_index']
    all_films = data['all_films']

    new_actors = message.text.strip()
    if new_actors:
        all_films[film_index]['actors'] = [x.strip() for x in new_actors.split(", ")]
        logger.info(f"Акторів змінено на: {all_films[film_index]['actors']}")

    await state.set_state(FilmEdit.poster)
    await message.answer(
        f"Введіть нове посилання на постер (поточний: {all_films[film_index]['poster']}):"
    )


@dp.message(FilmEdit.poster)
async def edit_poster(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    film_index = data['film_index']
    all_films = data['all_films']

    new_poster = message.text.strip()
    if new_poster:
        all_films[film_index]['poster'] = new_poster
        logger.info(f"Постер змінено на: {new_poster}")

    try:
        with open("data.json", "w", encoding="utf-8") as fp:
            json.dump(all_films, fp, indent=4, ensure_ascii=False)
        logger.info("Всі зміни збережено у файл")
        await message.answer(f"Фільм '{all_films[film_index]['name']}' успішно відредаговано!")
    except Exception as e:
        logger.error(f"Помилка при збереженні: {str(e)}")
        await message.answer(f"Помилка при збереженні: {str(e)}")

    await state.clear()


@dp.message(DELETE_FILM_COMMAND)
async def delete_film(message: Message, state: FSMContext) -> None:
    await state.set_state(FilmDelete.delete_query)
    all_films = get_films()
    if not all_films:
        await message.answer("Список фільмів порожній!")
        await state.clear()
        return
    await message.answer(
        "Введіть назву фільму, який хочете видалити",
        reply_markup=films_keyboard_markup(all_films)
    )


@dp.message(FilmDelete.delete_query)
async def process_delete_query(message: Message, state: FSMContext) -> None:
    film_name = message.text.lower()
    all_films = get_films()
    film_index = next((i for i, film in enumerate(all_films) if film['name'].lower() == film_name), -1)

    if film_index == -1:
        await message.answer("Фільм не знайдено!")
        await state.clear()
        return

    deleted_film = all_films.pop(film_index)

    with open("data.json", "w") as fp:
        json.dump(all_films, fp, indent=4, ensure_ascii=False)

    await message.answer(f"Фільм '{deleted_film['name']}' успішно видалено!")
    await state.clear()

@dp.message(SEARCH_MOVIE_COMMAND)
async def search_film(message: Message, state: FSMContext) -> None:
    await state.set_state(FilmSort.search_query)
    await message.answer(
        'Введiть назву фiльму.',
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(SEARCH_FILM_BY_ACTOR)
async def search_by_actor(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchByActor.actor_query)
    await message.answer(
        'Введите имя актера для поиска.',
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(SearchByActor.actor_query)
async def process_actor_query(message: Message, state: FSMContext) -> None:
    actor_query = message.text.lower()
    all_films = get_films()
    results = [film for film in all_films if any(actor_query in actor.lower() for actor in film['actors'])]
    if results:
        await message.reply('Поиск выполнен', reply_markup=films_keyboard_markup(results))
    else:
        await message.reply('Ничего не найдено')
    await state.clear()


@dp.message(FILM_STATS_COMMAND)
async def film_stats(message: Message) -> None:
    all_films = get_films()
    if not all_films:
        await message.answer("Список фільмів порожній! Немає даних для статистики.")
        return

    total_films = len(all_films)

    avg_rating = sum(film['rating'] for film in all_films) / total_films

    genres = [film['genre'].split(',')[0].strip().lower() for film in all_films]
    most_common_genre = Counter(genres).most_common(1)[0]
    popular_genre = f"{most_common_genre[0]} ({most_common_genre[1]} фільмів)"

    years = [film['year'] for film in all_films]
    oldest_year = min(years)
    newest_year = max(years)

    stats_text = (
        f"📊 **Статистика фільмів** 📊\n\n"
        f"Кількість фільмів: {total_films}\n"
        f"Середній рейтинг: {avg_rating:.2f}\n"
        f"Найпопулярніший жанр: {popular_genre}\n"
        f"Найстаріший рік: {oldest_year}\n"
        f"Найновіший рік: {newest_year}"
    )

    await message.answer(stats_text, parse_mode=ParseMode.MARKDOWN)
    logger.info("Показана статистика фільмів")

@dp.message(FILTER_MOVIES_COMMAND)
async def filter_films(message: Message, state: FSMContext) -> None:
    await state.set_state(FilmFilter.filter_criteria)
    await message.answer(
        'Введiть жанр або рейтинг для пошуку фiльму.',
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(FilmFilter.filter_criteria)
async def filter_criteria(message: Message, state: FSMContext) -> None:
    criteria = message.text.strip().lower()
    all_films = get_films()

    try:
        rating_criteria = float(criteria)
        result = [film for film in all_films if film["rating"] == rating_criteria]
    except ValueError:
        result = [film for film in all_films if criteria in film["genre"].lower()]

    if result:
        await message.reply(
            "Знайдені такі фільми:",
            reply_markup=films_keyboard_markup(result)
        )
    else:
        await message.reply(
            "Нiчого не знайдено за вашим запитом!"
        )

    await state.clear()


@dp.message(FilmSort.search_query)
async def search_query(message: Message, state: FSMContext) -> None:
    query = message.text.lower()
    all_films = get_films()
    results = [film for film in all_films if query in film['name'].lower()]
    if results:
        await message.reply('Поиск выполнен', reply_markup=films_keyboard_markup(results))
    else:
        await message.reply('Ничего не найдено')
    await state.clear()


@dp.message(Command("start"))
async def start(message: Message) -> None:
    logger.debug('Hello')
    await message.answer(
        f"Вітаю, {message.from_user.full_name}!\n"
        "шукай і редагуй фільми на свій смак! Щоб почати, скористайся командами з меню нижче.."
    )


@dp.message(FILMS_COMMAND)
async def films(message: Message) -> None:
    data = get_films()
    markup = films_keyboard_markup(films_list=data)
    await message.answer(
        f"Перелік фільмів. Натисніть на назву фільму для отримання деталей.",
        reply_markup=markup
    )


@dp.message(FILM_CREATE_COMMAND)
async def film_create(message: Message, state: FSMContext) -> None:
    await state.set_state(FilmForm.name)
    await message.answer(
        f"Введіть назву фільму.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.name)
async def film_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(FilmForm.description)
    await message.answer(
        f"Введіть опис фільму.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.description)
async def film_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(FilmForm.rating)
    await message.answer(
        f"Вкажіть рейтинг фільму від 0 до 10.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.rating)
async def film_rating(message: Message, state: FSMContext) -> None:
    await state.update_data(rating=float(message.text))
    await state.set_state(FilmForm.genre)
    await message.answer(
        f"Введіть жанр фільму.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.genre)
async def film_genre(message: Message, state: FSMContext) -> None:
    await state.update_data(genre=message.text)
    await state.set_state(FilmForm.year)
    await message.answer(
        "Введіть рік випуску фільму:",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.year)
async def film_year(message: Message, state: FSMContext) -> None:
    try:
        year = int(message.text.strip())
        if 1900 <= year <= 2100:
            await state.update_data(year=year)
            await state.set_state(FilmForm.actors)
            await message.answer("Введіть акторів через ', ':", reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer("Рік має бути від 1900 до 2100!")
    except ValueError:
        await message.answer("Введіть рік числом!")


@dp.message(FilmForm.actors)
async def film_actors(message: Message, state: FSMContext) -> None:
    await state.update_data(actors=[x.strip() for x in message.text.split(", ")])
    await state.set_state(FilmForm.poster)
    await message.answer(
        "Введіть посилання на постер фільму:",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(FilmForm.poster)
async def film_poster(message: Message, state: FSMContext) -> None:
    await state.update_data(poster=message.text)
    data = await state.get_data()
    film = Film(**data)
    add_film(film.model_dump())
    await message.answer(
        f"Фільм {film.name} успішно додано!",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.clear()


@dp.message()
async def echo_handler(message: Message, state:FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        if message.text and message.text.startswith('/'):
            await message.answer('Такой команды нет!')
        else:
            await message.answer("Не понимаю про что вы. Попробуйте команды с меню!")


@dp.callback_query(FilmCallback.filter())
async def callback_film(callback: CallbackQuery, callback_data: FilmCallback) -> None:
    film_name = callback_data.name
    all_films = get_films()
    film_data = next((film for film in all_films if film['name'] == film_name), None)

    if not film_data:
        await callback.message.answer("Фільм не знайдено!")
        return

    film = Film(**film_data)
    text = f"Фільм: {film.name}\n" \
           f"Опис: {film.description}\n" \
           f"Рейтинг: {film.rating}\n" \
           f"Жанр: {film.genre}\n" \
           f"Рік: {film.year}\n" \
           f"Актори: {', '.join(film.actors)}\n"
    await callback.message.answer_photo(
        caption=text,
        photo=URLInputFile(
            film.poster,
            filename=f"{film.name}_poster.{film.poster.split('.')[-1]}"
        )
    )


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.set_my_commands(BOT_COMMANDS)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())