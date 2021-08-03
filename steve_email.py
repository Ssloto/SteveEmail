import html2text
import traceback
import datetime
import re

from steve_constants import API_URL_BASE, SOCKETLABS_ID, SOCKETLABS_SECRET, UNSUBSCRIBE_KEY
from steve_templates import FIGURE_STYLE, IMAGE_STYLE, PlainTextEmailTemplate, HtmlEmailTemplate

from socketlabs.injectionapi import SocketLabsClient
from socketlabs.injectionapi.message.basicmessage import BasicMessage
from socketlabs.injectionapi.message.bulkmessage import BulkMessage
from socketlabs.injectionapi.message.bulkrecipient import BulkRecipient
from socketlabs.injectionapi.message.emailaddress import EmailAddress


class SteveBaseEmail:
    def __init__(self, message):
        self._client = SocketLabsClient(SOCKETLABS_ID, SOCKETLABS_SECRET)
        self.message = message
        self._finalized = False
        self._date_format = "%A, %B %d, %Y"
        
        self.item_count = 0
        self.subject_template = "Where-Is-Steve? | {}"

        self.html_contents = ""
        self.plaintext_contents = ""
        self.unsubscribe_url = None
        
        # It's a gigantic no-no for me to parse HTML with regexes, but, it's only a small block..
        # ...and yes, these should capture everything before the last ">"
        self.figure_open_re = re.compile(r'(<figure[^>]+)>')
        self.image_open_re = re.compile(r'(<img[^>]+)>')

    def set_subject(self, subject):
        self.message.subject = self.subject_template.format(subject).strip()
    
    def _fill_template_with_item(self, template, title, date, body, link_path=None, link_name="Continue Reading..."):
        destination = ""
        if self.item_count == 0:
            destination += template.open_body
            destination += template.header
        else:
            destination += template.singlepad
        
        destination += template.item_header.format(title, 
                        datetime.datetime.strftime(date, self._date_format))
        destination += template.item.format(body)

        if link_path is not None:
            destination += template.singlepad
            destination += template.item_footer.format(link_path, link_name)
        return destination


    def add_item(self, title, date, body, link_path=None, link_name="Continue Reading..."):
        if not body.lstrip()[0] == "<":
            body = "<p>{}</p>".format(body)
        if self._finalized:
            raise Exception("Cannot add content to a finalized message!")
        
        self.html_contents      += self._fill_template_with_item(HtmlEmailTemplate, 
                                                            title, date, body, link_path, link_name)
        self.plaintext_contents += self._fill_template_with_item(PlainTextEmailTemplate,
                                                            title, date, body, link_path, link_name)
        self.item_count += 1


    def finalize_contents(self, clean_plaintext=True):
        if self.item_count == 0 or not self.plaintext_contents or not self.html_contents:
            raise Exception("Cannot finalize a contents with no contents!")
        if self._finalized:
            raise Exception("Cannot finilize an already finished message!")
            
        if self.unsubscribe_url is not None:
            self.html_contents      += HtmlEmailTemplate.footer.format(self.unsubscribe_url)
            self.plaintext_contents += PlainTextEmailTemplate.footer.format(self.unsubscribe_url)
 
        self.html_contents += HtmlEmailTemplate.close_body
        self.plaintext_contents += PlainTextEmailTemplate.close_body

        # Strip any HTML from our plaintext contents...
        self.plaintext_contents = html2text.html2text(self.plaintext_contents)
        
        # Add any inline style sweeteners...
        self._fix_inline_styling()

        # Fill in the wrapped message's contents...
        self.message.html_body       = self.html_contents
        self.message.plain_text_body = self.plaintext_contents
        
        # Mark as sendable
        self._finalized = True

    def _fix_inline_styling(self):
        self.html_contents = self.figure_open_re.sub(r'\1 style="{0}">'.format(FIGURE_STYLE), self.html_contents)
        self.html_contents = self.image_open_re.sub(r'\1 style="{0}">'.format(IMAGE_STYLE), self.html_contents)


class SteveBulkEmail(SteveBaseEmail):
    def __init__(self, recipients):
        super().__init__(BulkMessage())
        self.unsubscribe_url = f"{API_URL_BASE}/Unsubscribe?code={UNSUBSCRIBE_KEY}&email=%%Email%%"
        self.message.from_email_address = EmailAddress("updates@where-is-steve.org")

        self.recipients = list()
        for recpient_email in recipients:
            br = BulkRecipient(recpient_email)
            br.add_merge_data("Email", recpient_email)
            self.recipients.append(br)

    def send(self):
        for recipient in self.recipients:
            self.message.add_to_recipient(recipient)
        return self._client.send(self.message)


class SteveSingleEmail(SteveBaseEmail):
    def __init__(self, recipient):
        super().__init__(BasicMessage())
        self.recipient = EmailAddress(recipient)
        self.message.from_email_address = EmailAddress("mail-daemon@where-is-steve.org")


    def send(self):
        self.message.to_email_address.append(self.recipient)
        return self._client.send(self.message)


    @staticmethod
    def send_from_exception(self, exception, funcname):
        excEmail = SteveSingleEmail("dev@where-is-steve.org")
        excEmail.set_subject("An exception occured in {}".format(funcname))
        stacktrace = ""

        for line in traceback.format_exception(exception.__class__, 
                                               exception, 
                                               exception.__traceback__):
            stacktrace += "<p>{}</p>\n".format(line)

        excEmail.add_item("Traceback follows",
                           datetime.datetime.now(),
                           stacktrace,
                           None)

        excEmail.finalize_contents()
        return excEmail.send()
