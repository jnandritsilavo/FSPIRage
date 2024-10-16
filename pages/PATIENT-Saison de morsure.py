import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.colors as pc

# Titre page
st.set_page_config(page_title="Saison Morsure", page_icon="☀️")
st.title("Affluence des patients par saison.")


 # Fonction saisons malgaches 
def get_season(date):
        if pd.isnull(date):
            return None
        if pd.Timestamp(year=date.year, month=9, day=15) <= date < pd.Timestamp(year=date.year, month=12, day=15):
            return 'Lohataona (été)'
        elif pd.Timestamp(year=date.year, month=12, day=15) <= date < pd.Timestamp(year=date.year+1, month=3, day=15):
            return 'Fahavratra (pluie)'
        elif pd.Timestamp(year=date.year, month=3, day=15) <= date < pd.Timestamp(year=date.year, month=6, day=15):
            return 'Fararano (automne)'
        else:
            return 'Ritinina (hiver)'

def plot_saison_morsure_ipm(ipm):
     #1 ref_mordu=1 patient
    ipm=ipm.drop_duplicates(subset=['ref_mordu'])

    ipm['dat_consu'] = pd.to_datetime(ipm['dat_consu'], format='%d/%m/%Y', errors='coerce')

    # Associer une saison à chaque date de consultation
    ipm['season'] = ipm['dat_consu'].apply(get_season)

    # Group by month, year, and sexe to count the number of patients for each sex
    monthly_sex_counts = ipm.groupby(['mois', 'Annee', 'sexe']).size().reset_index(name='count')

    months = list(range(1, 13)) 
    month_names = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
        'Sep', 'Oct', 'Nov', 'Dec'
    ]

    # Ajuster le zoom du la visualisation
    min_count = monthly_sex_counts['count'].min()
    max_count = monthly_sex_counts['count'].max()
    range_margin = (max_count - min_count) * 0.2  

    fig = go.Figure()

    male_colors = pc.sequential.Blues[::-1]  
    female_colors = pc.sequential.Reds[::-1]  

    years_sorted = sorted(monthly_sex_counts['Annee'].unique(), reverse=True)

    sexes = ['M', 'F']
    for i, year in enumerate(years_sorted):
        for j, sex in enumerate(sexes):
            df_year_sex = monthly_sex_counts[(monthly_sex_counts['Annee'] == year) & (monthly_sex_counts['sexe'] == sex)]
            df_year_sex = df_year_sex.set_index('mois').reindex(months).reset_index()
            df_year_sex['count'] = df_year_sex['count'].fillna(0)
            
            # Determine color based on gender
            if sex == 'M':
                color = male_colors[i % len(male_colors)]
            else:
                color = female_colors[i % len(female_colors)]

            fig.add_trace(go.Scatter(
                x=df_year_sex['mois'],
                y=df_year_sex['count'],
                mode='lines+markers',
                name=f"{int(year)} - {'Homme' if sex == 'M' else 'Femme'}", 
                marker=dict(size=8, color=color),  
                line=dict(width=2),
                visible="legendonly" if year < 2021 else True  
            ))

    season_backgrounds = {
        'Fahavratra (pluie)': (12, 3, 'rgba(186, 225, 255, 0.3)', 'rgb(186, 225, 255)'),
        'Fararano (automne)': (3.5, 6, 'rgba(255, 186, 186, 0.3)', 'rgb(255, 186, 186)'),
        'Ritinina (hiver)': (6.5, 9, 'rgba(186, 255, 201, 0.3)', 'rgb(186, 255, 201)'),
        'Lohataona (été)': (9.5, 11.5, 'rgba(255, 223, 186, 0.3)', 'rgb(255, 223, 186)')
    }

    shapes = []
    annotations = []

    for season, (start_month, end_month, color, text_color) in season_backgrounds.items():
        if end_month < start_month:
            shapes.append(dict(
                type='rect',
                x0=start_month - 1,
                x1=11,  
                y0=min_count - range_margin,
                y1=max_count + range_margin,
                fillcolor=color,
                line=dict(width=0),
                layer='below'
            ))
            shapes.append(dict(
                type='rect',
                x0=1 - 1,  
                x1=end_month - 0.5,
                y0=min_count - range_margin,
                y1=max_count + range_margin,
                fillcolor=color,
                line=dict(width=0),
                layer='below'
            ))
        else:
            shapes.append(dict(
                type='rect',
                x0=start_month - 1,
                x1=end_month - 0.5,
                y0=min_count - range_margin,
                y1=max_count + range_margin,
                fillcolor=color,
                line=dict(width=0),
                layer='below'
            ))

        annotations.append(dict(
            x=(start_month) / 10 if end_month < start_month else (start_month + end_month - 1) / 2,
            y=min_count - range_margin,  
            text=season,
            showarrow=False,
            font=dict(size=15, color=text_color),
            xanchor="center",
            yanchor="bottom"
        ))

    fig.update_layout(
        shapes=shapes,
        annotations=annotations,
        xaxis=dict(
            tickvals=months,
            ticktext=month_names,
            title='Mois',
            type='category',
            range=[-0.5, 12]  
        ),
        yaxis=dict(
            title='Nombre de patients venus à IPM',
            range=[min_count - range_margin, max_count + range_margin]  
        ),
        title={
            'text': "Affluence des patients venus au CTAR IPM sur période saisonnière d'une année",
            'x': 0.5,
            'xanchor': 'center'
        },
        height=700,  
        width=7400,  
        legend_title='Légende'
    )

    fig.for_each_trace(lambda trace: trace.update(showlegend=False) if trace.name in season_backgrounds else None)


    st.plotly_chart(fig, use_container_width=True)

