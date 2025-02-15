from openai import OpenAI
import anthropic
import numpy as np
anyscale_client = OpenAI(
    base_url = "https://api.endpoints.anyscale.com/v1",
    api_key = "esecret_shp3b2pv3sapkiymb2kz8hnd89"
)

anthropic_client = anthropic.Anthropic(
    api_key="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",
)

openai_client = OpenAI(api_key="sk-proj-ytNUcIPyuxJTjzsEyLjnT3BlbkFJ9vBCOqB8zPsWOtNQp6k5")


# def generate_llama2

def get_model_response(client,prompt,system_prompt=None, model="gpt-4o-mini",n=1,**kwargs):
  if(system_prompt is None):
    messages = [
        {"role": "user", "content": prompt}
      ]
  else:
    messages = [{"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
      ]
  response = client.chat.completions.create(
    model=model,
    messages=messages,
    n = n,
    **kwargs
  )
  return response

def get_claude_response(client,prompt,system_prompt,temperature, top_p,max_tokens, model="claude-3-sonnet-20240229"):
  if(system_prompt is None):
    response = client.messages.create(
      model=model,
      messages=prompt,
      max_tokens = max_tokens,
      temperature = temperature,
      top_p = top_p
    )
  else:
    system_prompt = system_prompt["content"]
    response = client.messages.create(
      model=model,
      system=system_prompt,
      messages=prompt,
      max_tokens = max_tokens,
      temperature = temperature,
      top_p = top_p
    )
  return response


def extract_log_prob(logprob_lst):
  result = []
  # found = False
  for i in logprob_lst:
    # if(i.token == "SELECT"):
    #   found = True
    # if(not found):
    #   continue
    result.append((i.token,i.logprob))
  # assert result[0][0] == 'SELECT'
  return result