# Importing required libraries
import pandas as pd
import re
from ml_pipeline.preprocessing import get_target_customers

def extract_features(df):

# calculating number of days active
    temp_days_active = df.groupby('User_id').agg({'Date': 'nunique'}).reset_index()
    temp_days_active.rename(columns={'Date':'no_of_days_active'},inplace=True)

    # Function to calculate purchase time difference 
    def purch_time_diff(x):
        if len(x) == 2:
            return (x[1]-x[0]).days

        if len(x) == 3:
            diff_12 = (x[1]-x[0]).days
            diff_23 = (x[2]-x[1]).days
            return (diff_12+diff_23)/2

# calculating average time between purchase
    temp = df.copy()
    temp_user_purchase_date = (temp[temp['Action']=='purchase'].sort_values(by='Date')
                            .groupby('User_id').agg({'Date': lambda x: list(x)}).reset_index())
    temp_user_purchase_date['purchase1'] = temp_user_purchase_date['Date'].apply(lambda x: x[0])
    temp_user_purchase_date['purchase2'] = temp_user_purchase_date['Date'].apply(lambda x: x[1] if len(x)>1 else 0)
    temp_user_purchase_date['purchase3'] = temp_user_purchase_date['Date'].apply(lambda x: x[2] if len(x)>2 else 0)
    temp_user_purchase_date['avg_time_between_purchase'] = temp_user_purchase_date['Date'].apply(purch_time_diff)

    # Function to calculate purchase ratios
    def purchase_ratios(data, action_col='add_to_cart',id_col='User_id', col_name='no_of_carts'):
        # Number of actions for each user
        test1 = (data[data['Action']==action_col]
                            .groupby(id_col).agg({'Session_id':'count'}).reset_index())
        test1.rename(columns={'Session_id': col_name},inplace=True)
        
        # Number of purchases for each user
        test2 = data[data['Action']=='purchase'].groupby(id_col).agg({'Session_id':'count'}).reset_index()
        test2.rename(columns={'Session_id':'no_of_purch'},inplace=True)
    
        test_ratio = pd.merge(test1,test2,on=id_col, how='left')
        test_ratio = test_ratio.fillna(0)
        test_ratio[col_name+'_to_purchase_ratio'] = (test_ratio['no_of_purch']
                                                        /test_ratio[col_name])
        return test_ratio

# calculating cart to purchase ratio
    #del temp
    temp = df.copy()
    # cart to purchase ratio
    temp_cart_purch_ratio_user = purchase_ratios(temp, action_col='add_to_cart',id_col='User_id',col_name='no_of_carts')
    

# calculating wishlist to purchase ratio
    del temp
    temp = df.copy()
    # Click wishlist to purchase ratio
    temp_click_wishlist_purch_ratio_user = purchase_ratios(temp, action_col='click_wishlist_page',
                                             id_col='User_id',col_name='no_of_click_wishlist')
    # Add wishlist to purchase ratio
    temp_add_wishlist_purch_ratio_user = purchase_ratios(temp, action_col='add_to_wishlist',
                                             id_col='User_id',col_name='no_of_add_wishlist')


# calculating paths to cart
    del temp
    temp = df.copy()
    # Filtering the dataset by max add_to_cart date for each user (All users who have done add_to_cart event)
    temp = (temp.sort_values(by='DateTime')
            [(temp.DateTime <= temp.User_id.map(temp[temp['Action']=='add_to_cart'].groupby('User_id').DateTime.max()))
            ])

    # Extracting the paths
    last_3_actions = r'((?:\S+\s+){0,3}\badd_to_cart)'
    temp_path =  temp.sort_values(by='DateTime').groupby('User_id').agg({'Action': lambda x: list(x)}).reset_index()
    temp_path['Action_cleaned'] = temp_path['Action'].apply(lambda x: ' '.join(x))
    temp_path['Last_3_Actions'] = temp_path['Action_cleaned'].apply(lambda x: re.findall(last_3_actions,x))

    # Cleaning and selecting the latest path for each user
    temp_path['Final_3_Actions'] = temp_path['Last_3_Actions'].apply(lambda x: x[0] if len(x)==1 else x)
    temp_path['Final_3_Actions'] = temp_path['Final_3_Actions'].apply(lambda x: x[1] if len(x)==2 else x)
    temp_path['Final_3_Actions'] = temp_path['Final_3_Actions'].apply(lambda x: x[2] if len(x)==3 else x)

    # Grouping the paths to top 10 and rest as others
    top_10_paths = temp_path.Final_3_Actions.value_counts()[:10].index.to_list()
    temp_path['top_paths'] = temp_path['Final_3_Actions'].apply(lambda x: x if x in top_10_paths else 'others')
   

#  calculating cart to purchase ratios category/subcategory wise
    del temp
    temp = df.copy()
    # Category level - cart_to_purchase_ratio
    temp_cart_purch_ratio_category = purchase_ratios(temp, action_col='add_to_cart',
                                                    id_col='Category',col_name='category_no_of_carts')

    # SubCategory level - cart_to_purchase_ratio
    temp_cart_purch_ratio_subcategory = (purchase_ratios(temp, action_col='add_to_cart',
                                                        id_col='SubCategory',col_name='subcategory_no_of_carts'))

