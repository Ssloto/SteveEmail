import azure.functions as func
import datetime


def generate_func_response(subject, body, link_name=None, link_path=None, status_code=200) -> func.HttpResponse:
    timestamp = datetime.datetime.now()
    continue_reading = ""
    if link_name is not None and link_path is not None:
        continue_reading = f"""<div class="continue-reading">
                                    <a href="{link_path}">{link_name}</a>
                                </div>"""
    response_html= f"""
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                    <meta name="theme-color" content="#8e44ad">
                    <meta http-equiv="X-UA-Compatible" content="ie=edge">  
                    <meta name="author" content="Steve">
                    <title>Where is Steve? - {subject}</title>
                    <link rel="stylesheet" href="https:&#x2F;&#x2F;where-is-steve.org&#x2F;main.css"/>
                </head>

                <body>

                    <header class="site-header">
                        <div class="site-header__title">
                            <a href="https:&#x2F;&#x2F;where-is-steve.org">
                                <h1>Where is Steve?</h1>
                            </a>
                        </div>
                    </header>

                    <div class="sidebar">&nbsp;</div>

                    <main class="site-content">
                        <div class="posts">
                            <div class="post-container">
                                <article class="post">

                                    <header class="post-header" style="max-height:300px;">
                                        <h1 class="post-header__title">{subject.strip()}</h1>
                                        <p class="post-header__info">
                                            &nbsp;
                                        </p>
                                    </header>

                                    <div class="post-body">
                                        <p>{body}</p>
                                    </div>

                                    {continue_reading}
                                </article>
                            </div>
                        </div>
                    </main>

                    <footer class="site-footer">
		                <span class="site-footer__text">© where-is-steve</span>
	                </footer>

                </body>

            </html>""" 
    return func.HttpResponse(body=response_html, 
                             status_code=status_code, 
                             mimetype="text/html")

class EmailTemplate():
    def __init__(self, header, footer, item, item_header, item_footer, singlepad, doublepad, open_body="", close_body=""):
        self.header = header
        self.footer = footer
        self.item = item
        self.item_header = item_header
        self.item_footer = item_footer
        self.singlepad = singlepad
        self.doublepad = doublepad
        self.open_body = open_body
        self.close_body = close_body

PlainTextEmailTemplate = EmailTemplate(
    header = """===========================
                |                         |
                |  WHERE - IS - STEVE - ? |
                |                         |
                ===========================""",
    item_header = """
    ---------------------------
    {}
    {}
    ---------------------------
        """,
    footer = "To unsubscribe, visit: {}",
    close_body = """
    ===========================
    |    (C) Where-Is-Steve   |
    ===========================
    """,
    singlepad = "\n===========================\n",
    doublepad = "\n\n===========================\n===========================\n\n",
    item = "\n{}\n",
    item_footer = "{1} at {0}"
)

HtmlEmailTemplate = EmailTemplate(

        header = """<tr><th style="background: black;
                                   color: white;
                                   font-family: Georgia,serif;
                                   font-size: 17px;
                                   margin: 1%;
                                   padding-top: 2.5%;
                                   padding-bottom: 2.5%;
                                   text-align:center;
                                   line-height: 2em;
                                   align-items:center;
                                   border: 1px solid black;">
                        <h1>Where-Is-Steve</h1>
                        </th></tr>""",
        item_header= """<tr>
                        <td style="background: #e6e6ff;
                            line-height: 0.75;
                            padding-top: 1%;
                            padding-left: 1%;
                            padding-right: 1%;
                            padding-bottom: 0%;
                            border: 1px solid black;">
                        <h2 style="font-family: Trebuche,
							-apple-system,BlinkMacSystemFont,
							Segoe UI,
							Roboto,
							Oxygen,
							Ubuntu,
							Cantarell,
							Linux Libertine G,
							Libertine,
							Open Sans,
							Helvetica Neue,
							sans-serif;">{}</h2>
                        <h3>{}</h3>
                        </td>
                        </tr>""",
        item="""<tr>
                <td style="font-family; Georgia,serif;
                font-size: 17px;
                line-height: 1.7;
                padding: 0.5% 2%;
                border: 1px solid black;
                background-color: white;">
                    {}
                </td>
                </tr>""",
        item_footer = """<tr>
                         <td style="background: navy;
                        color: white;
                        font-size: 21px;
                        line-height: 2;
                        padding: 1%;
                        border: 1px solid black;">
                    <a href="{}" style="color:white;">{}</a>
                    </td></tr>""",
        footer = """<tr><td style="background: black; color: white; font-size: 17px;">
                    <p><a href="{}" style="color: white;">Click here to unsubscribe!</a></p>
                    <p>(C) Where-Is-Steve, All Rights Reserved</p></a>
                    </td></tr>""",
        singlepad = """<tr><td><br></td></tr>""",
        doublepad = """<tr><td><br><br></td></tr>""",
        open_body = """<table border="0" 
                        cellpadding="1" 
                        cellspacing="0" 
                        width="100%">""",
        close_body = "</table>"
)