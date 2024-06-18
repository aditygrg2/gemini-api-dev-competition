import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import streamlit.components.v1 as components

# Sample sentiment analysis results in percentages
agent_sentiment = {
    'positive': 8,
    'neutral': 92,
    'negative': 0
}

contact_sentiment = {
    'positive': 25,
    'neutral': 50,
    'negative': 25
}

# Function to create a sentiment bar chart
def create_sentiment_bar(sentiment, title):
    labels = ['Positive', 'Neutral', 'Negative']
    values = [sentiment['positive'], sentiment['neutral'], sentiment['negative']]
    colors = ['green', 'yellow', 'red']

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
            <div style="width: 15px; height: 15px; border-radius: 50%; background-color: green; margin-right: 5px;"></div>
            <span>Positive</span>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 15px; height: 15px; border-radius: 50%; background-color: yellow; margin-right: 5px;"></div>
            <span>Neutral</span>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="width: 15px; height: 15px; border-radius: 50%; background-color: red; margin-right: 5px;"></div>
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

# Streamlit app
st.set_page_config(page_title='Streamlit App', page_icon=None, layout='wide', initial_sidebar_state='auto')
st.markdown(
    background_css,
    unsafe_allow_html=True
)

st.title('Sentiment Analysis Results')

# Create tabs
tab1, tab2 = st.tabs(["Sentiment Analysis", "Conversational Trackers"])

with tab1:
    # Create separate containers for the charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="container">
                <h3>Agent Sentiment Breakdown</h3>
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

    def fetch_data_from_db():
        # Here you would connect to your database and fetch the data
        # For now, we'll use a sample dataframe
        data = {
            "task_type": ["Incoming Call", "Incoming Call", "Manual Outbound Call"],
            "contact_name": ["Aditya Garg", "Aditya Garg", "Aditya Garg"],
            "contact_number": ["+918630111400", "+918630111400", "+918630111400"],
            "agent_name": ["Parteek Goyal", "Parteek Goyal", "Aditya"],
            "agent_id": ["parteekcoder", "parteekcoder", "aditya@it.com"],
            "contact_sentiment": ["Neutral Contact", "Positive Contact", "Negative Contact"],
            "agent_sentiment": ["Neutral Agent", "Neutral Agent", "Neutral Agent"]
        }
        return pd.DataFrame(data)

    # Fetch data
    data_df = fetch_data_from_db()

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
        for _, row in data_df.iterrows():
            contact_sentiment_class = {
                "Neutral Contact": "contact-sentiment-neutral",
                "Positive Contact": "contact-sentiment-positive",
                "Negative Contact": "contact-sentiment-negative"
            }.get(row['contact_sentiment'], "contact-sentiment-neutral")

            agent_sentiment_class = "agent-sentiment-neutral"

            rows.append(f"""
                <tr>
                    <td>{row['task_type']}</td>
                    <td>{row['contact_name']}<br>{row['contact_number']}</td>
                    <td>{row['agent_name']}<br>{row['agent_id']}</td>
                    <td><span class="{contact_sentiment_class}">{row['contact_sentiment']}</span></td>
                    <td><span class="{agent_sentiment_class}">{row['agent_sentiment']}</span></td>
                </tr>
            """)

        return f"""
        <table style="margin-bottom:100px;">
            <thead>
                <tr>
                    <th>Task Type</th>
                    <th>Contact</th>
                    <th>Agent</th>
                    <th>Contact Sentiment</th>
                    <th>Agent Sentiment</th>
                </tr>
            </thead>
            <tbody>
                            <tr>
                    <td>{row['task_type']}</td>
                    <td>{row['contact_name']}<br>{row['contact_number']}</td>
                    <td>{row['agent_name']}<br>{row['agent_id']}</td>
                    <td><span class="{contact_sentiment_class}">{row['contact_sentiment']}</span></td>
                    <td><span class="{agent_sentiment_class}">{row['agent_sentiment']}</span></td>
                </tr>
            </tbody>
        </table>
        """

    # Generate the table HTML
    table_html = generate_table_html(data_df)

    # Inject the CSS and HTML into the Streamlit app
    st.title("Log Table with Transcripts")
    st.markdown(table_css, unsafe_allow_html=True)
    st.markdown(table_html, unsafe_allow_html=True)

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                border: 1px solid #000;
                padding: 8px;
                text-align: center;
            }
            th {
                background-color: #f2f2f2;
            }
            .low-value {
                background-color: #ffcccc;
            }
        </style>
    </head>
    <body style="background-color:#ffffff;">
        <div id="table-container">
            <table id="agent-table">
                <thead>
                    <tr>
                        <th>Calls</th>
                        <th>Avg Agent Sentiment</th>
                        <th>Avg Contact Sentiment</th>
                        <th>% of Calls with Negative Agent Sentiment</th>
                        <th>% of Calls with Negative Contact Sentiment</th>
                        <th>Talk/Listen Ratio</th>
                        <th>Avg. Silence</th>
                        <th>Longest Monologue</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>50</td>
                        <td>0.75</td>
                        <td>0.80</td>
                        <td>10%</td>
                        <td>5%</td>
                        <td>1.2</td>
                        <td>0:02:30</td>
                        <td>0:05:00</td>
                    </tr>
                    <tr>
                        <td>45</td>
                        <td>0.60</td>
                        <td>0.65</td>
                        <td>15%</td>
                        <td>20%</td>
                        <td>1.0</td>
                        <td>0:03:00</td>
                        <td>0:04:30</td>
                    </tr>
                    <tr>
                        <td>60</td>
                        <td>0.85</td>
                        <td>0.90</td>
                        <td>5%</td>
                        <td>3%</td>
                        <td>1.5</td>
                        <td>0:01:45</td>
                        <td>0:03:50</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <script>
            // Threshold values for conditional formatting
            const thresholds = {
                avgAgentSentiment: 0.7,
                avgContactSentiment: 0.75,
                negativeAgentSentiment: 10,
                negativeContactSentiment: 10,
                talkListenRatio: 1.0,
            };

            // Apply conditional formatting
            document.querySelectorAll("tbody tr").forEach((row) => {
                const cells = row.children;
                if (parseFloat(cells[1].textContent) < thresholds.avgAgentSentiment) {
                    cells[1].classList.add("low-value");
                }
                if (parseFloat(cells[2].textContent) < thresholds.avgContactSentiment) {
                    cells[2].classList.add("low-value");
                }
                if (
                    parseFloat(cells[3].textContent) < thresholds.negativeAgentSentiment
                ) {
                    cells[3].classList.add("low-value");
                }
                if (
                    parseFloat(cells[4].textContent) < thresholds.negativeContactSentiment
                ) {
                    cells[4].classList.add("low-value");
                }
                if (parseFloat(cells[5].textContent) < thresholds.talkListenRatio) {
                    cells[5].classList.add("low-value");
                }
            });

            // Adjust height and width of the container
            const container = document.getElementById('table-container');
            const table = document.getElementById('agent-table');
            container.style.height = table.offsetHeight + 'px';
            container.style.width = table.offsetWidth + 'px';

        </script>
    </body>
    </html>
    """

    # Embed the HTML content into the Streamlit app without setting height and width statically
    st.title("Agent Call Status")
    components.html(html_content, height=250, width=800)

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
