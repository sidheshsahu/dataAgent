from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI



load_dotenv()

def pick_llm(level: str):
    if level.lower() == "low":
        llm = ChatGroq(model="openai/gpt-oss-120b")
    elif level.lower() == "high":
        llm = ChatGroq(model="openai/gpt-oss-120b")
    else:
        raise ValueError(f"Unsupported level: {level}")

    return llm

if __name__ == "__main__":
    llm_obj = pick_llm("low")  
    print(llm_obj.invoke("What is the capital of France?"))
