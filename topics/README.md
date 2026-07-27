# topics/ — topic_match

**Purpose:** text model to control the topic confounder. Decision tree on word features from title/abstract, Naïve Bayes as comparison; honest evaluation via cross-validation and confusion matrix.
**Owner:** Pierre
**Input:** titles/abstracts from `data/` (OpenAlex inverted index)
**Output:** `topic_match` per (author, journal, t) + soft labels (probabilities) for the EM coupling in `nets/`
