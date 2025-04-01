
import pandas as pd
import spacy
nlp = spacy.load("en_core_web_sm")


from text_processing import text_label



def compare(true_st, false_st):

    s1_df = text_label(true_st)
    s2_df = text_label(false_st)
    true_st = s1_df.loc[0, "Full sentence"]
    false_st = s2_df.loc[0, "Full sentence"]

    

    words_1 = true_st.split()
    words_2 = false_st.split()

    subject_1_index = s1_df.loc[0, "Subject"]
    subject_2_index = s2_df.loc[0, "Subject"]
    if subject_1_index != None and subject_2_index != None :
        for i in subject_1_index:
            subject_1 = words_1[int(i)] + " "
        for i in subject_2_index:
            subject_2 = words_2[int(i)] + " "

        if subject_1.lower() != subject_2.lower(): #need to check this 
            return False
    else:
        print("MISSING SUBJECT")
        return False
    
    verb_1_index = s1_df.loc[0, "Verb"]
    verb_2_index = s2_df.loc[0, "Verb"]

    if verb_1_index == None or verb_2_index == None :
        print("MISSING VERB")
        return False
    else:
        verb_1_index = str(verb_1_index)
        verb_2_index = str(verb_2_index)
        verb_1 = ""
        verb_2 = ""

        if len(verb_1_index) > 1:
            verb_1_index = ((verb_1_index[len(verb_1_index)-1]))
        if len(verb_1_index) ==1:
            verb_1 = words_1[int(verb_1_index)]
        if len(verb_2_index) > 1:
            verb_2_index = ((verb_2_index[len(verb_2_index)-1]))
        if len(verb_2_index) ==1:
            verb_2 = words_2[int(verb_2_index)]
        
        doc = nlp(verb_1)
        for token in doc:
            verb_1 = token.lemma_

        doc = nlp(verb_2)
        for token in doc:
            verb_2 = token.lemma_



    if verb_1 != verb_2:
        return False
    else:

        obj_1_index = s1_df.loc[0, "Obj"]
        obj_2_index = s2_df.loc[0, "Obj"]

        if obj_1_index == "" or obj_2_index == "": #not sure if this is completely correct
            doc = nlp(verb_1)
            for tok in doc:
                if tok.lemma_ == "be":
                    obj_1_index = int(verb_1_index)+1
                    obj_2_index = int(verb_2_index)+1
                    
                    if len(words_1) <= obj_1_index or len(words_2) <= obj_2_index:
                        return True
                else:
                    return True
           
        
        obj1 = words_1[int(obj_1_index)]
        obj2 = words_2[int(obj_2_index)]
        if obj1 in {"the", "a"}:
                obj1 = words_1[int(obj_1_index)+1]
        if obj2 in {"the", "a"}:
                obj2 = words_2[int(obj_2_index)+1]

        obj1 = obj1.replace(".", "")
        obj2 = obj2.replace(".", "")

        doc1 = nlp(obj1)
        doc2 = nlp(obj2)
        lemma1 = doc1[0].lemma_ if doc1 else obj1  
        lemma2 = doc2[0].lemma_ if doc2 else obj2


        if lemma1 == lemma2: #need to check this
            return True

    return False




# txt1 = "I eat fish"
# txt2 = "I do eat fishes"
# print(compare(txt1, txt2))







#gets a leaf that is at the end of the tableau, compares what is in True side and False side, and updates the "Contradiction" part of the leaf dataframe with "True" or "False", and returns boolean contradiction
def find_contradictions(leaf): 
    true_part = leaf.value["True Statements"].iloc[0]
    false_part = leaf.value["False Statements"].iloc[0]
    contradiction = False

    #if leaf only has statements in one side, it can't have a contradiction 
    if len(true_part) == 0 or len(false_part) == 0:
        return contradiction, "", ""
    
    if isinstance(true_part, str): #if it's a string (so only one statement), I make it into an array to correctly loop through it
        new_part = []
        new_part.append(true_part)
        true_part = new_part
    if isinstance(false_part, str): 
        new_part = []
        new_part.append(false_part)
        false_part = new_part   
    
    for true_statement in true_part: #need to add return for WHICH statemnets cause the contardiction
        for false_statement in false_part:
            s1_df = text_label(true_statement)
            s2_df = text_label(false_statement)
            if check_sentence_same(s1_df.loc[0, "Full sentence"], s2_df.loc[0, "Full sentence"]):
                return True, true_statement, false_statement
            
            if s1_df.loc[0, "Height"] == 5 and s2_df.loc[0, "Height"] == 5 and s1_df.loc[0, "Universal quantifier"] == "" and s2_df.loc[0, "Universal quantifier"] == "" and s1_df.loc[0, "Existential quantifier"] == "" and s2_df.loc[0, "Existential quantifier"] == ""   :
                contradiction = compare(true_statement, false_statement)
                if contradiction:
                    return True, true_statement, false_statement
            
    
    return False, "", ""


def check_sentence_same(true_statement, false_statement):
    true = []
    for word in true_statement:
        true.append(word.lower())
    false = []
    for word in false_statement:
        false.append(word.lower())
    
    if true == false:
        return True
    return False