import logging
import datetime
import azure.functions as func

from steve_constants import TEST_MODE, ACCOUNT_KEY
from steve_email import SteveSingleEmail
from steve_table import SteveTable
from steve_templates import generate_func_response


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
        steve_table = SteveTable(account_key=ACCOUNT_KEY, test_mode=TEST_MODE)
        try:
            steve_table.remove_subscriber(email)
        except:
            return generate_func_response(subject="Error Occured During Unsubscription",
                            body="Unable to remove your email from the list. Please email unsubscribe@where-is-steve.org for help",
                            status_code=400)
                

        # It's a very good idea to email our unsubscribers in case some PUNK unsubscribes someone intentionally,
        # but, we if we hit an exception in this block, it's also best to indicate to the user that the unsubscribe
        # succeeded rather than for them to see some computer-y JARGON
        final_email_msg = "Goodbye!"

        try:
            sse = SteveSingleEmail(email)
            sse.set_subject("Goodbye from Where-Is-Steve!")
            sse.add_item("Unsubscription Succeeded!",
                         datetime.datetime.now(),
                        """<p>You have been removed from the Where-Is-Steve mailing list. If this was a mistake, visit https://where-is-steve.org/subscribe to join again.</p>
                        <br>
                        <p>Cheers</p>
                        <p>Steve</p>""")
            sse.finalize_contents()
            if sse.send():
                final_email_message = "One final email is headed to your address to confirm your unsubscription."
        except:
            pass

        return generate_func_response(subject="Goodbye Forever!",
                        body=f"You have successfully been unsubscribed from the Where-Is-Steve mailing list. {final_email_msg}")
    else:
        return generate_func_response(subject="Invalid Request",
                            body="Unable to remove your email from the list. Please email unsubscribe@where-is-steve.org for help",
                            status_code=500)
        
