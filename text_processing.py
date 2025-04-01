import re
import pandas as pd
import spacy
nlp = spacy.load("en_core_web_sm")
from sentence_dataframe import pos
from textblob import TextBlob


universal = ["all", "every", "each"]
existential = ["some", "no"]
global token


def check_iff(text, df_index, pos_df):
    expressions = ["if and only if", "precisely when", "just in case", "exactly when", "when and only when", "if, but only if"]
    negatives = ["it is not the case that", "it is not true that"]
    
    for neg in negatives:
        if neg in text:
            text = text.replace(neg, "NOT")


    split_parts = [text] 

    for expression in expressions:
        temp_parts = []
        for part in split_parts:
            if expression in part:
                split_result = part.split(expression)
                temp_parts.extend(split_result)
            else:
                temp_parts.append(part)        
        split_parts = temp_parts 
    split_parts = [part.strip() for part in split_parts if part.strip()]
    if len(split_parts)>1:
        pos_df.loc[df_index, "Iff operator"] = str(len(split_parts)-1)
    
    
    
    return split_parts, pos_df


def check_period(text,df_index, pos_df):
    sentences = re.split(r'[.?!](?!\s*(therefore|thus|so)\b)', text)
    sentences = [sentence.strip() for sentence in sentences if sentence and sentence.strip()]
    if len(sentences)>1:
        pos_df.loc[df_index, "And operator"] = str(len(sentences)-1)
    return sentences, pos_df


    
def split_by_conjunctions(doc, df_index, pos_df):
    doc = [token for token in doc if token.text != ',']
    
    split_parts = []
    current_part = []
    remaining_text = [token.text for token in doc]
    length_orig_text = len(remaining_text)
    length_curr_text = len(remaining_text)
    index = 0
    length = len(doc)
    found_verb = False
    for index in range(length):
        current_part = [tok for tok in current_part if not tok.is_space]
        
        if len(current_part) == 0:
            updated_text = " ".join(t for t in remaining_text)
            doc = nlp(updated_text)
            length_curr_text = len(remaining_text)
            found_verb = False
        token_index = index-(length_orig_text-length_curr_text)
        token = doc[token_index]
        

        if index == length-1 and token.dep_ != "punct":
            current_part.append(token)
            split_parts.append(current_part)
            break
        elif index == length-1 and token.dep_ == "punct":
            split_parts.append(current_part)
            break

        if token.text == "NOT":
            pos_df.loc[df_index, "Not operator"] += " " +str(len(split_parts))+" all"
            
        elif token.dep_ == "ROOT" or token.dep_ == "advcl" or token.dep_ == "aux":
            found_verb = True
            current_part.append(token)

        elif token.dep_ == "mark" and token.text != "that": # if, because, since
            if token.text in {"because", "since"}:
                if len(current_part) > 0: #I cry because I am sad
                    
                    split_parts.append(current_part)
                    current_part = []
                
                and_input = " "+ str(len(split_parts)-1) + str(len(split_parts))
                
                pos_df.loc[df_index, "And operator"] += and_input
                
            else:
                if len(current_part) > 0: #I cry if I am sad
                    ifthen_input = " "+ str(len(split_parts)+1) +str(len(split_parts))
                    split_parts.append(current_part)
                    current_part = []
                else: #If I am sad I cry
                    ifthen_input = " "+ str(len(split_parts)) + str(len(split_parts)+1)
                
                pos_df.loc[df_index, "If-then operator"] += ifthen_input

        elif  token.dep_ in {'cc', 'punct', 'advmod'}:
            

            if token.text in {"therefore", "thus", "so"}:
                 #I cry therefore I am sad
                if len(current_part)>0:
                    split_parts.append(current_part)
                ifthen_input = " "+ str(len(split_parts)-1) +str(len(split_parts))
                pos_df.loc[df_index, "If-then operator"] += ifthen_input
                current_part = []
            elif token.text == "when":
                if len(current_part) > 0: #I cry when I am sad
                    ifthen_input = " "+ str(len(split_parts)+1) + str(len(split_parts))
                    split_parts.append(current_part)
                    current_part = []
                else: #When I am sad I cry
                    ifthen_input = " "+ str(len(split_parts)) +str(len(split_parts)+1)
                pos_df.loc[df_index, "If-then operator"] += ifthen_input
            elif token.text == "then":
                split_parts.append(current_part)
                current_part = []

            elif token.dep_ == 'cc'and found_verb == True:
                
                if index < length-2 and doc[token_index+1].dep_ == "conj" and ( doc[token_index+1].head.dep_ != "ROOT" and doc[token_index+2].head.dep_ != "ROOT" and doc[token_index+2].dep_ != "aux" and doc[token_index+2].dep_ != "ROOT" ):
                    current_part.append(token)
                elif index < length-3 and doc[token_index+2].dep_ == "conj"and (doc[token_index+1].head.dep_ != "ROOT" and doc[token_index+2].head.dep_ != "ROOT" and doc[token_index+3].dep_ != "aux" and doc[token_index+3].dep_ != "ROOT" ):
                    current_part.append(token)
                elif (index == length-2 and doc[token_index+1].dep_ == "conj"and (doc[token_index+1].head.dep_ == "dobj" or doc[token_index+1].head.dep_ == "nsubj" or doc[token_index+1].head.dep_ == "conj" or doc[token_index+1].pos_ == "NOUN")):
                    current_part.append(token)
                

                elif token.text == "or":
                    split_parts.append(current_part)
                    current_part = []
                    or_input = " "+ str(len(split_parts)-1)+ str(len(split_parts))
                    pos_df.loc[df_index, "Or operator"] += or_input
                elif token.text == "and":
                    split_parts.append(current_part)
                    current_part = []
                    and_input = " "+ str(len(split_parts)-1)+ str(len(split_parts))
                    pos_df.loc[df_index, "And operator"] += and_input
                elif token.text == "nor":
                    split_parts.append(current_part)
                    current_part = []
                    and_input = " "+ str(len(split_parts)-1)+ str(len(split_parts))
                    pos_df.loc[df_index, "Or operator"] += and_input
                    pos_df.loc[df_index, "Not operator"] += str(index)+" or"
                

            elif  token.dep_ == 'cc'and found_verb == False:
                current_part.append(token)
            
                
            elif token.dep_ == "punct" and index < length and doc[token_index+1].text in {"therefore", "thus", "so"} and doc[token_index+1].dep_ != "mark":
                if len(current_part)>0:
                    split_parts.append(current_part)
                current_part = []
                found_verb = False
            elif token.dep_ == 'advmod':
                current_part.append(token)
        elif token.text not in {"either", "neither"}:  
            current_part.append(token)
        del remaining_text[0]

    new_sentences = []
    for split in split_parts:
        reconstructed_text = " ".join(token.text for token in split)
        new_sentences.append(reconstructed_text)
    return new_sentences, pos_df



