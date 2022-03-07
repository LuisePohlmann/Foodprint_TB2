import pandas as pd
import datetime
from datetime import date, datetime

def get_values():
    entire_data = pd.read_csv("data/Food_Production.csv")
    food_data = entire_data[["Food product", "Total_emissions", "Freshwater withdrawals per kilogram (liters per kilogram)"]]

    food_footprints_CO2 = pd.read_csv("data/food-footprints.csv")
    food_footprints_CO2 = food_footprints_CO2[["Entity","GHG emissions per kilogram (Poore & Nemecek, 2018)" ]]
    food_footprints_CO2.rename(columns = {'Entity':'Food product', 'GHG emissions per kilogram (Poore & Nemecek, 2018)':'Total_emissions'}, inplace = True)

    food_df = food_data.merge(food_footprints_CO2, how="outer", on = "Food product")

    food_df["Total_emissions_total"] = (food_df["Total_emissions_x"] + food_df["Total_emissions_y"])/2
    food_df['Total_emissions_total'].fillna(food_df['Total_emissions_x'],inplace=True)
    food_df['Total_emissions_total'].fillna(food_df['Total_emissions_y'],inplace=True)

    food_df.pop("Total_emissions_x")
    food_df.pop("Total_emissions_y")
    food_df.rename(columns = {"Total_emissions_total": "CO2", "Freshwater withdrawals per kilogram (liters per kilogram)": "Water"}, inplace = True)

    food_df['Water'].fillna(food_df['Water'].mean(),inplace=True)

    df = food_df
    return(df)

def list(df):
    list_of_foods = []
    for i, row in df.iterrows():
        list_of_foods.append(df.loc[i,"Food product"])
    return(list_of_foods)

def get_food(df):
    global food
    food = df[df["Food product"]==search_food] #search_food not existing here! @Carina-Sophie
    food=dict(food)
    return(food)

def create_history():
    data = {"Food":"food","CO2":[0], "water":[0], "plastic":[0], "date": [date.today()]}
    history = pd.DataFrame(data)
    history.to_csv("data/history.csv")
    return(history)

def get_footprints(food, plastic):
    import pandas as pd
    from datetime import date
    history = pd.read_csv("data/history.csv", index_col=[0])
    CO2_footprint = float(food["CO2"])/10
    water_footprint = float(food["Water"]/10)
    plastic_footprint = plastic
    data = {"Food":food["Food product"], "CO2": [CO2_footprint], "water": [water_footprint], "plastic":[plastic_footprint], "date": [date.today()]}
    new_history = pd.DataFrame.from_dict(data)
    history = history.append(new_history)
    history.to_csv("data/history.csv")
    return(history)

def last_weeks(history):
    from datetime import timedelta
    today = date.today()
    week_1, week_2, week_3, week_4 = [],[],[],[]

    for i in range(28):
        d = today - timedelta(days=i)
        if i <= 7:
            week_1.append(str(d))
        if 7 < i <= 14:
            week_2.append(str(d))
        if 14 < i <= 21:
            week_3.append(str(d))
        if 21 < i <= 28:
            week_4.append(str(d))

    a = history.groupby(["date"]).sum()
    df_week_1, df_week_2, df_week_3, df_week_4 = a.copy(), a.copy(), a.copy(), a.copy()
    df_weeks = [df_week_1, df_week_2, df_week_3, df_week_4]

    for day, row in a.iterrows():
        if str(day) not in week_1:
            df_week_1 = df_week_1.drop([day])
        if str(day) not in week_2:
            df_week_2 = df_week_2.drop([day])
        if str(day) not in week_3:
            df_week_3 = df_week_3.drop([day])
        if str(day) not in week_4:
            df_week_4 = df_week_4.drop([day])

    for week in df_weeks:
        try:
            week.pop("Unnamed:0")
        except KeyError:
            week

    df_week_1.to_csv("data/week_1.csv")
    df_week_2.to_csv("data/week_2.csv")
    df_week_3.to_csv("data/week_3.csv")
    df_week_4.to_csv("data/week_4.csv")


def largest_table(history):
    water_max = history['water'].nlargest(n=4)
    water_max = water_max.reset_index(drop=True)
    CO2_max = history['CO2'].nlargest(n=4)
    CO2_max = CO2_max.reset_index(drop=True)

    water_max_df = history.loc[history['water'] == water_max[0]]
    CO2_max_df = history.loc[history['CO2'] == CO2_max[0]]

    for i in water_max:
        water_max_df = water_max_df.append(history.loc[history['water'] == i])
    for i in CO2_max:
        CO2_max_df = CO2_max_df.append(history.loc[history['CO2'] == i])

    CO2_max_df.to_csv("CO2_max.csv")
    water_max_df.to_csv("water_max.csv")
    return(water_max_df, CO2_max_df)

def sort_for_stats(data):
    labels = data.index.tolist()
    CO2_values = []
    water_values = []
    plastic_values = []
    for i in data["CO2"]:
        CO2_values.append(i)
    for i in data["water"]:
        water_values.append(i)
    for i in data["plastic"]:
        plastic_values.append(i)
    return(labels, CO2_values, water_values, plastic_values)

def totals():
    week_1 = pd.read_csv("data/week_1.csv", index_col=[0])
    thisweek = {}
    thisweek["CO2"] = week_1["CO2"].sum()
    thisweek["water"] = week_1["water"].sum()
    thisweek["plastic"] = week_1["plastic"].sum()
    return(thisweek)

def compare_weeks():
    week_1 = pd.read_csv("data/week_1.csv", index_col=[0])
    week_2 = pd.read_csv("data/week_2.csv", index_col=[0])
    week_3 = pd.read_csv("data/week_3.csv", index_col=[0])
    week_4 = pd.read_csv("data/week_4.csv", index_col=[0])

    weeks = [week_1, week_2, week_3, week_4]

    total_1, total_2, total_3, total_4 ={}, {},{},{}
    totals = [total_1, total_2, total_3, total_4]

    a = 0
    for i in totals:
        i["CO2"] = weeks[a]["CO2"].mean()
        i["water"] = weeks[a]["water"].mean()
        a += 1

    totals_labels = totals
    CO2_weeks, water_weeks = [], []
    for i in totals:
        CO2_weeks.append(i["CO2"])
        water_weeks.append(i["water"])

    if week_2.empty:
        message1 = "Congrats, your first week using the App! In future you can compare your weekly average CO2 Footprint here."
        message2 = "Congrats, your first week using the App! In future you can compare your weekly average water consumption here."
    else:
        if CO2_weeks[0] < CO2_weeks[1]:
            message1 = "Fantastic! You reduced your CO2 footprint in comparision to your average of the last 7 days!"
        else:
            message1 = "Try to reduce your CO2 emissions next week. Have a look at our Tips."
        if water_weeks[0] < water_weeks[1]:
            message2 = "Splendid! You reduced your water footprint in comparision to your average of the last 7 days!"
        else:
            message2 = "Try to reduce your water consumption next week. Have a look at our Tips."

    return(totals_labels, CO2_weeks, water_weeks, message1, message2)
