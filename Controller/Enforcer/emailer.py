import smtplib

def send(to, subject, message):
    fromaddr = '<fromAddress>'
    toaddrs  = '<toAddress>'
    msg = "\r\n".join([
        "From: " + fromaddr,
        "To: " + to,
        "Subject: " + subject,
        "",
        message
  ])
    username = '<Same as from address>'
    password = "<Password of the from's gmail account>"
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()