def remove_last_word(text):
    words = text.split() 
    if len(words) > 1:
        return ' '.join(words[:-1]) 
    return ''  



def seperate_subjects(orTxt, df_index, pos_df):
    
    new_sentences = []
    final_sentences = []
    raw_subjects = []
    subjects = []
    add_to_second_subject = ""
    verb = None
    extra_stuff = ""
    before_stuff = ""
    conjunction = []
    
    for i, token in enumerate(orTxt):
        #print(f"Token: {token.text}, Type: {token.dep_}, Head: {token.head.text}")
        detected = False
        
        if i > 0 and verb != None:
            extra_stuff = f"{extra_stuff} {token.text}"  
            detected = True   
        
        elif token.dep_ == "advcl" or token.dep_ == "ROOT":
            
            verb = token.text
            detected = True 
            if i > 0 and orTxt[i - 1].dep_ == "aux":
                before_stuff = remove_last_word(before_stuff)
                verb = f"{orTxt[i - 1].text} {verb}"

            
        elif token.dep_ == "nsubj":
            detected = True 
            subject = token.text
            raw_subjects.append(subject)

            if i > 0 and orTxt[i - 1].dep_ == "amod" and orTxt[i - 1].head.text == token.text: # HAPPY cats
                before_stuff = remove_last_word(before_stuff)
                add_to_second_subject = f"{orTxt[i - 1].text}"
                subject = f"{orTxt[i - 1].text} {subject}"
                if i > 1 and orTxt[i - 2].dep_ == "det" and orTxt[i - 2].head.text == token.text: # THE happy cats
                    before_stuff = remove_last_word(before_stuff)
                    add_to_second_subject = f"{orTxt[i - 2].text} {add_to_second_subject}"
                    
                    subject = f"{orTxt[i - 2].text} {subject}"
            if i > 0 and orTxt[i - 1].dep_ == "det" and orTxt[i - 1].head.text == token.text: # THE cats
                before_stuff = remove_last_word(before_stuff)
                add_to_second_subject = f"{orTxt[i - 1].text}"
                subject = f"{orTxt[i - 1].text} {subject}"
            subjects.append(subject)

        elif token.dep_ == "conj" and token.head.text in raw_subjects:
            detected = True 
            second_subject = token.text
            raw_subjects.append(second_subject)
            if i > 0 and orTxt[i - 1].dep_ == "cc": # birds AND cats
                before_stuff = remove_last_word(before_stuff)
                second_subject = f"{add_to_second_subject} {second_subject}" 
                conjunction.append(orTxt[i - 1].text)
            elif i > 1 and orTxt[i - 1].dep_ == "amod" and orTxt[i - 1].head.text == token.text and orTxt[i - 2].dep_ == "cc": # birds and HAPPY cats
                before_stuff = remove_last_word(before_stuff)
                before_stuff = remove_last_word(before_stuff)
                second_subject = f"{orTxt[i - 1].text} {second_subject}" 
                conjunction.append(orTxt[i - 2].text)
            elif i > 2 and orTxt[i - 1].dep_ == "amod" and orTxt[i - 2].dep_ == "det" and orTxt[i - 3].dep_ == "cc": # birds and THE happy cats
                before_stuff = remove_last_word(before_stuff)
                before_stuff = remove_last_word(before_stuff)
                before_stuff = remove_last_word(before_stuff)
                second_subject = f"{orTxt[i - 2].text} {second_subject}"
                conjunction.append(orTxt[i - 3].text)
            elif i > 0 and orTxt[i - 1].dep_ == "det" and orTxt[i - 2].dep_ == "cc": # birds and THE cats
                before_stuff = remove_last_word(before_stuff)
                before_stuff = remove_last_word(before_stuff)
                second_subject = f"{orTxt[i - 1].text} {second_subject}"
                conjunction.append(orTxt[i - 2].text)
            subjects.append(second_subject)
        
        elif detected == False and token.dep_ != "preconj":
            before_stuff = f"{before_stuff} {token.text}"  
    
    #print(conjunction)
    
    for k,cc in enumerate(conjunction):
        if cc == "and":
            text = " "+str(k)+str(k+1)
            pos_df.loc[df_index, "And operator"] += text
        elif cc == "or":
            text = " "+str(k)+str(k+1)
            pos_df.loc[df_index, "Or operator"] += text
        elif cc == "nor":
            text = " "+str(k)+str(k+1)
            pos_df.loc[df_index, "Or operator"] += text
            pos_df.loc[df_index, "Not operator"] += " or"

    if len(subjects) <= 1:
        
        reconstructed_text = " ".join(token.text for token in orTxt)
        new_sentences.append(reconstructed_text)
        return new_sentences, pos_df
    
    for subject in subjects:
        new_sentences.append(f"{subject} {verb}")
    
    for sent in new_sentences:
        sent = f"{before_stuff} {sent}{extra_stuff}"
        final_sentences.append(sent)

    
    return final_sentences, pos_df


