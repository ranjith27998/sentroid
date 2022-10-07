from django.db.models.functions import TruncDate
from django.db.models import Count
from apps.infraonemail.models import *
from django.db.models import F, Q


class EmailControllers:

    def get_data(self, request):
        """
        Function used for return the chart data
        :return:
        """
        try:


            obj_data = Communication.objects.annotate(y=TruncDate('sent_time')).values('y')\
                .annotate(a=(Count('sentiment_type', filter=Q(sentiment_type=1))),
                          b=(Count('sentiment_type', filter=Q(sentiment_type=0))),
                          c=(Count('sentiment_type', filter=Q(sentiment_type=-1)))
                        ).values('y', 'a', 'b', 'c')
            data = []
            for row in obj_data:
                temp_row ={}
                temp_row["y"] = row["y"].strftime("%Y-%m-%d")
                temp_row["a"] = row["a"]
                temp_row["b"] = row["b"]
                temp_row["c"] = row["c"]
                data.append(temp_row)

            return data
        except Exception as e:
            return []

    def updateNewEmails(self,request):
        try:
            # account credentials
            username = "bhuvara@infraon.io"
            password = "Bhuv@r@$2022"
            imap_server = "outlook.office365.com"
            
            def clean(text):
                # clean text for creating a folder
                return "".join(c if c.isalnum() else "_" for c in text)

            # create an IMAP4 class with SSL 
            imap = imaplib.IMAP4_SSL(imap_server)
            # authenticate
            imap.login(username, password)
            status, messages = imap.select("INBOX")
            print("Available Mail Box Lists : ",imap.list())
            # number of top emails to fetch
            N = 5
            # total number of emails
            messages = int(messages[0])
            print("Total no. of Emails in Inbox : ",messages)
            # objs = []

            for i in range(messages, messages-N, -1):
                # fetch the email message by ID
                obj = Communication()
                mail_content = ""
                try:
                    res, msg = imap.fetch(str(i), "(RFC822)")
                    for response in msg:
                        if isinstance(response, tuple):
                            # parse a bytes email into a message object
                            msg = email.message_from_bytes(response[1])
                            # decode the email subject
                            subject, encoding = decode_header(msg["Subject"])[0]
                            if isinstance(subject, bytes):
                                # if it's a bytes, decode to str
                                subject = subject.decode(encoding)
                                obj.subject = str(subject).strip()
                            # decode email sender
                            From, encoding = decode_header(msg.get("From"))[0]
                            if isinstance(From, bytes) and encoding:
                                From = From.decode(encoding)
                                obj.from_addr = str(From).strip()
                            print("Subject:", subject)
                            print("From:", From)
                            # if the email message is multipart
                            if msg.is_multipart():
                                # iterate over email parts
                                for part in msg.walk():
                                    # extract content type of email
                                    content_type = part.get_content_type()
                                    content_disposition = str(part.get("Content-Disposition"))
                                    try:
                                        # get the email body
                                        body = part.get_payload(decode=True).decode()
                                    except:
                                        pass
                                    if content_type == "text/plain" and "attachment" not in content_disposition:
                                        # print text/plain emails and skip attachments
                                        obj.mail_txt = str(body).strip()
                                        mail_content = str(body).strip()
                                        print(body)
                                    elif "attachment" in content_disposition:
                                    # else:
                                        obj.mail_txt = str(body).strip()
                                        print(body)
                                    # elif "attachment" in content_disposition:
                                    #     # download attachment
                                    #     filename = part.get_filename()
                                    #     if filename:
                                    #         folder_name = clean(subject)
                                    #         if not os.path.isdir(folder_name):
                                    #             # make a folder for this email (named after the subject)
                                    #             os.mkdir(folder_name)
                                    #         filepath = os.path.join(folder_name, filename)
                                    #         # download attachment and save it
                                    #         open(filepath, "wb").write(part.get_payload(decode=True))
                            else:
                                # extract content type of email
                                content_type = msg.get_content_type()
                                # get the email body
                                try:
                                    # get the email body
                                    body = msg.get_payload(decode=True).decode()
                                except:
                                    pass
                                print(body)
                                if content_type == "text/plain":
                                    # print only text email parts
                                    obj.mail_txt = str(body).strip()
                                    mail_content = str(body).strip()
                            if content_type == "text/html":
                                # obj.mail_txt = body
                                # mail_content = body
                                obj.mail_html = body
                                # if it's HTML, create a new HTML file and open it in browser
                                # folder_name = clean(subject)
                                # if not os.path.isdir(folder_name):
                                #     # make a folder for this email (named after the subject)
                                #     os.mkdir(folder_name)
                                # filename = "index.html"
                                # filepath = os.path.join(folder_name, filename)
                                # # write the file
                                # open(filepath, "w").write(body)
                                # # open in the default browser
                                # webbrowser.open(filepath)
                            # print("="*100)
                            obj.sentiment = self.getSentiment(mail_content)
                            obj.save()
                except:
                    pass
            # close the connection and logout
            try:
                imap.close()
                imap.logout()
            except:
                pass
        except Exception as msg:
            print("Exception in Mail Fetcher : ",msg)
    
    def getSentiment(self,text):
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