def plot_saison_peripheral(df):

    df['date_de_consultation']=pd.to_datetime(df['date_de_consultation'])

    df['season'] = df['date_de_consultation'].apply(get_season)
    df['mois'] = df['date_de_consultation'].dt.month
    df['Annee'] = df['date_de_consultation'].dt.year
    df=df[df['Annee']<=2024]

    monthly_sex_counts = df.groupby(['mois', 'Annee', 'sexe']).size().reset_index(name='count')

    months = list(range(1, 13)) 
    month_names = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
        'Sep', 'Oct', 'Nov', 'Dec'
    ]

    min_count = monthly_sex_counts['count'].min()
    max_count = monthly_sex_counts['count'].max()
    range_margin = (max_count - min_count) * 0.2  

    fig = go.Figure()

    male_colors = pc.sequential.Blues[::-1]  
    female_colors = pc.sequential.Reds[::-1]  

    years_sorted = sorted(monthly_sex_counts['Annee'].unique(), reverse=True)

    sexes = ['M', 'F']
    for i, year in enumerate(years_sorted):
        for j, sex in enumerate(sexes):
            df_year_sex = monthly_sex_counts[(monthly_sex_counts['Annee'] == year) & (monthly_sex_counts['sexe'] == sex)]
            df_year_sex = df_year_sex.set_index('mois').reindex(months).reset_index()
            df_year_sex['count'] = df_year_sex['count'].fillna(0)
            
            if sex == 'M':
                color = male_colors[i % len(male_colors)]
            else:
                color = female_colors[i % len(female_colors)]

            fig.add_trace(go.Scatter(
                x=df_year_sex['mois'],
                y=df_year_sex['count'],
                mode='lines+markers',
                name=f"{int(year)} - {'Homme' if sex == 'M' else 'Femme'}", 
                marker=dict(size=8, color=color), 
                line=dict(width=2),
                visible="legendonly" if year < 2021 else True  
            ))

    season_backgrounds = {
        'Fahavratra (pluie)': (12, 3, 'rgba(186, 225, 255, 0.3)', 'rgb(186, 225, 255)'),
        'Fararano (automne)': (3.5, 6, 'rgba(255, 186, 186, 0.3)', 'rgb(255, 186, 186)'),
        'Ritinina (hiver)': (6.5, 9, 'rgba(186, 255, 201, 0.3)', 'rgb(186, 255, 201)'),
        'Lohataona (été)': (9.5, 11.5, 'rgba(255, 223, 186, 0.3)', 'rgb(255, 223, 186)')
    }

    shapes = []
    annotations = []

    for season, (start_month, end_month, color, text_color) in season_backgrounds.items():
        if end_month < start_month:
            shapes.append(dict(
                type='rect',
                x0=start_month - 1,
                x1=11,  
                y0=min_count - range_margin,
                y1=max_count + range_margin,
                fillcolor=color,
                line=dict(width=0),
                layer='below'
            ))
            shapes.append(dict(
                type='rect',
                x0=1 - 1, 
                x1=end_month - 0.5,
                y0=min_count - range_margin,
                y1=max_count + range_margin,
                fillcolor=color,
                line=dict(width=0),
                layer='below'
            ))
        else:
            shapes.append(dict(
                type='rect',
                x0=start_month - 1,
                x1=end_month - 0.5,
                y0=min_count - range_margin,
                y1=max_count + range_margin,
                fillcolor=color,
                line=dict(width=0),
                layer='below'
            ))

        annotations.append(dict(
            x=(start_month) / 10 if end_month < start_month else (start_month + end_month - 1) / 2,
            y=min_count - range_margin,  
            text=season,
            showarrow=False,
            font=dict(size=15, color=text_color),
            xanchor="center",
            yanchor="bottom"
        ))

    fig.update_layout(
        shapes=shapes,
        annotations=annotations,
        xaxis=dict(
            tickvals=months,
            ticktext=month_names,
            title='Mois',
            type='category',
            range=[-0.5, 12]  
        ),
        yaxis=dict(
            title='Nombre de patients venus au CTAR',
            range=[min_count - range_margin, max_count + range_margin]  
        ),
        title={
            'text': "Affluence des patients venus au CTAR périphérique sur période saisonnière d'une année",
            'x': 0.5,
            'xanchor': 'center'
        },
        height=700, 
        width=7400,  
        legend_title='Légende'
    )

    fig.for_each_trace(lambda trace: trace.update(showlegend=False) if trace.name in season_backgrounds else None)


    st.plotly_chart(fig, use_container_width=True)

