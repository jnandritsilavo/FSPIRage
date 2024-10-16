import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Titre page 
st.set_page_config(page_title="Lésion", page_icon="🩹")
st.title("Nombre de lésions par patient.")


def plot_cat1_ipm(ipm):
    # 1 patient= 1 ID ref_mordu
    ipm=ipm.drop_duplicates(subset=['ref_mordu'])

   # Nettoyage colonne nombre lésions : format integer  :TOUTE COLONNES NULLE ALORS  DROP 
    lesion_columns = ['nbtet', 'nb_sup', 'nb_extr_s', 'nb_inf', 'nb_extr_i', 'nb_abdo', 'nb_dos', 'nb_genit']
    for col in lesion_columns:
            ipm[col] = ipm[col].dropna().astype(int)

    # Définir les tranches d'âge (de 5 en 5)
    bins = list(range(0, 105, 5)) + [float('inf')]
    labels = [f'{i}-{i+4}' for i in bins[:-2]] + ['100+']
    age_groups = pd.cut(ipm['age'], bins=bins, labels=labels, right=False)
    ipm['Age Group'] = age_groups 

    # Grouper par âge et calculer la moyenne et la médiane des lésions par partie du corps
    grouped = ipm.groupby('Age Group').agg({col: ['mean', 'median', 'var'] for col in lesion_columns}).reset_index()
    
    grouped.columns = ['Age Group'] + [f'{col}_{stat}' for col, stat in grouped.columns[1:]]

    # Renommer les colonnes pour la légende
    grouped.rename(columns={
            'nbtet_mean': 'Tête_mean', 'nbtet_median': 'Tête_median', 'nbtet_var': 'Tête_var',
            'nb_sup_mean': 'Bras et avant-bras_mean', 'nb_sup_median': 'Bras et avant-bras_median', 'nb_sup_var': 'Bras et avant-bras_var',
            'nb_extr_s_mean': 'Main_mean', 'nb_extr_s_median': 'Main_median', 'nb_extr_s_var': 'Main_var',
            'nb_inf_mean': 'Cuisse et Jambe_mean', 'nb_inf_median': 'Cuisse et Jambe_median', 'nb_inf_var': 'Cuisse et Jambe_var',
            'nb_extr_i_mean': 'Pied_mean', 'nb_extr_i_median': 'Pied_median', 'nb_extr_i_var': 'Pied_var',
            'nb_abdo_mean': 'Abdomen_mean', 'nb_abdo_median': 'Abdomen_median', 'nb_abdo_var': 'Abdomen_var',
            'nb_dos_mean': 'Dos_mean', 'nb_dos_median': 'Dos_median', 'nb_dos_var': 'Dos_var',
            'nb_genit_mean': 'Parties génitales_mean', 'nb_genit_median': 'Parties génitales_median', 'nb_genit_var': 'Parties génitales_var'
        }, inplace=True)

    # Colonne des categories en type string 
    for col in grouped.select_dtypes(include='category').columns:
            grouped[col] = grouped[col].astype(str)    
    grouped.fillna(0, inplace=True)
        
    fig = go.Figure()

    # Légende couleurs pour chaque partie du corps
    body_parts = [
            ('Tête', 'blue'),
            ('Bras et avant-bras', 'green'),
            ('Main', 'red'),
            ('Cuisse et Jambe', 'purple'),
            ('Pied', 'orange'),
            ('Abdomen', 'brown'),
            ('Dos', 'pink'),
            ('Parties génitales', 'cyan')
        ]

    sizeref = 70 * max(grouped[f'{part}_mean'].max() for part, _ in body_parts) / (100. ** 2)

    for part, color in body_parts:
        fig.add_trace(go.Scatter(
                x=grouped['Age Group'], y=grouped[f'{part}_mean'], mode='markers', name=f'{part} Moyenne',
                marker=dict(size=grouped[f'{part}_mean'] * 4, sizemode='area', sizeref=sizeref, sizemin=1, color=color),
                showlegend=True
            ))

        variance_val = grouped[f'{part}_var']
        fig.add_trace(go.Scatter(
                x=grouped['Age Group'], y=variance_val, mode='lines',
                line=dict(color=color, width=2, dash='dot'), name=f'{part} Variance', showlegend=True, visible='legendonly'
            ))

        median_val = grouped[f'{part}_median']
        fig.add_trace(go.Scatter(
                x=grouped['Age Group'], y=median_val, mode='lines',
                line=dict(color=color, width=2, dash='dash'), name=f'{part} Médiane', showlegend=True, visible='legendonly'
            ))

    fig.update_layout(
            title=f" Distribution du nombre de lésions sur {len(ipm)} patients de CTAR IPM.",
            xaxis=dict(title="Groupe d'âge", tickangle=-45),  
            yaxis=dict(title='Nombre de lésions '),
            legend=dict(title="Légende", orientation="v", yanchor="top", y=0.95, xanchor="right", x=1.35,
                        traceorder="normal", tracegroupgap=20),
            height=850,  
            width=1000,
            margin=dict(b=250) 
        )

    st.plotly_chart(fig, use_container_width=True)

