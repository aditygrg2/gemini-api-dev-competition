# Virtual Customer Service - Amazon HackOn 2024 Submission Project

## Problem Statement:
Build a next-generation multi-lingual virtual customer service solution powered by Large Language models (LLM) and Deep learning algorithms. The goal is to enable seamless, natural communication over the phone, offering quicker query resolution without the limitations of traditional chatbots. Implement sentiment analysis to understand customer emotions better and adjust the agent's responses accordingly, improving the overall experience and service quality. By implementing LLM, Gen AI, IVR, and Text-to-Speech capabilities, Amazon can streamline customer support while optimizing costs

## Features:
- Provides a seamless and natural conversational flow over the phone with a live conversational agent.
- Can fetch data from real-time Amazon databases and input it into LLM for rich outputs.
- Implements sentiment analysis on the go, transferring the call to an agent if the sentiment becomes negative at any point.
- Provides enriched data for analysis, including call transcripts, conversation trackers, feedback, interactive charts, and much more.
- Available 24x7.
- Easily configurable to adapt to specific requirements and integrate with existing systems.
- A next-generation multi-lingual service

## Technologies Used:

- **Large Language Model (LLM):** Powered by Gemini, providing intelligent responses.
- **Python:** Primary programming language used for developing the backend.
- **React:** Used for developing the frontend interface.
- **Socket.IO:** For real-time, bidirectional communication between the client and server.
- **Google Text-to-Speech and Speech-to-Text:** For converting text to speech and vice versa.
- **FFmpeg:** For audio processing.
- **Streamlit:** For building the agent analysis dashboard.
- **Sentiment Analysis:** Using the Hubert-base-superb model to analyze sentiments.
- **MongoDB:** Used as a temporary backend solution, to be integrated with existing systems.
- **FAISS Embeddings:** For handling text embeddings efficiently and quick querying
- **AWS Services:** For hosting and scaling the application. (To be implemented)

## Implementation Details

<img width="682" alt="Screenshot 2024-06-22 at 22 30 32" src="https://github.com/aditygrg2/ivr-llm/assets/98523623/fc235686-05db-458c-80f2-2ea86b633d73">

Our project architecture is designed to efficiently handle customer queries through a seamless integration of various services. Here's a detailed walkthrough:

1. **Customer Query Initiation**: 
   - The process begins when a customer makes a query, which is captured as an audio input.

2. **Parallel Processing Services**:
   - The customer's audio is simultaneously passed to three key services:
     - **LLM Agent Service**
     - **Logging Service**
     - **Sentiment Analysis Service**

3. **LLM Agent Service**:
   - **Speech-to-Text Conversion**: The user's speech is converted to text using advanced Speech-to-Text technology.
   - **Text Processing by LLM**: The transcribed text is processed by our pre-trained Large Language Model (LLM), which has been trained on customer call recordings and Amazon help documents to generate accurate and relevant responses.
   - **Text-to-Speech Conversion**: The AI-generated response is then converted back into speech and sent to the customer's phone.

4. **Sentiment Analysis Service**:
   - **Sentiment Detection**: The system performs sentiment analysis on the user's speech. If negative sentiment (such as frustration or anger) is detected, the call is forwarded to a human agent.
   - **Positive/Neutral Sentiment Handling**: If the sentiment is positive or neutral, the automated system continues to interact with the customer to resolve their query.

5. **Logging Service**:
   - **Conversation Logging**: All conversations are logged with conversational trackers that monitor and store keywords and phrases used during the call, tracking the customer's topics of interest.
   - **Keyword Tracking**: For example, tracking words like "sale," "great," or "Indian" helps us analyze interest in the Amazon Great Indian Sale.
   - **Data Storage**: The logging service stores call recordings and transcriptions in a database for future analysis.

<img width="655" alt="Screenshot 2024-06-22 at 22 30 00" src="https://github.com/aditygrg2/ivr-llm/assets/98523623/dabdcd25-947f-4089-9f0f-1842a911962d">

Talking about low level, we follow a two-step process:

1.⁠ ⁠*Verification Chain*: This step ensures that the agent is speaking to the account owner. It can call three different functions:
   - If the user fails to verify themselves, the call is terminated.
   - If the user is successfully verified, the call is transferred to the During Call Chain.
   - If real-time data is required, the Verification Chain can request this from the database by querying the phone number. This call is made onto MongoDB in real-time.

2.⁠ ⁠*During Call Chain*: This step is responsible for addressing and resolving the user’s query. It can call four different functions:
   - Requesting user data from the database, similar to the verification chain but this chain is allowed to request for any data. Unlike the verification chain, where it was allowed to fetch only some particular data such as name, phone_number, and verification-only details.
   - Fetching documents from the vector store, is done using FAISS (Facebook AI Similarity Search) in this implementation. The embeddings are made using the data provided in [data](/data.txt)
   - Transferring the call to the agent, this will be routed directly to an agent.
   - Terminating the call

The best part is that all of this happens in real time.

## Audio Demos with Different Scenarios

### Good Case Complete Call

