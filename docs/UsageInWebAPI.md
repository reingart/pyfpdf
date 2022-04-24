# Usage in web APIs #

## Django ##
[Django](https://www.djangoproject.com/) is:
> a high-level Python web framework that encourages rapid development and clean, pragmatic design

There is how you can return a PDF document from a [Django view](https://docs.djangoproject.com/en/4.0/topics/http/views/):

```python
from django.http import HttpResponse
from fpdf import FPDF

def report(request):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=24)
    pdf.cell(txt="hello world")
    return HttpResponse(bytes(pdf.output()), content_type="application/pdf")
```

## Flask ##
[Flask](https://flask.palletsprojects.com) is a micro web framework written in Python.

The following code can be placed in a `app.py` file and launched using `flask run`:

```python
from flask import Flask, make_response
from fpdf import FPDF

app = Flask(__name__)

@app.route("/")
def hello_world():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=24)
    pdf.cell(txt="hello world")
    response = make_response(pdf.output())
    response.headers["Content-Type"] = "application/pdf"
    return response
```

## AWS lambda ##
The following code demonstrates some minimal [AWS lambda handler function](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html)
that returns a PDF file as binary output:
```python
from base64 import b64encode
from fpdf import FPDF

def handler(event, context):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=24)
    pdf.cell(txt="hello world")
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': b64encode(pdf.output()).decode('utf-8'),
        'isBase64Encoded': True
    }
```

This AWS lambda function can then be linked to a HTTP endpoint using [API Gateway](https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html),
or simply exposed as a [Lambda Function URL](https://aws.amazon.com/fr/blogs/aws/announcing-aws-lambda-function-urls-built-in-https-endpoints-for-single-function-microservices/).
More information on those pages:

* [Tutorial: Creating a Lambda function with a function URL](https://docs.aws.amazon.com/lambda/latest/dg/urls-tutorial.html)
* [Return binary media from a Lambda](https://docs.aws.amazon.com/apigateway/latest/developerguide/lambda-proxy-binary-media.html)


## streamlit ##
[streamlit](https://streamlit.io) is:
> a Python library that makes it easy to create and share custom web apps for data science

The following code demonstrates how to display a PDF and add a button allowing to download it:

```python
from base64 import b64encode
from fpdf import FPDF
import streamlit as st

st.title("Demo of fpdf2 usage with streamlit")

@st.cache
def gen_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=24)
    pdf.cell(txt="hello world")
    return bytes(pdf.output())

# Embed PDF to display it:
base64_pdf = b64encode(gen_pdf()).decode("utf-8")
pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="400" type="application/pdf">'
st.markdown(pdf_display, unsafe_allow_html=True)

# Add a download button:
st.download_button(
    label="Download PDF",
    data=gen_pdf(),
    file_name="file_name.pdf",
    mime="application/pdf",
)
```

## web2py ##
Usage of the original PyFPDF lib with [web2py](http://www.web2py.com/) is described here: <https://github.com/reingart/pyfpdf/blob/master/docs/Web2Py.md>

`v1.7.2` of PyFPDF is included in `web2py` since release `1.85.2`: <https://github.com/web2py/web2py/tree/master/gluon/contrib/fpdf>
