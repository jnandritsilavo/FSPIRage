import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Titre page
st.set_page_config(page_title="Utilisation Savon", page_icon="🧼")
st.title("Lavage au savon sur plaie.")

def plot_age_sex_savon_distribution(ipm):
    # 1ref_mordu = 1 patient
    ipm=ipm.drop_duplicates(subset=['ref_mordu'])
    # Convert 'age' column to numeric, coerce errors to NaN
    ipm['age'] = pd.to_numeric(ipm['age'], errors='coerce')

    ipmm = ipm.dropna(subset=['age'])
    ipmm=ipmm[ipmm.age>0]

    not_null_pairs = ipmm[['age', 'sexe', 'savon']].notnull().all(axis=1).sum()

    age_sex_savon_counts = ipmm.groupby(['age', 'sexe', 'savon']).size().reset_index(name='count')
    age_sex_savon_counts = age_sex_savon_counts.sort_values(by='age')

    total_counts = age_sex_savon_counts.groupby(['sexe', 'savon'])['count'].sum()

    age_sex_savon_counts['percentage'] = age_sex_savon_counts.apply(
        lambda row: round((row['count'] / total_counts[row['sexe'], row['savon']]) * 100, 2)
        if total_counts[row['sexe'], row['savon']] != 0 else 0, axis=1
    )

    color_palette = {
        ('M', 'OUI'): 'rgba(50, 171, 96, 0.6)',   
        ('M', 'NON'): 'rgba(50, 171, 96, 0.9)',   
        ('F', 'OUI'): 'rgba(171, 50, 96, 0.6)',  
        ('F', 'NON'): 'rgba(171, 50, 96, 0.9)'    
    }

    fig = go.Figure()

    for sex in age_sex_savon_counts['sexe'].unique():
        data_oui = age_sex_savon_counts[(age_sex_savon_counts['sexe'] == sex) & (age_sex_savon_counts['savon'] == 'OUI')]
        data_non = age_sex_savon_counts[(age_sex_savon_counts['sexe'] == sex) & (age_sex_savon_counts['savon'] == 'NON')]
        
        data_oui = data_oui.sort_values(by='age')
        data_non = data_non.sort_values(by='age')
        
        if not data_oui.empty:
            fig.add_trace(go.Bar(
                x=data_oui['age'],
                y=data_oui['count'],
                name=f'{sex} - Savon: OUI',
                marker_color=color_palette[(sex, 'OUI')],
                base=0,  
                offsetgroup=sex,
            ))
        
        if not data_non.empty:
            fig.add_trace(go.Bar(
                x=data_non['age'],
                y=data_non['count'],
                name=f'{sex} - Savon: NON',
                marker_color=color_palette[(sex, 'NON')],
                base=0,  
                offsetgroup=sex,
            ))

  
    fig.update_layout(
        barmode='stack', 
        title_text=f'Distribution des patients par Âge, Genre et Lavage au savon (sur {not_null_pairs} patients IPM)',
        xaxis_title='Âge',
        yaxis_title='Nombre de patients',
        legend_title='Genre et Savon',
        width=1000,
        height=600,
        xaxis={'type': 'category'},
        legend=dict(
            orientation='h',
            x=0, y=1.1,
        )
    )

    st.plotly_chart(fig)

def plot_peripheral_data(df):
    
    peripheral_data = df[['sexe', 'age', 'lavage_savon']]

    peripheral_data = peripheral_data[peripheral_data['lavage_savon'] != 'Non rempli']

    peripheral_data['age'] = pd.to_numeric(peripheral_data['age'], errors='coerce')
    peripheral_data['lavage_savon']=peripheral_data['lavage_savon'].replace('0', 'NON')

    peripheral_data = peripheral_data.dropna(subset=['age'])

    num_patients = peripheral_data.shape[0]

    age_sex_savon_counts = peripheral_data.groupby(['age', 'sexe', 'lavage_savon']).size().reset_index(name='count')

    age_sex_savon_counts = age_sex_savon_counts.sort_values(by='age')

    color_palette = {
        ('M', 'OUI'): 'rgba(50, 171, 96, 0.6)',   
        ('M', 'NON'): 'rgba(50, 171, 96, 0.9)',   
        ('F', 'OUI'): 'rgba(171, 50, 96, 0.6)', 
        ('F', 'NON'): 'rgba(171, 50, 96, 0.9)'    
    }

    fig = go.Figure()

    for sex in age_sex_savon_counts['sexe'].unique():
        for savon in age_sex_savon_counts['lavage_savon'].unique():
            data = age_sex_savon_counts[(age_sex_savon_counts['sexe'] == sex) & (age_sex_savon_counts['lavage_savon'] == savon)]
            
            if not data.empty:
                fig.add_trace(go.Bar(
                    x=data['age'],
                    y=data['count'],
                    name=f'{sex} - Savon: {savon}',
                    marker_color=color_palette[(sex, savon)],
                    base=0,  
                    offsetgroup=sex,
                ))

    fig.update_layout(
        barmode='stack',
        title_text=f'Distribution des patients par Âge, Genre et Lavage au savon (sur {num_patients} patient(s))',
        xaxis_title='Âge',
        yaxis_title='Nombre de patients',
        legend_title='Genre et Savon',
        width=1000,
        height=600,
        xaxis={'type': 'category'},
        legend=dict(
            orientation='h',
            x=0, y=1.1,
        )
    )

    if num_patients>1:
        return(st.plotly_chart(fig))
    else:
        return(st.info('Données indisponibles pour ce CTAR périphérique.'))

# Main
if 'dataframes' in st.session_state:

    dataframes = st.session_state['dataframes']

    selected_file = st.selectbox("Sélectionnez un fichier pour l'analyse", options=list(dataframes.keys()))

    if selected_file:
        df = dataframes[selected_file]

        # BDD CTAR IPM
        if selected_file == "CTAR_ipmdata20022024_cleaned.csv":
            plot_age_sex_savon_distribution(df)

        # BDD CTAR périphérique
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
                    plot_peripheral_data(df)
            elif all_ctars_selected and selected_year:  
                st.info("Cliquez sur agrandir l'image en haut à droite du graphique.")
                df= df[df['Annee'].isin(selected_year)]
                plot_peripheral_data(df) 
            elif all_ctars_selected and not selected_year:
                st.warning("Veuillez sélectionner au moins une année pour afficher l'analyse.")
           

else:
    st.error("Aucun fichier n'a été téléchargé. Veuillez retourner à la page d'accueil pour télécharger un fichier.")


# Sidebar de la page
with st.sidebar.container():
    st.image("Logo-CORAMAD.jpg", use_column_width=True, width=250, caption="FSPI Rage")