#coding: utf-8 
from datetime import datetime
import json,re,nltk,gzip,string,unicodedata,time

#===============================================================================
# excecao desenvolvida para ser lancada quando um post nao tiver mensagem textual
#===============================================================================
class PostWithoutMessageException(Exception):
    pass

#===============================================================================
# remove urls
#===============================================================================
def remove_url(text):
    return re.sub(r"http\S+", "", text)

#===============================================================================
# remove numeros no texto
#===============================================================================
def remove_numbers(text):
    return re.sub(r'\d+','',text)

#===============================================================================
# tokeniza o texto - 'hello world' return ['hello','world']
#===============================================================================
def tokenization(text):
    return nltk.word_tokenize(text)

#===============================================================================
# converte o texto para minusculo
#===============================================================================
def convert_to_lower(text):
    return text.lower()

#===============================================================================
# remove todos simbolos dentro da lista string.punctuation
#===============================================================================
def remove_symbols(tokenized_pre_processed_message):
    # ponctuations less [\] because unicode patterns
    ponctuations = string.punctuation.replace('[\]','')
    new_words = []
    for word in tokenized_pre_processed_message:
        new_word = ''.join([letter for letter 
            in word if letter not in ponctuations])
        if new_word != '':
            new_words.append(new_word)
    return new_words 

#===============================================================================
# remover stop words
#===============================================================================
def replace_stop_words(tokenized_pre_processed_message):
    stop_words = [get_unicode_normalized(word) for word in nltk.corpus.stopwords.words('portuguese')]
    processed_text = [word for word in tokenized_pre_processed_message
         if word not in stop_words]
    return processed_text

#===============================================================================
# substituir todos /n dentro de um texto por um espaco em branco
#===============================================================================
def replace_break_lines(text):
    return text.replace('\n', ' ')


#===============================================================================
# substituir todas as , dentro de um texto por um espaco em branco
#===============================================================================
def replace_commas(text):
    return text.replace(',', ' ')

#===============================================================================
# funcao para chamar todas as funcoes intermediarias do pre-processamento 
#===============================================================================
def complete_pre_process_message(message):
    pre_processed_message = remove_url(message)
    pre_processed_message = get_unicode_normalized(pre_processed_message)
    pre_processed_message = convert_to_lower(pre_processed_message)
    pre_processed_message = replace_break_lines(pre_processed_message)
    pre_processed_message = remove_numbers(pre_processed_message)
    tokenized_pre_processed_message = tokenization(pre_processed_message)
    tokenized_pre_processed_message = replace_stop_words(tokenized_pre_processed_message)
    tokenized_pre_processed_message = remove_symbols(tokenized_pre_processed_message)
    return tokenized_pre_processed_message

#===============================================================================
# funcao para chamar algumas funcoes intermediarias do pre-processamento 
#===============================================================================
def partial_pre_process_message(message):
    pre_processed_message = get_unicode_normalized(message)
    pre_processed_message = replace_commas(pre_processed_message)
    pre_processed_message = convert_to_lower(pre_processed_message)
    pre_processed_message = replace_break_lines(pre_processed_message)
    tokenized_pre_processed_message = tokenization(pre_processed_message)
    return tokenized_pre_processed_message

#===============================================================================
# retorna a lista com os posts do path passado como parametro
 #==============================================================================
def get_list_posts_from_path(posts_file_path):
    with gzip.open(posts_file_path) as post_file:
        post_list =  post_file.readlines()
    return post_list

#===============================================================================
# normaliza os textos removendo caracteres nao ascii
#===============================================================================
def get_unicode_normalized(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf8')

#===============================================================================
# retorna lista com o par chave/valor de menssagens pre-processadas
#===============================================================================
def generate_list_pre_processed_posts(post_list):
    pre_processed_post_list = []
    for post in post_list:
        try:
            if not isinstance(post,dict):
                dict_post = json.loads(post)
            if not 'message' in dict_post.keys() or dict_post['message'] =='':
                raise PostWithoutMessageException('this post does not have message')
            message = dict_post["message"]
            dict_post["pre_processed_message"] = complete_pre_process_message(message)
            dict_post['message_min_processed'] = partial_pre_process_message(message)
            dict_post['has_textual_message'] = True
            pre_processed_post_list.append(dict_post)
        except PostWithoutMessageException as err:
            dict_post['has_textual_message'] = False
            dict_post["pre_processed_message"] = ' '
            dict_post['message_min_processed'] = ' '
            pre_processed_post_list.append(dict_post)
    return pre_processed_post_list

#===============================================================================
# converte list para str - ['hello','world'] -> 'hello world'
#===============================================================================
def join_tokenized_message(tokenized_message):
    if tokenized_message == None:
        return None
    elif tokenized_message == []:
        return ' '
    else:
        message_str = ' '
        message_str = message_str.join(tokenized_message)
        return message_str


def write_list_in_csv_file(pre_processed_post_list,output_file,political_collection):
    with open(output_file, 'wt') as file:
        file.write('created_time,id,pre_processed_message,message_min_processed,shares,status_type,full_picture,reactions_like,reactions_haha,reactions_wow,reactions_sad,reactions_angry,reactions_love,has_textual_message,author\n')
        for processed_post in pre_processed_post_list:
            file.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14}\n'
                .format(str(processed_post['created_time']),
                        str(processed_post['id']),
                        str(join_tokenized_message(processed_post['pre_processed_message'])),
                        str(join_tokenized_message(processed_post['message_min_processed'])),
                        str(processed_post['shares']['count'] if ('shares' in processed_post) else 0),
                        str(processed_post['status_type']),
                        str(processed_post['full_picture'] if ('full_picture' in processed_post) else None),
                        str(processed_post['reactions_like']['summary']['total_count']),
                        str(processed_post['reactions_haha']['summary']['total_count']),
                        str(processed_post['reactions_wow']['summary']['total_count']),
                        str(processed_post['reactions_sad']['summary']['total_count']),
                        str(processed_post['reactions_angry']['summary']['total_count']),
                        str(processed_post['reactions_love']['summary']['total_count']),
                        str(processed_post['has_textual_message']),
                        str(political_collection)
                )
            )

