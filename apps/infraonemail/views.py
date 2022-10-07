from urllib import request
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from apps.infraonemail.serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from apps.infraonemail.controllers import *
import copy
import time
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import imaplib
import email
from email.header import decode_header
from datetime import datetime
import email.utils
from email.utils import parseaddr
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

obj = EmailControllers()
noneList = [None, "None", "Null", "null", "", -1, "-1", "0", "Select", [], {}, [''], '']


@csrf_exempt
def get_line_chart_data(request):
    response = obj.get_data(request)
    return HttpResponse(json.dumps(response))


def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)


def parse_email_id(email_str, is_lower=False):
    """
    Function used to return the only email address. removing the name and <> from email address if found
    :params email_str: Email ids string ex: foo@bar.com; "www, xxyyzz" <something@else.com>
    return string ex 'foo@bar.com,something@else.com
    """
    try:
        # logger.info("Enter into parse_email_id on EmailConverter")
        only_email = []
        email_list = email.utils.getaddresses([email_str])
        for item in email_list:
            if item[1] not in noneList:
                temp_data = item[1]
                if is_lower:
                    temp_data = temp_data.lower()
                only_email.append(temp_data)
        return_str = ",".join(only_email)
        # logger.info("Exit from parse_email_id on EmailConverter")
        return return_str
    except Exception as e:
        return email_str


def set_params(mail_data):
    """
    Function to set the parameters of individual mails
    :param mail_data: the particular mail details
    :return: email data dict
    """
    try:
        text_body = None
        html_body = None
        email_contain = None
        email_body = mail_data[0][1]  # getting the mail content
        msg = email.message_from_bytes(email_body)  # parsing the mail content to get a mail object
        email_from = msg['from']
        if email_from.__contains__('<'):
            email_from = parse_email_id(email_from)
            #email_from[email_from.find("<") + 1:email_from.find(">")]
        try:
            try:
                sub_message = copy.deepcopy(msg['Subject'])
                sub_message = sub_message.encode('ascii').decode('unicode_escape')
                decode = email.header.decode_header(sub_message)[0]
                email_subject = decode[0].decode('utf-8')
            except:
                decode = email.header.decode_header(msg['Subject'])[0]
                email_subject = str(decode[0])
        except Exception as decodeerror:
            email_subject = msg['subject']
        email_to = msg['to']
        email_date = ''
        if msg['Date']:
            try:
                date_tuple = email.utils.parsedate_tz(msg['Date'])
                if date_tuple:
                    email_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            except Exception as e:
                pass
        email_cc_list = msg['Cc']
        if email_cc_list is None:
            email_cc_list = ''
        email_bcc_list = msg['Bcc']
        if email_bcc_list is None:
            email_bcc_list = ''
        file_data_set = []
        file_key_map = {}
        is_disposition = False
        attach_file_name = []
        email_body_txt = ''
        for elem in msg.walk():
            decode_flag = False
            charset = elem.get_content_charset()
            if elem.get_content_type() == "text/plain" and elem.get('Content-Disposition') in noneList:
                # email_body = elem.get_payload(decode=True)
                temp_text_body = str(elem.get_payload(decode=True), str(charset), "ignore")
                if is_disposition:
                    if temp_text_body and text_body:
                        text_body = text_body + "" + temp_text_body
                    else:
                        text_body = temp_text_body
                else:
                    text_body = temp_text_body
            if elem.get_content_type() == 'text/html' and elem.get('Content-Disposition') in noneList:
                temp_html_body = str(elem.get_payload(decode=True), str(charset), "ignore")
                if temp_html_body:
                    temp_html_body = temp_html_body.replace('\r', '').replace('\n', '')
                if is_disposition:
                    if temp_html_body and html_body:
                        html_body = html_body + "" + temp_html_body
                    else:
                        html_body = temp_html_body
                else:
                    html_body = temp_html_body
            if elem.get_content_type() == 'text/xml':
                decode_flag = True
            if elem.get('Content-Disposition') is None:
                is_disposition = True
                # continue
            # end here bug id 6764
            filename = elem.get_filename()
            if filename not in noneList:
                attach_file_name.append(filename)
            file_data = elem.get_payload(decode=decode_flag)
            file_size = len(file_data)
            description = elem.get_content_type()
            cid = elem.get('Content-ID')
            if cid is not None:
                cid = cid.replace('<', '').replace('>', '')
                file_ext = ".png"
                if filename:
                    try:
                        file_ext = filename.split('.')
                        file_ext = file_ext[1]
                    except Exception as e:
                        pass
                filename = str(cid) + str(int(round(time.time() * 1000))) + "." +str(file_ext)
                file_key_map[cid] = filename
            # Saving the attachments
            file_data_set.append({'file_name': filename, 'file_data': file_data, 'description': description,
                                  'cid': cid, 'file_size': file_size})
        if html_body is None:
            email_contain = text_body
        else:
            email_contain = html_body
            soup = BeautifulSoup(email_contain, features="html.parser")
            if soup.find('meta'):
                soup.find('meta').decompose()
            body = soup.find('body')
            if body:
                email_body_txt = body.getText()
                body_tag = body.findChildren(recursive=False)
                if body_tag:
                    # bug fix for 14460
                    temp_email_contain = ''
                    for tag_dt in body_tag:
                        temp_email_contain = temp_email_contain + str(tag_dt)
                    if temp_email_contain:
                        email_contain = temp_email_contain
            # getattr(soup, 'body').unwrap()
            # soup.find('head').decompose()
        # removing the base tag from email body.
        # if email_contain:
        #     my_regex = r"<base href=.*>"
        #     email_contain = re.sub(my_regex, "", email_contain)
        if text_body in noneList:
            text_body = email_body_txt
        email_data = {'msg': msg, 'from_address': email_from, 'to_address': email_to, 'subject': email_subject,
                      'email_date': email_date, 'cc_address': email_cc_list, 'bcc_address': email_bcc_list,
                      'reply_mail': email_contain, 'txt_mail': text_body, 'file_data_set': file_data_set,
                      'file_key_map': file_key_map, 'attach_file_name': attach_file_name}
        return email_data
    except Exception as err:
        return {}


