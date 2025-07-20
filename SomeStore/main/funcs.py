from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, secrets, difflib
import requests, time

sender_email = "shaxrux243@gmail.com"
sender_password = "ojfb hvou npgr qfhi"  # Используйте пароль приложения, а не обычный!


def send_token_to_email(receiver_email):
    token = secrets.token_hex(16)
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Регистрация!"
    body = f"Ваш ссылка => https://somestorebackend.onrender.com/auth?token={token}"
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        return {"status": True, "token": token}
    except Exception as e:
        return {"status": False, "error": str(e)}


def send_login_message_to_mail(receiver_email, user_agent):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Был вход на ваш устройство"
    body = f"был вход с устройства {user_agent}"
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        return {"status": True}
    except Exception as e:
        return {"status": False, "error": str(e)}


def check_datas(type, data, data2=None):
	if type == "username":
		if len(data) < 4:
			return {"status": False, "error": "very briefly", "type": type}
		if len(data) > 16:
			return {"status": False, "error": "very long", "type": type}
		if " " in data:
			return {"status": False, "error": "without space", "type": type}
		
		symbols = [i for i in "qwertyuiopasdfghjklzxcvbnm1234567890_"]
		for i in data:
			if i not in symbols:
				return {"status": False, "error": f"symbol '{i}' not found", "type": type}
		return {"status": True, "message": data, "type": type}
	
	elif type == "password":
		if len(data) < 8:
			return {"status": False, "error": "very briefly", "type": type}
		if data != data2:
			return {"status": False, "error": "password not match", "type": type}
		
		return {"status": True, "message": data, "type": type}
	
	elif type == "email":
		if "@gmail.com" not in data:
			return {"status": False, "error": "uncorrect email", "type": type}
		return {"status": True, "message": data, "type": type}
	return {"status": False, "error": "what?", "type": type}


def watch_service():
	while True:
		TOKEN = '8158445939:AAHmoesq6Em6F5QdxcNhRJYSVL2pTLpUyn0'
		CHAT_ID = '6181120570'
		url = "https://somestorebackend.onrender.com"
		bot_url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
		res = requests.get(url)
		
		body = {
			"chat_id": CHAT_ID,
			"text": str(res),
			"parse_mode": "HTML"
		}
		requests.post(bot_url, data=body)
		time.sleep(5)


def get_tg_file_path(file_id):
	token = "8158445939:AAHmoesq6Em6F5QdxcNhRJYSVL2pTLpUyn0"
	
	get_file_url = f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}"
	res = requests.get(get_file_url)
	file_path = res.json()["result"]["file_path"]
	return file_path


def search_products(query, products):
    results = []

    for row in products:
        title = row[1].lower()
        description = row[2].lower()
        if query in title or query in description:
            results.append(row)
        else:
            matches = difflib.get_close_matches(query, [title], cutoff=0.6)
            if matches:
                results.append(row)

    return results