def seperate_objects(orTxt, df_index, pos_df):
    new_sentences = []
    final_sentences = []
    raw_objects = []
    objects = []
    add_to_second_subject = ""
    verb = None
    extra_stuff = ""
    before_stuff = ""
    conjunction = []
    for i, token in enumerate(orTxt):
        #print(f"Token: {token.text}, Type: {token.dep_}, Head: {token.head.text}")
        detected = False
        
        
        if token.dep_ == "advcl" or token.dep_ == "ROOT":
            verb = token.text
            detected = True 
            if i > 0 and orTxt[i - 1].dep_ == "aux":
                extra_stuff = remove_last_word(extra_stuff)
                verb = f"{orTxt[i - 1].text} {verb}"

        if i > 0 and verb == None:
            before_stuff = f"{before_stuff} {token.text}"  
            detected = True 
        
        elif (token.dep_ == "dobj" or token.dep_ == "attr" or token.dep_ == "acomp") and verb !=None:
            detected = True 
            subject = token.text
            raw_objects.append(subject)
            if i > 0 and orTxt[i - 1].dep_ == "det" and orTxt[i - 1].head.text == token.text: # THE cats
                before_stuff = remove_last_word(before_stuff)
                add_to_second_subject = f"{orTxt[i - 1].text}"
                subject = f"{orTxt[i - 1].text} {subject}"
            objects.append(subject)

        elif token.dep_ == "conj" and token.head.text in raw_objects:
            detected = True 
            second_subject = token.text
            raw_objects.append(second_subject)
            if i > 0 and orTxt[i - 1].dep_ == "cc": # birds AND cats
                before_stuff = remove_last_word(before_stuff)
                second_subject = f"{add_to_second_subject} {second_subject}" 
                conjunction.append(orTxt[i - 1].text)
            elif i > 0 and orTxt[i - 1].dep_ == "det" and orTxt[i - 2].dep_ == "cc": # birds and THE cats
                before_stuff = remove_last_word(before_stuff)
                before_stuff = remove_last_word(before_stuff)
                second_subject = f"{orTxt[i - 1].text} {second_subject}"
                conjunction.append(orTxt[i - 2].text)
            objects.append(second_subject)
        
        elif detected == False  and token.dep_ != "preconj":
            before_stuff = f"{before_stuff} {token.text}"  
    
    #print(conjunction)
    
    for k,cc in enumerate(conjunction):
        if cc == "and":
            text = " "+str(k)+str(k+1)
            pos_df.loc[df_index, "And operator"] += text
        elif cc == "or":
            text = " "+str(k)+str(k+1)
            pos_df.loc[df_index, "Or operator"] += text
        elif cc == "nor":
            text = " not "+str(k)+str(k+1)
            pos_df.loc[df_index, "Or operator"] += str(k)+str(k+1)
            pos_df.loc[df_index, "Not operator"] += " or"
    

    if len(objects) < 2:        
        reconstructed_text = " ".join(token.text for token in orTxt)
        new_sentences.append(reconstructed_text)
        return new_sentences, pos_df
    
    for subject in objects:
        new_sentences.append(f"{verb} {subject}")
    
    for sent in new_sentences:
        sent = f"{extra_stuff} {before_stuff} {sent}"
        final_sentences.append(sent)

    
    return final_sentences, pos_df



