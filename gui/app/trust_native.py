"""Unedited six TrustRAG filter functions; provenance records original source hashes."""
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from nltk.translate.bleu_score import sentence_bleu
from rouge_score import rouge_scorer
from itertools import combinations

def calculate_similarity(embedding1, embedding2):
    similarity = cosine_similarity([embedding1], [embedding2])
    return similarity[0][0]

def calculate_pairwise_rouge(sent1,sent2, rouge_types=['rouge1', 'rougeL']):

    scorer = rouge_scorer.RougeScorer(rouge_types, use_stemmer=True)
    score = scorer.score(sent1, sent2)

    return score

def calculate_pairwise_bleu(sentences):

    results = []
    tokenized_sentences = [sentence.split() for sentence in sentences]
    
    for (i, sent1), (j, sent2) in combinations(enumerate(tokenized_sentences), 2):
        score = sentence_bleu([sent1], sent2)
        results.append(((i, j), score))
    
    return results

def calculate_average_score(sent1,sent2, metric='rouge'):
    if metric == 'bleu':
        results = calculate_pairwise_bleu(sent1,sent2)
    elif metric == 'rouge':
        results = calculate_pairwise_rouge(sent1,sent2, rouge_types=['rougeL'])

    return results['rougeL'].fmeasure

def group_n_gram_filtering(topk_contents):
    current_del_list = []
    temp_save_list = []
    for index, sentence in enumerate(topk_contents):
        if index in current_del_list:
            pass
        else:
            for index_temp in range(index+1,len(topk_contents)):
                if calculate_average_score(topk_contents[index], topk_contents[index_temp],'rouge') > 0.25:
                    current_del_list.append(index)
                    current_del_list.append(index_temp)
                    temp_save_list.append(topk_contents[index])
                    break
            if len(temp_save_list)!=0:
                if calculate_average_score(topk_contents[index], temp_save_list[0],'rouge') > 0.25:
                    current_del_list.append(index)
    return list(set(current_del_list))

def k_mean_filtering(embedding_topk, topk_contents, adv_text_set, n_gram):
    if n_gram:
        n_gram_flag = 0
        metric = 'rouge' 
        for sentence in range(len(topk_contents)):
            for sentence_1 in range(sentence + 1, len(topk_contents)):
                score = calculate_average_score(topk_contents[sentence], topk_contents[sentence_1], metric=metric)
                if score > 0.25: 
                    n_gram_flag = 1
                    break
            if n_gram_flag==1: 
                break
        if not n_gram_flag: 
            return embedding_topk, topk_contents

    scaler = StandardScaler()
    embedding_topk_norm = scaler.fit_transform(embedding_topk) 

    length = np.sqrt((embedding_topk_norm**2).sum(axis=1))[:,None] 
    embedding_topk_norm = embedding_topk_norm / length 
    kmeans = KMeans(n_clusters=2,n_init=10,max_iter=500, random_state=0).fit(embedding_topk_norm) 
   
 
    array_1 = [topk_contents[index] for index in range(len(kmeans.labels_)) if kmeans.labels_[index] == 1] 
    array_1_emb = [embedding_topk[index] for index in range(len(kmeans.labels_)) if kmeans.labels_[index] == 1] 
    array_0 = [topk_contents[index] for index in range(len(kmeans.labels_)) if kmeans.labels_[index] == 0] 
    array_0_emb = [embedding_topk[index] for index in range(len(kmeans.labels_)) if kmeans.labels_[index] == 0] 
    
    array_1_avg=[] 
    for index in range(len(array_1)):
        for index_1 in range(index + 1, len(array_1)):
            similarity_score = calculate_similarity(array_1_emb[index], array_1_emb[index_1]) 
            array_1_avg.append(similarity_score) 

    array_0_avg=[] 
    for index in range(len(array_0)):
        for index_1 in range(index + 1, len(array_0)):
            similarity_score = calculate_similarity(array_0_emb[index], array_0_emb[index_1]) 
            array_0_avg.append(similarity_score) 

    threshold=0.88 

    if len(array_1_avg)==0: 
        if (np.mean(array_0_avg)>threshold): 
            if calculate_similarity(array_0_emb[0], array_1_emb[0]) > threshold: 
                return [],[]
            topk_contents = array_1
            topk_embeddings = array_1_emb
            return topk_embeddings,topk_contents
        else:
            topk_contents = array_0
            topk_embeddings = array_0_emb
            return topk_embeddings,topk_contents

    if len(array_0_avg)==0: 
        if (np.mean(array_1_avg)>threshold): 
            if calculate_similarity(array_0_emb[0], array_1_emb[0]) > threshold:
                return [],[]
            topk_contents = array_0
            topk_embeddings = array_0_emb
            return topk_embeddings,topk_contents
        else:
            topk_contents = array_1
            topk_embeddings = array_1_emb
            return topk_embeddings,topk_contents
   
    if np.mean(array_1_avg) > np.mean(array_0_avg):
        if  np.mean(array_0_avg) >threshold:
            return [],[]
        if np.mean(array_1_avg)<threshold:
                del_list_1 = group_n_gram_filtering(array_1)
                del_list_0 = group_n_gram_filtering(array_0)

                array_1 = [element for index, element in enumerate(array_1) if index not in del_list_1]
                array_0 = [element for index, element in enumerate(array_0) if index not in del_list_0]
                array_1_emb = [element for index, element in enumerate(array_1_emb) if index not in del_list_1]
                array_0_emb = [element for index, element in enumerate(array_0_emb) if index not in del_list_0]
                array_1.extend(array_0)
                array_1_emb.extend(array_0_emb)
                topk_contents = array_1
                topk_embeddings = array_1_emb      
        else:
            del_list_0 = group_n_gram_filtering(array_0)
            array_0 = [element for index, element in enumerate(array_0) if index not in del_list_0]
            array_0_emb = [element for index, element in enumerate(array_0_emb) if index not in del_list_0]


            topk_contents = array_0
            topk_embeddings = array_0_emb
    else:
        if  np.mean(array_1_avg) >threshold:
                return [],[]
        if np.mean(array_0_avg)<threshold:
                del_list_1 = group_n_gram_filtering(array_1)
                del_list_0 = group_n_gram_filtering(array_0)

                array_1 = [element for index, element in enumerate(array_1) if index not in del_list_1]
                array_0 = [element for index, element in enumerate(array_0) if index not in del_list_0]
                array_1_emb = [element for index, element in enumerate(array_1_emb) if index not in del_list_1]
                array_0_emb = [element for index, element in enumerate(array_0_emb) if index not in del_list_0]
                array_1.extend(array_0)
                array_1_emb.extend(array_0_emb)
                topk_contents = array_1
                topk_embeddings = array_1_emb
        
        else:
            del_list_1 = group_n_gram_filtering(array_1)
            array_1 = [element for index, element in enumerate(array_1) if index not in del_list_1]
            array_1_emb = [element for index, element in enumerate(array_1_emb) if index not in del_list_1]


            topk_contents = array_1
            topk_embeddings = array_1_emb
    return topk_embeddings,topk_contents
