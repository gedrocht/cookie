# from nemo_text_processing.text_normalization.normalize import Normalizer
from nemo.collections.nlp.data.text_normalization.normalize import Normalizer


normalizer = Normalizer(lang="en")
text = "Dr. Smith earned $2.5 million in 2023."
normalized_text = normalizer.normalize(text)
print(normalized_text)  # Output might be "Doctor Smith earned two point five million dollars in twenty twenty-three."

