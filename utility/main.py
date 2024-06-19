
class Helper():

    def __init__(self) -> None:
        pass

    def get_audio_score_for_agent(self, call_sent):
        count = {'pos':0,'neu':0,'neg':0}
        for item in call_sent:
            if item['type']=="AI":
                if item['sent'] == 'neu':
                    item['sent'] = 'neu'
                count[item['sent']] = count[item['sent']] + 1
        return count

    def get_audio_score_for_customer(self, call_sent):
        count = {'pos':0,'neu':0,'neg':0}
        for item in call_sent:
            if item['type']=="human":
                if item['sent'] == 'neu':
                    item['sent'] = 'neu'
                count[item['sent']] = count[item['sent']] + 1
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
        audio_analysis = self.get_audio_score(call_data['call_sent'])
        return {"phone_number": call_data['phone_number'], "contact_sentiment":audio_analysis['contact_sentiment'],"agent_sentiment": audio_analysis['agent_sentiment'],"customer_feedback_rating": call_data['feedback']['score'],"customer_feedback_text":call_data['feedback']['text']}

    def create_analysis(self, call_list):
        recent = self.get_recent_call_analysis(call_list)
        sentiment_list = []
        for call in call_list:
            sentiment_list.append(self.calculate_call_sentiment(call))

        return {"recent":recent, "sentiment_list": sentiment_list}