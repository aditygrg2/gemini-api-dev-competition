import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import streamlit.components.v1 as components
from dotenv import load_dotenv
from pymongo import MongoClient
import os
import math
load_dotenv()

client = MongoClient(os.environ['MONGO_URL'])
db = client['amazon_data']
analysisColl = db['analysis']
trackerColl = db['trackers']

class Helper():

    def __init__(self) -> None:
        pass

    def get_audio_score_for_agent(self, call_sent):
        count = {'pos':0,'neu':0,'neg':0}
        for item in call_sent:
            if item['type']=="AI":
                count[item['sent']] = count[item['sent']] + 1
        total = len(call_sent)
        count['pos'] = math.ceil(count['pos']*100/total)
        count['neg'] = math.ceil(count['neg']*100/total)
        count['neu'] = 100 - count['neg'] - count['pos']
        return count

    def get_audio_score_for_human(self, call_sent):
        count = {'pos':0,'neu':0,'neg':0}
        for item in call_sent:
            if item['type']=="Human":
                count[item['sent']] = count[item['sent']] + 1
        total = len(call_sent)
        count['pos'] = math.ceil(count['pos']*100/total)
        count['neg'] = math.ceil(count['neg']*100/total)
        count['neu'] = 100 - count['neg'] - count['pos']
        return count

    def get_audio_score(self, call_sent):
        def get_overall_sentiment(sent: dict):
            max_key = max(sent, key=lambda k: sent[k])
            sent['overall'] = max_key
            if max_key =='pos':
                sent['text'] = "Positive sentiment"
            elif max_key == 'neg':
                sent['text'] = 'Negative sentiment'
            else:
                sent['text'] = 'Neutral sentiment'
            return sent

        ai = self.get_audio_score_for_agent(call_sent)
        human = self.get_audio_score_for_human(call_sent)
        return {"agent_sentiment":get_overall_sentiment(ai),"contact_sentiment":get_overall_sentiment(human)}

    def get_recent_call_analysis(self, call_sent):
        return self.get_audio_score(call_sent[0]['call_sent'])


    def calculate_call_sentiment(self, call_data):
        try:
            audio_analysis = self.get_audio_score(call_data['call_sent'])
            len_transcribed = len(call_data.get("transcribe",""))
            return {"phone_number": call_data['phone_number'], "transcribe": call_data.get("transcribe","Can't generate transcribe") ,"contact_sentiment":audio_analysis['contact_sentiment'],"agent_sentiment": audio_analysis['agent_sentiment'],"customer_feedback_rating": call_data.get('contact_feedback',dict()).get('score',"not given"),"customer_feedback_text":call_data.get('contact_feedback',dict()).get('text',"not given"),"agent_feedback_rating": call_data.get('agent_feedback',dict()).get('score',"not given"),"agent_feedback_text": call_data.get('agent_feedback',dict()).get('text',"not given")}
        except Exception as e:
            print(e)

    def calculate_tracker_count(self, call_list, trackers_list):
        ans = []
        for tr in trackers_list:
            temp = {}
            for call in call_list:
                cur_tracker = call.get("trackers",[])
                for cur_tracker_cnt in cur_tracker:
                    if tr['title']== cur_tracker_cnt['title']:
                        cur_tracker_tokens = cur_tracker_cnt['trackerCount']
                        for word in tr['words']:
                            val = cur_tracker_tokens.get(word,0)
                            temp[word] = temp.get(word,0) + val 
                        break
            tr['word_count'] = temp
            ans.append(tr)
        return ans


    def create_analysis(self, call_list):
        recent = self.get_recent_call_analysis(call_list)
        trackers = trackerColl.find()
        trck = []
        for t in trackers:
            trck.append(t)
        sentiment_list = []
        trackerList = []
        for call in call_list:
            sentiment_list.append(self.calculate_call_sentiment(call))
        
        trackerList = self.calculate_tracker_count(call_list, trck)

        return {"recent": recent, "sentiment_list": sentiment_list,"tracker_list": trackerList}


