from src.extraction_utils import load_file
class CandidateGenerator:
    def __init__(self, llm_oracle, prompt_path="template/generate_candidate_json.txt"):
        """
        Initializes the CandidateGenerator with two oracles.
        
        :param llm_oracle: A callable that takes a prompt and returns an SQL query.
        :param prompt_template: A prompt template for generating SQL queries.
        """
        self.llm_oracle = llm_oracle
        self.prompt_template = load_file(prompt_path)
    def process_output(self, chat_completions):
        if(isinstance(chat_completions, tuple)):
            return chat_completions
            
        generated_messages = []
        all_logprobs = []
        for chat_completion in chat_completions:
            logprobs = chat_completion.choices[0].logprobs.content
            generated_message = chat_completion.choices[0].message.content

            # Print logprobs for each token
            logprobs_lst = []
            for token_info in logprobs:
                logprobs_lst.append((token_info.token,token_info.logprob))
            generated_messages.append(generated_message)
            all_logprobs.append(logprobs_lst)

        return generated_messages, all_logprobs
    def generate_candidates(self, input_query, schema, hint= "", k = 5, logprobs=True):
        """
        Generates candidate SQL queries for a given user question and database schema.
        
        :param user_question: The natural language question from the user.
        :param schema: The database schema as a string or structured format.
        :param hint: The hint from the user.
        :param k: The number of candidates.
        :return: A list of candidate SQL queries and logit
        """
        prompt = self.prompt_template.format(dialect='SQLite',input_query=input_query, schema=schema, hint=hint)
        
        llm_out = self.llm_oracle.generate(prompt,n=k,logprobs=logprobs)
        return self.process_output(llm_out)