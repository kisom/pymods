#!/usr/bin/env python
# -*- coding: utf-8 -*-
# file: mailer.py
# author: kyle isom <coder@kyleisom.net>
# license: ISC / public domain dual-licensed
#
# wrapper for some of python's email functionality - provides field checking 
# and formatting
"""
mailer

This provides a simple way to send emails while still sanitizing fields and 
preventing bad fields from being sent out. The module is simple to use:

import mailer
if not mailer.set_sender('john.q.public@megacorp.net') : 
    # process the error
if not mailer.simple(list_of_recipients, subject_string, body_string) :
    # process the error

The module has been designed so these are the only two functions a user will
need to run. Both return True or False based on whether the function 
returned successfully or not.

Important methods:
    simple: simple send email
    with_text: simple email with text attachments
    build_message: build a mulitpart message base (for attaching attachments to)
    attach_text: attach text files to a message
    send: send an email

If you plan on using some of the other internal functions, bear in mind that
every function will return a True or False indicating success, except for 
the following processing functions:
    sanitize - returns sanitized version of string
    check_tolist: checks a list of email addresses - returns a string of the
        email address (used by MIMEtext)
    get_sender: returns a string containing the current sender
    toggle_local: always returns true

The module has two attributes: sender and allow_local.

sender should be accessed with get_sender() and modified with set_sender().

allow_local: this is a boolean value that determines whether local addresses
i.e. RFC 1918 addresses or usernames-only as addresses are valid addresses.
allow_local is False by default (local addresses are not valid) and may be
toggled with toggle_local() and accessed with local_allowed().

TODO:
    * allow email addresses of the form displayName <email_address>
"""


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
import getopt
import os
import smtplib
import sys

sender = [ "pymailer" ]
allow_local = False

def sanitize(input_string) :
    """
    Performs all sanitization functions that I found myself doing repeatedly 
    on multiple variables. Presently strips out leading and trailing 
    whitespace, as well as newlines and carriage returns.
    """
    input_string = input_string.strip()
    input_string = input_string.replace('\n', '')
    input_string = input_string.replace('\r', '')
    input_string = input_string.replace('\x0a', '')
    input_string = input_string.replace('\x0d', '')
    return input_string

def check_ipv4(ip) :
    """
    Checks IP addresses for sanity.
    """

    octet = ip.split('.')
    if not 4 == len(octet): return False

    # if the octets aren't ints, reject them
    for i in range(0, len(octet)) :
        try:    octet[i] = int(octet[i])
        except: return False
    # RFC1918 addresses
    if not allow_local and 10 == octet[0]: 
        return False
    if not allow_local and 172 == octet[0] and 15 < octet[1] < 32: 
        return False
    if not allow_local and 192 == octet[0] and 0 <= octet[2] <= 255: 
        return False

    # reject blatantly stupid addresses
    if octet[0]  < 0:   return False
    if octet[0] > 223:  return False
    if 255 == octet[3]: return False
    if 0 == octet[3]:   return False

    # make sure all the octets are in range
    for i in range(0, len(octet)):
        try:
            if 255 < octet[i]:  return False
            if 0 > octet[i]:    return False
        except:
            return False

    return True

def check_email(email) :
    # number of times @ symbol appears - it should *never*
    # apear more than once and may not appear if local
    # addresses are being used

    atsym_n = email.count('@')                  
    if 1 < atsym_n :
        return False
    elif 0 == atsym_n and not allow_local :
        return False
    else :
        pass

    if email.count('@') :
        user, domain = email.split('@')
    else :
        user = email
        domain = ""     # use empty string instead of None to simplify
                        # operations that should apply to both

    # add support for user@[ip] addresses
    if '[' == domain[0] and not '[' == domain[len(domain) - 1]:
        return False
    elif not '[' == domain[0] and '[' == domain[len(domain) - 1]:
        return False
    elif not '[' == domain[0]:
        pass
    else:
        ip = domain[1:-1]
        if not check_ipv4(ip): 
            return False
  

    if '.' == domain[len(domain) - 1]:
        return False
    elif '.' == domain[0]:
        return False
    else:
        return True

