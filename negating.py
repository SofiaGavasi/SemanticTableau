
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
    
    #checking for Universal in subject  (TODO: for object)
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
                        elif i == verb_index+1:
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




    #checking for Existential in subject  (TODO: for object)
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


# def negate_level_4(index,df,kb, curr_level, tree_index):
#     kb_new = []
    
#     tree_level = curr_level+1
    

#     text = str(df.loc[index, "Full sentence"])
#     var = nlp(text)
#     and_op = str(df.loc[index, "And operator"])
#     or_op = str(df.loc[index, "Or operator"])
#     # Finding the indices (in dataframe) of where the splitted sections are
#     list_indices = ""
#     for i in df['Direct parent'].index:
#         if df.at[i, 'Direct parent'] == index:
#            list_indices += str(i)

 
#     if and_op != "":
#         splits=[]
#         for i in range(1, len(and_op), 3):
#             split = list_indices[int(and_op[i])]+list_indices[int(and_op[i+1])]
#             splits.append(split)
#         kb1 = []
#         kb2 = []
#         for k in kb:
#             kb1.append(k)
#             kb2.append(k)
#         for i,split in enumerate(splits):
#             original_clause1 = negate_level_5(int(split[0]), df)
#             original_clause2 = negate_level_5(int(split[1]), df)
#             kb1.append(original_clause1)
#             kb2.append(original_clause2)
#         kb_new.append(kb1)
#         kb_new.append(kb2)         
#     if or_op != "":
#         splits=[]
#         for i in range(1, len(or_op), 3):
#             split = list_indices[int(or_op[i])]+list_indices[int(or_op[i+1])]
#             splits.append(split)
        
#         kb1 = []
#         for k in kb:
#             kb1.append(k)
#         for i,split in enumerate(splits):
                        
#             original_clause1 = negate_level_5(int(split[0]), df)
#             original_clause2 = negate_level_5(int(split[1]), df)            
#             kb1.append(original_clause1)
#             kb1.append(original_clause2)
           
#         kb_new.append(kb1)
    
#     for k in kb_new:
#         tree_df.loc[tree_index, "Tree level"] = tree_level
#         tree_df.loc[tree_index, "Sentence"] = k
#         tree_df.loc[tree_index, "Child index"] = ""
#         tree_index+=1
    
#     return kb_new, tree_index


# def negate_level_3(index,df, kb, curr_level, tree_index):
#     text = str(df.loc[index, "Full sentence"])
#     kb_new= []
#     previous_kb = kb
#     and_op = str(df.loc[index, "And operator"])
#     or_op = str(df.loc[index, "Or operator"])
#     initial_index = tree_index
#     curr_level = curr_level+1
    
#     # Finding the indices (in dataframe) of where the splitted sections are
#     list_indices = ""
#     list_heights = ""
#     for i in df['Direct parent'].index:
#         if df.at[i, 'Direct parent'] == index:
#            list_indices += str(i)
#            list_heights += str(int(df.loc[i, "Height"]))
#     if and_op != "":
#         splits=[]
#         heights =[]
#         kb1 = []
#         kb2 = []
#         for k in kb:
#             kb1.append(k)
#             kb2.append(k)
#         for i in range(1, len(and_op), 3):
#             split = list_indices[int(and_op[i])]+list_indices[int(and_op[i+1])]
#             height = list_heights[int(and_op[i])]+list_heights[int(and_op[i+1])]
#             splits.append(split)
#             heights.append(height)  
#         for i,split in enumerate(splits):
#             curr_height = heights[i]
                        
#             if int(curr_height[0]) == 5:
#                 original_clause1 = negate_level_5(int(split[0]), df)
#                 original_clause2 = negate_level_5(int(split[1]), df)
                
#             elif int(curr_height[0]) == 4:
#                 original_clause1, tree_index= negate_level_4(int(split[1]), df, kb, curr_level, tree_index)
#                 original_clause2, tree_index= negate_level_4(int(split[0]), df, kb, curr_level, tree_index)
#             kb1.append(original_clause1)
#             kb2.append(original_clause2)
#         kb_new.append(kb1)
#         kb_new.append(kb2)
            
                
#     if or_op != "":
#         splits=[]
#         heights =[]
#         kb1 = []
#         for k in kb:
#             kb1.append(k)
#         for i in range(1, len(or_op), 3):
#             split = list_indices[int(or_op[i])]+list_indices[int(or_op[i+1])]
#             height = list_heights[int(or_op[i])]+list_heights[int(or_op[i+1])]
#             splits.append(split)
#             heights.append(height)
#         for i,split in enumerate(splits):
            
#             curr_height = heights[i]
#             if int(curr_height[0]) == 5:
#                 original_clause1 = negate_level_5(int(split[0]), df)
#                 original_clause2 = negate_level_5(int(split[1]), df)
#                 kb1.append(original_clause1)
#                 kb1.append(original_clause2)
#                 kb_new.append(kb1)
                
