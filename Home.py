import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="CTAR Analysis",
    page_icon="🌐"
)

primary_color = "#4c8dc1"  # Blue
secondary_color = "#ffffff"  # White

st.markdown(
    f"""
    <style>
        .reportview-container {{
            background-color: {secondary_color};
            color: #000000;
        }}
        .stButton > button {{
            background-color: {primary_color};
            color: {secondary_color};
        }}
        .stTextInput > div > div > input {{
            background-color: {secondary_color};
            color: #000000;
        }}
        .stDataFrame > div > div > div > div > table {{
            background-color: {secondary_color};
        }}
        .custom-background {{
            background-color: {primary_color};
            padding: 10px;
            border-radius: 10px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Bienvenue sur CTAR Indicateurs")
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("###### Une application d'analyse des indicateurs de performance des CTAR de Madagascar, à l'initiative de l'Institut Pasteur de Madagascar.")


def main():
    st.markdown("<h3 style='text-align: left; margin-top: 20px;'>1. Téléchargez vos fichiers :</h3>", unsafe_allow_html=True)

    uploaded_files = st.file_uploader("Sélectionnez les fichiers CSV", type=["csv"], accept_multiple_files=True)

    if uploaded_files:
        dataframes = {}

        for uploaded_file in uploaded_files:
            try:
                df = pd.read_csv(uploaded_file, encoding='ISO-8859-1', sep=',')
                dataframes[uploaded_file.name] = df
            except UnicodeDecodeError as e:
                st.error(f"Erreur de décodage pour le fichier {uploaded_file.name}: {e}")
                continue

        st.session_state['dataframes'] = dataframes

        st.header(f"Contenu du fichier: {list(dataframes.keys())[0]}")
        st.dataframe(df.head())


    else:
        st.warning("Veuillez télécharger au moins un fichier CSV.")


if __name__ == '__main__':
    main()

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.write("Pour toute question/information : aima.mohammad.pro@gmail.com ")
st.markdown("---")
st.write("IPM © 2024")

with st.sidebar.container():
    st.image("Logo-CORAMAD.jpg", use_column_width=True, width=250, caption="FSPI Rage")
