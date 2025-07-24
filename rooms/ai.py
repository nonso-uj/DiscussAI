from transformers import pipeline
import torch

device = 0 if torch.cuda.is_available() else -1

summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6",
    tokenizer="sshleifer/distilbart-cnn-12-6",
    device=device,
)

tokenizer = summarizer.tokenizer

# Warm-up call to load everything into memory
_ = summarizer("This is a warm-up example to prepare model", max_length=50, min_length=10, do_sample=False)
