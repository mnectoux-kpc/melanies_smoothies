# Import python packages.
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Write directly to the app.
st.title(f":cup_with_straw: Customize your Smoothie :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order = st.text_input('Name on your Smoothie')
st.write('The name on your smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

# MODIFICATION 1 : On sélectionne toutes les colonnes pour avoir SEARCH_ON
my_dataframe = session.table("smoothies.public.fruit_options")

# MODIFICATION 2 : On convertit le dataframe Snowflake en DataFrame Pandas
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect (
    'Choose up to 5 ingredients:'
    , my_dataframe # Conserve my_dataframe ici pour l'affichage de la liste
    , max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # MODIFICATION 3 : Récupération de la valeur technique de recherche avec Pandas
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        
        # MODIFICATION 4 : On utilise maintenant "search_on" à la place de "fruit_chosen" dans l'URL
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                    values ('""" + ingredients_string + """','"""+name_on_order+"""')"""

    st.write(my_insert_stmt)
    
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")