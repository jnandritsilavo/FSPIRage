import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.colors as pc

# Page titre
st.set_page_config(page_title="LPS", page_icon="👅")
st.title("Exposition catégorie 1 : Léchage sur Peau Saine (LPS).")


def plot_cat1_ipm(ipm):
    
    # 1 patient = 1 ID ref_mordu 
    ipm=ipm.drop_duplicates(subset=['ref_mordu'])
    
    # Définir les tranches d'âge (de 5 en 5)
    bins = list(range(0, 105, 5)) + [float('inf')]
    labels = [f'{i}-{i+4}' for i in bins[:-2]] + ['100+']
    age_groups = pd.cut(ipm['age'], bins=bins, labels=labels, right=False)
    ipm['Age Group'] = age_groups

    # Correspondance valeurs parties du corps pour la légende
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

    # Sous tableau pour compter le nombre de catégorie LPS pour chaque partie du corps et groupe d'âge
    lps_counts = pd.DataFrame(columns=['Age Group', 'Body Part', 'LPS Count'])

    # Remplir le tableau lps_counts
    for part, column in body_parts.items():
            part_counts = ipm[ipm[column] == 'LPS'].groupby('Age Group').size().reset_index(name='LPS Count')
            part_counts['Body Part'] = part
            lps_counts = pd.concat([lps_counts, part_counts], ignore_index=True)

    # Visualisation
    fig = px.bar(
            lps_counts, 
            x='Age Group', 
            y='LPS Count', 
            color='Body Part', 
            barmode='group',
            title=f"Proportion de {len(lps_counts)} patients qui ont l'exposition de catégorie 1 ('LPS') par âge et partie du corps.",
            labels={'LPS Count': 'Nombre de LPS', 'Age Group': 'Groupe d\'âge', 'Body Part': 'Partie du corps'}
        )


    st.info('Pas de visualisation disponible.')

def plot_cat1_peripheral(df):
     
    # Définir les tranches d'âge (de 5 en 5)
    bins = list(range(0, 105, 5)) + [float('inf')]
    labels = [f'{i}-{i+4}' for i in bins[:-2]] + ['100+']
    age_groups = pd.cut(df['age'], bins=bins, labels=labels, right=False)
    df['Age Group'] = age_groups

    # Correspondance valeurs parties du corps pour la légende
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

    # Sous tableau pour compter le nombre de catégorie LPS pour chaque partie du corps et groupe d'âge
    lps_counts = pd.DataFrame(columns=['Age Group', 'Body Part', 'LPS Count'])

    # Remplir le tableau lps_counts
    for part, column in body_parts.items():
            part_counts = df[(df[column] == 1)&(df.type_contact___1=='OUI')].groupby('Age Group').size().reset_index(name='LPS Count')
            part_counts['Body Part'] = part
            lps_counts = pd.concat([lps_counts, part_counts], ignore_index=True)

    # Visualisation
    fig = px.bar(
            lps_counts, 
            x='Age Group', 
            y='LPS Count', 
            color='Body Part', 
            barmode='group',
            title=f"Proportion de patients qui ont l'exposition de catégorie 1 (LPS) par âge et partie du corps.",
            labels={'LPS Count': 'Nombre de LPS', 'Age Group': 'Groupe d\'âge', 'Body Part': 'Partie du corps'}
        )

    
    return (st.plotly_chart(fig, use_container_width=True))


# Main
if 'dataframes' in st.session_state:
    dataframes = st.session_state['dataframes']

    selected_file = st.selectbox("Sélectionnez un fichier pour l'analyse", options=list(dataframes.keys()))

    if selected_file:
        df = dataframes[selected_file]

        # BDD IPM CTAR
        if selected_file == "CTAR_ipmdata20022024_cleaned.csv":
            plot_cat1_ipm(df)

        #  BDD IPM périphériques
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
                    plot_cat1_peripheral(df)
            elif all_ctars_selected and selected_year:  
                st.info("Cliquez sur agrandir l'image en haut à droite du graphique.")
                df= df[df['Annee'].isin(selected_year)]
                plot_cat1_peripheral(df) 
            elif all_ctars_selected and not selected_year:
                st.warning("Veuillez sélectionner au moins une année pour afficher l'analyse.")
        else:
            st.warning('Veuillez sélectionner un fichier entre "CTAR_peripheriquedata20022024_cleaned.csv" et "CTAR_ipmdata20022024_cleaned.csv".')        
  
else:
    st.error("Aucun fichier n'a été téléchargé. Veuillez retourner à la page d'accueil pour télécharger un fichier.")

# Sidebar de la page
with st.sidebar.container():
    st.image("Logo-CORAMAD.jpg", use_column_width=True, width=250, caption="FSPI Rage")