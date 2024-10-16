import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Titre page
st.set_page_config(page_title="Ange et Sexe", page_icon="⚧️")
st.title("Age et sexe des victimes.")


def age_sexe(df_clean):
    # Colonne 'age' est de type numerique
    df_clean['age'] = pd.to_numeric(df_clean['age'], errors='coerce')
    # L'âge des patients ne peut pas être au dessus de 120ans
    df_clean=df_clean[df_clean['age']<=120]

    # Compter les pairs (age, sexe) non nulles
    not_null_pairs = df_clean[['age', 'sexe']].notnull().all(axis=1).sum()

    # Grouper et compter l'occurence des pairs (age, sexe)
    age_sex_counts = df_clean.groupby(['age', 'sexe']).size().reset_index(name='count')

    # Sort by age (ensured to be numeric)
    age_sex_counts = age_sex_counts.sort_values(by='age')

    fig = go.Figure()

    # Itérer sur chaque sexe et âge et créer un barplot
    for sex in age_sex_counts['sexe'].unique():
        data = age_sex_counts[age_sex_counts['sexe'] == sex]
        # Utiliser le rouge pour Féminin ('F'), et la couleur par défaut pour Masculin ('M')
        color = 'red' if sex == 'F' else None
        fig.add_trace(go.Bar(
            x=data['age'],
            y=data['count'],
            name=f'{sex}',  
            marker_color=color  
        ))

    # Légende et esthétique de la visualisation
    fig.update_layout(
        barmode='group',  
        title_text=f'Distribution des patients par Âge et Genre (sur {not_null_pairs} patient(s))',
        xaxis_title='Âge',
        yaxis_title='Nombre de patients',
        legend_title='Genre',
        width=1500,   
        height=600,   
        xaxis=dict(
            type='linear',  
            tickmode='linear',  
            tick0=age_sex_counts['age'].min(),  
            dtick=1,  
        ),
        legend=dict(
            orientation='h',  
            x=0, y=1.1,  
        )
    )

    st.plotly_chart(fig)


# Main
if 'dataframes' in st.session_state:
    dataframes = st.session_state['dataframes']

    selected_file = st.selectbox("Sélectionnez un fichier pour l'analyse", options=list(dataframes.keys()))

    if selected_file:
        df = dataframes[selected_file]

        # BDD CTAR IPM : 
        if selected_file == "CTAR_ipmdata20022024_cleaned.csv":
            # 1 patient = 1 ID ref_mordu
            df = df.drop_duplicates(subset=['ref_mordu'])
            st.info("Cliquez sur agrandir l'image en haut à droite du graphique.")
            age_sexe(df)

        # BDD CTAR périphériques
        elif selected_file == "CTAR_peripheriquedata20022024_cleaned.csv":

            #  Ne pas comptabiliser les lignes sans ID 'id_ctar' = CTAR périphériques inconnues 
            df = df.dropna(subset=['id_ctar'])
            df = df.dropna(subset=['date_de_consultation'])

            # Liste des CTARs périphériques pour leur sélection
            unique_ctars = df['id_ctar'].unique()

            df['date_de_consultation']=pd.to_datetime(df['date_de_consultation'])

            df['Annee'] = df['date_de_consultation'].dt.year
            df['Annee']=df['Annee'].astype(int)
            df=df[df['Annee']<=2024]
            unique_year=df['Annee'].unique()

            # Analyse de l'ensemble des CTAR périphériques
            all_ctars_selected = st.checkbox("Sélectionnez tous les CTARs")
            selected_year = st.multiselect(
                    "Sélectionnez une ou plusieurs année(s)",
                    options=sorted(list(unique_year)))

            if not all_ctars_selected:
                selected_ctars = st.multiselect(
                    "Sélectionnez un ou plusieurs CTARs",
                    options=list(unique_ctars))
                if not selected_ctars or not selected_year:
                    st.warning("Veuillez sélectionner au moins un CTAR et une année pour afficher l'analyse.")
                else:
                    df= df[df['id_ctar'].isin(selected_ctars)&df['Annee'].isin(selected_year)]
                    st.info("Cliquez sur agrandir l'image en haut à droite du graphique.")
                    age_sexe(df)
            elif all_ctars_selected and selected_year:  
                st.info("Cliquez sur agrandir l'image en haut à droite du graphique.")
                df= df[df['Annee'].isin(selected_year)]
                age_sexe(df) 
            elif all_ctars_selected and not selected_year:
                st.warning("Veuillez sélectionner au moins une année pour afficher l'analyse.")


        else:
            st.warning('Veuillez sélectionner un fichier entre "CTAR_peripheriquedata20022024_cleaned.csv" et "CTAR_ipmdata20022024_cleaned.csv".')        

else:
    st.error("Aucun fichier n'a été téléchargé. Veuillez retourner à la page d'accueil pour télécharger un fichier.")


# Sidebar de la page
with st.sidebar.container():
    st.image("Logo-CORAMAD.jpg", use_column_width=True, width=250, caption="FSPI Rage")