def add_to_subject(token_index,doc,df_index, pos_df):
    
    i = token_index
    index = str(i)

    universal_noun = ["everybody", "everyone", "all", "anyone", "everything", "anything"]
    existential_noun = ["nobody", "somebody", "someone", "something"]
    exi = existential 
    exi.append("a")
    exi.append("an")

    
    if doc[i].text in universal_noun:
        if i > 0 and doc[i - 1].text == "not": #not everybody is happy
            pos_df.loc[df_index, 'Not operator'] += " "+str(i - 1) + " exi"
            pos_df.loc[df_index, 'Existential quantifier'] += " "+str(i) + " subj"
        else:
            pos_df.loc[df_index, "Universal quantifier"] += " "+str(i) + " subj"
    elif doc[i].text in existential_noun:
        if doc[i].text == "nobody":
            pos_df.loc[df_index, 'Not operator'] += " "+str(i) + " exi"
            pos_df.loc[df_index, 'Existential quantifier'] += " "+str(i) + " subj"
        else:
            pos_df.loc[df_index, 'Existential quantifier'] += " "+str(i) + " subj"
    
    else:
   

        if i > 0 and doc[i - 1].dep_ == "amod" and doc[i - 1].head.text == token.text: # HAPPY cats
            index = str(i-1) + index
            if i > 1 and doc[i - 2].dep_ == "det" and doc[i - 2].head.text == token.text: # THE happy cats          
                if doc[i - 2].text in exi:
                    pos_df.loc[df_index, 'Existential quantifier'] += " "+str(i - 2) + " subj"
                    if doc[i - 2].text == "no":
                        pos_df.loc[df_index, 'Not operator'] += " "+str(i - 2) + " exi"
                elif doc[i - 2].text in universal:
                    if i>2 and doc[i - 3].text == "not":
                        pos_df.loc[df_index, "Universal quantifier"] += " "+str(i - 2) + " subj"
                        pos_df.loc[df_index, 'Not operator'] +=" "+str(i - 3) + " uni"
                    else:
                        pos_df.loc[df_index, "Universal quantifier"] += " "+str(i - 2) + " subj"

        elif i > 0 and doc[i - 1].dep_ == "det": # THE cats
            if doc[i - 1].text in exi:
                    pos_df.loc[df_index, 'Existential quantifier'] += " "+str(i-1) +" subj"
                    if doc[i - 1].text == "no":
                        pos_df.loc[df_index, 'Not operator'] += " "+str(i-1) +" exi"
            elif doc[i - 1].text in universal:
                if i>1 and doc[i - 2].text == "not":
                    pos_df.loc[df_index, "Universal quantifier"] +=  " "+str(i - 1)+ " subj"
                    pos_df.loc[df_index, 'Not operator'] += " "+str(i - 2) + " uni"
                else:
                    pos_df.loc[df_index, "Universal quantifier"] += " "+str(i-1) + " subj"
        
    
    pos_df.loc[df_index, "Subject"] = index
    return pos_df