def get_analysis():
    try:
        call_data = analysisColl.find()
        data = []
        for doc in call_data:
            data.append(doc)
        analysis = Helper().create_analysis(data)
        return analysis
    except Exception as e:
        print(e)


def get_trackers():
    try:
        trackers = trackerColl.find()
        ans = []
        for tr in trackers:
            ans.append(tr)
        return ans
    except Exception as e:
        print(e)

analysis = get_analysis()
recent_call = analysis['recent']
agent_sentiment = {
    'positive': recent_call['agent_sentiment']['pos'] ,
    'neutral':  recent_call['agent_sentiment']['neu'],
    'negative':  recent_call['agent_sentiment']['neg'],
}

contact_sentiment = {
    'positive':  recent_call['contact_sentiment']['pos'] ,
    'neutral':  recent_call['contact_sentiment']['neu'] ,
    'negative':  recent_call['contact_sentiment']['neg'] ,
}

# Function to create a sentiment bar chart
def create_sentiment_bar(sentiment, title):
    labels = ['Positive', 'Neutral', 'Negative']
    values = [sentiment['positive'], sentiment['neutral'], sentiment['negative']]
    colors = ['#ABB9A2', '#F9E076', '#AB6465']

    fig = go.Figure()

    # Add positive bar
    fig.add_trace(go.Bar(
        x=[values[0]], y=[title],
        orientation='h',
        marker=dict(color=colors[0]),
        name='Positive',
        text=[f'{values[0]}%'],
        textposition='inside',
        insidetextanchor='middle'
    ))

    # Add neutral bar
    fig.add_trace(go.Bar(
        x=[values[1]], y=[title],
        orientation='h',
        marker=dict(color=colors[1]),
        name='Neutral',
        text=[f'{values[1]}%'],
        textposition='inside',
        insidetextanchor='middle'
    ))

    # Add negative bar
    fig.add_trace(go.Bar(
        x=[values[2]], y=[title],
        orientation='h',
        marker=dict(color=colors[2]),
        name='Negative',
        text=[f'{values[2]}%'],
        textposition='inside',
        insidetextanchor='middle'
    ))

    fig.update_layout(
        barmode='stack',
        title='',
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False
    )

    return fig

# Function to create a custom legend
def create_custom_legend():
    legend_html = """
    <div style="display: flex; justify-content: space-around; margin-top: 10px; ">
        <div style="display: flex; align-items: center;">
            <div style="width: 15px; height: 15px; border-radius: 50%; background-color: #ABB9A2; margin-right: 5px;"></div>
            <span>Positive</span>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 15px; height: 15px; border-radius: 50%; background-color: #F9E076; margin-right: 5px;"></div>
            <span>Neutral</span>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 15px; height: 15px; border-radius: 50%; background-color: #AB6465; margin-right: 5px;"></div>
            <span>Negative</span>
        </div>
    </div>
    """
    return legend_html

background_css = """
<style>
body {
    background-color: #ffffff; /* Light blue color */
}
.container {
        border: 1px solid #ddd; 
        border-radius:6px; 
        padding: 20px; 
        margin-bottom: 20px;
    }
    .container h3 {
        text-align: center;
    }
</style>
"""

header_html = """
<style>
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
    }
    .header-content {
        display: flex;
        align-items: center;
    }
    .header-title {
        font-size: 42px;
        margin: 0 10px;
        font-weight:bold;
    }
    .divider {
        height: 60px;
        border-left: 2px solid #aaa;
        margin: 0 20px;
    }
    .header-logo {
        width: 120px; /* Adjust size as needed */
        height: auto;
        margin-right: 10px;
        border-radius: 6px;
    }
</style>
<div class="header-container">
    <div class="header-content">
        <img src="https://www.hatchwise.com/wp-content/uploads/2022/05/amazon-logo-1024x683.png" class="header-logo">
        <div class="divider"></div>
        <div class="header-title">Call Analysis Dashboard</div>
    </div>
</div>
"""

