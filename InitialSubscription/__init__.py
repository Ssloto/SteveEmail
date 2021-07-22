import logging
import datetime
import azure.functions as func

from steve_email import SteveSingleEmail
from steve_constants import API_URL_BASE, CONFIRM_SUBSCRIBE_KEY
from steve_table import SteveTable
from steve_templates import generate_func_response

def email_is_valid(email):
    return '@' in email and \
            '.' in email.split('@')[1] and \
            ' ' not in email


def sent_subscription_email(email):
    try:
        # TO DO: html encode email here properly...
        confirm_subscription_url = f"{API_URL_BASE}/ConfirmSubscription?code={CONFIRM_SUBSCRIBE_KEY}&email={email}"
        subEmail = SteveSingleEmail(email)
        subEmail.set_subject("Please Confirm Your Subscription to Where-Is-Steve")
        subEmail.add_item("One More Step to Confirm Your Subscription...",
                        datetime.datetime.now(),
                        f"""<p>Hi!</p>
                        <p>I'm Steve of Where-Is-Steve, and I am <em>thrilled</em> to have you join my mailing list.</p>
                        <p>Please <a href="{confirm_subscription_url}">click here</a> to confirm your subscription
                        and start receiving an email each time I add a new blogpost to my website.</p>
                        <p>(If the link doesn't work, try copy-pasting {confirm_subscription_url} into your browser window.)<p>""",
                        None)
        subEmail.finalize_contents()
        return subEmail.send()  
    except:
        return False

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    email = req.params.get('email')
    if not email:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            email = req_body.get('email')

    if email:
        if not email_is_valid(email):
            return generate_func_response(subject="Invalid Submission",
                            body=f"Unfortunately, the email address  was not valid. Please try again.",
                            link_name="Return to the Subscribe Page",
                            link_path="https:&#x2F;&#x2F;where-is-steve.org&#x2F;subscribe",
                            status_code=400)


        try:
            SteveTable().add_pending_subscriber(email)
        except:
            return generate_func_response(subject="Pre-Authorization Error",
                body="We encountered a problem authorizing your email address for subscription. Please email subscribe@where-is-steve.org for assistance.",
                status_code=500)
        

        if not sent_subscription_email(email):
            return generate_func_response(subject="Unknown Error",
                            body="We encountered a problem sending your confirmation email. Please email subscribe@where-is-steve.org for assistance.",
                            status_code=500)
        else:
            return generate_func_response(subject="Thanks for your Subscription Request!",
                            body="Thanks for signing up to join the Where-Is-Steve newsletter. We've sent an email to your address to confirm your subscription.",
                            link_name="Return to the Home Page",
                            link_path="https:&#x2F;&#x2F;where-is-steve.org")
        
    else:
        return generate_func_response(subject="Invalid Submission",
                        body="Unfortunately, the email address was not valid. Please try again.",
                        link_name="Return to the Subscribe Page",
                        link_path="https:&#x2F;&#x2F;where-is-steve.org&#x2F;subscribe",
                        status_code=400)