import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
import emojis
from collections import Counter
import plotly.graph_objs as go
import numpy as np
import re


@st.cache_data
def process_chat_file(file_contents):
    pattern = r"(\d+\/\d+\/\d+), (\d+:\d+\s(am|pm)) \- ([^\:]*):(.*)"
    data = []

    for line in file_contents.split("\n"):
        # Match the line with the pattern
        match = re.match(pattern, line)
        try:
            if match:
                date, time, ampm, author, message = match.groups()
                if "am" in time:
                    time=time.replace("\u202fam","")
                if "pm" in time:
                    time=time.replace("\u202fpm","")
                data.append({"Date": date, "Time": time.replace(r"\u202f",""),"AM/PM":ampm, "Author": author.strip(), "Message": message.strip()})
        except:
            continue

    df = pd.DataFrame(data)

    def split_count(text):
        emoji_list=[]
        data=emojis.get(str(text))
        return data

    df["Emoji"] = df["Message"].apply(split_count)

    image_messages_df = df[df["Message"] == '<Media omitted>']
    message_df=df.drop(image_messages_df.index)

    message_df["Date"] = pd.to_datetime(message_df.Date)

    message_df["Time"] = pd.to_datetime(message_df.Time).dt.strftime('%H:%M')

    message_df['Letter_Count'] = message_df['Message'].apply(lambda s : len(str(s)))
    message_df['Word_count'] = message_df['Message'].apply(lambda s : len(str(s).split(' ')))

    total_emojis_list=list([a for b in message_df.Emoji for a in b])
    authors = message_df.Author

    emoji_author_counts = {}
    for emoji, author in zip(total_emojis_list, authors):
        if author not in emoji_author_counts:
            emoji_author_counts[author] = Counter()
        emoji_author_counts[author][emoji] += 1

    emoji_author_df = pd.DataFrame.from_dict(emoji_author_counts, orient='index').fillna(0)

    emoji_dict = dict(Counter(total_emojis_list))
    emoji_dict = sorted(emoji_dict.items(), key=lambda x: x[1], reverse=True)

    emoji_df = pd.DataFrame(emoji_dict).rename(columns={0: "emoji", 1: "count"})

    # Combine 'Date' and 'Time' columns into 'DateTime'
    message_df['DateTime'] = pd.to_datetime(message_df['Date'].dt.strftime('%Y-%m-%d') + ' ' + message_df['Time'] + ' ' + message_df['AM/PM'], format='%Y-%m-%d %I:%M %p')
    message_df = message_df.sort_values(by='DateTime')

    # Create 'Response Time' column
    message_df['Response Time'] = pd.NaT

    last_message_time = {}

    for index, row in message_df.iterrows():
        author = row['Author']
        current_time = row['DateTime']
        
        if author in last_message_time:
            last_time = last_message_time[author]
            if last_time is not pd.NaT:
                response_time = current_time - last_time
                message_df.at[index, 'Response Time'] = response_time
        
        last_message_time[author] = current_time


    # Convert 'Response Time' to seconds
    message_df['Response Time'] = message_df['Response Time'].apply(lambda x: x.total_seconds() if pd.notnull(x) else None)

    
    return message_df, message_df, emoji_df, emoji_author_df

