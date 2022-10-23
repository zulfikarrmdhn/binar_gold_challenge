import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3

#Add HS-Abusive Column
conn = sqlite3.connect('gold_challenge_upload_file.db', check_same_thread=False)
conn.execute("""ALTER TABLE clean_tweet ADD COLUMN HSvsAbusive VARCHAR(50)""")
conn.execute("""UPDATE clean_tweet SET HSvsAbusive = "HS_Abusive" WHERE HS = 1 AND Abusive = 1""")
conn.execute("""UPDATE clean_tweet SET HSvsAbusive = "HS_NonAbusive" WHERE HS = 1 AND Abusive = 0""")
conn.execute("""UPDATE clean_tweet SET HSvsAbusive = "NonHS_Abusive" WHERE HS = 0 AND Abusive = 1""")
conn.execute("""UPDATE clean_tweet SET HSvsAbusive = "NonHS_NonAbusive" WHERE HS = 0 AND Abusive = 0""")
conn.commit()
conn.close()

#Add Target Hate Speech Column
conn = sqlite3.connect('gold_challenge_upload_file.db', check_same_thread=False)
conn.execute("""ALTER TABLE clean_tweet ADD COLUMN HS_Target VARCHAR(50)""")
conn.execute("""UPDATE clean_tweet SET HS_Target = "Individual" WHERE HS_Individual = 1""")
conn.execute("""UPDATE clean_tweet SET HS_Target = "Group" WHERE HS_Group = 1""")
conn.commit()
conn.close()

#Add Category Hate Speech Column
conn = sqlite3.connect('gold_challenge_upload_file.db', check_same_thread=False)
conn.execute("""ALTER TABLE clean_tweet ADD COLUMN HS_Category VARCHAR(50)""")
conn.execute("""UPDATE clean_tweet SET HS_Category = "Religion" WHERE HS_Religion = 1""")
conn.execute("""UPDATE clean_tweet SET HS_Category = "Race" WHERE HS_Race = 1""")
conn.execute("""UPDATE clean_tweet SET HS_Category = "Physical" WHERE HS_Physical = 1""")
conn.execute("""UPDATE clean_tweet SET HS_Category = "Gender" WHERE HS_Gender = 1""")
conn.execute("""UPDATE clean_tweet SET HS_Category = "Other" WHERE HS_Other = 1""")
conn.commit()
conn.close()

#Add Level Hate Speech Column
conn = sqlite3.connect('gold_challenge_upload_file.db', check_same_thread=False)
conn.execute("""ALTER TABLE clean_tweet ADD COLUMN HS_Level VARCHAR(50)""")
conn.execute("""UPDATE clean_tweet SET HS_Level = "Weak" WHERE HS_Weak = 1""")
conn.execute("""UPDATE clean_tweet SET HS_Level = "Moderate" WHERE HS_Moderate = 1""")
conn.execute("""UPDATE clean_tweet SET HS_Level = "Strong" WHERE HS_Strong = 1""")
conn.commit()
conn.close()

#Save New DataFrame to Directory
conn = sqlite3.connect('gold_challenge_upload_file.db', check_same_thread=False)
new_df = pd.read_sql_query("SELECT new_tweet, HSvsAbusive, HS_Target, HS_Category, HS_Level FROM clean_tweet", conn)
new_df.to_csv("Data_Visualize.csv")
conn.close()

#Save CSV to Database
conn = sqlite3.connect('gold_challenge_upload_file.db', check_same_thread=False)
Data_Visualize = pd.read_csv("Data_Visualize.csv", encoding="latin-1")
Data_Visualize.to_sql("Data_Visualize", con=conn, index=False, if_exists='append')
conn.close()

#Hate Speech vs Abusive Visualize
HSvsAbusive_count = Data_Visualize["HSvsAbusive"].value_counts()
HSvsAbusive_count = pd.DataFrame({"HSvsAbusive":HSvsAbusive_count.index,"Total":HSvsAbusive_count.values})
palette_color = sns.color_palette('pastel')
plt.pie(HSvsAbusive_count['Total'], labels=HSvsAbusive_count['HSvsAbusive'], colors=palette_color, autopct='%1.0f%%', pctdistance=0.5, labeldistance=1.2)
plt.title("Hate Speech vs Abusive")
plt.show()

#Hate Speech Category by Level Visualize
plt.figure(figsize=(12,8))
ax = sns.countplot(data=Data_Visualize,x="HS_Level",hue="HS_Category")
plt.title("Hate Speech Level to Category")
plt.xlabel("Level of Hate Speech")
plt.ylabel("Number of Hate Speech")
for p in ax.patches:
        ax.annotate('{:.0f}'.format(p.get_height()), (p.get_x()+0.05, p.get_height()+50))
plt.show()

#Hate Speech Target by Level Visualize
plt.figure(figsize=(12,8))
ax = sns.countplot(data=Data_Visualize,x="HS_Level",hue="HS_Target")
plt.title("Hate Speech Level to Target")
plt.xlabel("Level of Hate Speech")
plt.ylabel("Number of Hate Speech")
for p in ax.patches:
        ax.annotate('{:.0f}'.format(p.get_height()), (p.get_x()+0.1, p.get_height()+50))
plt.show()

print("Data Visualization Success")