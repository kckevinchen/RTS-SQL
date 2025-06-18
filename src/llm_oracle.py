from abc import ABC, abstractmethod
import openai
import concurrent.futures
import time
import random
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch.nn.functional as F
class LLMOracle(ABC):
    """
    Abstract base class for LLM oracles.
    """
    @abstractmethod
    def generate(self, prompt: str,system_prompt: str =None,**kwargs):
        pass

class OpenAIOracle(LLMOracle):
    def __init__(self, api_key: str = "", model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def generate(self, prompt: str,system_prompt: str =None,**kwargs):
        if(system_prompt is None):
            messages = [
                {"role": "user", "content": prompt}
            ]
        else:
            messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response
    

class XiYanSQLOracle(LLMOracle):
    def __init__(self, model: str = "./XiYanSQL-QwenCoder-32B-2412"):
        self.model = AutoModelForCausalLM.from_pretrained(
                        model,
                        torch_dtype=torch.bfloat16,
                        device_map="auto",
                        local_files_only=True
                    )
        self.model.eval()
        self.tokenizer = AutoTokenizer.from_pretrained(model)

    def generate(self, prompt: str, system_prompt: str = None, n=1, **kwargs):
        message = [{'role': 'user', 'content': prompt}]
        
        text = self.tokenizer.apply_chat_template(
            message,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            # Generate multiple sequences if n > 1
            outputs = self.model.generate(
                **model_inputs,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                temperature=0.5,
                top_p=0.8,
                do_sample=True,
                num_return_sequences=n,  # this is the key modification
                output_logits=True, 
                return_dict_in_generate=True
            )
        input_length = len(model_inputs[0])
        generated_ids = outputs.sequences.detach().cpu()
        logits = outputs.logits
        scores=[F.log_softmax(logits[i].detach().cpu(), dim=-1) for i in range(len(logits))]
        transition_scores = model.compute_transition_scores(
            generated_ids, scores
        )
        generated_ids = [i[input_length:] for i in generated_ids]
        generated_text = tokenizer.batch_decode(generated_ids)
        token_probs = []
        for i in range(len(transition_scores)):
            transition_score = transition_scores[i]
            generated_id = generated_ids[i]
            for token,prob in zip(generated_id,transition_score):
                token_probs.append((token.item(),prob.item()))
        return generated_text, token_probs

class DeepseekOracle(LLMOracle):
    def __init__(self, api_key: str = "", model: str = "deepseek-chat", max_retries: int = 3, backoff_factor: float = 1.5):
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.model = model
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def _generate_single(self, prompt: str, system_prompt: str, kwargs: dict) -> str:
        """
        Helper function to generate a single response from the API with retry logic.
        """
        if system_prompt is None:
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = [{"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}]
        
        retries = 0
        while retries <= self.max_retries:
            try:
                # Try making the API request
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    **kwargs
                )
                return response
            
            except Exception as e:
                # Handle specific API errors (e.g., rate limiting, timeout, etc.)
                if retries < self.max_retries:
                    retries += 1
                    # Exponential backoff with jitter
                    wait_time = (self.backoff_factor ** retries) + random.uniform(0, 1)
                    print(f"Retrying... ({retries}/{self.max_retries}) Waiting {wait_time:.2f} seconds.")
                    time.sleep(wait_time)
                else:
                    # After max retries, raise the error
                    print(f"Failed after {self.max_retries} retries.")
                    raise e
    
    def generate(self, prompt: str,system_prompt: str =None,n=1,**kwargs) -> str:
        with concurrent.futures.ThreadPoolExecutor(max_workers=n) as executor:
                    # Start n parallel requests
                    futures = [
                        executor.submit(self._generate_single, prompt, system_prompt, kwargs)
                        for _ in range(n)
                    ]
                    
                    # Wait for all futures to complete and return their results
                    responses = [future.result() for future in concurrent.futures.as_completed(futures)]
                
        return responses