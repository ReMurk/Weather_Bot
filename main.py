from loguru import logger
import requests
from aiogram import Bot, Dispatcher, executor, types
from config import telegram_api_key, openweathermap_APIKEY

bot = Bot(token=telegram_api_key)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    user = message.from_user
    await message.answer(f'🌤 Привет {user.first_name}, я простой бот который поможет тебе узнать погоду в любом городе.\n'
                         '🔎 Пришли мне название города в котором ты хочешь узнать погоду')


@dp.message_handler()
async def get_city(message: types.Message):
    city = message.text
    city_cods = get_city_cords(city)
    if city_cods == 'Server Error':
        await message.answer('Ошибка соединения с сервером при получении координат, попробуйте позже')
    else:
        lat = city_cods[0]
        lon = city_cods[1]
        wtr_in_user_city = get_weather_now(lat, lon)
        if wtr_in_user_city == 'Server Error':
            await message.answer('Ошибка соединения с сервером, попробуйте позже')
        else:
            wtr_desc = f"⛅ {wtr_in_user_city['weather'][0]['description']}"
            wtr_desc = str(wtr_desc).capitalize()
            wtr_temp = f"🌡 Температура: {round(int(wtr_in_user_city['main']['temp']))}°C.\n" \
                       f"    🔸 Ощущается как: {round(int(wtr_in_user_city['main']['feels_like']))}°C"
            wtr_temp_min = f"    🔸 Минимальная темпаратура: {round(int(wtr_in_user_city['main']['temp_min']))}°C"
            wtr_temp_max = f"    🔸 Максимальная темпаратура: {round(int(wtr_in_user_city['main']['temp_max']))}°C."
            wtr_pressure = f"🌱 Давление: {wtr_in_user_city['main']['pressure']} hPa"
            wtr_humidity = f"💧 Влажность: {wtr_in_user_city['main']['humidity']}%"
            wtr_visibility = f"🌫 Видимость: {wtr_in_user_city['visibility']}м"
            wtr_wind_speed = f"🌬 Скорость ветра: {wtr_in_user_city['wind']['speed']}м\с"
            mes_title = f'🌍 Погода в городе {city}:'
            await message.answer(f'{mes_title}\n'
                                 f'{wtr_desc}\n'
                                 f'{wtr_temp}\n'
                                 f'{wtr_temp_max}\n'
                                 f'{wtr_temp_min}\n'
                                 f'{wtr_pressure}\n'
                                 f'{wtr_humidity}\n'
                                 f'{wtr_visibility}\n'
                                 f'{wtr_wind_speed}\n')
            wth_today = get_today_weather(lat, lon)
            await message.answer(f'🌡 Температура в ближайшие 24 часа:\n'
                                 f'⏱ {wth_today["list"][0]["dt_txt"]}:'
                                 f' 🌡 {round(int(wth_today["list"][0]["main"]["temp"]))}°C\n'
                                 f'⏱ {wth_today["list"][1]["dt_txt"]}:'
                                 f' 🌡 {round(int(wth_today["list"][1]["main"]["temp"]))}°C\n'
                                 f'⏱ {wth_today["list"][2]["dt_txt"]}:'
                                 f' 🌡 {round(int(wth_today["list"][2]["main"]["temp"]))}°C\n'
                                 f'⏱ {wth_today["list"][3]["dt_txt"]}:'
                                 f' 🌡 {round(int(wth_today["list"][3]["main"]["temp"]))}°C\n'
                                 f'⏱ {wth_today["list"][4]["dt_txt"]}:'
                                 f' 🌡 {round(int(wth_today["list"][4]["main"]["temp"]))}°C\n'
                                 f'⏱ {wth_today["list"][5]["dt_txt"]}:'
                                 f' 🌡 {round(int(wth_today["list"][5]["main"]["temp"]))}°C\n'
                                 f'⏱ {wth_today["list"][6]["dt_txt"]}:'
                                 f' 🌡 {round(int(wth_today["list"][6]["main"]["temp"]))}°C\n'
                                 f'⏱ {wth_today["list"][7]["dt_txt"]}:'
                                 f' 🌡 {round(int(wth_today["list"][7]["main"]["temp"]))}°C\n'
                                 )


def get_city_cords(city):
    cords_req_url = f'http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={openweathermap_APIKEY}'
    req = requests.get(cords_req_url)
    if req.status_code == 200:
        req = req.json()
        lat = req[0]['lat']
        lon = req[0]['lon']
        return [lat, lon]
    else:
        return 'Server Error'


def get_weather_now(lat, lon):
    get_weather_url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}' \
                      f'&units=metric&appid={openweathermap_APIKEY}&lang=ru'
    req = requests.get(get_weather_url)
    if req.status_code == 200:
        req = req.json()
        return req
    else:
        logger.error('Ошибка при запросе на сервер с погодой')
        return 'Server Error'


def get_today_weather(lat, lon):
    url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={openweathermap_APIKEY}' \
          f'&units=metric&cnt=8&lang=ru'
    req = requests.get(url)
    if req.status_code == 200:
        req = req.json()
        return req
    else:
        return 'Server Error'


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
