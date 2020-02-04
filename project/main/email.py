from project import app, mail
import smtplib
from email.mime.text import MIMEText

def sendEmail(to, subject, template):
	server=smtplib.SMTP(app.config['MAIL_SERVER_PORT'])
	server.ehlo()
	server.starttls()
	server.login(app.config['MAIL_USERNAME'],app.config['MAIL_PASSWORD'])
	recipients = ['equipos@qairadrones.com','l.montalvo@qairadrones.com', 's.campos@qairadrones.com','p.casabona@qairadrones.com','c.laurel@qairadrones.com']	
	try:
		msg = MIMEText(template)
		msg['Subject'] = subject
		msg['From'] = app.config['MAIL_DEFAULT_SENDER']
		msg['To'] = ", ".join(recipients)
		server.sendmail(app.config['MAIL_DEFAULT_SENDER'],recipients,msg.as_string().encode('utf-8').strip())	
		server.quit()
		print("Success: Email Sent!!!")
	except:
		print("Email failed to send!!!")