tab_css = """
<style>
/* Style the tab container */
.stTabs [role="tablist"] {
    display: flex;
    justify-content: flex-start; /* Align tabs to the left */
    gap: 10px; /* Space between tabs */
    border-bottom: 2px solid #232f3f; /* Border at the bottom */
}

/* Style each tab */
.stTabs [role="tab"] {
    padding: 10px 20px;
    font-size: 24px; /* Make the text larger */
    font-weight: bold;
    border-radius: 10px 10px 0 0; /* Rounded top corners */
    cursor: pointer;
    color: black; /* White text color */
    background-color: #fffff; /* Background color */
    border: 2px solid #232f3f; /* Border color */
    border-bottom: none; /* Remove the bottom border */
    transition: none; /* Remove the transition effect */
}

/* Style the selected tab */
.stTabs [role="tab"][aria-selected="true"] {
    background-color: #232f3f; /* Same background color for selected tab */
    color: white; /* White text color for selected tab */
    border-color: #ff9900; /* Border color for selected tab */
    border-bottom: 2px solid #232f3f; /* Border at the bottom */
}

</style>
"""



# Streamlit app
st.set_page_config(page_title='Streamlit App', page_icon=None, layout='wide', initial_sidebar_state='auto')
st.markdown(
    header_html,
    unsafe_allow_html=True
)
st.markdown(tab_css, unsafe_allow_html=True)

# Create tabs
tab1, tab2 = st.tabs(["Sentiment Analysis", "Conversational Trackers"])

