from app.services.summarizer import summarize_text

sample_text = """
Java is a high-level programming language used to build enterprise,
mobile, and web applications. It follows object-oriented principles
and is platform-independent.
"""

summary = summarize_text(sample_text, depth="easy")
print("SUMMARY:\n", summary)
