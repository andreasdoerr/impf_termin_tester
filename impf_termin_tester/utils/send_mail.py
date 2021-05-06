"""
generating an e-mail and sending it via SMTP

E-Mail generation:
- support unicode in from/to/subject/body
- support pure text body plus optional html body content
- support cc / bcc
- automatic msgid and date generation
- support "Auto-Submitted" header

E-Mail sending:
- hostname or IP, optionally append :port (e.g. :587)
- do TLS, if possible
- try login with user/password if given
- catch the usual exceptions, return easy to process result
"""

import logging
import os
import smtplib
import socket
from email.message import EmailMessage
from email.utils import formatdate, make_msgid


def send_mail(
    *,
    mail_from,
    to=None,
    cc=None,
    bcc=None,
    subject,
    text,
    html=None,
    mail_server,
    login_user=None,
    login_password=None
):
    """ Create and send a text/plain message

    Return a tuple of success or error indicator and message.

    :param mail_from: sender (FROM)
    :type text: str
    :param to: recipients (TO)
    :type to: list of str
    :param cc: recipients (CC)
    :type cc: list of str
    :param bcc: recipients (BCC)
    :type bcc: list of str
    :param subject: subject of email
    :type subject: str
    :param text: email body text
    :type text: str
    :param html: html email body text (optional)
    :type html: str

    :param mail_server: SMTP server hostname or IP, with optional :port (default 25)
    :type text: str
    :param login_user: SMTP server login username (optional)
    :type text: str
    :param login_password: SMTP server login password (optional)
    :type text: str

    :rtype: tuple
    :returns: (is_ok, Description of error or OK message)
    """

    logging.debug("send mail, from: {0!r}, subj: {1!r}".format(mail_from, subject))
    logging.debug("send mail, to: {0!r}".format(to))

    if not to and not cc and not bcc:
        return False, "No recipients, nothing to do"

    # Create the message
    msg = EmailMessage()

    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")

    msg["From"] = mail_from
    if to:
        msg["To"] = to
    if cc:
        msg["CC"] = cc
    if bcc:
        msg["BCC"] = bcc
    msg["Subject"] = subject
    msg["Date"] = formatdate()
    msg["Message-ID"] = make_msgid()
    msg["Auto-Submitted"] = "auto-generated"  # RFC 3834 section 5

    # Send the message
    try:
        logging.debug(
            "trying to send mail (smtp) via smtp server '{0}'".format(mail_server)
        )
        host, port = (mail_server + ":25").split(":")[:2]
        server = smtplib.SMTP(host, int(port))
        try:
            server.ehlo()
            try:  # try to do TLS
                if server.has_extn("starttls"):
                    server.starttls()
                    server.ehlo()
                    logging.debug("tls connection to smtp server established")
            except Exception:
                logging.debug(
                    "could not establish a tls connection to smtp server, continuing without tls"
                )
            # server.set_debuglevel(1)
            if login_user is not None and login_password is not None:
                logging.debug(
                    "trying to log in to smtp server using account '{0}'".format(
                        login_user
                    )
                )
                server.login(login_user, login_password)
            server.send_message(msg)
        finally:
            try:
                server.quit()
            except AttributeError:
                # in case the connection failed, SMTP has no "sock" attribute
                pass
    except smtplib.SMTPException as e:
        logging.exception("smtp mail failed with an exception.")
        return False, str(e)
    except (os.error, socket.error) as e:
        logging.exception("smtp mail failed with an exception.")
        return False, "Connection to mailserver '%s' failed: %s" % (mail_server, str(e))

    logging.debug("Mail sent successfully")
    return True, "Mail sent successfully"


if __name__ == "__main__":
    # some testing code you can edit to play with this code by calling it directly like: python3 send_mail.py
    me = '"Joe Doe-Sender" <joe@example.org>'
    them = '"Jane Doe-Receiver" <jane@example.org>'
    # note: if sending to many people, respect their privacy and put them ALL into BCC,
    #       so you do not disclose all their email addresses to all of them!
    #       of course, you need to put also something into TO - just use same address as FROM for that.
    ok, msg = send_mail(
        mail_from=me,
        to=[me,],
        bcc=[them, them, them,],
        subject="Test send_mail",
        text="Test!",
        mail_server="mail.example.org:587",
        login_user="username",
        login_password="password",
    )
    print("ok: %r, msg: %r" % (ok, msg))