#             elif int(curr_height[0]) == 4:
#                 pass_kb1 = negate_level_5(int(split[0]), df)
#                 pass_kb2 = negate_level_5(int(split[1]), df)
#                 previous_kb = kb
#                 previous_kb.append(pass_kb1)
#                 original_clause1, tree_index= negate_level_4(int(split[0]), df, previous_kb, curr_level, tree_index)
#                 previous_kb = kb
#                 previous_kb.append(pass_kb2)
#                 original_clause2, tree_index= negate_level_4(int(split[1]), df, previous_kb, curr_level, tree_index)
#                 kb_new.append(original_clause1)
#                 kb_new.append(original_clause2)
        

#     children = ""
#     for i in range(initial_index, tree_index):
#         children+=str(i)
        
#     while isinstance(kb_new, list) and len(kb_new) == 1:
#             kb_new = kb_new[0] 
#     for k in kb_new:
#         while isinstance(k, list) and len(k) == 1:
#             k = k[0] 
            
#         tree_df.loc[tree_index, "Tree level"] = curr_level
#         tree_df.loc[tree_index, "Sentence"] = k
#         c_indices = ""
#         for i in range(0,len(children)):
#             if tree_df.loc[int(children[i]), "Sentence"] in k:
#                 c_indices+=children[i]
#         tree_df.loc[tree_index, "Child index"] = c_indices
        
        
#         tree_index+=1
#     return kb_new
        
# def negate_level_2_ifthen(df, if_statement_index, then_statement_index):
     
#     kb_new = []
#     neg_then_statement = find_negation(then_statement_index, df)

#     kb_new.append(str(df.loc[if_statement_index, 'Full sentence']))
#     kb_new.append(neg_then_statement)
    
#     return kb_new
        
# def find_negation(index,df):
#     negation = ""
#     height = (int(df.loc[index, "Height"]))
#     if height == 5:
#         negation = negate_level_5(index,df)
#     elif height == 4:
#         negation = negate_level_4(index,df)
#     elif height == 3:
#         negation = negate_level_3(index,df)
    
#     return negation
    
# def rest_level_2(list_indices, or_split, and_split, ifthen_split, df):
#     new_sentences = []
#     kb_new = []
#     length = len(list_indices)
#     for i in range(0,length-1):
#         if str(list_indices[i]) in list_indices:
#             sent1 = int(list_indices[i])
#             sent2 = -1
#             and_statement1 = False
#             or_statement1 = False
#             if_statement1 = False
#             for split in and_split:
#                 if str(i) == split[0] and list_indices[int(split[1])] != "n":
#                     and_statement1 = True
#                     sent2 = int(split[1])
#             for split in or_split:
#                 if str(i) == split[0] and list_indices[int(split[1])] != "n":
#                     or_statement1 = True
#                     sent2 = int(split[1])
#             for split in ifthen_split:
#                 if str(i) == split[0] and list_indices[int(split[1])] != "n":
#                     if_statement1 = True
#                     sent2 = int(split[1])
#             if sent2 !=-1:
#                 sent2 = int(list_indices[sent2])
            
#             if and_statement1:
#                 neg1 = find_negation(sent1, df)
#                 neg2 = find_negation(sent2, df)
#                 list_indices.replace(str(sent1), "n")
#                 kb1 = []
#                 kb2 = []
#                 kb1.append(neg1)
#                 kb2.append(neg2)
#                 if kb1 not in kb_new: #this is wrong, need to add indices or smt
#                     kb_new.append(kb1)
#                 if kb2 not in kb_new:
#                     kb_new.append(kb2)
#             elif or_statement1:
#                 neg1 = find_negation(sent1, df)
#                 neg2 = find_negation(sent2, df)
#                 list_indices.replace(str(sent1), "n")
#                 if neg1 not in kb_new:
#                     kb_new.append(neg1)
#                 if neg2 not in kb_new:
#                     kb_new.append(neg2)
#             elif if_statement1:
#                 kb_new.append(negate_level_2_ifthen(df, sent1, sent2))
#                 list_indices.replace(str(sent1), "n")
                
#             else:
#                 list_indices.replace(str(sent1), "n")
#                 neg2 = find_negation(sent1, df)
#                 new_sentences.append(neg2)
    
    

#     return kb_new
        

# def negate_level_2(index,df,kb):
#     text = ""
#     new_sentences = []
#     list_indices = ""
#     list_heights = ""
#     for i in df['Direct parent'].index:
#         if df.at[i, 'Direct parent'] == index:
#            list_indices += str(i)
#            list_heights += str(int(df.loc[i, "Height"]))

#     original_text = str(df.loc[index, "Full sentence"])
#     ifthen_op = str(df.loc[index, "If-then operator"])
#     ifthen_split = ifthen_op.split()
#     and_op = str(df.loc[index, "And operator"])
#     and_split = and_op.split()
#     or_op = str(df.loc[index, "Or operator"])
#     or_split = or_op.split()
#     not_op = str(df.loc[index, "Not operator"])
#     not_split = not_op.split()

