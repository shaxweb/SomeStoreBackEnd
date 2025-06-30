from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, secrets, difflib

sender_email = "shaxrux243@gmail.com"
sender_password = "ojfb hvou npgr qfhi"  # Используйте пароль приложения, а не обычный!


def send_token_to_email(receiver_email):
    token = secrets.token_hex(16)
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Регистрация!"
    body = f"Ваш ссылка => http://127.0.0.1:8000/auth?token={token}"
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


def check_datas(type, data, data2=None):
	if type == "username":
		if len(data) < 4:
			return {"status": False, "error": "very briefly", "type": type}
		if len(data) > 16:
			return {"status": False, "error": "very long", "type": type}
		
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