def add_to_verb(i,doc,df_index,pos_df):
    
    index = str(i)

    if i > 0 and doc[i - 1].dep_ == "aux" and doc[i - 1].head.text == token.text:
        index = str(i-1) + index
    elif i > 1 and doc[i - 2].dep_ == "aux" and doc[i - 1].dep_ == "neg":
        index = str(i-2) + index
        pos_df.loc[df_index, 'Not operator'] +=" "+str(i-1) +" verb"
    elif i < len(doc)-1 and doc[i + 1].dep_ == "neg":
        pos_df.loc[df_index, 'Not operator'] +=" "+str(i+1) +" verb"
    elif i>0 and doc[i - 1].text == "never":
        pos_df.loc[df_index, 'Not operator'] +=" "+str(i-1) +" verb"
    pos_df.loc[df_index, "Verb"] = index
    return pos_df



def add_to_object(i,doc,df_index,pos_df):
    obj = doc[i].text
    index = str(i)
    universal_noun = ["everybody", "everyone", "all", "everything" ]
    existential_noun = ["nobody", "somebody", "someone", "anyone", "anything"]

    
    if doc[i].text in universal_noun: #I hate everyone
        pos_df.loc[df_index, "Universal quantifier"] += " "+str(i) + " obj"

    elif doc[i].text in existential_noun:
        if doc[i].text == "nobody":
            pos_df.loc[df_index, 'Not operator'] += " "+str(i) + " exi"
            pos_df.loc[df_index, 'Existential quantifier'] += " "+str(i) + " obj"
        else:
            pos_df.loc[df_index, 'Existential quantifier'] += " "+str(i) + " obj"
    
    else:
   
        if i > 0 and doc[i - 1].dep_ == "det" and doc[i - 1].head.text == token.text:
            if doc[i - 1].text in existential:
                pos_df.loc[df_index, 'Existential quantifier'] += " "+str(i-1) + " obj"
            elif doc[i - 1].text in universal:
                pos_df.loc[df_index, "Universal quantifier"] += " "+str(i-1) + " obj"
    pos_df.loc[df_index, "Obj"] = index
    
    return pos_df

def analize_clause(doc, df_index, pos_df):
    
    skip = False
    for i,toke in enumerate(doc):
        global token
        token = toke
        if token.dep_ == "auxpass" and ((i < len(doc)-1 and doc[i+1].dep_ == "ROOT") or (i < len(doc)-2 and doc[i+2].dep_ == "ROOT")) :
            pos_df.loc[df_index, "Verb"] = str(i)
            pos_df.loc[df_index, "Obj"] = str(i+1)
            if (i < len(doc)-2 and doc[i+2].dep_ == "ROOT")  and doc[i+1].dep_ == "neg":
                pos_df.loc[df_index, 'Not operator'] +=" "+str(i+1) +" verb"
            skip = True
        elif token.dep_ == "nsubj" or token.dep_ == "nsubjpass":
            pos_df = add_to_subject(i,doc,df_index,pos_df)
        elif token.dep_ == "ROOT" and not skip:
            pos_df = add_to_verb(i,doc,df_index,pos_df)
        elif token.dep_ == "acomp" or token.dep_ == "dobj":
            pos_df = add_to_object(i,doc,df_index,pos_df)
    return pos_df



def eliminate_extra_spaces(input_string):
    return re.sub(r'\s+', ' ', input_string).strip()


def clean_adjectives_and_auxiliaries(text):
    doc = nlp(text.strip())
    cleaned_words = []

    for token in doc:
        if (token.pos_ == "ADJ" or token.pos_ == "ADV") and token.text.lower() in {"very", "extremely", "too", "quite"}:
            continue
        
        cleaned_words.append(token.text)

    return " ".join(cleaned_words).strip()