- [Audio Link](https://github.com/aditygrg2/ivr-llm/raw/main/sample-audios/MainSampleTechnicalAudio.mp3)

This call is a sample of a completely successful good case where all conversations are smooth. There are no mistakes on the client side and hopefully, everything goes well.

### Intelligent Model

- [Audio Link](https://github.com/aditygrg2/ivr-llm/raw/main/sample-audios/7AnUnderstandingAgent.mp3)

When the agent felt that the query was a little weird, as the customer was requesting a refund status for an unsuccessful order, it automatically redirected the call and the agent got the below request from the model automatically.

Function Call:
```
{'function_name': 'send_to_agent_for_manual_intervention', 'function_args': {'query': 'Customer is looking for a refund status for an unsuccessful order (Order ID: 100001). Could you please assist the customer with their refund?'}}
```

### Call with an angry/frustrated customer

- [Audio Link](https://github.com/aditygrg2/ivr-llm/raw/main/sample-audios/Frustration1.mp3)

Here, the customer is angry, and as soon as the model gets to know this, the call is directly transferred to an agent.

### Crucial Operations are only handled by a real agent

- [Audio Link](https://github.com/aditygrg2/ivr-llm/raw/main/sample-audios/6Successful_Termination.mp3)

A crucial query (for example a refund or replacement request) which is risky to automate, will be transferred to the agent directly. (We assume here that return/replacements are crucial and should not be handled by the model directly, this can be anything that can be configured beyond this prototype)

This JSON was fetched by the model from DB while this call happened.

```
{
  "phone_number": "8630111400",
  "name": "Aditya Garg",
  "town_city": "Nanakmatta",
  "state": "Uttarakhand",
  "pincode": "262311",
  "email": "uber6707@gmail.com",
  "previous_orders": [
    {
      "order_id": "12556",
      "status": "In-Transit",
      "transaction": {
        "transaction_id": "9827465",
        "status": "Successful",
        "payment_method": "Amazon Pay",
        "total_amount": "48000",
        "timestamp": {
          "$date": "2024-06-18T22:50:12.987Z"
        }
      },
      "items": [
        {
          "product_id": "10001",
          "name": "Brand X Model Y Laptop",
          "description": "16GB RAM, 512GB SSD, 15.6\" display",
          "category": "Electronics",
          "average_rating": "4",
          "price": "45000",
          "reviews": [
            "Nice product"
          ]
        },
        {
          "product_id": "20001",
          "name": "Brand B T-Shirt (Blue)",
          "description": "Cotton blend, Crew neck, Size M",
          "category": "Clothing & Apparel",
          "average_rating": "4",
          "price": "3000",
          "reviews": [
            "Worth the hype",
            "Makes you feel young"
          ]
        }
      ],
      "timestamp": {
        "$date": "2024-06-18T17:20:12.987Z"
      },
      "estimated_delivery_time": "19/06/24 , by 9 PM",
      "last_location_update": "Panipat, Haryana"
    }
  ],
  "subscription_status": false
}
```

### Model failed to think of a solution and transferred the call to an agent

- [Audio Link](https://github.com/aditygrg2/ivr-llm/raw/main/sample-audios/3Failed_And_Transferred.mp3)

Not every time the model can provide the solution, in that case, the call is automatically transferred to the agent, to not hamper the user experience.

### Multilingual? Yes! A Hindi customer with not providing correct information.

- [Audio Link](https://github.com/aditygrg2/ivr-llm/raw/main/sample-audios/4Multilingual_Incorrect_Pincode.mp3)

Here, the user does not provide the correct PIN code. The verification of the customer is necessary so that the agent knows that he is talking to the correct person.

### Call Fallback

- [Audio Link](https://github.com/aditygrg2/ivr-llm/raw/main/sample-audios/5Fallback_Audio.mp3)

If there is a network error or anything unexpected happens. Fallback happens accordingly.

### Technical Problem

- [Audio Link](https://github.com/aditygrg2/ivr-llm/raw/main/sample-audios/TechnicalProblem.mp3)

This is where the agent helps nicely and navigates user par with a technical issue.

### Question related to Amazon Prime

- [Audio Link](https://github.com/aditygrg2/ivr-llm/raw/main/sample-audios/AmazonPrimeRelatedQuestions.mp3)

## Setting Up Project


- Clone the project
  
```
git clone https://github.com/aditygrg2/ivr-llm

cd ivr-llm
```
- Create environment file

```
cp .sample.env .env
```

### For Linux/MacOS

#### Running Frontend

- Go to `amazon-frontend` directory
  
```
cd amazon-frontend
```

- install the packages 
```
npm install
```
> Note: Make sure you have nodejs [installed](https://nodejs.org/en/download/package-manager)
> If you are getting any dependency error do `npm install --force`

- run the project

```
npm run start
```

- You can see the website running at http://localhost:3000

#### Call Analysis Dashboard

- Go to streamlit folder

```
cd amazon-streamlit
```

- Install streamlit

```
pip install streamlit
```

- Run the dashboard

```
streamlit run app.py
```

- You can see the dashboard at http://localhost:8501


#### Running backend

- Go to the root directory of the project
- Install the python libraries

```
pip install -r req.txt
```
> Note: The recommended python version is 3.10.x

- Install `ffmpeg`

In linux run:
```
sudo apt-get install ffmpeg
```

In Mac run:
```
brew install ffmpeg
```

- Start the server

```
python app.py
```
- Server will be started at http://localhost:8000

### Creating Credentials for Gemini API

- Steps:

1. Setup Vertex AI: https://cloud.google.com/vertex-ai/docs/start/cloud-environment
2. Create ADC Credentials: https://cloud.google.com/docs/authentication/provide-credentials-adc
3. Setup the environment variable. An example Application Developer Credentials file is present as an example [here](.sample.application_default_credentials.json)

