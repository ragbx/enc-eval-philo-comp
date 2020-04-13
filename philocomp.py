import pandas as pd
import numpy as np

def get_heatmap(lda_model, num_topics, corpus, corp, data):
    """
    Création d'une carte de chaleur
    """
    topics = [lda_model[corpus[i]] for i in range(len(data))]
    def topics_document_to_dataframe(topics_document, num_topics):
        res = pd.DataFrame(columns=range(num_topics))
        for topic_weight in topics_document:
            res.loc[0, topic_weight[0]] = topic_weight[1]
        return res
    document_topic = pd.concat([topics_document_to_dataframe(topics_document, num_topics=num_topics) for topics_document in topics]).reset_index(drop=True).fillna(0)
    doc_columns = [f"th_{i:02}" for i in np.arange(1,num_topics+1,1)]
    document_topic.columns = doc_columns
    metadata = corp[['id_piece']]
    metadata = metadata.reset_index()
    metadata['leg'] = metadata['index'].astype(str) + '_' + metadata['id_piece']
    metadata = metadata[['id_piece']]
    result = pd.merge(metadata, document_topic, left_index=True, right_index=True)
    return result.set_index('id_piece')


def get_lemmas(df):
    """
    Renvoie sous forme de Series l'ensemble des mots contenus dans un dataframe d'échantillons.
    """
    words = []
    for text in df['lemmes'].str.split():
        if type(text) is list:
            for word in text:
                words.append(word)
    return pd.Series(words)

def get_freq_lemmas(lemmas, max_cum_freq, pref_file_out=None):
    """
    En entrée, une Series de mots, en sortie les fréquences de ces mots.
    """
    df = pd.DataFrame(lemmas.value_counts())
    df = df.reset_index().rename(columns={'index': 'lemma', 0: 'freq'})
    df['cum_freq'] = 100*df.freq.cumsum()/df.freq.sum()

    out = df[df['cum_freq'] <= max_cum_freq]
    if pref_file_out:
        file_out = f"resultats/{pref_file_out}_stop{max_cum_freq}.csv"
        out.to_csv(file_out, header=True, index=False)
    return out

def remove_stop_words(text, stop_words):
    lemmas_list = text.split()
    lemmas_list_without_stop_words = [item for item in lemmas_list if item not in stop_words]
    #lemmas_without_stop_words = " ".join(lemmas_list_without_stop_words)
    return " ".join(lemmas_list_without_stop_words)

def get_prc_contrib(x):
    if x:
        return round(x[1], 4)* 100

def get_topics_contrib_by_doc(model, corpus, documents, pref_file_out=None):
    topics_df = pd.DataFrame(model[corpus])
    for i in topics_df.columns:
        n = i + 1
        col_name = f"th_{n:02}"
        topics_df[col_name] = topics_df[i].apply(get_prc_contrib)
        topics_df = topics_df.drop(columns=i)
    topics_df = topics_df.unstack()
    topics_df = topics_df.reset_index()
    topics_df.columns = ['thème', 'indice_doc', 'prc_contribution']
    metadata = documents[['id_piece', 'genre', 'inspiration']]
    metadata = metadata.reset_index()
    metadata.columns = ['indice_doc', 'id_piece', 'genre', 'inspiration']
    result = pd.merge(topics_df, metadata, on='indice_doc')
    if pref_file_out:
        file_out = f"resultats/{pref_file_out}_topics_contrib_by_doc.xlsx"
        result.to_excel(file_out, index=False)
    return result

def get_main_topic_by_doc(lda_model, corpus, documents, pref_file_out=None):
    topics_main_contrib_df = pd.DataFrame()
    for i, row_list in enumerate(lda_model[corpus]):
        row = row_list[0] if lda_model.per_word_topics else row_list
        row = sorted(row, key=lambda x: (x[1]), reverse=True)
        for j, (topic_num, prc_contribution) in enumerate(row):
            if j == 0:
                topic_num = topic_num + 1
                topic = f"th_{topic_num:02}"
                topics_main_contrib_df = topics_main_contrib_df.append(pd.Series([topic, round(prc_contribution,4) * 100]), ignore_index=True)
            else:
                break
    topics_main_contrib_df = topics_main_contrib_df.reset_index()
    topics_main_contrib_df.columns = ['indice_doc', 'thème', 'prc_contribution']
    metadata = documents[['id_piece', 'genre', 'inspiration']]
    metadata = metadata.reset_index()
    metadata.columns = ['indice_doc', 'id_piece', 'genre', 'inspiration']
    result = pd.merge(topics_main_contrib_df, metadata, on='indice_doc')
    if pref_file_out:
        file_out = f"resultats/{pref_file_out}_main_topic_by_doc.xlsx"
        result.to_excel(file_out, index=False)
    return result

def print_topics(lda_model):
    topics = lda_model.print_topics()
    for topic in topics:
        topic_ind = topic[0] + 1
        print(f"Thème : th_{topic_ind:02}\nmots : {topic[1]}\n")