def plot_cat1_peripheral(ctar):
    #Nettoyage cas particulier colonnes 'ctar' et 'nb_lesion'
    ctar['nb_lesion'] = ctar['nb_lesion'].replace({
            '01': '1', '02': '2', '03': '3', '04': '4', '05': '5', 
            '06': '6', '07': '7', '08': '8', '09': '9', '022': '22', 
            '052': '52', '002': '2', '021': '21'
        })
    ctar=ctar.dropna(subset=['nb_lesion'])

    ctar.at[26659, 'ctar'] = 'Antsohihy'
    ctar.at[36582, 'ctar'] = 'Morondava'
    ctar.at[38479, 'ctar'] = 'Vangaindrano'
    ctar.at[42574, 'ctar'] = 'Fianarantsoa'
    ctar.at[42575, 'ctar'] = 'Fianarantsoa'

   
        # Fill NaNs with -1 and convert to int
    #ctar['nb_lesion_filled'] = ctar['nb_lesion'].fillna(-1).astype(int)

    # Calculate statistics, ignoring the marker value for NaNs
    mean_lesions = ctar[ctar['nb_lesion'] != -1]['nb_lesion'].mean()
    median_lesions = ctar[ctar['nb_lesion'] != -1]['nb_lesion'].median()
    variance_lesions = ctar[ctar['nb_lesion'] != -1]['nb_lesion'].var()

        # Count the values 
    value_counts = ctar['nb_lesion'].value_counts().sort_index()

    if (len(value_counts) - 1)>0:
            # Convert the index to a list of strings for x-axis labeling, converting -1 back to 'NaN'
        x_labels = [int(x) if x != -1 else 'NaN' for x in value_counts.index]

         # Gradient de couleur (orange) basé sur le nombre de lésions
        dark_oranges = px.colors.sequential.Oranges[::-1] 
        color_scale = [dark_oranges[int((i) * (len(dark_oranges) - 1) / (len(value_counts) - 1))] for i in range(len(value_counts))]

        fig = go.Figure()

        fig.add_trace(go.Bar(
                x=(x_labels),
                y=value_counts.values,
                marker_color=color_scale,
                name='Nombre de patients'
            ))

        fig.add_trace(go.Scatter(
                x=(x_labels),
                y=[mean_lesions] * len(x_labels),
                mode='lines',
                line=dict(color='red', dash='dash'),
                name=f'Moyenne: {mean_lesions:.2f}'
            ))

        fig.add_trace(go.Scatter(
                x=(x_labels),
                y=[median_lesions] * len(x_labels),
                mode='lines',
                line=dict(color='green', dash='solid'),
                name=f'Médiane: {median_lesions:.2f}'
            ))

        fig.update_layout(
                title=f'Distribution du nombre de lésions sur {len(ctar)} patients des CTAR périphériques.',
                xaxis_title='Nombre de lésions',
                yaxis_title='Nombre de patients',
                xaxis=dict(tickmode='array', tickvals=x_labels, ticktext=x_labels),
                template='plotly_white'
            )

        fig.add_annotation(
                x=len(x_labels) - 1,
                y=max(value_counts.values),
                text=f'Variance: {variance_lesions:.2f}',
                showarrow=False,
                yshift=10,
                xshift=-10,
                font=dict(color='black', size=12)
            )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader('Statistiques:')
        st.write(f'Moyenne des lésions: {mean_lesions:.2f}')
        st.write(f'Médiane des lésions: {median_lesions:.2f}')
        st.write(f'Variance des lésions: {variance_lesions:.2f}')
    else:
         st.info("Pas de donnée pour ce CTAR périphérique.")

    
# Main 
if 'dataframes' in st.session_state:
    dataframes = st.session_state['dataframes']

    selected_file = st.selectbox("Sélectionnez un fichier pour l'analyse", options=list(dataframes.keys()))

    if selected_file:
        df = dataframes[selected_file]

        # BDD CTAR IPM
        if selected_file == "CTAR_ipmdata20022024_cleaned.csv":
            plot_cat1_ipm(df)

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
                    plot_cat1_peripheral(df)
            elif all_ctars_selected and selected_year:  
                st.info("Cliquez sur agrandir l'image en haut à droite du graphique.")
                df= df[df['Annee'].isin(selected_year)]
                plot_cat1_peripheral(df) 
            elif all_ctars_selected and not selected_year:
                st.warning("Veuillez sélectionner au moins une année pour afficher l'analyse.")
           

else:
    st.error("Aucun fichier n'a été téléchargé. Veuillez retourner à la page d'accueil pour télécharger un fichier.")

# Sidebar de la page
with st.sidebar.container():
    st.image("Logo-CORAMAD.jpg", use_column_width=True, width=250, caption="FSPI Rage")