#  calculating wishlist to puchase ration category/subcategory wise
    del temp
    temp = df.copy()
    # Category level - click_wishlist_to_purchase_ratio
    temp_click_wishlist_purch_ratio_category = (purchase_ratios(temp, action_col='click_wishlist_page',
                                                        id_col='Category',col_name='category_no_of_click_wishlist'))

    # SubCategory level - click_wishlist_to_purchase_ratio
    temp_click_wishlist_purch_ratio_subcategory = (purchase_ratios(temp, action_col='click_wishlist_page',
                                                        id_col='SubCategory',col_name='subcategory_no_of_click_wishlist'))

    # Category level - add_wishlist_to_purchase_ratio
    temp_add_wishlist_purch_ratio_category = (purchase_ratios(temp, action_col='add_to_wishlist',
                                                            id_col='Category',col_name='category_no_of_add_wishlist'))

    # SubCategory level - add_wishlist_to_purchase_ratio
    temp_add_wishlist_purch_ratio_subcategory = (purchase_ratios(temp, action_col='add_to_wishlist',
                                                        id_col='SubCategory',col_name='subcategory_no_of_add_wishlist'))
   
#  calculating product view to purchase ratio category/subcategory wise
    del temp 
    temp = df.copy()
    # Category level - produc_view_wishlist_to_purchase_ratio
    temp_product_view_purch_ratio_category = (purchase_ratios(temp, action_col='product_view',
                                                            id_col='Category',col_name='category_no_of_product_view')) 

    # SubCategory level - produc_view_wishlist_to_purchase_ratio
    temp_product_view_purch_ratio_subcategory = (purchase_ratios(temp, action_col='product_view',
                                                        id_col='SubCategory',col_name='subcategory_no_of_product_view'))


    # Target group of people are those who added items to the cart (Trigger point)
    df_base = get_target_customers(df)

    # Adding rfm features   
    df_base = pd.merge(df_base, temp_days_active, on='User_id', how='left')

    temp_rfm_feats = df.groupby('User_id').agg({'R': 'max','F':'max','M':'max','Loyalty_Level':'max'}).reset_index()
    df_base = pd.merge(df_base, temp_rfm_feats, on='User_id', how='left')

    # Adding average time between purchase
    df_base = pd.merge(df_base, temp_user_purchase_date[['User_id','avg_time_between_purchase']], 
                    on='User_id', how='left')

    # Adding carts to purchase ratio
    df_base = pd.merge(df_base, temp_cart_purch_ratio_user[['User_id','no_of_carts_to_purchase_ratio']], 
                    on='User_id', how='left')

    # Adding wishlist to purchase ratios (click & add)
    df_base = pd.merge(df_base, 
                    temp_click_wishlist_purch_ratio_user[['User_id','no_of_click_wishlist_to_purchase_ratio']], 
                    on='User_id', how='left')
    df_base = pd.merge(df_base, 
                    temp_add_wishlist_purch_ratio_user[['User_id','no_of_add_wishlist_to_purchase_ratio']], 
                    on='User_id', how='left')     

    # Adding top path-to-cart
    df_base = pd.merge(df_base, temp_path[['User_id','top_paths']], 
                    on='User_id', how='left')

    # Adding Category & SubCategory level carts-to-purchase ratio
    df_base = pd.merge(df_base, temp_cart_purch_ratio_category[['Category','category_no_of_carts_to_purchase_ratio']], 
                    on='Category', how='left')

    df_base = pd.merge(df_base,
                    temp_cart_purch_ratio_subcategory[['SubCategory','subcategory_no_of_carts_to_purchase_ratio']], 
                    on='SubCategory', how='left')
    # Adding Category & SubCategory level wishlist-to-purchase ratio (click & add)
    df_base = pd.merge(df_base, 
                    temp_click_wishlist_purch_ratio_category[['Category','category_no_of_click_wishlist_to_purchase_ratio']], 
                    on='Category', how='left')

    df_base = pd.merge(df_base,
                    temp_click_wishlist_purch_ratio_subcategory[['SubCategory','subcategory_no_of_click_wishlist_to_purchase_ratio']], 
                    on='SubCategory', how='left')

    df_base = pd.merge(df_base, 
                    temp_add_wishlist_purch_ratio_category[['Category','category_no_of_add_wishlist_to_purchase_ratio']], 
                    on='Category', how='left')

    df_base = pd.merge(df_base,
                    temp_add_wishlist_purch_ratio_subcategory[['SubCategory','subcategory_no_of_add_wishlist_to_purchase_ratio']], 
                    on='SubCategory', how='left')

    # Adding Category & SubCategory level product_view-to-purchase ratio (click & add)
    df_base = pd.merge(df_base, 
                    temp_product_view_purch_ratio_category[['Category','category_no_of_product_view_to_purchase_ratio']], 
                    on='Category', how='left')

    df_base = pd.merge(df_base,
                    temp_product_view_purch_ratio_subcategory[['SubCategory','subcategory_no_of_product_view_to_purchase_ratio']], 
                    on='SubCategory', how='left')
    return df_base


