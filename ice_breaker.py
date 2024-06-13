from typing import Tuple
from langchain.prompts.prompt import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from third_parties.linkedin import scrape_linkedin_profile
from third_parties.twitter import scrape_user_tweet
from agents.linkedin_lookup_agent import lookup as linkedin_lookup_agent
from agents.twitter_lookup_agent import lookup as twitter_lookup_agent
from output_parsers import summary_parser, Summary

def ice_break_with(name: str) -> Tuple[Summary, str]:
    linkedin_username = linkedin_lookup_agent(name=name)
    linkedin_data = scrape_linkedin_profile(linkedin_profile_url=linkedin_username)

    twitter_username = twitter_lookup_agent(name=name)
    tweets = scrape_user_tweet(username=twitter_username)

    summary_template = """
        given the information about a person from linkedin {information},
        and their latest twitter posts {twitter_posts} I want you to create:
        1. A short summary
        2. two interesting facts about them 

        Use both information from twitter and Linkedin
        \n{format_instructions}
        """
    summary_prompt_template = PromptTemplate(
        input_variables=["information", "twitter_posts"], template=summary_template,
        partial_variables={"format_instructions": summary_parser.get_format_instructions()},
    )

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    #chain = summary_prompt_template | llm
    chain = summary_prompt_template | llm | summary_parser
    res:Summary = chain.invoke(input={"information": linkedin_data, "twitter_posts":tweets})
    
    return res, linkedin_data.get("profile_pic_url")


if __name__ == "__main__":
    load_dotenv()
    print("Ice Breaker Enter")
    ice_break_with(name="Harrison Chase Langchain")
