import streamlit as st
from sqlalchemy import select

from database import get_engine
from json_parser import BoolWithNA
from tables import RetrievedInformation

st.set_page_config(layout="wide")
st.title("Retrieved Information")

col1, col2, col3, col4, col5 = st.columns(5)
show_mortgage_register = col1.multiselect(
    "Mortgage Register",
    BoolWithNA.get_values(),
    BoolWithNA.get_values(),
)
show_lands_regulated = col2.multiselect(
    "Lands Regulated",
    BoolWithNA.get_values(),
    BoolWithNA.get_values(),
)
show_two_sided = col3.multiselect(
    "Two Sided",
    BoolWithNA.get_values(),
    BoolWithNA.get_values(),
)
max_fee_check = col4.checkbox("Select maximum rent")
if max_fee_check:
    max_fee = col5.slider("rent", min_value=0, max_value=5_000, step=100)
else:
    max_fee = 5_000

with get_engine().connect() as cur:

    stmt = (
        select(RetrievedInformation)
        .filter(RetrievedInformation.mortgage_register.in_(show_mortgage_register))
        .filter(RetrievedInformation.lands_regulated.in_(show_lands_regulated))
        .filter(RetrievedInformation.two_sided.in_(show_two_sided))
    )
    if max_fee_check:
        stmt = stmt.filter(RetrievedInformation.rent_administration_fee < max_fee)
    rows = cur.execute(stmt)

if rows:
    for row in rows:
        col1, col2 = st.columns(spec=[0.3, 0.7])
        col1.markdown(row[0])
        col2.write(row[1])
else:
    st.write("No data found with the selected filters.")
