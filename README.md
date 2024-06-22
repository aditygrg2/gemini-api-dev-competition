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

## Audio Demos with Different Scenarios

### Good Case Complete Call

- [Audio Link](sample-audios/

This call is a sample of a completely successful good case where all conversations are smooth. There are no mistakes on the client side and hopefully, everything goes well.

### Call with an angry/frustrated customer

- [Audio Link](sample-audios/

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
sudo apt-get update
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

### Creating credentials for Gemini API