#     if len(not_split) >0:
#         # base case: only one
#         if len(not_split) == 2:
#             index_not = int(not_split[0])
#             if index_not ==0:
#                 return re.sub(r'\bNOT\b\s*', '', original_text)
#             else:
#                 negated_part = int(list_indices[index_not])
#                 negated_text = df.loc[negated_part, "Full sentence"]
#                 rest = ""
#                 for i in range(0, len(list_indices)):
#                     if i < index_not:
#                         rest +=str(int(list_indices[i]))
#                 negated_rest = rest_level_2(rest, or_split, and_split, ifthen_split, df)
#                 and_operator = False
#                 or_operator = False
#                 for split in and_split:
#                     if int(split[1]) == index_not:
#                         and_operator = True
#                 for split in or_split:
#                     if int(split[1]) == index_not:
#                         or_operator = True
#                 if and_operator:
#                     return negated_rest + " OR " + negated_text
#                 elif or_operator:
#                     return negated_rest + " AND " + negated_text
#         else: #if there are more, for now I assume the whole sentence in encapsulated within the it is not the case

#             texts = ""
            
#             for i,split in enumerate(not_split):
#                 and_operator = False
#                 or_operator = False
#                 if i % 2 == 0:
#                     print(i)
#                     index_not = int(not_split[0])
#                     text = re.sub(r'\bNOT\b\s*', '', str(df.loc[index_not, "Full sentence"]))
#                     for sp in and_split:
#                         if int(sp[0]) == index_not:
#                             and_operator = True
#                     for sp in or_split:
#                         if int(sp[0]) == index_not:
#                             or_operator = True
#                     if and_operator:
#                         if i < len(not_split)-2:
#                             texts += text + " OR "
#                         else:
#                             texts += text
#                     elif or_operator:
#                         if i < len(not_split)-2:
#                             texts += text + " AND "
#                         else:
#                             texts += text

#             return texts

#     else:
#         rest = rest_level_2(list_indices, or_split, and_split, ifthen_split, df)
        
#         return rest
        

#     return '. '.join(new_sentences)


# def negate_level_1(index,df):
#     #only iff
#     #for now just one iff
#     #¬(A↔B)≡(A∧¬B)∨(¬A∧B)
#     result = ""
#     new_sentences = []
#     list_indices = ""
#     list_heights = ""
#     for i in df['Direct parent'].index:
#         if df.at[i, 'Direct parent'] == index:
#            list_indices += str(i)
#            list_heights += str(int(df.loc[i, "Height"]))

#     original_text = str(df.loc[index, "Full sentence"])
#     iff_op = int(df.loc[index, "Iff operator"])
    
#     #assuming iff is 1 
#     child1 = int(list_indices[0])
#     child2 = int(list_indices[1])

#     or1 = str(df.loc[child1, "Full sentence"])
#     or2 = str(df.loc[child2, "Full sentence"])

#     child1_height = int(list_heights[0])
#     child2_height = int(list_heights[1])

#     neg1 = ""
#     if child1_height==2:
#         neg1 = negate_level_2(child1,df)
#     elif child1_height==3:
#         neg1 = negate_level_3(child1,df)
#     elif child1_height==4:  
#         neg1 = negate_level_4(child1,df)  
#     elif child1_height==5:
#         neg1 = negate_level_5(child1,df)
#     neg2 = ""
#     if child2_height==2:
#         neg2 = negate_level_2(child2,df)
#     elif child2_height==3:
#         neg2 = negate_level_3(child2,df)
#     elif child2_height==4:  
#         neg2 = negate_level_4(child2,df)  
#     elif child2_height==5:
#         neg2 = negate_level_5(child2,df)

#     text = or1 + " aND " +neg2+ " OR " +neg1 + " aND " + or2
#     return text



# def negate_level_0(index,df,kb): #TODO
#     #only .
#     result = ""
#     kb_new = []



# def negate_something(index,df):
#     result = ""
#     curr_level= -1
#     tree_index = 0
#     kb = []
#     if df.loc[index, "Height"] == 5:
#         new_sentence = negate_level_5(index,df)
#         print(new_sentence)
        
#     elif df.loc[index, "Height"] == 4:
        
#         new_sentence = negate_level_4(index,df,kb, curr_level, tree_index)
        
#     elif df.loc[index, "Height"] == 3:
#         new_sentence = negate_level_3(index,df, kb, curr_level, tree_index)
        
#     elif df.loc[index, "Height"] == 2:
#         new_sentence = negate_level_2(index,df,kb)
        

#     elif df.loc[index, "Height"] == 1:
#         new_sentence = negate_level_1(index,df, kb)
#         print(new_sentence)
    
#     elif df.loc[index, "Height"] == 0:
#         new_sentence = negate_level_0(index,df, kb)
#         print(new_sentence)
    

#     return new_sentence
