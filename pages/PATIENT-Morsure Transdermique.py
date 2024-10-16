import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.colors as pc

# Titre page
st.set_page_config(page_title="MT", page_icon="🐾")
st.title("Facteurs de risque des Morsures Transdermiques (MT).")


def plot_MT_ipm(ipm):

    # 1 patient = 1 ID ref_mordu
    ipm=ipm.drop_duplicates(subset=['ref_mordu'])

    # Définir les tranches d'âge (de 5 en 5)
    bins = list(range(0, 105, 5)) + [float('inf')]
    labels = [f'{i}-{i+4}' for i in bins[:-2]] + ['100+']
    age_groups = pd.cut(ipm['age'], bins=bins, labels=labels, right=False)
    ipm['Age Group'] = age_groups

    # Renommer partie du corps pour une légende plus visible
    body_parts = {
            'Tête': 'tet_cont',
            'Bras et avant-bras': 'm_sup_cont',
            'Main': 'ext_s_cont',
            'Cuisse et Jambe': 'm_inf_cont',
            'Pied': 'ext_i_cont',
            'Abdomen': 'abdo_cont',
            'Dos': 'dos_cont',
            'Parties génitales': 'geni_cont'
        }

    # Sous tableau pour compter le nombre de catégorie MT pour chaque partie du corps, genre et groupe d'âge
    mt_counts = pd.DataFrame(columns=['Age Group', 'Body Part', 'Gender', 'MT Count'])

    # Remplir le tableau mt_counts
    for part, column in body_parts.items():
            for gender in ipm['sexe'].dropna().unique():
                part_counts = ipm[(ipm[column] == 'MT') & (ipm['sexe'] == gender)].groupby('Age Group').size().reset_index(name='MT Count')
                part_counts['Body Part'] = part
                part_counts['Gender'] = gender
                mt_counts = pd.concat([mt_counts, part_counts], ignore_index=True)

    # Visualisation
    fig = px.bar(
            mt_counts,
            x='Age Group', 
            y='MT Count', 
            color='Body Part', 
            barmode='group',
            facet_col='Gender', 
            facet_col_wrap=2,
            title="Nombre de lésions 'MT' par groupe d'âge, partie du corps et sexe",
            labels={
                'MT Count': 'Nombre de MT', 
                'Age Group': "Groupe d'âge", 
                'Body Part': 'Partie du corps', 
                'Gender': 'Sexe'
            },
            category_orders={'Gender': ['M', 'F']}
        )

    fig.update_layout(
            title="Facteurs de risque des morsures transdermiques (âge, partie du corps et genre)",
            xaxis=dict(title="Groupe d'âge"),
            yaxis=dict(title="Nombre de Morsure Transdermique"),
            legend=dict(title="Partie du corps", orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.6),
            height=700,  
            width=1000,
            margin=dict(b=100)  
        )

    st.plotly_chart(fig)

    # Correspondance valeurs type d'animal pour la légende
    animal_type_mapping = {
            'A': 'Sauvage', 
            'B': 'Errant disparu', 
            'C': 'Errant vivant', 
            'D': 'Domestique Propriétaire Connu', 
            'E': 'Domestique Disparu', 
            'F': 'Domestique Abbatu', 
            'G': 'Domestique Mort'
        }

    ipm['typanim'] = ipm['typanim'].map(animal_type_mapping)

    # Sous tableau pour compter le nombre de catégorie MT pour chaque partie du corps, genre et groupe d'âge
    mt_counts = pd.DataFrame(columns=['Age Group', 'Body Part', 'Gender', 'Animal Type', 'MT Count'])

    # Remplir le tableau mt_counts
    for part, column in body_parts.items():
        for gender in ipm['sexe'].dropna().unique():
            for animal_type in ipm['typanim'].dropna().unique():
                    part_counts = ipm[(ipm[column] == 'MT') & (ipm['sexe'] == gender) & (ipm['typanim'] == animal_type)].groupby('Age Group').size().reset_index(name='MT Count')
                    part_counts['Body Part'] = part
                    part_counts['Gender'] = gender
                    part_counts['Animal Type'] = animal_type
                    mt_counts = pd.concat([mt_counts, part_counts], ignore_index=True)

    # Visualisation
    gender_icons = {'M': '♂', 'F': '♀'}
    mt_counts['Gender'] = mt_counts['Gender'].map(gender_icons)

    fig2 = px.bar(
            mt_counts, 
            x='Age Group', 
            y='MT Count', 
            color='Body Part', 
            barmode='group',
            facet_col='Gender', 
            facet_col_wrap=2, 
            facet_row='Animal Type',
            title="Nombre de lésions 'MT' par groupe d'âge, partie du corps, sexe et type d'animal",
            labels={
                'MT Count': 'Nombre de MT', 
                'Age Group': "Groupe d'âge", 
                'Body Part': 'Partie du corps', 
                'Gender': 'Sexe', 
                'Animal Type': ''
            },
            category_orders={
                'Gender': ['♂', '♀'], 
                'Animal Type': sorted(animal_type_mapping.values())  
            }
        )

    fig2.update_layout(
            title="Facteurs de risque des morsures transdermiques (MT) : âge, partie du corps, sexe et type d'animal",
            xaxis=dict(title="Groupe d'âge", tickfont=dict(size=10)),
            yaxis=dict(title="Nombre de MT", tickfont=dict(size=10)),
            legend=dict(title="Partie du corps :", orientation="h", yanchor="bottom", y=1.01, xanchor="auto", x=0.5),
            height=1900,  
            width=1000,
            margin=dict(b=400,t=250)  
        )

    fig2.update_yaxes(matches=None)  
    fig2.for_each_annotation(lambda a: a.update(text=a.text.split('=')[-1]))
    fig2.update_xaxes(tickfont=dict(size=10))
    fig2.update_yaxes(tickfont=dict(size=10))
    fig2.update_yaxes(automargin=True)

    st.plotly_chart(fig2)



