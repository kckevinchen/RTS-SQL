from src.extraction_utils import load_file
class QueryFixer:
    def __init__(self, llm_oracle,prompt_path="template/sql_fixer.txt"):
        """
        Initializes the QueryFixer with an LLM oracle.
        
        :param llm_oracle: A callable that takes a faulty SQL query and an error message and returns a fixed query.
        """
        self.llm_oracle = llm_oracle
        self.prompt_template = load_file(prompt_path)

    def fix_query(self, sql_query, error_message, schema):
        """
        Attempts to fix an invalid SQL query given the error message and schema.
        
        :param sql_query: The SQL query that failed execution.
        :param error_message: The error message returned from execution.
        :param schema: The database schema as a string or structured format.
        :return: A refined SQL query.
        """
        prompt = self.template.format(sql=sql_query,schema=schema,error_message=error_message)
        return self.llm_oracle(prompt)