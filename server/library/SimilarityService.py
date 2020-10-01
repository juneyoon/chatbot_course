import tensorflow as tf
import tensorflow_hub as hub

module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
sentence_encoder_model = hub.load(module_url)

def similarity_sentences(sentences, sentence, sentences_embeddings=None):
    sentence_embedding = sentence_encoder_model([sentence])[0]
    if sentences_embeddings is None:
        sentences_embeddings = sentence_encoder_model(sentences)
    scores = np.inner(sentence_embedding, sentences_embeddings)
    return scores
