import pandas as pd
import plotly.express as px
import streamlit as st

def suggest_visualization(df):
    """
    Analyzes the dataframe and suggests a visualization type.
    Returns: 'bar', 'line', 'pie', or None
    """
    if df.empty:
        return None
        
    # Check for date columns
    date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
    # Check for numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    # Check for categorical columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    
    if len(date_cols) > 0 and len(numeric_cols) > 0:
        return 'line'
    elif len(categorical_cols) > 0 and len(numeric_cols) > 0:
        return 'bar'
    elif len(categorical_cols) > 0 and 'count' in df.columns.str.lower():
        return 'bar'
    
    return None

def visualize_query_results(df):
    """
    Generates a Plotly chart based on the dataframe structure.
    """
    if df.empty:
        st.warning("No data to visualize.")
        return

    viz_type = suggest_visualization(df)
    
    # Heuristics for column selection
    numeric_cols = df.select_dtypes(include=['number']).columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    date_cols = [col for col in df.columns if 'date' in col.lower()]
    
    chart = None
    
    try:
        if viz_type == 'line':
            # Use first date col and first numeric col
            x_col = date_cols[0]
            y_col = numeric_cols[0]
            # Group by date if there are duplicates
            if df[x_col].duplicated().any():
                df_grouped = df.groupby(x_col)[y_col].sum().reset_index()
                chart = px.line(df_grouped, x=x_col, y=y_col, title=f"Sum of {y_col} over Time")
            else:
                chart = px.line(df, x=x_col, y=y_col, title=f"{y_col} over Time")
                
        elif viz_type == 'bar':
            # Use first categorical and first numeric
            x_col = categorical_cols[0]
            y_col = numeric_cols[0] if len(numeric_cols) > 0 else None
            
            if y_col:
                chart = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
            else:
                # Count plot
                chart = px.histogram(df, x=x_col, title=f"Count of Records by {x_col}")
        
        else:
            # Fallback: if we have at least 2 numeric, scatter
            if len(numeric_cols) >= 2:
                chart = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title=f"{numeric_cols[0]} vs {numeric_cols[1]}")
    
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("Could not automatically generate a chart for this data.")
            
    except Exception as e:
        st.warning(f"Could not generate visualization: {e}")
