def send_email_safely():
    import smtplib
    import ssl
    from email.message import EmailMessage

    sender = 'kapilmeghnani51@gmail.com'
    password = 'mheh khrt bwox hjrc'
    receiver = "Kapil_r_meghnani@hotmail.com"

    msg = EmailMessage()
    msg.set_content("This is a test email from smtplib.")
    msg["Subject"] = "Test Email"
    msg["From"] = sender
    msg["To"] = receiver

    context = ssl._create_unverified_context()

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login(sender, password)
            server.send_message(msg)
        return True
    except Exception as e:
        return str(e)
