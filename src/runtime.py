from __future__ import annotations

import streamlit as st

from real_estate_analysis import clean_real_estate_data, load_real_estate_data


@st.cache_data(show_spinner=False)
def get_clean_data():
    return clean_real_estate_data(load_real_estate_data())


def money(value: float | int | None) -> str:
    if value is None or value != value:
        return "₹0.00"
    return f"₹{float(value):,.2f}"