def plot_MT_peripheral(df):

    bins = list(range(0, 105, 5)) + [float('inf')]
    labels = [f'{i}-{i+4}' for i in bins[:-2]] + ['100+']
    age_groups = pd.cut(df['age'], bins=bins, labels=labels, right=False)
    df['Age Group'] = age_groups

    
    body_parts = {
            'Tête et Cou': 'singes_des_legions___1',
            'Bras et Avant-bras': 'singes_des_legions___2',
            'Main': 'singes_des_legions___3',
            'Cuisse et Jambe': 'singes_des_legions___4',
            'Pied': 'singes_des_legions___5',
            'Autres': 'singes_des_legions___9',
            'Dos et Torse': 'singes_des_legions___6',
            'Parties génitales': 'singes_des_legions___7'
        }

    
    mt_counts = pd.DataFrame(columns=['Age Group', 'Body Part', 'Gender', 'MT Count'])

    # Remplir le tableau mt_couts
    for part, column in body_parts.items():
            for gender in df['sexe'].dropna().unique():
                part_counts = df[(df[column] == 1) & (df.type_contact___5== 1)& (df['sexe'] == gender)].groupby('Age Group').size().reset_index(name='MT Count')
                part_counts['Body Part'] = part
                part_counts['Gender'] = gender
                mt_counts = pd.concat([mt_counts, part_counts], ignore_index=True)

    # Visualisation
    fig = px.bar(
            mt_counts,
            x='Age Group', 
            y='MT Count', 
            color='Body Part', 
            barmode='group',
            facet_col='Gender', 
            facet_col_wrap=2,
            title="Nombre de lésions 'MT' par groupe d'âge, partie du corps et sexe",
            labels={
                'MT Count': 'Nombre de MT', 
                'Age Group': "Groupe d'âge", 
                'Body Part': 'Partie du corps', 
                'Gender': 'Sexe'
            },
            category_orders={'Gender': ['M', 'F']}
        )

    fig.update_layout(
            title="Facteurs de risque des morsures transdermiques (âge, partie du corps et genre)",
            xaxis=dict(title="Groupe d'âge"),
            yaxis=dict(title="Nombre de Morsure Transdermique"),
            legend=dict(title="Partie du corps", orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.6),
            height=900,  
            width=1000,
            margin=dict(b=100) 
        )

    st.plotly_chart(fig)

     
    mt_counts = pd.DataFrame(columns=['Age Group', 'Body Part', 'Gender', 'Animal Type', 'MT Count'])
    df = df[~df['dev_carac'].astype(str).str.contains('nan-nan|nan-|nan-|-nan', regex=True)]

    for part, column in body_parts.items():
        for gender in df['sexe'].dropna().unique():
            for animal_type in df['dev_carac'].dropna().unique():
                    part_counts = df[(df[column] == 1) & (df.type_contact___5== 1) & (df['sexe'] == gender) & (df['dev_carac'] == animal_type)].groupby('Age Group').size().reset_index(name='MT Count')
                    part_counts['Body Part'] = part
                    part_counts['Gender'] = gender
                    part_counts['Animal Type'] = animal_type
                    mt_counts = pd.concat([mt_counts, part_counts], ignore_index=True)

    gender_icons = {'M': 'M', 'F': 'F'}
    mt_counts['Gender'] = mt_counts['Gender'].map(gender_icons)

    fig2 = px.bar(
            mt_counts, 
            x='Age Group', 
            y='MT Count', 
            color='Body Part', 
            barmode='group',
            facet_col='Gender', 
            facet_col_wrap=2, 
            facet_row='Animal Type',
            title="Nombre de lésions 'MT' par groupe d'âge, partie du corps, sexe et type d'animal",
            labels={
                'MT Count': 'Nombre de MT', 
                'Age Group': "Groupe d'âge", 
                'Body Part': 'Partie du corps', 
                'Gender': 'Sexe', 
                'Animal Type': ''
            },
            category_orders={
                'Gender': ['M', 'F'], 
                'Animal Type': sorted(df['dev_carac'].dropna().unique())  
            }
        )

    fig2.update_layout(
            title="Facteurs de risque des morsures transdermiques (MT) : âge, partie du corps, sexe et type d'animal",
            xaxis=dict(title="Groupe d'âge", tickfont=dict(size=10)),
            yaxis=dict(title="Nombre de MT", tickfont=dict(size=10)),
            legend=dict(title="Partie du corps :", orientation="h", yanchor="bottom", y=1.01, xanchor="auto", x=0.5),
            height=1900, 
            width=1000,
            margin=dict(b=400,t=250)  
        )

    fig2.update_yaxes(matches=None)  
    fig2.for_each_annotation(lambda a: a.update(text=a.text.split('=')[-1]))
    fig2.update_xaxes(tickfont=dict(size=10))
    fig2.update_yaxes(tickfont=dict(size=10))
    fig2.update_yaxes(automargin=True)

    st.plotly_chart(fig2)




# Main
if 'dataframes' in st.session_state:
    dataframes = st.session_state['dataframes']

    selected_file = st.selectbox("Sélectionnez un fichier pour l'analyse", options=list(dataframes.keys()))

    if selected_file:
        df = dataframes[selected_file]

        # BDD IPM CTAR
        if selected_file == "CTAR_ipmdata20022024_cleaned.csv":
            plot_MT_ipm(df)

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
                    plot_MT_peripheral(df)
            elif all_ctars_selected and selected_year:  
                st.info("Cliquez sur agrandir l'image en haut à droite du graphique.")
                df= df[df['Annee'].isin(selected_year)]
                plot_MT_peripheral(df) 
            elif all_ctars_selected and not selected_year:
                st.warning("Veuillez sélectionner au moins une année pour afficher l'analyse.")
           

else:
    st.error("Aucun fichier n'a été téléchargé. Veuillez retourner à la page d'accueil pour télécharger un fichier.")


# Sidebar de la page
with st.sidebar.container():
    st.image("Logo-CORAMAD.jpg", use_column_width=True, width=250, caption="FSPI Rage")