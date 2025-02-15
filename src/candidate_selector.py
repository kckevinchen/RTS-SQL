from src.extraction_utils import load_file
class CandidateSelector:
    def __init__(self, ranking_oracle, prompt_template="template/candidate_selection.txt"):
        """
        Initializes the CandidateSelector with a ranking oracle.
        
        :param ranking_oracle: A callable that takes a list of SQL queries and ranks them.
        """
        self.ranking_oracle = ranking_oracle
        self.prompt_template = load_file(prompt_template)

    def generate_score_for_candidates(self, candidate, user_question, schema, hint=""):
        """
        Generate the score for candidate SQL query from a list of candidates.
        
        :param candidates: A list of candidate SQL queries.
        :param user_question: The natural language question from the user.
        :param schema: The database schema as a string or structured format.
        :return: The best-ranked SQL query.
        """
        llm_out = self.prompt_template.format(generated_sql=candidate,input_query=user_question, schema=schema, hint=hint)
        return llm_out
    def extract_prob():
        pass