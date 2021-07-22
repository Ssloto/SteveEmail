import logging
import datetime
import azure.functions as func

from steve_constants import API_URL_BASE, UNSUBSCRIBE_KEY
from steve_email import SteveSingleEmail
from steve_table import SteveTable
from steve_templates import generate_func_response


def try_send_welcome_email(email):
    try:
        sse = SteveSingleEmail(email)
        sse.set_subject("Welcome to the Where-Is-Steve Mailing List!")
        sse.add_item("Your subscription has been confirmed",
                    datetime.datetime.now(),
                    """<p>Thank you so much for signing up for my email list and confirming your subscription! Lots of content will be coming your way soon. "
                    Feel free to write me back with your thoughts and comments.</p>
                    
                    <p>Cheers</p>
                    <p>Steve</p>""")
        sse.unsubscribe_url = f"{API_URL_BASE}/Unsubscribe?{UNSUBSCRIBE_KEY}&email={email}"
        sse.finalize_contents()
        return sse.send()
    except:
        return False

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    email = req.params.get('email')
    if not email:
        try:
            req_body = req.get_json()
            email = req_body.get('email')
        except ValueError:
            pass

    if email:
        try:
            steve_table = SteveTable()
            steve_table.add_subscriber(email)
        except:
            return generate_func_response("An Error Occured",
                    "An error occured when confirming your subscription to the mailing list. Please email subscribe@where-is-steve.org for assistance",
                    status_code=500)

        try_send_welcome_email(email)

        return generate_func_response("You have confirmed your subscription",
        "Thanks! I'm looking forward to having you on board. :) Feel free to reply to the emails too, if you want.",
        "Return to the Home Page",
        "https:&#x2F;&#x2F;where-is-steve.org")

    else:
        return generate_func_response("An Error Occured",
        "An error occured when confirming your subscription to the mailing list. Please email subscribe@where-is-steve.org for assistance",
        status_code=500)
