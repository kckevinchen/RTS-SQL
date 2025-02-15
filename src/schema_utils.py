import sql_metadata
from sql_metadata import Parser
import sqlparse
import re
end_token = ');'
def is_quoted_string(string):
    return string.startswith("'") and string.endswith("'") or string.startswith('"') and string.endswith('"')
def wrap_with_quotes_if_needed(input_string):
    # Check if the string contains a space and is not wrapped with double quotes
    if " " in input_string and not (is_quoted_string(input_string)):
        input_string = input_string.replace('"',"'")
        # Wrap the string with double quotes
        if input_string.endswith("'"):
            return f"'{input_string}"
        elif input_string.startswith("'"):
            return f"{input_string}'"
        else:
          return f"'{input_string}'"
    return input_string

def convert_sql_to_template(sql):
    table_token = "|TABLE|"
    column_token = "|COLUMN|"
    subquery_name = "|QUERY|"
    table_type = sql_metadata.keywords_lists.TokenType.TABLE
    column_type = sql_metadata.keywords_lists.TokenType.COLUMN
    alias = sql_metadata.keywords_lists.TokenType.TABLE_ALIAS
    # subquery_name = sql_metadata.keywords_lists.TokenType.SUB_QUERY_NAME
    sql_list = Parser(sqlparse.format(sql))
    sql_list.columns
    sql_list.tables
    template = []
    correct_value = []
    for token in sql_list.tokens:
      if(token.token_type == table_type):
          template.append(table_token)

          correct_value.append(wrap_with_quotes_if_needed(token.value))
      elif(token.token_type == column_type):
            template.append(column_token)
            correct_value.append(wrap_with_quotes_if_needed(token.value))
      # elif(token.is_keyword and token.value.lower() == "as"):
      #     continue
      # elif(not token.is_keyword and token.token_type == alias):
      #     continue
      elif(not token.is_keyword):
          template.append(wrap_with_quotes_if_needed(token.value))
      else:
          template.append(token.value)
                # sql_list.subqueries_names
    return sqlparse.format(" ".join(template)),correct_value

def find_table_name(text):
        # Regular expression pattern to extract the table name
    # pattern = re.compile(r'CREATE\s+TABLE\s+(\w+)\(', re.IGNORECASE)
    pattern = re.compile(r'CREATE\s+TABLE\s+([A-Za-z_][A-Za-z0-9_\-\s]*)\s*\(', re.IGNORECASE)

    # Search for the pattern in the SQL script
    match = pattern.search(text)

    if match:
        table_name = match.group(1)
    else:
        print(text)
        print("Table name not found.")
        table_name = None
    return table_name


def lowercase_schema(sql_script):
    # Convert CREATE TABLE statements to lowercase table names

    # Convert column names to lowercase
    sql_script = re.sub(r'(?i)(\b[\w\s]+)(\s+\w+)', lambda match: match.group(1).lower() + match.group(2).upper(), sql_script)
    sql_script = re.sub(r'(?i)(CREATE TABLE )([\w\s]+)', lambda match: match.group(1).upper() + match.group(2).lower(), sql_script)
    return sql_script


def get_all_column_names(table_text):
    # Remove comments from the SQL statement
    sql_statement = re.sub(r"/\*.*?\*/", "", table_text, flags=re.DOTALL).strip()
    # Extract the part of the statement that contains the column definitions
    columns_part = re.search(r"\((.*?)\)", sql_statement, re.DOTALL).group(1)
    # Regular expression to match column names
    column_pattern = re.compile(r"\s*([a-zA-Z_][a-zA-Z0-9_ ]*)\s+[a-zA-Z]+")

    # Find all matches in the SQL statement
    matches = column_pattern.findall(columns_part)

    matches = [match.strip() for match in matches]
    # Print column names
    return matches

def find_table_name(text):
        # Regular expression pattern to extract the table name
    # pattern = re.compile(r'CREATE\s+TABLE\s+(\w+)\(', re.IGNORECASE)
    pattern = re.compile(r'CREATE\s+TABLE\s+([A-Za-z_][A-Za-z0-9_\-\s]*)\s*\(', re.IGNORECASE)

    # Search for the pattern in the SQL script
    match = pattern.search(text)

    if match:
        table_name = match.group(1)
    else:
        print(text)
        print("Table name not found.")
        table_name = None
    return table_name
def get_table_dict(text):
    cur = []
    tables = {}
    for i in text.split("\n"):
        if(not i):
            continue
        if(i != end_token):
            cur.append(i)
        else:
            cur.append(i)
            table_text = "\n".join(cur)
            # table_text = lowercase_schema(table_text)
            table_name = find_table_name(table_text).lower()
            tables[table_name] = table_text
            cur = []
    return tables

def get_table_dict_list(text_list):
    cur = []
    tables = {}
    for table_text in text_list:
        table_name = find_table_name(table_text).lower()
        tables[table_name] = table_text
    return tables
def get_table_column(column):
    tables = {}
    for i in column:
        table,col = i.split(".")[0],i.split(".")[-1]
        if(table.lower() != "t"):
            tables.setdefault(table.lower(),[]).append(col.lower())
    return tables

def extract_column_from_text(text):
    table_header = ""
    column_dict = {}
    found_header = False
    cur = []
    for i in text.split("\n"):
        if(i.startswith("/*")):
            cur.append(i)
        elif(i.startswith(");")):
            break
        else:
            cur.append(i)
            if(found_header):
                column_name = " ".join(i.split()[:-1])
                column_dict[column_name.lower()] = "\n".join(cur)
            else:
                table_header = "\n".join(cur)
                found_header = True
            cur = []
    return table_header, column_dict

def get_correct_schema(db_data):
  schema = db_data["db_text"]
  tables = db_data["tables"]
  table_dict = get_table_dict_list(schema)
  golden_schema = [table_dict[i.lower()] for i in tables]
  return golden_schema