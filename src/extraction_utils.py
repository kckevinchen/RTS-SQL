import numpy as np
import json

def get_index_for_prefix(tokens, prefix):
  s = ""
  selected_idx = None
  for idx, t in enumerate(tokens):
    s += t
    if(prefix in s):
      selected_idx = idx + 1
      break
  return selected_idx

def load_file(file_path):
    """Load a file based on its extension."""
    # Check file extension and choose appropriate loading method
    if file_path.endswith('.txt'):
        with open(file_path, 'r',encoding="utf-8") as file:
            return file.read()
    
    elif file_path.endswith('.json'):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")

def get_index_for_suffix(tokens, suffix):
  s = ""
  selected_idx = None
  for idx, t in enumerate(reversed(tokens)):
    s = t + s
    if(suffix in s):
      selected_idx = idx + 1
      break
  return -selected_idx


def get_sql_and_logit(tokens,sql_start_token = 'SELECT',sql_end_token = "</FINAL_ANSWER>"):
  all_tokens = [i[0] for i in tokens]
  all_logits = [i[1] for i in tokens]
  start_idx = get_index_for_prefix(all_tokens,sql_start_token)
  end_idx = get_index_for_suffix(all_tokens,sql_end_token)
  selected_logits = all_logits[start_idx:end_idx]
  selected_tokens = all_tokens[start_idx:end_idx]
  return "".join(selected_tokens), np.mean(selected_logits)

def extract_formated_result(result,sql_start_token = '<FINAL_ANSWER>',sql_end_token = '</FINAL_ANSWER>'):
    formated_result = []
    error_index = []
    for index,i in enumerate(result):
        cur_res = []
        for idx in range(len(i[0])):
            try:
                cur_logit  = i[1][idx]
                cur_text,cur_logit = get_sql_and_logit(cur_logit,sql_start_token = sql_start_token,sql_end_token = sql_end_token)
                cur_res.append((cur_text.strip(),cur_logit))
            except Exception as e:
                error_index.append(index)
        if(cur_res):
            formated_result.append(cur_res)
        else:
            error_index.append(index)
    return formated_result,list(set(error_index))


def get_correct_schema(db_data):
  schema = db_data["db_text"]
  tables = db_data["tables"]
  table_dict = get_table_dict_list(schema)
  golden_schema = [table_dict[i.lower()] for i in tables]
  return golden_schema