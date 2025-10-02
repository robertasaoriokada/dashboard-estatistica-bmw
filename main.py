import altair as alt
import streamlit as st
import pandas as pd
import copy
import json
import numpy as np

#alter the theme of the page into a dark theme
st.markdown("""
    <style>
    .reportview-container {
        background: #0E1117
    }
   .sidebar .sidebar-content {
        background: #0E1117
    }
    </style>
    """, unsafe_allow_html=True
)

df = pd.read_csv('dados/df.csv')
df_color = pd.read_csv('dados/df_color.csv')

st.set_page_config(
    page_title="BMW Estatísticas",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# alt.themes.enable("dark")

cols = st.columns(2)

model_unicos = df['Model'].unique()

def models_to_str(model):
    return ",".join(model_unicos)


if "model_input" not in st.session_state:
    st.session_state.model_input = st.query_params.get(
        "stocks", models_to_str(model_unicos)
    ).split(",")


#LEFT CELL:
top_left_cell = cols[0].container(
    border=True, height="stretch", vertical_alignment="center", width="stretch"
)


with top_left_cell:
    models = st.multiselect(
        "Modelos de carros da BMW",
        options=sorted(set(model_unicos) | set(st.session_state.model_input)),
        default=st.session_state.model_input,
        placeholder="Escolha um modelo para visualizar e comparar. Ex: X1",
        accept_new_options=True,
    )

df_region = pd.read_csv('dados/df_region.csv')
regions = np.sort(df_region["Region"].unique())

with top_left_cell:
    # Multi-select for picking multiple regions
    selected_regions = st.multiselect(
        "Regiões",
        options=regions,
        default=regions,
        placeholder="Escolha uma ou mais regiões para filtrar"
    )

df_transmission = pd.read_csv('dados/df_transmission.csv')
transmission_types = df_transmission['Transmission'].unique()
with top_left_cell:
    # Multi-select for picking multiple transmission types
    selected_transmissions = st.multiselect(
        "Tipo de Transmissão",
        options=transmission_types,
        default=transmission_types,
        placeholder="Escolha um ou mais tipos de transmissão"
    )


df_sales_classification = pd.read_csv('dados/df_sales_classification.csv')
sales_classifications = df_sales_classification['Sales_Classification'].unique()
with top_left_cell:
    # Multi-select for picking multiple sales classifications
    selected_sales_classifications = st.multiselect(
        "Classificação de Vendas",
        options=sales_classifications,
        default=sales_classifications,
        placeholder="Escolha uma ou mais classificações de vendas"
    )

    # Filtro de Anos com Slider de Intervalo
    years_available = sorted(df['Year'].unique())
    min_year, max_year = min(years_available), max(years_available)
    
    st.markdown("📅 **Período de Análise**")
    year_range = st.slider(
        "Selecione o intervalo de anos:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        help="Arraste para selecionar o período de análise"
    )
    selected_years = list(range(year_range[0], year_range[1] + 1))


#Right Cell
right_cell = cols[1].container(
    border=True, height="stretch", vertical_alignment="center"
)

def calcular_metricas(filtered_df, models, selected_regions, selected_transmissions, selected_sales_classifications):
       # Filter data for selected models
    filtered_df = df[df['Model'].isin(models)].copy()
        
        # If regions are selected, filter by regions
    if selected_regions:
        region_ids = df_region[df_region['Region'].isin(selected_regions)]['Id'].tolist()
        filtered_df = filtered_df[filtered_df['Region'].isin(region_ids)].copy()

    if selected_transmissions:
        transmission_ids = df_transmission[df_transmission['Transmission'].isin(selected_transmissions)]['Id'].tolist()
        filtered_df = filtered_df[filtered_df['Transmission'].isin(transmission_ids)].copy()

    if selected_sales_classifications:
        sales_classification_ids = df_sales_classification[df_sales_classification['Sales_Classification'].isin(selected_sales_classifications)]['Id'].tolist()
        filtered_df = filtered_df[filtered_df['Sales_Classification'].isin(sales_classification_ids)].copy()

    if selected_years:
        filtered_df = filtered_df[filtered_df['Year'].isin(selected_years)].copy()
    return filtered_df

with right_cell:
    if models:
        filtered_df = df[df['Model'].isin(models)].copy()
        # Filter data for selected models
        filtered_df = calcular_metricas(filtered_df, models, selected_regions, selected_transmissions, selected_sales_classifications)
        if not filtered_df.empty:
            # Group by Model and Year to get average price for better visualization
            price_comparison = filtered_df.groupby(['Model', 'Year'])['Price_USD'].mean().reset_index()
            
            # Create the chart
            chart = alt.Chart(price_comparison).mark_line(point=True).encode(
                x=alt.X('Year:O', title='Ano', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('Price_USD:Q', title='Preço Médio (USD)', scale=alt.Scale(zero=False)),
                color=alt.Color('Model:N', scale=alt.Scale(scheme='category10')),
                tooltip=['Model:N', 'Year:O', alt.Tooltip('Price_USD:Q', format='.0f', title='Preço (USD)')]
            ).properties(
                title=f'Comparação de Preços por Modelo ao Longo dos Anos',
                height=400,
                width='container'
            )
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("Nenhum dado encontrado para os modelos selecionados.")
    else:
        st.info("Selecione pelo menos um modelo para visualizar a comparação de preços.")

cols = st.columns(2)

with cols[0]:
    st.subheader("Volume de vendas ao ano por modelo")
    if models:
        filtered_df = df[df['Model'].isin(models)].copy()
        # Filter data for selected models
        filtered_df = calcular_metricas(filtered_df, models, selected_regions, selected_transmissions, selected_sales_classifications)
        if not filtered_df.empty:
            # Group by Model and Year to get total sales volume for better visualization
            sales_comparison = filtered_df.groupby(['Model', 'Year'])['Sales_Volume'].sum().reset_index()
         
            chart = alt.Chart(sales_comparison).mark_bar(point=True).encode(
                x=alt.X('Year:O', title='Ano', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('Sales_Volume:Q', title='Volume de Vendas', scale=alt.Scale(zero=False)),
                color=alt.Color('Model:N', scale=alt.Scale(scheme='category10')),
                tooltip=['Model:N', 'Year:O', alt.Tooltip('Sales_Volume:Q', format=',.0f', title='Volume de Vendas')]
            ).properties(
                title=f'Participação dos Modelos no Mercado ao Longo dos Anos',
                height=400,
                width='container'
            )
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("Nenhum dado encontrado para os modelos selecionados.")

with cols[1]:
    st.subheader("Variação anual do preço médio por modelo")
    if models:
        filtered_df = df[df['Model'].isin(models)].copy()
        # Filter data for selected models
        filtered_df = calcular_metricas(filtered_df, models, selected_regions, selected_transmissions, selected_sales_classifications)
        if not filtered_df.empty:
            # Use raw data for boxplot to show actual price distribution
            # Don't aggregate the data - boxplot needs individual data points
            
            chart = alt.Chart(filtered_df).mark_boxplot(size=50).encode(
                x=alt.X('Model:N', title='Modelo', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Price_USD:Q', title='Preço (USD)', scale=alt.Scale(zero=False)),
                color=alt.Color('Model:N', scale=alt.Scale(scheme='category10'), legend=None),
                tooltip=['Model:N', alt.Tooltip('Price_USD:Q', format=',.0f', title='Preço (USD)')]
            ).properties(
                title='Distribuição de Preços por Modelo (Boxplot)',
                height=400,
                width='container'
            )

            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("Nenhum dado encontrado para os modelos selecionados.")

cols = st.columns(4)

#Métricas principais em 4 colunas organizadas
modelo_de_maior_preco = cols[0].container(
    border=True, height="stretch", vertical_alignment="center"
)

modelo_de_menor_preco = cols[1].container(
    border=True, height="stretch", vertical_alignment="center"
)

modelo_de_maior_variancia_de_preco_por_ano = cols[2].container(
    border=True, height="stretch", vertical_alignment="center"
)

modelo_de_menor_variancia_de_preco_por_ano = cols[3].container(
    border=True, height="stretch", vertical_alignment="center"
)


# Adicionando uma nova linha para a métrica de participação de mercado
cols_segunda_linha = st.columns(4)
modelo_de_maior_participacao_de_mercado = cols_segunda_linha[0].container(
    border=True, height="stretch", vertical_alignment="center"
)

modelo_de_maior_faturamento = cols_segunda_linha[1].container(
    border=True, height="stretch", vertical_alignment="center"
)

ano_de_maior_faturamento = cols_segunda_linha[2].container(
    border=True, height="stretch", vertical_alignment="center"
)

ano_de_menor_faturamento = cols_segunda_linha[3].container(
    border=True, height="stretch", vertical_alignment="center"
)

cols_terceira_linha = st.columns(4)

modelo_de_menor_faturamento = cols_terceira_linha[0].container(
    border=True, height="stretch", vertical_alignment="center"
)


with modelo_de_maior_preco:
    if models:
        filtered_df = calcular_metricas(filtered_df, models, selected_regions, selected_transmissions, selected_sales_classifications)
        if not filtered_df.empty:
            # Calculate average price per model
            avg_price = filtered_df.groupby('Model')['Price_USD'].mean().reset_index()
            avg_price = avg_price.sort_values(by='Price_USD', ascending=False)
            top_model = avg_price.iloc[0]
            st.metric("🚗 Modelo de Maior Preço Médio", f"{top_model['Model']}", f"${top_model['Price_USD']:,.0f}"  )


with modelo_de_menor_preco:
    if models:
        filtered_df = calcular_metricas(filtered_df, models, selected_regions, selected_transmissions, selected_sales_classifications)
        if not filtered_df.empty:
            # Calculate average price per model
            avg_price = filtered_df.groupby('Model')['Price_USD'].mean().reset_index()
            avg_price = avg_price.sort_values(by='Price_USD', ascending=True)
            top_model = avg_price.iloc[0]
            st.metric("🚗 Modelo de Menor Preço Médio", f"{top_model['Model']}", f"${top_model['Price_USD']:,.0f}"  )


with modelo_de_maior_variancia_de_preco_por_ano:
    if models:
        filtered_df = calcular_metricas(filtered_df, models, selected_regions, selected_transmissions, selected_sales_classifications)
        if not filtered_df.empty:
            # Calculate price variance per model
            price_variance = filtered_df.groupby('Model')['Price_USD'].var().reset_index()
            price_variance = price_variance.sort_values(by='Price_USD', ascending=False)
            top_model = price_variance.iloc[0]
            st.metric("🚗 Modelo de Maior Variância de Preço", f"{top_model['Model']}", f"${top_model['Price_USD']:,.0f}"  )


with modelo_de_menor_variancia_de_preco_por_ano:
    if models:
        filtered_df = calcular_metricas(filtered_df, models, selected_regions, selected_transmissions, selected_sales_classifications)
        if not filtered_df.empty:
            # Calculate price variance per model
            price_variance = filtered_df.groupby('Model')['Price_USD'].var().reset_index()
            price_variance = price_variance.sort_values(by='Price_USD', ascending=True)
            top_model = price_variance.iloc[0]
            st.metric("🚗 Modelo de Menor Variância de Preço", f"{top_model['Model']}", f"${top_model['Price_USD']:,.0f}")

with modelo_de_maior_participacao_de_mercado:
    if models:
        filtered_df = calcular_metricas(filtered_df, models, selected_regions, selected_transmissions, selected_sales_classifications)
        if not filtered_df.empty:
            # Calculate market share per model
            total_sales = filtered_df['Sales_Volume'].sum()
            market_share = filtered_df.groupby('Model')['Sales_Volume'].sum().reset_index()
            market_share['Market_Share'] = (market_share['Sales_Volume'] / total_sales) * 100
            market_share = market_share.sort_values(by='Market_Share', ascending=False)
            top_model = market_share.iloc[0]
            st.metric("🚗 Modelo de Maior Participação de Mercado", f"{top_model['Model']}", f"{top_model['Market_Share']:.2f}%"
        )

with modelo_de_maior_faturamento:
    if models:
        filtered_df = calcular_metricas(filtered_df, models, selected_regions, selected_transmissions, selected_sales_classifications)
        if not filtered_df.empty:
            # Calculate total revenue per model
            filtered_df['Revenue'] = filtered_df['Price_USD'] * filtered_df['Sales_Volume']
            revenue = filtered_df.groupby('Model')['Revenue'].sum().reset_index()
            revenue = revenue.sort_values(by='Revenue', ascending=False)
            top_model = revenue.iloc[0]
            st.metric("🚗 Modelo de Maior Faturamentos De Acordo Com Os Filtros", f"{top_model['Model']}", f"${top_model['Revenue']:,.0f}"
        )
            
with modelo_de_menor_faturamento:
    if models:
        filtered_df = calcular_metricas(filtered_df, models, selected_regions, selected_transmissions, selected_sales_classifications)
        if not filtered_df.empty:
            # Calculate total revenue per model
            filtered_df['Revenue'] = filtered_df['Price_USD'] * filtered_df['Sales_Volume']
            revenue = filtered_df.groupby('Model')['Revenue'].sum().reset_index()
            revenue = revenue.sort_values(by='Revenue', ascending=True)
            top_model = revenue.iloc[0]
            st.metric("🚗 Modelo de Menor Faturamento De Acordo Com Os Filtros", f"{top_model['Model']}", f"${top_model['Revenue']:,.0f}"
        )

#Só muda de acordo com o ano que eu puxo
with ano_de_maior_faturamento:
    if models:
        filtered_df = calcular_metricas(filtered_df, models, selected_regions, selected_transmissions, selected_sales_classifications)
        if not filtered_df.empty:
            # Calculate revenue for this container
            filtered_df['Revenue'] = filtered_df['Price_USD'] * filtered_df['Sales_Volume']
            revenue_year = filtered_df.groupby('Year')['Revenue'].sum().reset_index()
            revenue_year = revenue_year.sort_values(by='Revenue', ascending=False)
            top_year = revenue_year.iloc[0]
            st.metric("📅 Ano de Maior Faturamento", f"{top_year['Year']}", f"${top_year['Revenue']:,.0f}"
        )
            

            
with ano_de_menor_faturamento:
    if models:
        filtered_df = calcular_metricas(filtered_df, models, selected_regions, selected_transmissions, selected_sales_classifications)
        if not filtered_df.empty:
            # Calculate total revenue per year
            filtered_df['Revenue'] = filtered_df['Price_USD'] * filtered_df['Sales_Volume']
            revenue_year = filtered_df.groupby('Year')['Revenue'].sum().reset_index()
            revenue_year = revenue_year.sort_values(by='Revenue', ascending=True)
            top_year = revenue_year.iloc[0]
            st.metric("📅 Ano de Menor Faturamento", f"{top_year['Year']}", f"${top_year['Revenue']:,.0f}"
        )

# Análise de Volume de Vendas por Região
st.subheader("📊 Volume de Vendas por Região")

if selected_years and models:
    # Filter data based on selections
    region_filtered_df = df[df['Model'].isin(models) & df['Year'].isin(selected_years)].copy()
    
    # If regions are selected, filter by regions
    if selected_regions:
        region_ids = df_region[df_region['Region'].isin(selected_regions)]['Id'].tolist()
        region_filtered_df = region_filtered_df[region_filtered_df['Region'].isin(region_ids)].copy()

    if selected_transmissions:
        transmission_ids = df_transmission[df_transmission['Transmission'].isin(selected_transmissions)]['Id'].tolist()
        region_filtered_df = region_filtered_df[region_filtered_df['Transmission'].isin(transmission_ids)].copy()
    
    if selected_sales_classifications:
        sales_classification_ids = df_sales_classification[df_sales_classification['Sales_Classification'].isin(selected_sales_classifications)]['Id'].tolist()
        region_filtered_df = region_filtered_df[region_filtered_df['Sales_Classification'].isin(sales_classification_ids)].copy()

    if not region_filtered_df.empty:
        # Merge with region names
        region_data = region_filtered_df.merge(df_region, left_on='Region', right_on='Id', how='left')
        
        # Calculate metrics by region
        region_metrics = region_data.groupby('Region_y').agg({
            'Sales_Volume': 'sum',
            'Price_USD': 'mean'
        }).reset_index()
        region_metrics.columns = ['Região', 'Volume_Total', 'Preço_Médio']
        region_metrics = region_metrics.sort_values('Volume_Total', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart for volume by region
            volume_chart = alt.Chart(region_metrics).mark_bar().encode(
                x=alt.X('Volume_Total:Q', title='Volume de Vendas'),
                y=alt.Y('Região:N', sort='-x', title='Região'),
                color=alt.Color('Volume_Total:Q', scale=alt.Scale(scheme='blues'), legend=None),
                tooltip=['Região:N', alt.Tooltip('Volume_Total:Q', format=',.0f', title='Volume Total')]
            ).properties(
                title='Volume de Vendas por Região',
                height=300
            )
            st.altair_chart(volume_chart, use_container_width=True)
        
        with col2:
            # Metrics table
            st.write("**Resumo por Região:**")
            region_metrics['Volume_Total'] = region_metrics['Volume_Total'].apply(lambda x: f"{x:,}")
            region_metrics['Preço_Médio'] = region_metrics['Preço_Médio'].apply(lambda x: f"${x:,.0f}")
            region_metrics.columns = ['Região', 'Volume Total', 'Preço Médio']
            st.dataframe(region_metrics, hide_index=True)
    else:
        st.warning("Nenhum dado encontrado para os modelos e anos selecionados.")
elif not selected_years:
    st.info("Selecione pelo menos um ano para visualizar a análise por região.")
else:
    st.info("Selecione pelo menos um modelo para visualizar a análise por região.")

# ===== INSIGHTS ESTRATÉGICOS REGIONAIS =====
st.markdown("---")
st.subheader("🎯 Insights Estratégicos Regionais")

if selected_years and models:
    # Use the same filtered data from above
    region_filtered_df = df[df['Model'].isin(models) & df['Year'].isin(selected_years)].copy()
    
    if selected_regions:
        region_ids = df_region[df_region['Region'].isin(selected_regions)]['Id'].tolist()
        region_filtered_df = region_filtered_df[region_filtered_df['Region'].isin(region_ids)].copy()

    if selected_transmissions:
        transmission_ids = df_transmission[df_transmission['Transmission'].isin(selected_transmissions)]['Id'].tolist()
        region_filtered_df = region_filtered_df[region_filtered_df['Transmission'].isin(transmission_ids)].copy()
    
    if selected_sales_classifications:
        sales_classification_ids = df_sales_classification[df_sales_classification['Sales_Classification'].isin(selected_sales_classifications)]['Id'].tolist()
        region_filtered_df = region_filtered_df[region_filtered_df['Sales_Classification'].isin(sales_classification_ids)].copy()

    if not region_filtered_df.empty:
        # Merge with region names for analysis
        regional_analysis = region_filtered_df.merge(df_region, left_on='Region', right_on='Id', how='left')
        
        # Calculate comprehensive regional metrics
        regional_summary = regional_analysis.groupby('Region_y').agg({
            'Sales_Volume': ['sum', 'mean'],
            'Price_USD': ['mean', 'std'],
            'Model': 'nunique'
        }).round(2)
        
        regional_summary.columns = ['Volume_Total', 'Volume_Médio', 'Preço_Médio', 'Desvio_Preço', 'Qtd_Modelos']
        regional_summary = regional_summary.reset_index()
        regional_summary['Market_Share_%'] = (regional_summary['Volume_Total'] / regional_summary['Volume_Total'].sum() * 100).round(1)
        
        # Key regional insights
        top_region = regional_summary.loc[regional_summary['Volume_Total'].idxmax()]
        most_expensive_region = regional_summary.loc[regional_summary['Preço_Médio'].idxmax()]
        most_diverse_region = regional_summary.loc[regional_summary['Qtd_Modelos'].idxmax()]
        
        insight_cols = st.columns(3)
        
        with insight_cols[0]:
            st.success(f"""
            **🏆 Região Líder em Volume:**
            - **{top_region['Region_y']}**
            - Volume: **{top_region['Volume_Total']:,.0f}** unidades
            - Participação: **{top_region['Market_Share_%']:.1f}%**
            - Oportunidade de expansão
            """)
        
        with insight_cols[1]:
            st.info(f"""
            **💰 Região Premium:**
            - **{most_expensive_region['Region_y']}**
            - Preço médio: **${most_expensive_region['Preço_Médio']:,.0f}**
            - Mercado de alto valor
            - Potencial para modelos premium
            """)
        
        with insight_cols[2]:
            st.warning(f"""
            **🌟 Região Mais Diversificada:**
            - **{most_diverse_region['Region_y']}**
            - Modelos ativos: **{most_diverse_region['Qtd_Modelos']:.0f}**
            - Mercado maduro e receptivo
            - Base para novos lançamentos
            """)
        
        # Market concentration analysis
        st.subheader("📊 Análise de Concentração de Mercado")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Market share pie chart
            market_share_chart = alt.Chart(regional_summary).mark_arc(innerRadius=50).encode(
                theta=alt.Theta('Volume_Total:Q'),
                color=alt.Color('Region_y:N', scale=alt.Scale(scheme='category10'), title='Região'),
                tooltip=['Region_y:N', 
                        alt.Tooltip('Volume_Total:Q', format=',.0f', title='Volume'),
                        alt.Tooltip('Market_Share_%:Q', format='.1f', title='Participação (%)')]
            ).properties(
                title='Distribuição de Market Share por Região',
                height=300
            )
            st.altair_chart(market_share_chart, use_container_width=True)
        
        with col2:
            # Price vs Volume scatter
            bubble_chart = alt.Chart(regional_summary).mark_circle(opacity=0.7).encode(
                x=alt.X('Preço_Médio:Q', title='Preço Médio (USD)'),
                y=alt.Y('Volume_Total:Q', title='Volume Total'),
                size=alt.Size('Market_Share_%:Q', scale=alt.Scale(range=[100, 800]), title='Market Share (%)'),
                color=alt.Color('Region_y:N', scale=alt.Scale(scheme='category10'), title='Região'),
                tooltip=['Region_y:N', 
                        alt.Tooltip('Preço_Médio:Q', format=',.0f', title='Preço Médio'),
                        alt.Tooltip('Volume_Total:Q', format=',.0f', title='Volume'),
                        alt.Tooltip('Market_Share_%:Q', format='.1f', title='Market Share (%)')]
            ).properties(
                title='Preço vs Volume por Região',
                height=300
            )
            st.altair_chart(bubble_chart, use_container_width=True)

# ===== ANÁLISE COMPLETA DE CORRELAÇÕES ENTRE VARIÁVEIS =====
st.markdown("---")
st.subheader("📊 Análise Completa de Correlações entre Variáveis")

if models:
    # Filter data for correlation analysis
    correlation_df = df[df['Model'].isin(models)].copy()
    
    if selected_regions:
        region_ids = df_region[df_region['Region'].isin(selected_regions)]['Id'].tolist()
        correlation_df = correlation_df[correlation_df['Region'].isin(region_ids)].copy()
    
    if selected_transmissions:
        transmission_ids = df_transmission[df_transmission['Transmission'].isin(selected_transmissions)]['Id'].tolist()
        correlation_df = correlation_df[correlation_df['Transmission'].isin(transmission_ids)].copy()
    
    if selected_sales_classifications:
        sales_classification_ids = df_sales_classification[df_sales_classification['Sales_Classification'].isin(selected_sales_classifications)]['Id'].tolist()
        correlation_df = correlation_df[correlation_df['Sales_Classification'].isin(sales_classification_ids)].copy()
    
    if selected_years:
        correlation_df = correlation_df[correlation_df['Year'].isin(selected_years)].copy()

    if not correlation_df.empty and len(correlation_df) > 2:
        # Select numerical variables for correlation analysis
        numeric_vars = ['Price_USD', 'Sales_Volume', 'Engine_Size_L', 'Mileage_KM', 'Year']
        corr_data = correlation_df[numeric_vars].copy()
        
        # Calculate correlation matrix
        correlation_matrix = corr_data.corr()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📈 Matriz de Correlação - Heatmap**")
            
            # Prepare data for heatmap
            corr_melted = correlation_matrix.reset_index().melt('index')
            corr_melted.columns = ['Variable_1', 'Variable_2', 'Correlation']
            
            # Create heatmap
            heatmap = alt.Chart(corr_melted).mark_rect().encode(
                x=alt.X('Variable_1:O', title='Variáveis'),
                y=alt.Y('Variable_2:O', title='Variáveis'),
                color=alt.Color('Correlation:Q', 
                              scale=alt.Scale(scheme='redblue', domain=[-1, 1]),
                              title='Correlação'),
                tooltip=['Variable_1:O', 'Variable_2:O', 'Correlation:Q']
            ).properties(
                title='Matriz de Correlação entre Variáveis',
                width=350,
                height=350
            )
            
            # Add text labels
            text = alt.Chart(corr_melted).mark_text(baseline='middle', fontSize=10).encode(
                x=alt.X('Variable_1:O'),
                y=alt.Y('Variable_2:O'),
                text=alt.Text('Correlation:Q', format='.2f'),
                color=alt.condition(alt.datum.Correlation > 0.5, alt.value('white'), alt.value('black'))
            )
            
            st.altair_chart(heatmap + text, use_container_width=True)
        
        with col2:
            st.write("**🔍 Correlações Significativas (|r| ≥ 0.3)**")
            
            # Find strong correlations
            strong_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    var1 = correlation_matrix.columns[i]
                    var2 = correlation_matrix.columns[j]
                    corr_value = correlation_matrix.iloc[i, j]
                    
                    if abs(corr_value) >= 0.3:
                        strong_correlations.append({
                            'Variável 1': var1.replace('_', ' '),
                            'Variável 2': var2.replace('_', ' '),
                            'Correlação': corr_value,
                            'Força': 'Forte' if abs(corr_value) >= 0.7 else 'Moderada',
                            'Direção': 'Positiva' if corr_value > 0 else 'Negativa'
                        })
            
            if strong_correlations:
                corr_df = pd.DataFrame(strong_correlations)
                corr_df = corr_df.sort_values('Correlação', key=abs, ascending=False)
                
                # Format for display
                display_corr = corr_df.copy()
                display_corr['Correlação'] = display_corr['Correlação'].apply(lambda x: f"{x:.3f}")
                
                st.dataframe(display_corr, width='stretch')
                
                # Business insights
                st.write("**💡 Insights de Negócio:**")
                
                for _, row in corr_df.iterrows():
                    var1 = row['Variável 1']
                    var2 = row['Variável 2']
                    corr = row['Correlação']
                    
                    if 'Price' in var1 or 'Price' in var2:
                        if 'Engine' in var1 or 'Engine' in var2:
                            if corr > 0:
                                st.info(f"💰 **Preço vs Tamanho Motor:** Motores maiores = preços mais altos ({corr:.3f})")
                        elif 'Sales' in var1 or 'Sales' in var2:
                            if corr < 0:
                                st.warning(f"📉 **Preço vs Vendas:** Preços altos reduzem volume de vendas ({corr:.3f})")
                            else:
                                st.success(f"📈 **Preço vs Vendas:** Preços premium impulsionam vendas ({corr:.3f})")
                        elif 'Mileage' in var1 or 'Mileage' in var2:
                            if corr < 0:
                                st.info(f"🚗 **Preço vs Quilometragem:** Maior uso reduz valor de revenda ({corr:.3f})")
                    
                    elif 'Engine' in var1 or 'Engine' in var2:
                        if 'Sales' in var1 or 'Sales' in var2:
                            if corr > 0:
                                st.success(f"🔧 **Motor vs Vendas:** Motores potentes vendem mais ({corr:.3f})")
                            else:
                                st.warning(f"⚡ **Motor vs Vendas:** Preferência por motores menores ({corr:.3f})")
                
                # Summary statistics
                st.write("**📊 Resumo Estatístico:**")
                avg_corr = np.mean([abs(c['Correlação']) for c in strong_correlations])
                max_corr = max([abs(c['Correlação']) for c in strong_correlations])
                
                st.metric("Correlação Média", f"{avg_corr:.3f}")
                st.metric("Correlação Máxima", f"{max_corr:.3f}")
                
            else:
                st.info("Nenhuma correlação significativa encontrada (|r| ≥ 0.3)")
                
    else:
        st.warning("Dados insuficientes para análise de correlação completa.")
else:
    st.info("Selecione pelo menos um modelo para análise de correlação.")


# Load fuel type data
df_fuel_types = pd.read_csv('dados/df_fuel_type.csv')
fuel_types_unicos = df_fuel_types['Fuel_Type'].unique()

cols = st.columns(2)

# 🔋 COMPREHENSIVE FUEL TYPE ANALYSIS - CLIENT WOW SECTION
st.markdown("---")
st.header("🔋 Análise Estratégica: Evolução dos Combustíveis BMW")

# Load fuel type data
df_fuel_type = pd.read_csv('dados/df_fuel_type.csv')

# Create comprehensive analysis with applied filters
analysis_df = df.copy()

# Apply all selected filters to the analysis
if models:
    analysis_df = analysis_df[analysis_df['Model'].isin(models)].copy()
if selected_regions:
    region_ids = df_region[df_region['Region'].isin(selected_regions)]['Id'].tolist()
    analysis_df = analysis_df[analysis_df['Region'].isin(region_ids)].copy()
if selected_transmissions:
    transmission_ids = df_transmission[df_transmission['Transmission'].isin(selected_transmissions)]['Id'].tolist()
    analysis_df = analysis_df[analysis_df['Transmission'].isin(transmission_ids)].copy()
if selected_sales_classifications:
    sales_classification_ids = df_sales_classification[df_sales_classification['Sales_Classification'].isin(selected_sales_classifications)]['Id'].tolist()
    analysis_df = analysis_df[analysis_df['Sales_Classification'].isin(sales_classification_ids)].copy()
if selected_years:
    analysis_df = analysis_df[analysis_df['Year'].isin(selected_years)].copy()


# Merge with fuel type names
fuel_analysis = analysis_df.merge(df_fuel_type, left_on='Fuel_Type', right_on='Id', how='left')

if not fuel_analysis.empty:
    # Key Metrics Row
    st.subheader("📊 Métricas Principais por Tipo de Combustível")
    
    # Calculate key metrics
    fuel_metrics = fuel_analysis.groupby('Fuel_Type_y').agg({
        'Sales_Volume': 'sum',
        'Price_USD': 'mean',
        'Year': 'nunique'
    }).round(0).reset_index()
    fuel_metrics.columns = ['Tipo_Combustível', 'Volume_Total', 'Preço_Médio', 'Anos_Presentes']
    
    # Display metrics in columns
    metric_cols = st.columns(len(fuel_metrics))
    for i, (_, row) in enumerate(fuel_metrics.iterrows()):
        with metric_cols[i]:
            st.metric(
                label=f"🚗 {row['Tipo_Combustível']}", 
                value=f"{row['Volume_Total']:,.0f}",
                delta=f"${row['Preço_Médio']:,.0f} médio"
            )
    
    # Main Analysis Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Evolução do Volume de Vendas")
        
        # Sales volume evolution
        sales_evolution = fuel_analysis.groupby(['Year', 'Fuel_Type_y'])['Sales_Volume'].sum().reset_index()
        
        sales_chart = alt.Chart(sales_evolution).mark_line(point=True, strokeWidth=3).encode(
            x=alt.X('Year:O', title='Ano'),
            y=alt.Y('Sales_Volume:Q', title='Volume de Vendas'),
            color=alt.Color('Fuel_Type_y:N', 
                          title='Tipo de Combustível',
                          scale=alt.Scale(scheme='category10')),
            tooltip=['Year:O', 'Fuel_Type_y:N', alt.Tooltip('Sales_Volume:Q', format=',.0f', title='Volume')]
        ).properties(
            title='Tendências de Vendas por Combustível',
            height=350
        )
        
        st.altair_chart(sales_chart, use_container_width=True)
        
        # Market share analysis
        st.subheader("🥧 Participação de Mercado")
        
        # Calculate market share by fuel type
        market_share = fuel_analysis.groupby('Fuel_Type_y')['Sales_Volume'].sum().reset_index()
        market_share['Percentage'] = (market_share['Sales_Volume'] / market_share['Sales_Volume'].sum() * 100).round(1)
        
        pie_chart = alt.Chart(market_share).mark_arc(innerRadius=50).encode(
            theta=alt.Theta('Sales_Volume:Q'),
            color=alt.Color('Fuel_Type_y:N', 
                          title='Tipo de Combustível',
                          scale=alt.Scale(scheme='category10')),
            tooltip=['Fuel_Type_y:N', 
                    alt.Tooltip('Sales_Volume:Q', format=',.0f', title='Volume'),
                    alt.Tooltip('Percentage:Q', format='.1f', title='Participação (%)')]
        ).properties(
            title='Distribuição do Volume de Vendas por Combustível',
            height=300
        )
        
        st.altair_chart(pie_chart, use_container_width=True)
    
    with col2:
        st.subheader("💰 Evolução dos Preços Médios")
        
        # Price evolution
        price_evolution = fuel_analysis.groupby(['Year', 'Fuel_Type_y'])['Price_USD'].mean().reset_index()
        
        price_chart = alt.Chart(price_evolution).mark_line(point=True, strokeWidth=3).encode(
            x=alt.X('Year:O', title='Ano'),
            y=alt.Y('Price_USD:Q', title='Preço Médio (USD)', scale=alt.Scale(zero=False)),
            color=alt.Color('Fuel_Type_y:N', 
                          title='Tipo de Combustível',
                          scale=alt.Scale(scheme='category10')),
            tooltip=['Year:O', 'Fuel_Type_y:N', alt.Tooltip('Price_USD:Q', format=',.0f', title='Preço')]
        ).properties(
            title='Evolução de Preços por Combustível',
            height=350
        )
        
        st.altair_chart(price_chart, use_container_width=True)
        
        # Price vs Volume correlation
        st.subheader("📊 Preço vs Volume (Elasticidade)")
        
        # Aggregate data for correlation
        correlation_data = fuel_analysis.groupby(['Year', 'Fuel_Type_y']).agg({
            'Price_USD': 'mean',
            'Sales_Volume': 'sum'
        }).reset_index()
        
        scatter_chart = alt.Chart(correlation_data).mark_circle(size=100, opacity=0.7).encode(
            x=alt.X('Price_USD:Q', title='Preço Médio (USD)'),
            y=alt.Y('Sales_Volume:Q', title='Volume de Vendas'),
            color=alt.Color('Fuel_Type_y:N', 
                          title='Tipo de Combustível',
                          scale=alt.Scale(scheme='category10')),
            size=alt.value(150),
            tooltip=['Year:O', 'Fuel_Type_y:N', 
                    alt.Tooltip('Price_USD:Q', format=',.0f', title='Preço'),
                    alt.Tooltip('Sales_Volume:Q', format=',.0f', title='Volume')]
        ).properties(
            title='Relação Preço-Volume por Combustível',
            height=300
        )
        
        st.altair_chart(scatter_chart, use_container_width=True)
    
    # Strategic Insights Section
    st.markdown("---")
    st.subheader("🎯 Insights Estratégicos")
    
    # Calculate insights
    latest_year = fuel_analysis['Year'].max()
    previous_year = latest_year - 1
    
    latest_data = fuel_analysis[fuel_analysis['Year'] == latest_year].groupby('Fuel_Type_y').agg({
        'Sales_Volume': 'sum',
        'Price_USD': 'mean'
    })
    
    previous_data = fuel_analysis[fuel_analysis['Year'] == previous_year].groupby('Fuel_Type_y').agg({
        'Sales_Volume': 'sum', 
        'Price_USD': 'mean'
    })
    
    # Growth analysis
    if not previous_data.empty and not latest_data.empty:
        growth_analysis = ((latest_data - previous_data) / previous_data * 100).round(1)
    else:
        growth_analysis = pd.DataFrame()
    
    insight_cols = st.columns(3)
    
    with insight_cols[0]:
        st.info("📊 **Tendência de Mercado**\n\n" + 
                f"• Maior volume: **{market_share.loc[market_share['Sales_Volume'].idxmax(), 'Fuel_Type_y']}**\n" +
                f"• Participação: **{market_share['Percentage'].max():.1f}%**\n" +
                f"• Crescimento sustentável identificado")
    
    with insight_cols[1]:
        if not growth_analysis.empty and 'Sales_Volume' in growth_analysis.columns and len(growth_analysis) > 0:
            fastest_growing = growth_analysis['Sales_Volume'].idxmax()
            growth_rate = growth_analysis.loc[fastest_growing, 'Sales_Volume']
            st.success(f"🚀 **Crescimento Acelerado**\n\n" + 
                      f"• **{fastest_growing}** lidera crescimento\n" +
                      f"• Taxa: **{growth_rate:+.1f}%** vs ano anterior\n" +
                      f"• Oportunidade estratégica")
        else:
            st.info("🚀 **Crescimento Acelerado**\n\n• Dados insuficientes para análise\n• Expandir período de análise")
    
    with insight_cols[2]:
        avg_price = fuel_analysis['Price_USD'].mean()
        premium_fuels = fuel_analysis[fuel_analysis['Price_USD'] > avg_price]['Fuel_Type_y'].unique()
        st.warning("💎 **Segmento Premium**\n\n" + 
                  f"• Preço médio: **${avg_price:,.0f}**\n" +
                  f"• Combustíveis premium: **{len(premium_fuels)}**\n" +
                  f"• Potencial de margem alta")

else:
    st.warning("⚠️ Nenhum dado disponível para a análise de combustível com os filtros selecionados.")

# ===== ANÁLISE DETALHADA POR COR DE CARRO =====
st.markdown("---")
st.header("🎨 Análise Detalhada: Cores dos Veículos BMW")

# Create comprehensive analysis with applied filters
if models:
    color_filtered_df = df[df['Model'].isin(models)].copy()
    
    # Apply all filters
    if selected_regions:
        region_ids = df_region[df_region['Region'].isin(selected_regions)]['Id'].tolist()
        color_filtered_df = color_filtered_df[color_filtered_df['Region'].isin(region_ids)].copy()
    
    if selected_transmissions:
        transmission_ids = df_transmission[df_transmission['Transmission'].isin(selected_transmissions)]['Id'].tolist()
        color_filtered_df = color_filtered_df[color_filtered_df['Transmission'].isin(transmission_ids)].copy()
    
    if selected_sales_classifications:
        sales_classification_ids = df_sales_classification[df_sales_classification['Sales_Classification'].isin(selected_sales_classifications)]['Id'].tolist()
        color_filtered_df = color_filtered_df[color_filtered_df['Sales_Classification'].isin(sales_classification_ids)].copy()
    
    if selected_years:
        color_filtered_df = color_filtered_df[color_filtered_df['Year'].isin(selected_years)].copy()
    
    # Merge with color data
    color_analysis = color_filtered_df.merge(df_color, left_on='Color', right_on='Id', how='left')
    
    if not color_analysis.empty:
        # Calculate comprehensive color metrics
        color_metrics = color_analysis.groupby('Color_y').agg({
            'Sales_Volume': ['sum', 'count'],
            'Price_USD': ['mean', 'min', 'max']
        }).round(2)
        
        # Flatten column names
        color_metrics.columns = ['Volume_Total', 'Qtd_Vendas', 'Preço_Médio', 'Preço_Min', 'Preço_Max']
        color_metrics = color_metrics.reset_index()
        color_metrics['Participação_%'] = (color_metrics['Volume_Total'] / color_metrics['Volume_Total'].sum() * 100).round(1)
        
        # Calculate revenue
        color_analysis['Revenue'] = color_analysis['Price_USD'] * color_analysis['Sales_Volume']
        color_revenue = color_analysis.groupby('Color_y')['Revenue'].sum().reset_index()
        color_metrics = color_metrics.merge(color_revenue, left_on='Color_y', right_on='Color_y', how='left')
        
        # Sort by volume
        color_metrics = color_metrics.sort_values('Volume_Total', ascending=False)
        
        # Key insights section
        st.subheader("🏆 Insights Principais - Cores")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Most sold color
        top_color = color_metrics.iloc[0]
        with col1:
            st.metric(
                "🥇 Cor Mais Vendida",
                top_color['Color_y'],
                f"{top_color['Volume_Total']:,.0f} unidades"
            )
        
        # Highest revenue color
        highest_revenue_color = color_metrics.loc[color_metrics['Revenue'].idxmax()]
        with col2:
            st.metric(
                "💰 Maior Faturamento",
                highest_revenue_color['Color_y'],
                f"${highest_revenue_color['Revenue']:,.0f}"
            )
        
        # Most expensive color on average
        most_expensive_color = color_metrics.loc[color_metrics['Preço_Médio'].idxmax()]
        with col3:
            st.metric(
                "💎 Cor Premium",
                most_expensive_color['Color_y'],
                f"${most_expensive_color['Preço_Médio']:,.0f} médio"
            )
        
        # Market leader percentage
        leader_percentage = top_color['Participação_%']
        with col4:
            st.metric(
                "📊 Dominância de Mercado",
                f"{leader_percentage:.1f}%",
                f"Liderança: {top_color['Color_y']}"
            )
        
        # Detailed analysis charts
        st.subheader("📈 Análise Comparativa por Cor")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Volume comparison chart
            volume_chart = alt.Chart(color_metrics).mark_bar().encode(
                x=alt.X('Volume_Total:Q', title='Volume Total de Vendas'),
                y=alt.Y('Color_y:N', sort='-x', title='Cor'),
                color=alt.Color('Color_y:N', scale=alt.Scale(scheme='set1'), legend=None),
                tooltip=[
                    'Color_y:N',
                    alt.Tooltip('Volume_Total:Q', format=',.0f', title='Volume'),
                    alt.Tooltip('Participação_%:Q', format='.1f', title='Participação (%)')
                ]
            ).properties(
                title='Volume de Vendas por Cor',
                height=300
            )
            st.altair_chart(volume_chart, use_container_width=True)
        
        with col2:
            # Price comparison chart
            price_chart = alt.Chart(color_metrics).mark_bar().encode(
                x=alt.X('Preço_Médio:Q', title='Preço Médio (USD)'),
                y=alt.Y('Color_y:N', sort='-x', title='Cor'),
                color=alt.Color('Color_y:N', scale=alt.Scale(scheme='set1'), legend=None),
                tooltip=[
                    'Color_y:N',
                    alt.Tooltip('Preço_Médio:Q', format=',.0f', title='Preço Médio'),
                    alt.Tooltip('Preço_Min:Q', format=',.0f', title='Preço Mín'),
                    alt.Tooltip('Preço_Max:Q', format=',.0f', title='Preço Máx')
                ]
            ).properties(
                title='Preço Médio por Cor',
                height=300
            )
            st.altair_chart(price_chart, use_container_width=True)
        
        # Detailed table
        st.subheader("📋 Tabela Detalhada por Cor")
        
        # Format table for display
        display_color_metrics = color_metrics.copy()
        display_color_metrics['Volume_Total'] = display_color_metrics['Volume_Total'].apply(lambda x: f"{x:,.0f}")
        display_color_metrics['Preço_Médio'] = display_color_metrics['Preço_Médio'].apply(lambda x: f"${x:,.0f}")
        display_color_metrics['Preço_Min'] = display_color_metrics['Preço_Min'].apply(lambda x: f"${x:,.0f}")
        display_color_metrics['Preço_Max'] = display_color_metrics['Preço_Max'].apply(lambda x: f"${x:,.0f}")
        display_color_metrics['Revenue'] = display_color_metrics['Revenue'].apply(lambda x: f"${x:,.0f}")
        
        display_color_metrics.columns = [
            'Cor', 'Volume Total', 'Qtd Vendas', 'Preço Médio', 
            'Preço Mín', 'Preço Máx', 'Participação %', 'Faturamento'
        ]
        
        st.dataframe(display_color_metrics, width='stretch')
        
        # Business insights
        st.subheader("💡 Insights de Negócio")
        
        # Calculate additional insights
        total_colors = len(color_metrics)
        top_3_colors = color_metrics.head(3)
        top_3_share = top_3_colors['Participação_%'].sum()
        
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            st.info(f"""
            **📊 Concentração de Mercado:**
            - Total de cores disponíveis: **{total_colors}**
            - Top 3 cores representam: **{top_3_share:.1f}%** do mercado
            - Cor líder ({top_color['Color_y']}) domina **{leader_percentage:.1f}%**
            """)
            
            # Price range analysis
            price_range = most_expensive_color['Preço_Médio'] - color_metrics['Preço_Médio'].min()
            st.success(f"""
            **💰 Estratégia de Preços:**
            - Diferença de preço entre cores: **${price_range:,.0f}**
            - Cor premium: **{most_expensive_color['Color_y']}**
            - Oportunidade de segmentação por cor
            """)
        
        with insight_col2:
            # Volume vs Price correlation
            volume_leader = top_color['Color_y']
            price_leader = most_expensive_color['Color_y']
            
            if volume_leader == price_leader:
                correlation_insight = f"**{volume_leader}** lidera tanto em volume quanto em preço - cor premium dominante"
            else:
                correlation_insight = f"Mercado segmentado: **{volume_leader}** (volume) vs **{price_leader}** (premium)"
            
            st.warning(f"""
            **🎯 Posicionamento Estratégico:**
            - {correlation_insight}
            - Diversificação de portfólio por cor
            - Potencial de crescimento em cores premium
            """)
            
            # Recommendation
            least_sold_color = color_metrics.iloc[-1]['Color_y']
            st.error(f"""
            **⚠️ Atenção Estratégica:**
            - Cor com menor performance: **{least_sold_color}**
            - Revisar estratégia de marketing
            - Considerar descontinuação ou promoção
            """)
    
    else:
        st.warning("⚠️ Nenhum dado de cor disponível com os filtros selecionados.")
else:
    st.info("👈 Selecione pelo menos um modelo na sidebar para visualizar a análise de cores.")