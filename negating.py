
import re
import pandas as pd
import spacy
nlp = spacy.load("en_core_web_sm")



#TODO all these methods need to be updated



def negate_level_5(index,df):
    text = str(df.loc[index, "Full sentence"])
    subj = int(df.loc[index, "Subject"])
    obj = df.loc[index, "Obj"]
   

    var = nlp(text)
    words = [token.text for token in var]

    verb_index = str(df.loc[index, "Verb"])
    if obj == "":
        obj = int(verb_index)+1
    negation_verb_index = -1
    negation_uni_index = -1
    negation_exi_index = -1

    all_negated = False

    not_op = str(df.loc[index, "Not operator"])
    not_op_split = not_op.split()
    for i,tok in enumerate(not_op_split):
        if tok == "verb" and i>0:
            negation_verb_index = int(not_op_split[i-1])
        if tok == "uni" and i>0:
            negation_uni_index = int(not_op_split[i-1])
        if tok == "exi" and i>0:
            negation_exi_index = int(not_op_split[i-1])
        if tok == "all":
            all_negated = True
        
    
    uni_quant = str(df.loc[index, "Universal quantifier"])
    uni_quant_split = uni_quant.split()
    
    
    exi_quant = str(df.loc[index, "Existential quantifier"])
    exi_quant_split = exi_quant.split()
    
    if "all" in not_op:
        return text
    
    #checking for Universal in subject  
    if uni_quant != "":
        if "subj" in uni_quant_split:   
            uni_index = -1
            for i,tok in enumerate(uni_quant_split):
                if tok == "subj" and i>0:
                    uni_index = int(uni_quant_split[i-1])

            
            if uni_index == subj: 
                if "verb" in not_op: #everyone is not happy -> everyone is happy
                    del words[negation_verb_index] 
                else: #everyone is happy -> someone is not happy
                    new_words = []
                    for i,word in enumerate(words):
                        if i == uni_index:
                            new_words.append("someone")
                        elif i == int(verb_index)+1:
                            new_words.append("not")
                        else:
                            new_words.append(word)
                    words = new_words


            if "verb" in not_op and  "uni" in not_op: # not all cats don't eat meat -> all cats don't eat meat
                if 0 <= negation_uni_index < len(words):
                    del words[negation_uni_index]  
            elif  "uni" in not_op:                     # not all cats eat meat  ->  all cats eat meat
                if 0 <= negation_uni_index < len(words):
                    del words[negation_uni_index]     
            elif "verb" in not_op:                     # all cats don't eat meat -> some cats eat meat
                words[uni_index] = "some"
                if 0 <= negation_verb_index < len(words):
                     del words[negation_verb_index] 
            else:                                       # all cats eat meat  ->  not all cats eat meat
                new_words = []
                for i,word in enumerate(words):
                    if i == uni_index:
                        new_words.append("not")
                    new_words.append(word)
                words = new_words
        
        
        elif "obj" in uni_quant_split:  # I don't hate anyone
            uni_index = -1
            for i,tok in enumerate(uni_quant_split):
                if tok == "obj" and i>0:
                    uni_index = int(uni_quant_split[i-1])
            
            if uni_index == obj: 
                if "verb" in not_op: # I don't hate everyone-> I do hate everyone
                    del words[negation_verb_index] 

                else: # I hate everyone -> I hate not someone
                    new_words = []
                    for i,word in enumerate(words):
                        if i == uni_index:
                            new_words.append("someone")
                        elif i == verb_index+1:
                            new_words.append("not")
                        else:
                            new_words.append(word)
                    words = new_words
            
             
            elif "verb" in not_op:                     # I don't hate every human -> I do hate every human
                if 0 <= negation_verb_index < len(words):
                     del words[negation_verb_index] 
            else:                                       # I hate every human -> I don't hate every human
                new_words = []
                for i,word in enumerate(words):
                    if i == uni_index:
                        new_words.append("not")
                    new_words.append(word)
                words = new_words




    #checking for Existential in subject  
    elif exi_quant != "":
        if "subj" in exi_quant_split:
            exi_index = -1
            for i,tok in enumerate(exi_quant_split):
                if tok == "subj" and i>0:
                    exi_index = int(exi_quant_split[i-1])



            
            if exi_index == subj and "exi" in not_op:
                if negation_exi_index != subj:  # not everyone is happy -> everyone is happy
                    del words[negation_exi_index]
                else:  #nobody is happy -> someone is happy
                    words[exi_index] = "someone"


            elif  "exi" in not_op and "verb" in not_op:  # no cats don't eat meat  ->  some cats don’t eat meat
                words[exi_index] = "some"
            elif  "exi" in not_op:                     # no cats eat meat  ->  some cats eat meat
                if 0 <= exi_index < len(words):
                    words[exi_index] = "some"
            elif  "verb" in not_op:                   # some cats don't eat meat  ->  all cats eat meat
                words[exi_index] = "every"
                if 0 <= negation_verb_index < len(words):
                     del words[negation_verb_index]
            else:                                       # some cats eat meat  ->  no cats eat meat
                if 0 <= exi_index < len(words):
                    words[exi_index] = "no"


        elif "obj" in exi_quant_split:  # I don't hate someone
            exi_index = -1
            for i,tok in enumerate(exi_quant_split):
                if tok == "obj" and i>0:
                    exi_index = int(exi_quant_split[i-1])
            
            if exi_index == obj: 
                if "verb" in not_op: # I don't hate someone/anyone > I do hate someone
                    words[obj] = "someone"
                    del words[negation_verb_index] 
                    

                else: # I hate someone -> I don't hate anyone
                    new_words = []
                    for i,word in enumerate(words):
                        if i == exi_index:
                            new_words.append("anyone")
                        elif i == verb_index+1:
                            new_words.append("not")
                        else:
                            new_words.append(word)
                    words = new_words
            elif  "verb" in not_op:                   #  I don't hate someone -> I do hate someone
                words[exi_index] = "every"
                if 0 <= negation_verb_index < len(words):
                     del words[negation_verb_index]
            else:                                       # I hate someone -> I don't hate anyone
                new_words = []
                for i,word in enumerate(words):
                    if i == exi_index:
                        new_words.append("anyone")
                    elif i == verb_index+1:
                        new_words.append("not")
                    else:
                        new_words.append(word)
                words = new_words
    
    #checking if the whole sentence is already negated (by looking if the verb is negated)
    elif "verb" in not_op:
        if 0 <= negation_verb_index < len(words):
            del words[negation_verb_index] 
    # Basic case: no quantifiers or operations
    elif all_negated == False:
        joined_words = ' '.join(words)
        joined_words = "it is not the case that "+joined_words
        return joined_words

    if all_negated:
        joined_words = ' '.join(words)
        return joined_words
    
    
    return ' '.join(words)
