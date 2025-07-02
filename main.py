import telebot
from telebot import types
from together import Together
import requests
import time

# різні апі та токени для роботи з ботом та моделями
BOT_TOKEN = "PUT YOUR TOKEN HERE IF YOU WANT TO TEST"
TOGETHER_API_KEY = "PUT YOUR TOKEN HERE IF YOU WANT TO TEST"
API_URL = "PUT YOUR TOKEN HERE IF YOU WANT TO TEST"
headers = {"PUT YOUR TOKEN HERE IF YOU WANT TO TEST"}

bot = telebot.TeleBot(BOT_TOKEN)

# статус користувача, щоб знати де він
user_mode = {}

# меню
@bot.message_handler(commands=['start', 'menu', 'home', 'exit'])
def send_main_menu(message):
    # створення меню
    menu_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # створення до нього кнопок
    btn1 = types.KeyboardButton("GPT🤖")
    btn2 = types.KeyboardButton("Image Generation🌌")
    btn3 = types.KeyboardButton("Profile")
    btn4 = types.KeyboardButton("Close")
    # додавання кнопок до меню, та створення user_mode який використовується, щоб знати де знаходиться користувач
    menu_buttons.add(btn1, btn2, btn3, btn4)
    user_mode[message.chat.id] = None

    bot.send_message(message.chat.id, "menu:", reply_markup=menu_buttons)

# Text AI
# масив для історії чату
chat_histories = {}

# функція ловить повідомлення GPT🤖 яке друкується при нажатті кноопки
@bot.message_handler(func=lambda message: message.text == "GPT🤖")
def together_ai(message):
    bot.send_message(message.chat.id, "Ask your question or type /exit to return to the menu",
                     reply_markup=types.ReplyKeyboardRemove())
    # масив для запису історії чату, щоб AI пам'ятав попередьні запитання
    chat_histories[message.chat.id] = [{"role": "system", "content": ""}]
    # присвоєння користувачу статусу gpt
    user_mode[message.chat.id] = "gpt"

# функція ловить всі повідомлення якщо статус користувача gpt
@bot.message_handler(func=lambda message: user_mode.get(message.chat.id) == "gpt")
def ask_together_ai(message):
    # створення об'єкта текстової моделі, та додавання запиту користувача до історії
    client = Together(api_key=TOGETHER_API_KEY)
    chat_histories[message.chat.id].append({"role": "user", "content": message.text})

    # генерація відповіді
    answer = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        temperature=0.7,
        top_p=0.9,
        messages=chat_histories[message.chat.id],
    )

    # отримання, виддача та запис відповіді
    response_text = answer.choices[0].message.content
    bot.send_message(message.chat.id, response_text)
    chat_histories[message.chat.id].append({"role": "assistant", "content": response_text})

# Image Generation
# тут код ловить повідомлення Image Generation🌌 яке відправляється при натисканні кнопки
@bot.message_handler(func=lambda message: message.text == "Image Generation🌌")
def request_image_prompt(message):
    bot.send_message(message.chat.id, "Enter your prompt, or type /exit to return to the menu", reply_markup=types.ReplyKeyboardRemove())
    # присвоєння статуса користувачу
    user_mode[message.chat.id] = "img_g"

# функція ловить повідомлення якщо статус користувача img_g
@bot.message_handler(func=lambda message: user_mode.get(message.chat.id) == "img_g")
def generate_images(message):
    seed = int(time.time() * 1000)
    # виклик моделі
    def query(payload):
        bot.send_message(message.chat.id, "⏳ Generating image...")
        # запис зображення та перевірка чи немає помилок
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Error: {response.status_code}")
            bot.send_message(message.chat.id, "sorry something went wrong, try again later")

    # генерація зображення
    image = query({
    "inputs": message.text,
    "options": {
        "num_inference_steps": 150,
        "seed": seed
    }
})
    # посилання зображення користувачу
    bot.send_photo(message.chat.id, image)



# Other stuff
# міні функція яка виводить інформацію про користувача
@bot.message_handler(func=lambda message: message.text == "Profile")
def close_menu(message):
    bot.send_message(message.chat.id, f"name:{message.from_user.first_name}"
                                      f"\nusername:{message.from_user.username}"
                                      f"\nid:{message.from_user.id}"
                                      f"\npremium:{message.from_user.is_premium}")







# функція, щоб закрити меню
@bot.message_handler(func=lambda message: message.text == "Close")
def close_menu(message):
    bot.send_message(message.chat.id, "See ya soon", reply_markup=types.ReplyKeyboardRemove())

# функція info, яка мала б виводити інформацію про бота.
@bot.message_handler(commands=['info'])
def info_command(message):
    bot.send_message(message.chat.id, "Too lazy to write allat😞😓")

# 🤫
@bot.message_handler(commands=['secret'])
def secret(message):
    bot.send_message(message.chat.id,'https://youtu.be/dQw4w9WgXcQ?si=NlklcvW9zAWhss4t')

print("Bot started...")
# команда яка заставляє бота працювати вічно
bot.polling()