with tab1:
    # Create separate containers for the charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="container">
                <h3 ">Agent Sentiment Breakdown</h3>
            """,
            unsafe_allow_html=True
        )
        st.plotly_chart(create_sentiment_bar(agent_sentiment, ''), use_container_width=True)
        st.markdown(create_custom_legend(), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            """
            <div class="container">
                <h3>Contact Sentiment Breakdown</h3>
            """,
            unsafe_allow_html=True
        )
        st.plotly_chart(create_sentiment_bar(contact_sentiment, ''), use_container_width=True)
        st.markdown(create_custom_legend(), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


    # Fetch data
    data_df = analysis['sentiment_list']

    # CSS for styling the table
    table_css = """
    <style>
    table {
        width: 100%;
        border-collapse: collapse;
    }
    thead th {
        border-bottom: 2px solid #ddd;
        text-align: left;
        padding: 8px;
    }
    tbody td {
        border-bottom: 1px solid #ddd;
        padding: 8px;
        min-width:180px;
        width:auto;
        text-overflow: clip; 
    }
    .contact-sentiment-neutral,
    .contact-sentiment-positive,
    .contact-sentiment-negative,
    .agent-sentiment-neutral {
        display: inline-block;
        padding: 5px;
        border-radius: 5px;
        text-align: center; /* Center align the text */
        font-weight:600;
    }
    .contact-sentiment-neutral {
        background-color: #f0f0f0;
        padding: 5px;
        border-radius: 5px;
        color: #555;
    }
    .contact-sentiment-positive {
        background-color: #d4edda;
        padding: 5px;
        border-radius: 5px;
        color: #155724;
    }
    .contact-sentiment-negative {
        background-color: #f8d7da;
        padding: 5px;
        border-radius: 5px;
        color: #721c24;
    }
    .agent-sentiment-neutral {
        background-color: #f0f0f0;
        padding: 5px;
        border-radius: 5px;
        color: #555;
    }
    </style>
    """

    # Convert the DataFrame to HTML
    def generate_table_html(data_df):
        rows = []
        for row in data_df:
            print(row)
            contact_sentiment_class = {
                "Neutral sentiment": "contact-sentiment-neutral",
                "Positive sentiment": "contact-sentiment-positive",
                "Negative sentiment": "contact-sentiment-negative"
            }.get(row.get('contact_sentiment',dict()).get('text',"Neutral sentiment"), "contact-sentiment-neutral")

            agent_sentiment_class = "agent-sentiment-neutral"

            rows.append(f"""<tr>
                    <td>{row['phone_number']}</td>
                    <td><span class="{contact_sentiment_class}">{row['contact_sentiment']['text']}</span></td>
                    <td><span class="{agent_sentiment_class}">{row['agent_sentiment']['text']}</span></td>
                    <td>{row['customer_feedback_rating']}</td>
                    <td>{row['customer_feedback_text']}</td>
                    <td>{row['agent_feedback_rating']}</td>
                    <td>{row['agent_feedback_text']}</td>
                    <td>play</td>
                    <td>
                        <details>
                        <summary>Show Transcription</summary>
                        <p>{row['transcribe']}</p>
                        </details>
                    </td>
                </tr>""")

        return f"""
        <table style="margin-bottom:100px;">
            <thead>
                <tr>
                    <th>Phone Number</th>
                    <th>Contact Sentiment</th>
                    <th>Agent Sentiment</th>
                    <th>Customer feedback score</th>
                    <th>Customer Feedback text</th>
                    <th>Agent feedback score</th>
                    <th>Agent Feedback text</th>
                    <th>Recording</th>
                    <th>transcribe</th>
                </tr>
            </thead>
            <tbody>
            {''.join(rows)}
            </tbody>
        </table>
        """

    # Generate the table HTML
    table_html = generate_table_html(data_df)

    # Inject the CSS and HTML into the Streamlit app
    st.title("Call Log Table")
    st.markdown(table_css, unsafe_allow_html=True)
    st.markdown(table_html, unsafe_allow_html=True)
    def generate_table_html_tracker(data_df):
        rows = []
        # last = row['words'].pop()
        for row in data_df:

            rows.append(f"""<tr>
                    <td>{row['title']}</td>
                    <td><span>{', '.join(row['words'])}</span></td>
                    </tr>""")
        return f"""
        <table style="margin-bottom:100px;">
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Tokens/Words</th>
                </tr>
            </thead>
            <tbody>
            {''.join(rows)}
            </tbody>
        </table>
        """
    
    table_html = generate_table_html_tracker(get_trackers())
    st.title("Conversational Trackers")
    # components.html(table_html, height=250, width=800)
    st.markdown(table_css, unsafe_allow_html=True)
    st.markdown(table_html, unsafe_allow_html=True)

    trackers = analysis['tracker_list']
    st.title("Conversational Trackers")
    for tracker in trackers:
        st.markdown(f"### {tracker['title']}")


        words_data = tracker['word_count']
        labels = list(words_data.keys())
        values = list(words_data.values())
        pie_fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])

        tracker_name = tracker['title']

        pie_fig.update_layout(
            title=f'Count of Words for {tracker_name}',
            annotations=[dict(text='Words', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )

        st.plotly_chart(pie_fig)

        
with tab2:
    st.title("Conversational Trackers")

    # Use session state to store the list of words
    if 'word_list' not in st.session_state:
        st.session_state.word_list = []

    def add_word(word):
        if word and word not in st.session_state.word_list:
            st.session_state.word_list.append(word)

    with st.form("trackers_form"):
        tracker_title = st.text_input("Title", placeholder="Enter the title for tracker like 'Amazon great Indian sale'")
        new_word = st.text_input("Words", placeholder="Enter words separated by commas")
        submitted = st.form_submit_button("Submit")

        if submitted and new_word:
            # Add new word to the list
            add_word(new_word)
            # Clear the input field by resetting the key
            st.experimental_rerun()

    if st.session_state.word_list:
        for word in st.session_state.word_list:
            st.markdown(f"<div style='border: 1px solid #ddd; border-radius: 10px; padding: 10px; margin: 5px; display: inline-block;'>{word} <button style='background: none; border: none; color: red; cursor: pointer;'>&times;</button></div>", unsafe_allow_html=True)
