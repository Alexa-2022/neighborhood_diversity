# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col   
import requests 

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw: ")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")  # add this line
session = cnx.session ()  # session = get_active_session() / change this line

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

# Convert the Snowflake Dataframe to a Panda Dataframe so we can use the LOC func
pd_df=my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()

# Add a Multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:"
    , my_dataframe
    , max_selections = 5
)


# output the String
if ingredients_list:       
    ingredients_string = ''           #3 Create the INGREDIENTS_STRING Variable

    for fruit_chosen in ingredients_list:   #4 For Block to loop
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
      
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    #st.write(ingredients_string)   #5 should be part of the IF block but not part of the FOR Loop. 
    
    #9 Writing the NAME_ON_ORDER Entry to the Snowflake Table
    my_insert_stmt = """ insert into smoothies.public.orders   
                 (name_on_order, ingredients)   
                 values ('"""+name_on_order+ """','""" + ingredients_string + """')"""

    #st.write(my_insert_stmt)
    # st.stop()
    #7 Insert the Order into Snowflake
    # if ingredients_string:

    #8 Add a Submit Button
    time_to_insert = st.button('Sumbit Order')
    if time_to_insert:   
   
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")



 