def save_communication(email_data, sentiment_level):
    """
    Function used for save the email data to table.
    :param email_data: Email data which we got from email
    :param sentiment_level: as per ML/AI level of sentiment, it will have -1, 0, 1 for negative, Neutral, Positive
    :return: None
    """
    try:
        obj = Communication()
        obj.sent_time = email_data.get('email_date', None)
        obj.creation_time = datetime.now()
        obj.is_deleted = False
        obj.subject = email_data.get('subject', '')
        obj.to_address = email_data.get('to_address', '')
        obj.cc_address = email_data.get('cc_address', '')
        obj.bcc_address = email_data.get('bcc_address', '')
        obj.from_address = email_data.get('from_address', '')
        obj.content = email_data.get('reply_mail', '')
        obj.txt_content = email_data.get('text_body', '')
        if len(email_data.get('attach_file_name', [])) > 0:
            obj.is_attachment = True
        else:
            obj.is_attachment = False
        obj.status = 1
        obj.conversations_flag = 2
        obj.is_system_gen = False
        obj.sentiment_type = sentiment_level
        obj.save()
    except Exception as e:
        pass


@csrf_exempt
def updateNewEmails(request):
    try:
        # account credentials
        username = "bhuvara@infraon.io"
        password = "Bhuv@r@$2022"
        imap_server = "outlook.office365.com"        

        # create an IMAP4 class with SSL 
        imap = imaplib.IMAP4_SSL(imap_server)
        # authenticate
        imap.login(username, password)
        # status, messages = imap.select("INBOX")
        # print("Available Mail Box Lists : ",imap.list())
        imap.select("INBOX")
        # Get only Unread mails
        resp, mail = imap.search(None, "(UNSEEN)")
        # self.items = items[0].split()  # getting the mails id
        mail_ids = mail[0].decode().split()
        for emailid in mail_ids:
            resp, mail_data = imap.fetch(emailid, '(RFC822)')
            email_data = set_params(mail_data)
            sentiment = getSentiment(email_data.get('txt_mail', ''))
            resp_code, response = imap.store(emailid, '+FLAGS', '\\Seen')
            # save the data to table
            save_communication(email_data, sentiment)
        # close the connection and logout
        try:
            imap.close()
            imap.logout()
        except:
            pass
    except Exception as msg:
        print("Exception in Mail Fetcher : ",msg)
    return HttpResponse("Successfully Updated...!!")

def getSentiment(text):
    try:
        analyzer = SentimentIntensityAnalyzer()
        pos_correct,neg_correct,neu_correct = 0,0,0
        status = 0
        for line in filter(lambda a:a,text.split('\n')):
            vs = analyzer.polarity_scores(line)
            # print("VS in Pos : ",vs)
            if vs['neg'] > 0.1:
                if vs['pos']-vs['neg'] < 0 or vs['compound'] <= -0.05:
                    neg_correct += 1
                # neg_count +=1
            elif vs['pos']  > 0.1 or vs['compound'] >= 0.05:
                if vs['pos']-vs['neg'] > 0:
                    pos_correct += 1
                # pos_count +=1
            else:
                if vs['pos']-vs['neg'] == 0:
                    neu_correct += 1
                # neu_count += 1

        # print("neg_correct : ",neg_correct)
        # print("pos_correct : ",pos_correct)
        # print("neu_correct : ",neu_correct)

        # print("*************************************")
        if neg_correct:
            print("Result : >>>> Negative :((")
            status = -1
        elif neu_correct:
            print("Result : >>>> Neutral :||")
            status = 0
        else:
            print("Result : >>>> Positive :))")
            status = 1
        # print("*************************************")
        return status
    except Exception as msg:
        print("Exception in sentiment Finder : ",msg)
    return 0