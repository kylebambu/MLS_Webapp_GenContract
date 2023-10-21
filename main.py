import streamlit as st
from datetime import datetime, timedelta
from utils import *
import fillpdf
from fillpdf import fillpdfs
from io import BytesIO
import base64

st.header("MLS Offer Generator")
mls_input = st.text_input("MLS Number:")

if mls_input:
    url = "https://api.bridgedataoutput.com/api/v2/OData/virtual_armls/Property('" + mls_input + "')"

    params = {
        'access_token': st.secrets['MLS_API']
    }

    http_output = make_http_request(url, params=params)

    st.subheader('Address: ' + http_output['UnparsedAddress'])
    col1, col2, col3 = st.columns(3)
    col1.subheader('List Price: $' + str(http_output['ListPrice']))
    col3.subheader('Days On Market: ' + str(http_output['DaysOnMarket']))
    st.subheader('')

    purchase_price = st.number_input('Purchase Price', value=http_output['ListPrice'])
    emd = st.number_input('EMD', value=10000)
    col1, col2, col3 = st.columns(3)
    days_until_close = col1.number_input('Days to Close', value=30)

    current_date = datetime.now()
    date_plus_days_from_now = current_date + timedelta(days=days_until_close)
    closing_date = date_plus_days_from_now.strftime('%m/%d/%Y')
    col3.markdown('Closing Date: ' + closing_date)

    col1, col2, col3 = st.columns(3)
    days_until_offer_expire = col1.number_input("Days Until Offer Expiration", value=1)
    date_plus_days_from_now = current_date + timedelta(days=days_until_offer_expire)
    offer_expiration_date = date_plus_days_from_now.strftime('%m/%d/%Y')
    col3.markdown('Offer Expiration: ' + offer_expiration_date)

    st.selectbox('Buyer', ['Steve Furst', 'Kyle Bambu'])


    default_value = """1) The Buyer shall procure the property using either cash or a financial instrument akin to cash, such as a hard money loan or a similar financial arrangement. It is expressly stipulated that this provision does not constitute a financing contingency and shall not impede the closing process.

2) The Buyer holds a valid real estate license in the State of Arizona.

3) The Buyer retains the unilateral right to transfer this property interest to a Limited Liability Company (LLC) or introduce additional Buyers into the transaction, provided that the original Buyer maintains a vested ownership interest.

4) The Buyer agrees to acquire the property in its current "as-is" condition.

5) The Buyer shall be granted a period of 10 days to engage in a due diligence examination of the property. The Buyer, at their sole discretion, reserves the right to rescind the offer during this period and receive a refund of the Earnest Money.
"""
    st.text_area('Additional Terms and Conditions', value=default_value, height=401)

    if st.button("Create Contract"):

        dict = {
        'Buyer': 'hi',
        'Seller': http_output['OwnerName'],
        'Property_Address': http_output['UnparsedAddress'],
        'Parcel_Num': http_output['ParcelNumber'],
        'City': http_output['City'],
        'County': http_output['CountyOrParish'],
        'Zip': http_output['PostalCode'],
        'legal_desc': '',
        'Purchase_Price': purchase_price,
        'EMD': emd,
        'COE_MO': '',
        'COE_DAY': '',
        'COE_YR': ''
        }

        template_pdf = "Residential Purchase Contract.pdf"

        output_pdf = "modified_form.pdf"

        #fillpdfs.write_fillable_pdf("Residential Purchase Contract.pdf", 'output.pdf', data_dict=dict, flatten=False)
        
        #pdf_data_url = pdf_to_data_url('output.pdf')


        #st.markdown(f'<iframe src="data:application/pdf;base64,{pdf_data_url}" width="700" height="500"></iframe>', unsafe_allow_html=True)

        output_pdf = BytesIO()
        fillpdfs.write_fillable_pdf(template_pdf, output_pdf, data_dict=dict, flatten=False)

        # Display the generated PDF in Streamlit
        pdf_data = output_pdf.getvalue()
        pdf_data_base64 = base64.b64encode(pdf_data).decode("utf-8")
        pdf_data_url = f"data:application/pdf;base64,{pdf_data_base64}"
        st.markdown(f'<iframe src="{pdf_data_url}" width="700" height="500"></iframe>', unsafe_allow_html=True)

        # Offer a download link for the generated PDF
        st.write("Download the generated PDF:")
        st.download_button("Download PDF", pdf_data, key="download_pdf", file_name="generated.pdf")