def check_tolist(to_list) :
    """
        Checks the list of recipients. Returns a string of email addresses
        in the format expected by smtplib.
    """

    to_string = ""

    # ensure addresses are in proper mailbox format
    for i in range(0, len(to_list)): 
        address = to_list[i]
        address = sanitize(address)

        if not check_email(address):
            sys.stderr.write('!! mailer: bad address ' + address + '\n')
            to_list[i] = ''
            continue
        if not address[0] == '<':
            address = "<" + address[:]
        if not address[len(address) - 1] == ">":
            address = address[:] + ">"

        to_list[i] = address

    while '' in to_list:
        to_list.remove('')

    for i in range(0, len(to_list)):
        to_string = to_string + to_list[i] + ", "
    
    # remove final comma and space
    to_string = to_string[:-2]

    return to_string

def build_message(to_list, subject = "", body = ""):
    if not to_list :
        return False

    if not subject and not body :
        return False

    to_string = check_tolist(to_list)
    if subject :
        subject = sanitize(subject)    

    mail = MIMEMultipart()
    mail['subject'] = subject
    mail['To']      = to_string
    mail['From']    = get_sender()
    mail.preamble   = "pymailer message follows"
    mail.attach(MIMEText(body))

    return mail

def send(email, to_list):
    s = smtplib.SMTP()
    try:
        s.connect('localhost')
        s.sendmail(get_sender(), to_list, email.as_string())
    except smtplib.SMTPException as e:
        print e
        return False
    else:
        return True


def simple(to_list, subject = "", body = "") :
    """
        simple(to_list = [], subject = "mailer.py", body = "") 

        to_list should be a list of email addresses. If they are not already in
        the standard angle format, they will be converted to that format, i.e.

            [ 'joe.blow@megacorp.net', 'important.person@megacorp.net' ]
            will be converted to
            [ '<joe.bloe@megacorp.net>', '<important.person@megacorp.net>' ]

        Both subject and body should be strings. While care should be taken in
        what is passed into the function, subject will be stripped of any 
        newlines and carriage returns. Body is not touched as the python 
        smtplib should be able to handle anything that can be represented as
        a string.

    """

    mail = build_message(to_list, subject, body)
    send(mail, to_list)


    return True
    
def set_sender(new_sender) :
    """
        set_sender(new_sender = "")

        A function to set the From address for this module. Returns false if
        an invalid email address is passed in.
    """

    new_sender = sanitize(new_sender)
    new_sender = check_tolist([ new_sender ])

    if not new_sender or not check_email(new_sender):
        return False
    else :
        sender[0] = "\"pymailer\" "+ new_sender
        return True

def get_sender() :
    return sender[0]

def toggle_local() :
    """
        Toggles the value of allow_local.
    """
    allow_local = not allow_local
    return True

def local_allowed() :
    """
        If true, local addresses (i.e. user v. user@somehost) are allowed.
    """

    return allow_local

def with_text(to_list, subject = "", body = "", file_list = []):
    """
        Build a multipart message with the plain text files specified in
        file_list and send that off to the wide wide world.
    """
    mail = build_message(to_list, subject, body)
    mail = attach_text(mail, file_list)
    return send(mail, to_list)


def attach_text(mail, file_list):
    """
        Takes a MIME multipart message object 'mail' and attaches the
        files specified in file_list (which should be the full filenames
        of plain text files to be attached), and returns the message with
        attachments.
    """
    for file in file_list:
        try:
            f = open(file)
        except IOError as e:
            print e
            print 'failed to attach', file
            pass
        txt = MIMEText(f.read())
        txt.add_header('Content-Disposition', 'attachment', 
                       filename = os.path.basename(file))
        mail.attach(txt)

    return mail

if __name__ == "__main__" :
    # usage:
    # -t <to> add a person to the to-list
    # -s <subj> add a subject line
    # -b <body> add the body
    # -f <file> attach file 
    # -r <addr> set from
    opts, args = getopt.getopt(sys.argv[1:], 'r:t:s:b:f:')

    to = [ ]
    files = [ ]
    subj = "pymailer message"
    body = "EOF"
    res = False                                  # default result is False 
                                                 # because we haven't sent
                                                 # anything yet

    for opt, val in opts:
        opt = opt.lstrip('-')
        if opt is 't':
            to.append(val)
        if opt is 'r':
            set_sender(val)
        if opt is 's':
            subj = val
        if opt is 'b':
            body = val + '\n'
        if opt is 'f':
            files.append(val)

    if files:
        res = with_text(to, subj, body, files)
    else:
        res = simple(to, subj, body)
        
    if res:
        print 'successfully sent message!'
    else:
        print 'failed to send message!'