def format_text(text):
    doc = nlp(text.strip())
    corrected_words = []
    for token in doc:
        if token.pos_ == "PROPN" or token.text == "I":
            corrected_words.append(token.text)
        elif token.pos_ =="NOUN" and token.text[0].isupper():
            corrected_words.append(token.text)
        else:
           # corrected_word = str(TextBlob(token.text).correct())
            corrected_word = token.text
            corrected_words.append(corrected_word.lower())

    corrected_text = " ".join(corrected_words)
    
    if corrected_text.endswith("."):
        corrected_text = corrected_text[:-1]

    return corrected_text.strip()

def adjust_verb_forms(text):
    doc = nlp(text.strip())
    corrected_words = []
    for i,token in enumerate(doc):
        if token.pos_ == "VERB" or token.dep_ == "ROOT":
            subject = [child for child in token.children if child.dep_ in {"nsubj", "nsubjpass"}]
            if subject:
                subject = subject[0]
                if ((subject.text.lower() in {"he", "she", "it"} and not token.text.endswith("s"))  or (subject.pos_ == "PROPN" and not token.text.endswith("s"))):
                    if (doc[i-1].dep_ != "aux" and (i>1 and doc[i-2].dep_ != "aux")):
                        corrected_words.append(token.text + "s")
                    else:
                        corrected_words.append(token.text)
                    continue
                elif subject.text.lower() == "i" and token.text.endswith("s"):
                    if token.lemma_ == "be":
                        corrected_words.append("am")
                    else:
                        corrected_words.append(token.text[:-1])
                    continue
                elif subject.text.lower() == "you" and token.text.endswith("s"):
                    if token.lemma_ == "be":
                        corrected_words.append("are")
                    else:
                        corrected_words.append(token.text[:-1])
                    continue
        corrected_words.append(token.text)

    return " ".join(corrected_words).strip()

def replace_pronouns(sentence: str) -> str:
    
    doc = nlp(sentence)
    
    proper_noun = None
    tokens = []
    
    for token in doc:
        if token.pos_ == "PROPN":  # Store the last encountered proper noun
            proper_noun = token.text
        
        if token.pos_ == "PRON" and proper_noun and token.text in {"he", "she"}:  # Replace pronoun with proper noun
            tokens.append(proper_noun)
        else:
            tokens.append(token.text)
    
    return " ".join(tokens)

def merge_compound_nouns(text):
    """
    Identifies compound nouns (e.g., "film director", "playback singer")
    and removes the space between them.
    
    Args:
        text (str): The input text.
    
    Returns:
        str: The modified text with compound nouns merged.
    """
    
    doc = nlp(text)
    
    new_tokens = []
    i = 0
    while i < len(doc):
        token = doc[i]
        if token.dep_ == "compound" and i + 1 < len(doc) and doc[i + 1].pos_ == "NOUN":
            
            merged_token = token.text + doc[i + 1].text
            new_tokens.append(merged_token)
            i += 2  
        else:
            new_tokens.append(token.text)
            i += 1

    return " ".join(new_tokens)

def remove_hyphens(text):
    return re.sub(r'(\b\w+)-(\w+\b)', r'\1\2', text)

def replace_all_the(text):
    
    return text.replace("all the", "all")


def add_all_to_plural_subject(text):
    """Adds 'all' before plural subjects that lack a determiner, considering adjectives."""
    doc = nlp(text)
    new_tokens = []
    i = 0

    while i < len(doc):
        token = doc[i]
        if token.pos_ == "NOUN" and token.tag_ == "NNS" and token.dep_ == "nsubj" and not token.text[0].isupper():
            if i > 0:
                if doc[i-1].pos_ == "ADJ":
                    if i > 1 and (doc[i-2].pos_ != "DET" or doc[i-2].text == "the") :
                        new_tokens.pop()
                        new_tokens.pop()
                        new_tokens.append("all")
                        new_tokens.append(doc[i-1].text)
                    elif i == 1:
                        new_tokens.pop()
                        new_tokens.append("all")
                        new_tokens.append(doc[i-1].text)
                elif doc[i-1].text == "the":
                    new_tokens.pop()
                    new_tokens.append("all")

            else:
                new_tokens.append("all")


            new_tokens.append(token.text)
            i += 1
        else:
            new_tokens.append(token.text)
            i += 1

    return " ".join(new_tokens)