# Main
if 'dataframes' in st.session_state:
    dataframes = st.session_state['dataframes']

    selected_file = st.selectbox("Sélectionnez un fichier pour l'analyse", options=list(dataframes.keys()))

    if selected_file:
        df = dataframes[selected_file]

        # BDD CTAR IPM 
        if selected_file == "CTAR_ipmdata20022024_cleaned.csv":
            st.info("Cliquez sur agrandir l'image en haut à droite.")
            plot_saison_morsure_ipm(df)

        # BDD CTAR périphérique
        elif selected_file == "CTAR_peripheriquedata20022024_cleaned.csv":

            df = df.dropna(subset=['id_ctar'])

            # Liste des CTARs périphériques pour leur sélection
            unique_ctars = df['id_ctar'].unique()

            # Analyse de l'ensemble des CTAR périphériques
            all_ctars_selected = st.checkbox("Sélectionnez tous les CTARs")

            if not all_ctars_selected:
                selected_ctars = st.multiselect(
                    "Sélectionnez un ou plusieurs CTARs",
                    options=list(unique_ctars))
                if not selected_ctars:
                    st.warning("Veuillez sélectionner au moins un CTAR pour afficher l'analyse.")
                else:
                    df= df[df['id_ctar'].isin(selected_ctars)]
                    plot_saison_peripheral(df)
            elif all_ctars_selected:  
                plot_saison_peripheral(df)
           

else:
    st.error("Aucun fichier n'a été téléchargé. Veuillez retourner à la page d'accueil pour télécharger un fichier.")


# Sidebar de la page
with st.sidebar.container():
    st.image("Logo-CORAMAD.jpg", use_column_width=True, width=250, caption="FSPI Rage")