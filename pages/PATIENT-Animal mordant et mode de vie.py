import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Titre page
st.set_page_config(page_title="Espèce responsable et mode de vie.", page_icon="🐕")
st.title("Espèce responsable et leur mode de vie.")

# Correspondance typanim valeurs pour la légende
label_mapping = {
    'A': 'Sauvage',
    'B': 'Errant disparu',
    'C': 'Errant vivant',
    'D': 'Domestique propriétaire connu',
    'E': 'Domestique disparu',
    'F': 'Domestique abbatu',
    'G': 'Domestique mort'
}

def create_donut_chart(df, label_col, count_col, title, is_peripherique=False):
            counts = df[label_col].value_counts().reset_index()
            counts.columns = [label_col, count_col]

            fig = go.Figure(go.Pie(
                labels=counts[label_col],
                values=counts[count_col],
                hole=0.6,
                textinfo='label+percent',
                marker=dict(colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0'][:len(counts)]),
                direction='clockwise'
            ))

            # Esthétique de la visualisation
            top_margin = 70 if is_peripherique else 100  
            fig.update_layout(
                title_text=title,
                margin=dict(t=top_margin, l=70, r=70, b=40),  
                height=800,
                width=1000,
                showlegend=True,
            )

            return fig

def create_pie_chart(df, label_col, count_col, title, is_peripherique=False):
            counts = df[label_col].value_counts().reset_index()
            counts.columns = [label_col, count_col]

            fig = go.Figure(go.Pie(
                labels=counts[label_col],
                values=counts[count_col],
                textinfo='label+percent',
                marker=dict(colors=['#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'][:len(counts)]),
            ))

            # Esthétique de la visualisation
            top_margin = 70 if is_peripherique else 100  
            fig.update_layout(
                title_text=title,
                margin=dict(t=top_margin, l=40, r=40, b=70), 
                height=580,
                width=600,
                showlegend=True,
            )

            return fig
      
        
def anim_mord(df):
    
    df_clean = df.drop_duplicates(subset=['ref_mordu'])

    # Selection box pour animal
    selected_animal = st.selectbox("Sélectionnez un animal pour voir le type d'animal", options=df_clean['animal'].dropna().unique())

    # Filter la BDD pour l'animal sélectionné
    filtered_df = df_clean[df_clean['animal'] == selected_animal]

    # Remplacer dans le colonne 'typanim' lettres par valuers pour la légende de la visualisation
    filtered_df['typanim'] = filtered_df['typanim'].map(label_mapping)

    # Visualisation pour le mode de vie de l'animal
    fig_typanim = create_donut_chart(filtered_df, 'typanim', 'count', f"Répartition du mode de vie de l'animal pour : {len(filtered_df)} {selected_animal}(s) ")
    st.plotly_chart(fig_typanim, use_container_width=True)

    # Selectionnez d'autres animaux à analyser
    additional_animals = df_clean['animal'].value_counts().index.tolist()
    selected_additional = st.multiselect("Sélectionnez d'autres animaux à afficher", options=additional_animals, default=additional_animals[:4])

    # Visualisation pour l(es) animal(aux) sélectionné(s)
    if selected_additional:
        filtered_additional = df_clean[df_clean['animal'].isin(selected_additional)]
        fig_additional_animals = create_pie_chart(filtered_additional, 'animal', 'count', f"Répartition des espèces responsables (tout type de contact) ({len(filtered_additional)} animaux)")
        st.plotly_chart(fig_additional_animals, use_container_width=True)

def anim_mord_perif(df):
    df = df.dropna(subset=['espece'])
    selected_animal = st.selectbox("Sélectionnez un animal pour voir le type d'animal", options=df['espece'].dropna().unique())

    df = df[~df['dev_carac'].astype(str).str.contains('nan-nan|nan-|nan-|-nan', regex=True)]

    # Selectionnez d'autres animaux à analyser
    additional_animals = df['espece'].value_counts().index.tolist()

    # Visualisation pour le mode de vie de l'animal
    animal_type = df[df['espece']==selected_animal]
    fig_typanim_ctar = create_donut_chart(animal_type, 'dev_carac', 'count', f"Répartition du mode de vie de l'animal pour : {len(df[df.espece==selected_animal])}  {selected_animal}(s) ", is_peripherique=True)
    st.plotly_chart(fig_typanim_ctar, use_container_width=True)

    selected_additional = st.multiselect("Sélectionnez d'autres animaux à afficher", options=additional_animals, default=additional_animals[:4])
            
    # Visualisation pour l(es) animal(aux) sélectionné(s)
    if selected_additional:
        filtered_additional = df[df['espece'].isin(selected_additional)]
        fig_additional_animals = create_pie_chart(filtered_additional, 'espece', 'count', f"Répartition des espèces responsables (tout type de contact) ({len(filtered_additional)} animaux/animal)", is_peripherique=True)
        st.plotly_chart(fig_additional_animals, use_container_width=True)
            

# Main 
if 'dataframes' in st.session_state:
    dataframes = st.session_state['dataframes']

    selected_file = st.selectbox("Sélectionnez un fichier pour l'analyse", options=list(dataframes.keys()))

    if selected_file:
        df = dataframes[selected_file]

        # BDD CTAR IPM
        if selected_file == "CTAR_ipmdata20022024_cleaned.csv":
            anim_mord(df)

        #  BDD CTAR Périphériques
        elif selected_file == "CTAR_peripheriquedata20022024_cleaned.csv":
            #  Ne pas comptabiliser les lignes sans ID 'id_ctar' = CTAR périphériques inconnues 
            df = df.dropna(subset=['id_ctar'])
            df = df.dropna(subset=['date_de_consultation'])

            # Liste des CTARs périphériques pour leur sélection
            unique_ctars = df['id_ctar'].unique()

            df['date_de_consultation']=pd.to_datetime(df['date_de_consultation'])

            df['Annee'] = df['date_de_consultation'].dt.year
            df=df[df['Annee']<=2024]
            df['Annee']=df['Annee'].astype(int)
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
                    anim_mord_perif(df)
            elif all_ctars_selected and selected_year:  
                st.info("Cliquez sur agrandir l'image en haut à droite du graphique.")
                df= df[df['Annee'].isin(selected_year)]
                anim_mord_perif(df) 
            elif all_ctars_selected and not selected_year:
                st.warning("Veuillez sélectionner au moins une année pour afficher l'analyse.")


        else:
            st.warning('Veuillez sélectionner un fichier entre "CTAR_peripheriquedata20022024_cleaned.csv" et "CTAR_ipmdata20022024_cleaned.csv".')        

           

else:
    st.error("Aucun fichier n'a été téléchargé. Veuillez retourner à la page d'accueil pour télécharger un fichier.")

# Sidebar de la page
with st.sidebar.container():
    st.image("Logo-CORAMAD.jpg", use_column_width=True, width=250, caption="FSPI Rage")

