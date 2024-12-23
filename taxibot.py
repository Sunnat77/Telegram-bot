import json
import requests

TOKEN = '7764939373:AAESwA2W6MZMq-RHms-8fMRXfJIY_LkXpyg'
ADMIN_ID = '7303011450'
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"
SUBSCRIBERS_FILE = 'obunachi.txt'

def add_user(chat_id):
    with open(SUBSCRIBERS_FILE, 'a+') as f:
        f.seek(0)
        users = f.read().splitlines()
        if str(chat_id) not in users:
            f.write(f"{chat_id}\n")

def send_message(chat_id, text, keyboard=None):
    data = {
        'chat_id': chat_id,
        'text': text,
    }
    if keyboard:
        data['reply_markup'] = json.dumps(keyboard)
    
    response = requests.post(BASE_URL + 'sendMessage', data=data)
    return response.json()

def send_to_admin(message):
    data = {
        'chat_id': ADMIN_ID,
        'text': message
    }
    response = requests.get(BASE_URL + 'sendMessage', params=data)
    return response.json()

def handle_message(update):
    chat_id = update['message']['chat']['id']
    message = update['message']['text']
    username = update['message']['chat'].get('username', 'Noma\'lum')

    if message == "/start":
        add_user(chat_id)
        keyboard = {
            'inline_keyboard': [
                [{'text': 'Taksi zakaz (app)', 'url': 'http://t.me/eQatnovBot/taxi'}],
                [{'text': '🧍‍♂️ Yo\'lovchi', 'callback_data': 'passenger'},
                 {'text': '📦 Pochta', 'callback_data': 'post'}],
                [{'text': '👨‍✈️ Haydovchilikka ariza', 'callback_data': 'driver'}]
            ]
        }
        send_message(chat_id, "👋 Assalomu alaykum!\n\n🚕 Toshkent-Buxoro yo'nalishi transport xizmatiga xush kelibsiz!\n\n✅ Quyidagi xizmatlardan birini tanlang:", keyboard)
    else:
        with open(f"session_{chat_id}.json", 'r') as f:
            session = json.load(f)
        
        if session['type'] == 'post':
            route = session['route']
            admin_message = f"📦 Pochta ma'lumotlari:\nYo'nalish: {route}\nMa'lumot: {message}\nFoydalanuvchi ID: {chat_id}\nUsername: @{username}\nVaqt: {datetime.now().strftime('%H:%M:%S')}"
            send_to_admin(admin_message)
            send_message(chat_id, "📦 Pochta ma'lumotlari adminlarga yuborildi.")
            os.remove(f"session_{chat_id}.json")
        
        elif session['type'] == 'passenger':
            route = session['route']
            people = session['people']
            admin_message = f"🧍‍♂️ Yo'lovchi ma'lumotlari:\nYo'nalish: {route}\nKishi soni: {people}\nFoydalanuvchi ID: {chat_id}\nUsername: @{username}\nVaqt: {datetime.now().strftime('%H:%M:%S')}"
            send_to_admin(admin_message)
            send_message(chat_id, "Yo'lovchi ma'lumotlari adminlarga yuborildi.")
            os.remove(f"session_{chat_id}.json")
        
        elif session['type'] == 'driver':
            admin_message = f"👨‍✈️ Haydovchi ma'lumotlari:\nIsm: {message}\nFoydalanuvchi ID: {chat_id}\nUsername: @{username}\nVaqt: {datetime.now().strftime('%H:%M:%S')}"
            send_to_admin(admin_message)
            send_message(chat_id, "👨‍✈️ Haydovchi ma'lumotlari adminlarga yuborildi.")
            os.remove(f"session_{chat_id}.json")

def handle_callback_query(update):
    callback_query = update['callback_query']
    chat_id = callback_query['message']['chat']['id']
    message_id = callback_query['message']['message_id']
    data = callback_query['data']
    username = callback_query['from'].get('username', 'Noma\'lum')

    if data == 'post':
        keyboard = {
            'inline_keyboard': [
                [{'text': 'Toshkent » Buxoro', 'callback_data': 'Toshkent-Buxoro'},
                 {'text': 'Buxoro » Toshkent', 'callback_data': 'Buxoro-Toshkent'}]
            ]
        }
        send_message(chat_id, "📦 Pochta uchun qaysi yo'nalishda yubormoqchisiz?", keyboard)

    elif data == 'passenger':
        keyboard = {
            'inline_keyboard': [
                [{'text': 'Toshkent » Buxoro', 'callback_data': 'passenger_Toshkent-Buxoro'},
                 {'text': 'Buxoro » Toshkent', 'callback_data': 'passenger_Buxoro-Toshkent'}]
            ]
        }
        send_message(chat_id, "🧍‍♂️ Yo'lovchi uchun qaysi yo'nalishda ketmoqchisiz?", keyboard)

    elif data.startswith('passenger_'):
        route = data.split('_')[1]
        keyboard = {
            'inline_keyboard': [
                [{'text': '1', 'callback_data': f'passenger_{route}_1'},
                 {'text': '2', 'callback_data': f'passenger_{route}_2'},
                 {'text': '3', 'callback_data': f'passenger_{route}_3'},
                 {'text': '4', 'callback_data': f'passenger_{route}_4'}]
            ]
        }
        send_message(chat_id, "Necha kishi ketmoqchisiz?", keyboard)

    elif 'passenger_' in data:
        route, number_of_people = data.split('_')[1], data.split('_')[2]
        session_data = {'type': 'passenger', 'route': route, 'people': number_of_people}
        with open(f"session_{chat_id}.json", 'w') as f:
            json.dump(session_data, f)
        send_message(chat_id, "Telefon raqamingizni yuboring (format: +998901234567)")

    elif data in ['Toshkent-Buxoro', 'Buxoro-Toshkent']:
        route = data
        session_data = {'type': 'post', 'route': route}
        with open(f"session_{chat_id}.json", 'w') as f:
            json.dump(session_data, f)
        send_message(chat_id, "📞 Telefon raqamingizni yuboring (format: +998901234567)")

    elif data == 'driver':
        send_message(chat_id, "Ism va familiyangizni kiriting, telefon raqamingizni kiriting.")
        session_data = {'type': 'driver'}
        with open(f"session_{chat_id}.json", 'w') as f:
            json.dump(session_data, f)

def main():
    update = json.loads(requests.get('php://input').text)
    
    if 'message' in update:
        handle_message(update)
    elif 'callback_query' in update:
        handle_callback_query(update)

if __name__ == '__main__':
    main()
