import streamlit as st
import pandas as pd
from pymongo import MongoClient
import certifi

MONGODB_URI = st.secrets.get("MONGODB_URI", "")

client = MongoClient(
    MONGODB_URI,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=15000,
)
client.admin.command("ping")

def get_data_frame(collection, database="stupid-bird", query=None):
    if query is None:
        query = {}

    db = client[database]
    collection = db[collection]
    cursor = collection.find(query)

    return pd.DataFrame(list(cursor))

users_df = get_data_frame("users")
users_df = users_df[["pictureUrl", "userId", "displayName", "coin", "daimond", "lastLogin", "loginStack"]]

st.write("https://stupid-bird.vercel.app/")

st.header("All game logs")
all_game_logs = get_data_frame("game-log", query={})
if len(all_game_logs) > 0:
    st.write(f"""
    Game count: {all_game_logs.shape[0]} game(s)

    Max score: {all_game_logs["point"].max()}

    Max coins: {all_game_logs["coin"].max()}
    """)

st.line_chart(all_game_logs, x="time", y=["point", "coin"])

st.header("All users")
event = st.dataframe(users_df,
             column_config={
                 "pictureUrl": st.column_config.ImageColumn(
                     "pictureUrl", help="Streamlit app preview screenshots", width="small"
                 )
             },
             on_select="rerun",
             selection_mode="single-row",
             use_container_width=True,
             hide_index=True)

if len(event.selection.rows) > 0:
    select_user = event.selection.rows
    user_df = users_df.iloc[select_user]
    st.header(f"{user_df["displayName"].values[0]}'s game logs")

    st.image(user_df["pictureUrl"].values[0], width=300)

    user_game_logs = get_data_frame("game-log", query={"userId": user_df["userId"].values[0]})

    user_items = get_data_frame("items", query={"userId": user_df["userId"].values[0], "isInstall": True})
    item_info = get_data_frame("items-info")
    item_info["itemId"] = item_info["_id"]

    if len(user_items) > 0 :
        user_item = pd.merge(user_items, item_info, on="itemId", how="left")
        user_item = user_item[["name", "type", "image", "level_x", "skill"]]

        st.dataframe(user_item,
                     column_config={
                         "image": st.column_config.ImageColumn(
                             "image", help="Streamlit app preview screenshots", width="small"
                         )
                     },
                     use_container_width=True,
                     hide_index=True)

    if len(user_game_logs) > 0:
        st.write(f"""
        Game count: {user_game_logs.shape[0]} game(s)

        Max score: {user_game_logs["point"].max()}
        
        Max coins: {user_game_logs["coin"].max()}
        """)

    st.line_chart(user_game_logs, x="time", y=["point", "coin"])
    st.dataframe(user_game_logs,
                 use_container_width=True,
                 hide_index=True)
