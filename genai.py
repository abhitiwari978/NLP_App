from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage

load_dotenv()


embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# === 2. Load Gemini Pro LLM ===
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.2
)

def sentiment_check(user_text):
    # messages=[
    # SystemMessage(content="you are a sentiment analyst if there are negative words in text show NEGATIVE and if positive consent then POSITIVE else NUETRAl")
    # ]
    # messages.append(HumanMessage(content=user_text))
    # result = llm.invoke(user_text)
    # return result
    txt="you are a sentiment analyst if there are negative words or consent in text show NEGATIVE and if positive consent then POSITIVE else NUETRAl:"+user_text

    result = llm.invoke(txt)
    return result.content

def emotion_check(user_text):

    txt="you are a emotion detector, based on the user text tell that what is the sentiment by the consent of text and show in one word like HAPPY, SAD, ANGRY, BORED, EXCITED, FEAR,etc:"+user_text

    result = llm.invoke(txt)
    return result.content

