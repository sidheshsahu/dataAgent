from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

def pick_llm(level: str):
    if level.lower() == "low":
        llm = ChatGroq()
    elif level.lower() == "medium":
        llm = ChatGroq()
    elif level.lower() == "high":
        llm = ChatGroq()
    else:
        raise ValueError(f"Unsupported level: {level}")

    return llm

if __name__ == "__main__":
    llm_obj = pick_llm("low")  
    print(llm_obj.invoke("What is the capital of France?"))