def text_label(text):
    pos_df = pd.DataFrame(pos)
    df_index = 0

    
    text = remove_hyphens(text)
    text = format_text(text)
    text = clean_adjectives_and_auxiliaries(text)
    text = adjust_verb_forms(text)
    text = replace_all_the(text)
    text = replace_pronouns(text)
    text = merge_compound_nouns(text)
    text = add_all_to_plural_subject(text)


    pos_df.loc[df_index, "Full sentence"] = text
    pos_df.loc[df_index, "Height"] = 0
    pos_df.loc[df_index, "Direct parent"] = -1
    pos_df.fillna("", inplace=True)
    
    

    split_by_period, pos_df = check_period(text,df_index, pos_df)
    if len(split_by_period)>1:
        hold1 = df_index
    else:
        hold1 = -1
    for split1 in split_by_period:  
        
        if len(split_by_period)>1:
            #print(split1)
            df_index +=1  
            pos_df.loc[df_index, "Direct parent"] = hold1
        pos_df.loc[df_index, "Full sentence"] = split1
        pos_df.loc[df_index, "Height"] = 1
        pos_df.fillna("", inplace=True)
        
        split_by_iff, pos_df = check_iff(split1, df_index, pos_df)

        if len(split_by_iff) > 1:
            hold2 = df_index
        else:
            hold2 = hold1

        for split2 in split_by_iff:
            #print("2")
            
            split2 = nlp(split2)
            if len(split_by_iff) > 1:  
                #print(split2)
                df_index +=1
                pos_df.loc[df_index, "Direct parent"] = hold2
            pos_df.loc[df_index, "Full sentence"] = " ".join([token.text for token in split2])
            pos_df.loc[df_index, "Height"] = 2
            pos_df.fillna("", inplace=True)

            split_by_conj, pos_df = split_by_conjunctions(split2, df_index, pos_df)
            if  len(pos_df.loc[df_index, "Not operator"]) > 0:
                new_sentence = pos_df.loc[df_index, "Full sentence"]
                new_sentence = re.sub(r'\bNOT\b\s*', '', new_sentence)
                pos_df.loc[df_index, "Full sentence"] = new_sentence
                


            if len(split_by_conj) > 1:
                    hold3 = df_index
            else:
                hold3 = hold2

            for split3 in split_by_conj: 
                
                #print("3")
                split3 = eliminate_extra_spaces(split3)
                split3 = nlp(split3)
                if len(split_by_conj) > 1: 
                    #print(split3)   
                    df_index +=1
                    pos_df.loc[df_index, "Direct parent"] = hold3
                pos_df.loc[df_index, "Full sentence"] = " ".join([token.text for token in split3])
                pos_df.loc[df_index, "Height"] = 3
                pos_df.fillna("", inplace=True)

                split_by_subject, pos_df = seperate_subjects(split3, df_index, pos_df)

                if len(split_by_subject) > 1:
                    hold4 = df_index
                else:
                    hold4 = hold3
                for split4 in split_by_subject:
                    #print("4")
                    
                    split4 = eliminate_extra_spaces(split4)
                    split4 = nlp(split4)
                    if len(split_by_subject) > 1:
                        #print(split4)
                        df_index +=1
                        pos_df.loc[df_index, "Direct parent"] = hold4
                    pos_df.loc[df_index, "Full sentence"] = " ".join([token.text for token in split4])
                    pos_df.loc[df_index, "Height"] = 4
                    pos_df.fillna("", inplace=True)
                    
                    split_by_object, pos_df = seperate_objects(split4, df_index, pos_df)
                    
                    if len(split_by_object) > 1:
                        hold5 = df_index
                    else:
                        hold5 = hold4

                    for split5 in split_by_object:
                        split5 = eliminate_extra_spaces(split5)
                        split5 = nlp(split5)
                        if len(split_by_object) > 1:
                            #print(split5)
                            df_index +=1
                            pos_df.loc[df_index, "Direct parent"] = hold5
                        pos_df.loc[df_index, "Full sentence"] = " ".join([token.text for token in split5])
                        pos_df.loc[df_index, "Height"] = 5
                        pos_df.fillna("", inplace=True)
                        
                        pos_df = analize_clause(split5, df_index, pos_df)
    return pos_df