# Streamlit app
def main():
    st.title("Chat Data Visualization")
    
    # Upload chat file
    uploaded_file = st.file_uploader("Upload a chat file", type="txt")
    
    if uploaded_file is not None:

        file_contents = uploaded_file.read().decode("utf-8")
        # Process the chat file
        df, message_df, emoji_df, emoji_author_df = process_chat_file(file_contents)
        
        # Display basic information
        st.header("Basic Information (First 20 Conversations)")
        st.write(df.tail(20))

        st.header("Author Stats")
        l = message_df.Author.unique()

        l = message_df['Author'].unique()
        for i in range(len(l)):
            req_df = df[df["Author"] == l[i]]
            st.subheader(f'Stats of {l[i]}:')
            st.write(f'Message sent: {req_df.shape[0]}')
            words_per_message = (np.sum(req_df['Word_count'])) / req_df.shape[0]
            st.write(f"Words per message: {words_per_message:.2f}")
            emoji_count = sum(req_df['Emoji'].str.len())
            st.write(f'Emoji sent: {emoji_count}')
            avg_response_time = round(req_df['Response Time'].mean(),2)
            st.write(f'Average Response Time for {l[i]}: {avg_response_time} seconds')
            st.write('-----------------------------------')
        
        # Display emoji distribution
        st.header("Emoji Distribution")
        fig = px.pie(emoji_df, values='count', names='emoji', title='Emoji Distribution')
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig)
        
        # Display emoji usage by author
        st.header("Emoji Usage by Author")
        fig = px.bar(emoji_author_df, x=emoji_author_df.index, y=emoji_author_df.columns, title="Emoji Usage by Author", barmode='stack')
        fig.update_layout(xaxis_title="Emojis", yaxis_title="Count", legend_title="Authors")
        st.plotly_chart(fig)

        # Top 10 days with most messages
        st.header("Top 10 Days With Most Messages")
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%y', errors='coerce')
        messages_per_day = df.groupby(df['Date'].dt.date).size().reset_index(name='Messages')
        messages_per_day = messages_per_day.sort_values(by='Messages', ascending=False)
        top_days = messages_per_day.head(10)
        trace = go.Bar(
            x=top_days['Date'],
            y=top_days['Messages'],
            marker=dict(
                color='rgba(58, 71, 80, 0.6)',
                line=dict(
                    color='rgba(58, 71, 80, 1.0)',
                    width=1.5),
            ),
            text=top_days['Messages']
        )
        layout = go.Layout(
            title='Top 10 Days with Most Messages',
            xaxis=dict(
                title='Date',
                tickfont=dict(
                    size=14,
                    color='rgb(107, 107, 107)'
                )
            ),
            yaxis=dict(
                title='Number of Messages',
                titlefont=dict(
                    size=16,
                    color='rgb(107, 107, 107)'
                ),
                tickfont=dict(
                    size=14,
                    color='rgb(107, 107, 107)'
                )
            ),
            bargap=0.1,
            bargroupgap=0.1,
            paper_bgcolor='rgb(233, 233, 233)',
            plot_bgcolor='rgb(233, 233, 233)',
        )

        # Create the figure and plot the data
        fig = go.Figure(data=[trace], layout=layout)
        st.plotly_chart(fig)
        
        # Display message distribution by day
        st.header("Message Distribution by Day")
        day_df = pd.DataFrame(message_df["Message"])
        day_df['day_of_date'] = message_df['Date'].dt.weekday.astype(int)
        day_df['day_of_date'] = day_df["day_of_date"].apply(lambda i: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][int(i)])
        day_df["messagecount"] = 1
        day = day_df.groupby("day_of_date").sum()
        day.reset_index(inplace=True)
        fig = px.line_polar(day, r='messagecount', theta='day_of_date', line_close=True)
        fig.update_traces(fill='toself')
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True
                )
            ),
            showlegend=False
        )
        st.plotly_chart(fig)

        # Display word cloud
        st.header("Word Cloud")
        text = " ".join(str(review) for review in message_df.Message)
        nltk.download('stopwords')
        stopwords = set(nltk.corpus.stopwords.words('english'))
        stopwords.update(["acha", "okay", "yes", "no", "haa", "na", "ha", "tui", "ami", "amra", "amar", "bhai", "tor", "toke", "hoye", "sathe", "toh", "good", "bad", "kore", "ekta", "gulo", "khub", "kichu", "oki", "room", "dekhe", "te", "ki", "ke", "han", "korte", "bole", "class", "ok", "je", "eta", "ekhun", "ache", "keno", "theke", "kore", "bol", "dara", "jodi", "er", "ta", "niye", "ik", "korchish", "nijer", "now", "char", "boshe", "bollo", "okii", "even", "korbo", "bhalo", "nei", "kor", "amader", "legit", "jabo", "chilo", "ei", "bolche", "o", "nei", "debo", "kotha", "ekhon", "e", "Arey", "kal", "eto", "want", "pore", "jachi", "koto", "oi", "dekh", "u", "lol", "lmao", "ota", "achaa", "amake", "bolish", "emni", "kalke", "korchi", "ar", "pore", "ni", "ba", "shob", "lagche", "cuz", "yesh", "will", "abar", "jani", "ja", "korbi", "chole", "hobe", "de", "jaye", "call", "exactly", "jonne", "jonno", "hoyeche", "kaj", "jane", "last", "amay", "null", "gache", "aar", "holo", "thake", "tai", "ektu", "din", "diye", "onek", "aye", "ajke", "chai", "https", "ebar", "dekhi", "nije", "baje", "keu", "kintu", "phone", "nahole", "ashchi", "korle", "feel", "ashbi", "eksathe", "aaj", "bolechi", "done", "oder", "puro", "cho", "said", "kori", "bolbo", "tar", "age", "net", "see", "dite", "dekhbo", "noh", "kaaj", "abbe", "bollam", "noice", "gelo", "hie", "thakle", "jabi", "jache", "dekhte", "erom", "text", "give", "aro", "ekhuno", "take", "dekha", "jete", "kache", "onno", "opor", "ashbo", "aajke", "parish", "shudhu", "still", "achi", "lagbe", "nebo", "tarpor", "bolbo", "jabe", "eshe", "kheye", "giye", "koreche", "bhul", "chup", "hoto", "korish", "ig", "giye", "mane", "pare", "tell", "oh", "naah", "kora", "lage", "cholche", "tahole", "shotti", "icha", "ora", "shobai", "shon", "bolchi", "thik", "stop", "janina", "janena", "hoy", "beshi", "jokhon", "ashe", "make", "ne", "hole", "taka", "korche", "oke", "ager", "koi", "chele", "oo", "kono", "moto", "eishob", "need", "try", "mone", "bolbi", "pari", "let", "sure", "better", "roj", "heh", "mean", "dekhlam", "hocche", "waaah", "thakbo", "re", "chere", "bolte", "ma'am", "sir", "jinish", "jai", "naki", "hobena", "kobe", "dibi", "bar", "ask", "go", "one", "dilo", "boleche", "check", "fine", "anyway", "ekhono", "korbe", "ahhh", "korli", "know", "jiggesh", "diyechi", "jeta", "say", "thing", "normal", "pls", "boli", "wait", "baki", "parle", "korlam", "pakka", "jama", "se", "lok", "chilam", "debe", "diyeche", "bolli", "hobena", "jeta", "time", "send", "joldi", "anything", "nish", "kom", "floor", "sheta", "matha", "best", "chap", "korar", "der", "shei", "yaar", "sesh", "waah", "next", "chara", "naa", "bye", "uff", "theek", "khete", "wrong", "darun","hai","bhi","nhi","kya","tha","yeh","ho","mai","ko","ye","ka","haan","mujhe","raha","kuch","tumhara","kr","chal","hatt","mera","bas","maybe","tu","sahi","diya","naya","ek","maine","ghar","bhut","phir","baat","kaise","kya","karna","kuch","karna","log","aa","koi","kab","kabhi","tum","liye","mere","woh","pata","pr","ktu","tumhare","mein","main","wala","karo","beech","liya","hota","bhej","hum","sab","kiya","alag","hoga","kahan","kar","wara","tujhe","pehele","tumhe","abhi","dekho","wau","thi","itna","hu","jao","rhe","kaun","le","dekhti","hua","hun","jao","le","saal","hattt","fir","tab","abey","rha","also","paa","achhaa","huyi","suna","bolo","karti","jisne","khaana","kare","kisi","apne","jab","kitne","kitna","pasand","naaa"])
        wordcloud = WordCloud(width=800, height=400, random_state=1, background_color='white', colormap='Set2', collocations=False, stopwords=stopwords).generate(text)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)


        html_temp = """
        <div style="text-align: center; font-size: 14px; padding: 5px;">
        Created by Aritro Saha - 
        <a href="https://aritrosaha.netlify.com/">Website</a>, 
        <a href="https://github.com/halcyon-past">GitHub</a>, 
        <a href="https://www.linkedin.com/in/aritro-saha/">LinkedIn</a>
        </div>
        """
        st.markdown(html_temp, unsafe_allow_html=True)

if __name__ == "__main__":
    main()