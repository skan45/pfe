import logging
import os
from typing import Dict, Any

class LangChainProvider:
    """Service for interacting with Gemini via LangChain"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        """Initialize with API key and model"""
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key
        self.model_name = model
        
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain.prompts import PromptTemplate
            from langchain.chains import LLMChain, MultiPromptChain
            from langchain.chains.router import LLMRouterChain
            from langchain.memory import ConversationBufferMemory

            self.ChatGoogleGenerativeAI = ChatGoogleGenerativeAI
            self.PromptTemplate = PromptTemplate
            self.LLMChain = LLMChain
            self.MultiPromptChain = MultiPromptChain
            self.LLMRouterChain = LLMRouterChain
            self.ConversationBufferMemory = ConversationBufferMemory
            
            self.llm = ChatGoogleGenerativeAI(model=self.model_name, temperature=0, google_api_key=api_key)
            self.logger.info(f"Gemini initialized with model: {model}")
            
        except ImportError as e:
            self.logger.error(f"Gemini or LangChain package missing: {e}. Install with: pip install langchain-google-genai langchain")
            raise ImportError("Install with: pip install langchain-google-genai langchain")

    def create_chain(self, template: str) -> Any:
        self.logger.info("Creating Gemini chain")

        try:
            prompt = self.PromptTemplate(
                input_variables=["document_type", "extracted_data"],
                template=template
            )
            memory = self.ConversationBufferMemory()
            chain = self.LLMChain(
                llm=self.llm,
                prompt=prompt,
                memory=memory,
                verbose=True
            )
            self.logger.info("Successfully created Gemini chain")
            return chain

        except Exception as e:
            self.logger.error(f"Error creating Gemini chain: {str(e)}")
            raise

    def create_multi_chain_router(self, prompt_infos: Dict[str, Dict[str, Any]]) -> Any:
        self.logger.info("Creating Gemini multi-chain router")

        try:
            destination_chains = {}
            for name, info in prompt_infos.items():
                prompt = self.PromptTemplate(
                    template=info["template"],
                    input_variables=info["input_variables"]
                )
                chain = self.LLMChain(llm=self.llm, prompt=prompt)
                destination_chains[name] = chain

            router_template = """Given the following document information, decide which specialized chain should handle it.

            Document Type: {document_type}

            Available chains:
            {destinations}

            Choose the chain that best matches the document type.
            """
            router_prompt = self.PromptTemplate(
                template=router_template,
                input_variables=["document_type", "destinations"]
            )

            # This output parser can be replaced by your custom logic
            from langchain.output_parsers import RegexParser
            output_parser = RegexParser(regex=".*", output_keys=["destination"])

            router_chain = self.LLMRouterChain.from_llm(
                self.llm,
                router_prompt,
                output_parser
            )

            chain = self.MultiPromptChain(
                router_chain=router_chain,
                destination_chains=destination_chains,
                default_chain=destination_chains[list(destination_chains.keys())[0]],
                verbose=True
            )

            self.logger.info("Successfully created Gemini multi-chain router")
            return chain

        except Exception as e:
            self.logger.error(f"Error creating Gemini multi-chain router: {str(e)}")
            raise

    def add_agents(self, chain, tools=None):
        self.logger.info("Adding agent capabilities to Gemini chain")

        try:
            from langchain.agents import initialize_agent, AgentType

            if tools is None:
                from langchain.tools.python.tool import PythonREPLTool
                tools = [PythonREPLTool()]

            agent = initialize_agent(
                tools=tools,
                llm=self.llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True
            )

            self.logger.info("Successfully added agent capabilities")
            return agent

        except Exception as e:
            self.logger.error(f"Error adding agent capabilities: {str(e)}")
            raise

    def create_document_qa_chain(self):
        self.logger.info("Creating document QA chain with Gemini")

        try:
            from langchain.chains.question_answering import load_qa_chain
            qa_chain = load_qa_chain(self.llm, chain_type="stuff")

            self.logger.info("Successfully created document QA chain")
            return qa_chain

        except Exception as e:
            self.logger.error(f"Error creating document QA chain: {str(e)}")
            raise
